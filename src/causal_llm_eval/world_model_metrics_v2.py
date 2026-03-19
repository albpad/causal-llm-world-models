#!/usr/bin/env python3
"""
World Model Evaluation Metrics — v2
=====================================
Corrected framework that penalises consistent wrongness.

Key fix over v1:
    v1 treated Quality and Solidity as independent axes. This caused a model
    that is *consistently wrong* (high split-half agreement on non-detected
    edges) to score artificially well on Solidity. Llama 3.1-8B's 85.7%
    split-half agreement was mostly agreement on ABSENT edges — the metric
    rewarded systematic blindness.

    v2 decomposes consistency into:
      - VERIDICAL CONSISTENCY:   stable AND correct vs gold standard (reward)
      - CONFABULATORY RIGIDITY:  stable AND wrong vs gold standard (penalty)

    Only veridical consistency contributes positively. Confabulatory rigidity
    is a red flag — it means the model has solidified incorrect causal beliefs.

Five evaluation dimensions (no longer independent):
    1. COVERAGE        — fraction of gold-standard edges recovered
    2. FIDELITY        — direction accuracy + SID on recovered edges
    3. VERIDICAL STABILITY — of correctly recovered edges, run-to-run consistency
    4. DISCRIMINABILITY — SNR (causal vs null perturbation response)
    5. CONFABULATORY RIGIDITY — systematic wrong consistency (penalty)

Composite:
    World Model Score (WMS) integrates all five, with confabulatory rigidity
    acting as a multiplicative penalty rather than an independent axis.
    In the final study, however, primary interpretation should still rely on
    the individual domain metrics rather than on a single scalar summary.

References:
    - Craik (1943): cognition builds "small-scale models" of reality
    - Peters & Bühlmann (2015): SID for causal graph evaluation
    - Ferrari et al. (2025): Delphi consensus as gold standard
    - Lake, Ullman, Tenenbaum (2017): causal models for generalisation
"""

import json, math, argparse
from pathlib import Path
from collections import defaultdict, Counter
from dataclasses import dataclass, field, asdict
from typing import Optional, Dict, List, Tuple, Set
import numpy as np

try:
    from .json_utils import dump_json
except ImportError:
    from json_utils import dump_json


# =====================================================================
# DATA STRUCTURES
# =====================================================================

@dataclass
class WorldModelMetrics:
    """Complete world model evaluation for one model."""
    model: str = ""

    # --- 1. COVERAGE ---
    n_gold_edges: int = 0              # Total gold standard edges
    n_hard_detected: int = 0           # Detected at hard threshold
    n_soft_detected: int = 0           # Detected at soft threshold
    n_not_detected: int = 0            # Not detected at all
    hard_recall: float = 0.0
    soft_recall: float = 0.0

    # --- 2. FIDELITY ---
    sid: int = 0                       # Structural Intervention Distance (errors)
    sid_total: int = 0                 # Total interventional predictions tested
    sid_normalised: float = 0.0        # SID / total
    direction_accuracy: float = 0.0    # Of detected edges, fraction with correct direction
    n_correct_direction: int = 0
    n_wrong_direction: int = 0

    # --- 3. VERIDICAL STABILITY ---
    # Split-half: only on CORRECTLY detected edges
    veridical_split_half: float = 0.0  # Agreement rate on gold-matched edges
    veridical_n_edges: int = 0         # Number of gold-matched edges evaluated
    # Edge entropy: only on correctly detected edges
    veridical_entropy: float = 0.0     # Mean normalised entropy of correct edges
    veridical_flip_rate: float = 0.0   # Flip rate on correct edges

    # --- 4. DISCRIMINABILITY ---
    snr: float = 0.0                   # Signal-to-noise ratio
    mean_causal_jsd: float = 0.0
    mean_null_jsd: float = 0.0
    null_jsd_95: float = 0.0
    detection_power: float = 0.0       # Fraction of causal signals above noise floor

    # --- 5. CONFABULATORY RIGIDITY ---
    # Split-half on INCORRECTLY non-detected (or wrong-direction) edges
    confab_split_half: float = 0.0     # Agreement rate on gold-UNMATCHED edges
    confab_n_edges: int = 0            # Number of wrong edges evaluated
    confab_entropy: float = 0.0        # Mean entropy of wrong edges (low = rigid)
    confab_rigidity_score: float = 0.0 # 0-1, how rigidly wrong (higher = worse)

    # --- OVERALL SPLIT-HALF (for reference) ---
    raw_split_half: float = 0.0        # Original uncorrected split-half
    raw_split_half_shd: float = 0.0

    # --- COMPOSITE ---
    coverage_score: float = 0.0        # 0-1
    fidelity_score: float = 0.0        # 0-1
    stability_score: float = 0.0       # 0-1 (veridical only)
    discriminability_score: float = 0.0 # 0-1
    rigidity_penalty: float = 0.0      # 0-1, deducted from composite
    wms: float = 0.0                   # World Model Score (final)
    wms_label: str = ""


# =====================================================================
# 1. COVERAGE & FIDELITY (from existing kg2_enhanced data)
# =====================================================================

def compute_coverage_fidelity(kg2_enhanced_data, battery_items, edge_tests):
    """
    Compute coverage and fidelity from the KG2 enhanced comparison data.

    Also returns sets of edge IDs classified as correct vs incorrect,
    needed for the veridical/confabulatory decomposition.
    """
    results = {}

    # Also compute SID
    sid_results = _compute_sid(edge_tests, battery_items)

    for model, edges in kg2_enhanced_data.items():
        m = WorldModelMetrics(model=model)
        m.n_gold_edges = len(edges)

        correct_edges: Set[str] = set()   # Edges matching gold standard
        incorrect_edges: Set[str] = set() # Edges NOT matching gold standard

        for eid, e in edges.items():
            detected = e.get("detected", False)
            soft = e.get("soft_detected", False)
            dir_correct = e.get("direction_correct")

            if detected:
                m.n_hard_detected += 1
            if soft:
                m.n_soft_detected += 1
            if not soft and not detected:
                m.n_not_detected += 1

            # Classify edge as veridical or confabulatory
            # An edge is "veridical" if:
            #   - It is detected (soft or hard) AND direction is correct
            # An edge is "confabulatory" if:
            #   - It is NOT detected (model misses a real edge), OR
            #   - It IS detected but direction is wrong
            if (detected or soft) and dir_correct is True:
                correct_edges.add(eid)
                m.n_correct_direction += 1
            else:
                incorrect_edges.add(eid)
                if (detected or soft) and dir_correct is False:
                    m.n_wrong_direction += 1

        m.hard_recall = m.n_hard_detected / m.n_gold_edges if m.n_gold_edges > 0 else 0
        m.soft_recall = m.n_soft_detected / m.n_gold_edges if m.n_gold_edges > 0 else 0

        # Direction accuracy (of detected edges)
        n_dir_tested = m.n_correct_direction + m.n_wrong_direction
        m.direction_accuracy = m.n_correct_direction / n_dir_tested if n_dir_tested > 0 else 0

        # SID
        if model in sid_results:
            sd = sid_results[model]
            m.sid = sd["wrong"]
            m.sid_total = sd["total"]
            m.sid_normalised = sd["wrong"] / sd["total"] if sd["total"] > 0 else 1.0

        results[model] = (m, correct_edges, incorrect_edges)

    return results


def _compute_sid(edge_tests, battery_items):
    """SID computation (unchanged from v1)."""
    by_pert_model = defaultdict(list)
    for t in edge_tests:
        by_pert_model[(t["pert_id"], t["model"])].append(t)

    results = {}
    for (pert_id, model), tests in by_pert_model.items():
        if model not in results:
            results[model] = {"wrong": 0, "total": 0, "details": []}

        pert_item = battery_items.get(pert_id)
        if not pert_item or pert_item.get("type") in ("baseline", "null"):
            continue

        exp_rec = set(tests[0].get("exp_rec", []))
        exp_exc = set(tests[0].get("exp_exc", []))
        target_treatments = exp_rec | exp_exc

        for t in tests:
            tx = t["treatment"]
            if tx not in target_treatments:
                continue

            results[model]["total"] += 1
            base_rate = t.get("base_rec_rate", 0)
            pert_rate = t.get("pert_rec_rate", 0)
            significant = t.get("significant", False)

            wrong = False
            reason = ""
            if tx in exp_exc:
                if not significant:
                    wrong, reason = True, "no_shift_when_expected"
                elif pert_rate >= base_rate:
                    wrong, reason = True, "wrong_direction"
            elif tx in exp_rec:
                if significant and pert_rate < base_rate - 0.15:
                    wrong, reason = True, "unexpected_reduction"

            if wrong:
                results[model]["wrong"] += 1
            results[model]["details"].append({
                "pert_id": pert_id, "treatment": tx,
                "expected": "exclude" if tx in exp_exc else "maintain",
                "base_rate": base_rate, "pert_rate": pert_rate,
                "significant": significant, "wrong": wrong, "reason": reason,
            })

    return results


# =====================================================================
# 2. VERIDICAL vs CONFABULATORY SPLIT-HALF
# =====================================================================

def compute_decomposed_split_half(all_parsed, battery_items, edge_tests,
                                   correct_edges, incorrect_edges,
                                   kg2_enhanced_edges,
                                   n_splits=100, seed=42):
    """
    Split-half reliability decomposed into veridical and confabulatory components.

    For each random split of runs into halves A and B:
        - Build independent KGs from each half
        - For each edge, check if both halves agree on detection status
        - Cross-reference with gold standard:
            * Agreement on CORRECT edges → veridical consistency
            * Agreement on INCORRECT edges → confabulatory rigidity

    The key insight: if both halves agree an edge is absent, that's only
    "good reliability" if the edge SHOULD be absent in the gold standard.
    If it's a gold-standard edge that both halves miss → confabulatory rigidity.
    """
    rng = np.random.default_rng(seed)

    # Group parsed results by (item_id, model, run_idx)
    by_item_model = defaultdict(lambda: defaultdict(list))
    for p in all_parsed:
        key = (p["item_id"], p["model_name"])
        run_idx = p.get("run_idx", 0)
        by_item_model[key][run_idx].append(p)

    models = set(p["model_name"] for p in all_parsed)

    results = {}
    for model in models:
        all_runs = set()
        for (iid, mn), runs_dict in by_item_model.items():
            if mn == model:
                all_runs.update(runs_dict.keys())
        all_runs = sorted(all_runs)

        if len(all_runs) < 4:
            results[model] = {
                "raw_agreement": 0, "veridical_agreement": 0,
                "confab_agreement": 0, "n_splits": 0,
                "note": "Too few runs"
            }
            continue

        raw_agreements = []
        veridical_agreements = []
        confab_agreements = []
        shd_values = []

        # Get the set of gold-standard edge IDs this model should detect
        model_correct = correct_edges.get(model, set())
        model_incorrect = incorrect_edges.get(model, set())

        # Map from edge_justification IDs to whether they correspond to
        # correct or incorrect edges in the gold standard
        # We need to know which perturbation-treatment pairs correspond to
        # which gold-standard edges
        gold_edge_map = _build_gold_edge_map(
            battery_items, kg2_enhanced_edges.get(model, {}))

        for _ in range(n_splits):
            perm = rng.permutation(len(all_runs))
            half_size = len(all_runs) // 2
            runs_a = set(all_runs[i] for i in perm[:half_size])
            runs_b = set(all_runs[i] for i in perm[half_size:])

            edges_a = _detect_edges_for_runs(
                by_item_model, model, runs_a, battery_items)
            edges_b = _detect_edges_for_runs(
                by_item_model, model, runs_b, battery_items)

            all_edge_ids = set(edges_a.keys()) | set(edges_b.keys())
            if not all_edge_ids:
                continue

            total = 0
            agree = 0
            veridical_agree = 0
            veridical_total = 0
            confab_agree = 0
            confab_total = 0
            shd = 0

            for edge_id in all_edge_ids:
                det_a = edges_a.get(edge_id, False)
                det_b = edges_b.get(edge_id, False)
                total += 1

                # Is this edge in the gold standard as correct or incorrect?
                gold_status = gold_edge_map.get(edge_id)

                if det_a == det_b:
                    agree += 1

                    if gold_status == "correct":
                        # Both halves agree on a correct edge
                        veridical_total += 1
                        veridical_agree += 1
                    elif gold_status == "incorrect":
                        # Both halves agree on an incorrect edge
                        # (e.g., both miss a real edge, or both "detect"
                        # a spurious one consistently)
                        confab_total += 1
                        confab_agree += 1
                    else:
                        # Edge not in gold standard map (e.g., not a gold edge)
                        # Count as neutral
                        pass
                else:
                    shd += 1
                    if gold_status == "correct":
                        veridical_total += 1
                    elif gold_status == "incorrect":
                        confab_total += 1

            raw_agreements.append(agree / total if total > 0 else 0)
            veridical_agreements.append(
                veridical_agree / veridical_total if veridical_total > 0 else 0)
            confab_agreements.append(
                confab_agree / confab_total if confab_total > 0 else 0)
            shd_values.append(shd)

        results[model] = {
            "raw_agreement": float(np.mean(raw_agreements)) if raw_agreements else 0,
            "raw_shd_mean": float(np.mean(shd_values)) if shd_values else 0,
            "raw_shd_std": float(np.std(shd_values)) if shd_values else 0,
            "veridical_agreement": float(np.mean(veridical_agreements)) if veridical_agreements else 0,
            "veridical_std": float(np.std(veridical_agreements)) if veridical_agreements else 0,
            "confab_agreement": float(np.mean(confab_agreements)) if confab_agreements else 0,
            "confab_std": float(np.std(confab_agreements)) if confab_agreements else 0,
            "n_splits": len(raw_agreements),
        }

    return results


def _build_gold_edge_map(battery_items, kg2_edges):
    """
    Map edge_justification IDs from the battery to 'correct' or 'incorrect'
    based on the kg2_enhanced evaluation.

    An edge_justification ID appears in perturbation items. We check if the
    corresponding gold-standard edge was correctly detected.
    """
    gold_map = {}

    # kg2_edges is {edge_id: {detected, soft_detected, direction_correct, ...}}
    correct_edge_ids = set()
    incorrect_edge_ids = set()

    for eid, e in kg2_edges.items():
        det = e.get("detected", False) or e.get("soft_detected", False)
        dir_ok = e.get("direction_correct", False)
        if det and dir_ok:
            correct_edge_ids.add(eid)
        else:
            incorrect_edge_ids.add(eid)

    # Map perturbation edge_justification to gold status
    for item_id, item in battery_items.items():
        if item.get("type") == "baseline":
            continue
        edges = item.get("edge_justification", [])
        for edge_id in edges:
            if edge_id in correct_edge_ids:
                gold_map[edge_id] = "correct"
            elif edge_id in incorrect_edge_ids:
                gold_map[edge_id] = "incorrect"
            # If not in kg2 at all, leave unmapped

    return gold_map


def _detect_edges_for_runs(by_item_model, model, run_set, battery_items):
    """Lightweight edge detection using a subset of runs (unchanged from v1)."""
    count_tables = {}
    for (iid, mn), runs_dict in by_item_model.items():
        if mn != model:
            continue
        table = defaultdict(lambda: defaultdict(int))
        n_included = 0
        for run_idx, parsed_list in runs_dict.items():
            if run_idx not in run_set:
                continue
            n_included += 1
            for p in parsed_list:
                for s in p["stances"]:
                    table[s["treatment"]][s["stance"]] += 1
                    table[s["treatment"]]["total"] += 1
        if n_included > 0:
            count_tables[iid] = dict(table)

    edge_detections = {}
    for pert_item in battery_items.values():
        if pert_item.get("type") == "baseline":
            continue
        base_id = pert_item.get("baseline_id")
        if not base_id:
            continue
        edges = pert_item.get("edge_justification", [])
        exp_rec = set(pert_item.get("expected_recommendations", []))
        exp_exc = set(pert_item.get("expected_excluded", []))
        target_tx = exp_rec | exp_exc

        base_table = count_tables.get(base_id, {})
        pert_table = count_tables.get(pert_item["id"], {})
        if not base_table or not pert_table:
            continue

        for tx in target_tx:
            base_rec = base_table.get(tx, {}).get("recommended", 0)
            base_total = base_table.get(tx, {}).get("total", 0)
            pert_rec = pert_table.get(tx, {}).get("recommended", 0)
            pert_total = pert_table.get(tx, {}).get("total", 0)
            if base_total < 2 or pert_total < 2:
                continue

            base_rate = base_rec / base_total
            pert_rate = pert_rec / pert_total
            shift = abs(pert_rate - base_rate)

            for edge_id in edges:
                if edge_id not in edge_detections:
                    edge_detections[edge_id] = {"shifts": [], "detected_count": 0,
                                                 "total_count": 0}
                edge_detections[edge_id]["shifts"].append(shift)
                edge_detections[edge_id]["total_count"] += 1
                if shift > 0.25:
                    edge_detections[edge_id]["detected_count"] += 1

    result = {}
    for edge_id, data in edge_detections.items():
        if data["total_count"] > 0:
            rate = data["detected_count"] / data["total_count"]
            result[edge_id] = rate > 0.5
        else:
            result[edge_id] = False

    return result


# =====================================================================
# 3. DECOMPOSED EDGE ENTROPY
# =====================================================================

def compute_decomposed_entropy(all_parsed, battery_items,
                                correct_edges_by_model, incorrect_edges_by_model,
                                kg2_enhanced_data):
    """
    Edge consistency entropy decomposed into veridical and confabulatory.

    For correct edges: low entropy = good (stable correct beliefs)
    For incorrect edges: low entropy = BAD (rigid wrong beliefs)
    """
    # Build mapping: which (item_id, treatment) pairs correspond to correct edges?
    item_tx_gold_map = {}
    for model, kg2_edges in kg2_enhanced_data.items():
        model_map = {}
        correct_eids = correct_edges_by_model.get(model, set())

        for item_id, item in battery_items.items():
            if item.get("type") == "baseline":
                continue
            edge_ids = item.get("edge_justification", [])
            exp_rec = set(item.get("expected_recommendations", []))
            exp_exc = set(item.get("expected_excluded", []))

            for tx in exp_rec | exp_exc:
                # This (item, tx) pair tests edges in edge_ids
                # If any of those edges are in correct set, classify as veridical
                has_correct = any(eid in correct_eids for eid in edge_ids)
                model_map[(item_id, tx)] = "correct" if has_correct else "incorrect"

        item_tx_gold_map[model] = model_map

    # Group stances by (item_id, model, treatment)
    stance_counts = defaultdict(lambda: Counter())
    for p in all_parsed:
        for s in p["stances"]:
            key = (p["item_id"], p["model_name"], s["treatment"])
            stance_counts[key][s["stance"]] += 1

    results = {}
    for model in set(p["model_name"] for p in all_parsed):
        veridical_entropies = []
        confab_entropies = []
        all_entropies = []
        veridical_flips = {"flips": 0, "total": 0}
        confab_flips = {"flips": 0, "total": 0}

        model_gold = item_tx_gold_map.get(model, {})

        for (iid, mn, tx), counts in stance_counts.items():
            if mn != model:
                continue
            total = sum(counts.values())
            if total < 3:
                continue

            probs = np.array([c / total for c in counts.values()])
            entropy = float(-np.sum(probs * np.log2(probs + 1e-12)))
            n_cats = len(counts)
            max_ent = math.log2(n_cats) if n_cats > 1 else 1.0
            norm_ent = entropy / max_ent if max_ent > 0 else 0.0

            all_entropies.append(norm_ent)
            is_flip = counts.most_common(1)[0][1] / total < 0.8

            # Classify
            gold_status = model_gold.get((iid, tx))
            if gold_status == "correct":
                veridical_entropies.append(norm_ent)
                veridical_flips["total"] += 1
                if is_flip:
                    veridical_flips["flips"] += 1
            elif gold_status == "incorrect":
                confab_entropies.append(norm_ent)
                confab_flips["total"] += 1
                if is_flip:
                    confab_flips["flips"] += 1

        results[model] = {
            "overall_mean_entropy": float(np.mean(all_entropies)) if all_entropies else 0,
            "veridical_mean_entropy": float(np.mean(veridical_entropies)) if veridical_entropies else 0,
            "veridical_n": len(veridical_entropies),
            "veridical_flip_rate": (veridical_flips["flips"] / veridical_flips["total"]
                                     if veridical_flips["total"] > 0 else 0),
            "confab_mean_entropy": float(np.mean(confab_entropies)) if confab_entropies else 0,
            "confab_n": len(confab_entropies),
            "confab_flip_rate": (confab_flips["flips"] / confab_flips["total"]
                                  if confab_flips["total"] > 0 else 0),
        }

    return results


# =====================================================================
# 4. SIGNAL-TO-NOISE RATIO (unchanged from v1)
# =====================================================================

def compute_snr(edge_tests):
    """SNR = mean JSD(causal) / mean JSD(null)."""
    model_data = defaultdict(lambda: {"causal_jsds": [], "null_jsds": []})

    for t in edge_tests:
        model = t["model"]
        jsd = t.get("jsd", 0)
        tx = t["treatment"]
        target_tx = set(t.get("exp_rec", [])) | set(t.get("exp_exc", []))

        if t.get("type") == "null":
            model_data[model]["null_jsds"].append(jsd)
        elif tx in target_tx:
            model_data[model]["causal_jsds"].append(jsd)

    results = {}
    for model, data in model_data.items():
        causal = np.array(data["causal_jsds"]) if data["causal_jsds"] else np.array([0])
        null = np.array(data["null_jsds"]) if data["null_jsds"] else np.array([0])

        mean_causal = float(np.mean(causal))
        mean_null = float(np.mean(null)) if len(null) > 0 else 0.001
        null_95 = float(np.percentile(null, 95)) if len(null) > 0 else 0.0

        snr = mean_causal / max(mean_null, 0.001)
        above_noise = float(np.mean(causal > null_95)) if null_95 > 0 else 0.0

        results[model] = {
            "snr": snr,
            "mean_causal_jsd": mean_causal,
            "mean_null_jsd": float(np.mean(null)),
            "null_jsd_95": null_95,
            "detection_power": above_noise,
            "n_causal": len(data["causal_jsds"]),
            "n_null": len(data["null_jsds"]),
        }

    return results


# =====================================================================
# 5. COMPOSITE SCORING — WORLD MODEL SCORE (WMS)
# =====================================================================

def compute_composite(metrics: WorldModelMetrics) -> float:
    """
    Compute World Model Score (WMS).

    The score integrates five dimensions:

    1. COVERAGE (weight 0.25):
       Soft recall — fraction of gold edges recovered at soft threshold.

    2. FIDELITY (weight 0.25):
       Weighted combination of direction accuracy and (1 - SID_normalised).
       A model that detects edges but gets directions wrong loses fidelity.

    3. VERIDICAL STABILITY (weight 0.20):
       Split-half agreement ONLY on correctly detected edges, adjusted by
       veridical edge entropy (low entropy on correct edges = stable truth).

    4. DISCRIMINABILITY (weight 0.15):
       SNR capped at 5, plus detection power.

    5. CONFABULATORY RIGIDITY PENALTY (weight 0.15):
       Applied as a *subtraction*. High confabulatory agreement (consistent
       wrongness) with low confab entropy (rigid wrongness) = maximum penalty.
       This directly addresses the Llama problem: 85.7% agreement driven by
       systematic failure to detect 51/55 edges is now penalised.

    WMS = coverage + fidelity + stability + discriminability - rigidity_penalty
    All bounded to [0, 1].
    """
    # 1. Coverage
    coverage = metrics.soft_recall
    metrics.coverage_score = coverage

    # 2. Fidelity
    dir_acc = metrics.direction_accuracy
    sid_inv = max(0, 1.0 - metrics.sid_normalised)
    fidelity = 0.5 * dir_acc + 0.5 * sid_inv
    # But if nothing detected, fidelity is meaningless — scale by coverage
    fidelity *= min(1.0, metrics.soft_recall / 0.1) if metrics.soft_recall > 0 else 0
    metrics.fidelity_score = fidelity

    # 3. Veridical stability
    ver_split = metrics.veridical_split_half
    ver_ent_bonus = max(0, 1.0 - metrics.veridical_entropy)  # Low entropy = stable
    stability = 0.6 * ver_split + 0.4 * ver_ent_bonus
    # Scale by number of veridical edges (if none, stability = 0)
    if metrics.veridical_n_edges < 3:
        stability *= metrics.veridical_n_edges / 3.0
    metrics.stability_score = stability

    # 4. Discriminability
    snr_score = min(metrics.snr / 5.0, 1.0) if metrics.snr > 0 else 0
    disc = 0.6 * snr_score + 0.4 * metrics.detection_power
    metrics.discriminability_score = disc

    # 5. Confabulatory rigidity penalty
    # High confab_split_half + low confab_entropy = rigidly wrong
    confab_consistency = metrics.confab_split_half
    confab_rigidity = max(0, 1.0 - metrics.confab_entropy)  # Low entropy = rigid
    # Penalty scales with both consistency and rigidity AND number of wrong edges
    # More wrong edges = more penalty
    wrong_fraction = metrics.confab_n_edges / max(1, metrics.n_gold_edges)
    penalty = confab_consistency * confab_rigidity * wrong_fraction
    # Also penalize pathological SNR (< 1 means responding more to noise)
    if metrics.snr < 1.0 and metrics.snr > 0:
        snr_penalty = (1.0 - metrics.snr) * 0.5  # Up to 0.5 extra penalty
        penalty = min(1.0, penalty + snr_penalty)
    metrics.rigidity_penalty = min(penalty, 1.0)

    # Weighted composite
    raw = (0.25 * coverage +
           0.25 * fidelity +
           0.20 * stability +
           0.15 * disc -
           0.15 * metrics.rigidity_penalty)

    # Bound to [0, 1]
    wms = max(0.0, min(1.0, raw))
    metrics.wms = wms
    metrics.wms_label = _label_wms(wms)

    return wms


def _label_wms(wms: float) -> str:
    """Qualitative label for World Model Score."""
    if wms >= 0.75:
        return "Strong world model"
    elif wms >= 0.50:
        return "Moderate world model"
    elif wms >= 0.30:
        return "Weak world model"
    elif wms >= 0.15:
        return "Fragmentary world model"
    else:
        return "No coherent world model"


# =====================================================================
# 6. MAIN PIPELINE
# =====================================================================

def compute_world_model_metrics_v2(all_parsed, edge_tests, battery_items,
                                    kg2_enhanced_data, output_dir=None):
    """
    Run the v2 world model evaluation pipeline.

    Parameters:
        all_parsed: list of parsed results
        edge_tests: list from detect_edges()
        battery_items: dict {item_id: item_dict}
        kg2_enhanced_data: dict {model: {edge_id: edge_dict}}
        output_dir: path to save outputs

    Returns:
        dict {model: WorldModelMetrics}
    """
    print("=" * 70)
    print("WORLD MODEL EVALUATION v2 (corrected)")
    print("Decomposes consistency into veridical vs confabulatory")
    print("=" * 70)

    # 1. Coverage & fidelity (also classifies edges as correct/incorrect)
    print("\n[1/5] Computing coverage and fidelity...")
    cov_results = compute_coverage_fidelity(kg2_enhanced_data, battery_items, edge_tests)

    correct_edges_by_model = {}
    incorrect_edges_by_model = {}
    metrics_by_model = {}

    for model, (m, correct, incorrect) in cov_results.items():
        correct_edges_by_model[model] = correct
        incorrect_edges_by_model[model] = incorrect
        metrics_by_model[model] = m
        print(f"  {model}:")
        print(f"    Coverage: soft_recall = {m.soft_recall:.1%} "
              f"({m.n_soft_detected}/{m.n_gold_edges})")
        print(f"    Fidelity: SID = {m.sid}/{m.sid_total} "
              f"({m.sid_normalised:.1%} wrong), "
              f"direction_acc = {m.direction_accuracy:.1%}")
        print(f"    Correct edges: {len(correct)}, Incorrect: {len(incorrect)}")

    # 2. Decomposed split-half reliability
    print("\n[2/5] Computing decomposed split-half reliability...")
    split_results = compute_decomposed_split_half(
        all_parsed, battery_items, edge_tests,
        correct_edges_by_model, incorrect_edges_by_model,
        kg2_enhanced_data, n_splits=100)

    for model, sr in split_results.items():
        m = metrics_by_model[model]
        m.raw_split_half = sr["raw_agreement"]
        m.raw_split_half_shd = sr.get("raw_shd_mean", 0)
        m.veridical_split_half = sr["veridical_agreement"]
        m.confab_split_half = sr["confab_agreement"]

        print(f"  {model}:")
        print(f"    Raw split-half:    {sr['raw_agreement']:.1%} "
              f"(this was the v1 metric)")
        print(f"    VERIDICAL split:   {sr['veridical_agreement']:.1%} "
              f"(agreement on CORRECT edges)")
        print(f"    CONFABULATORY split:{sr['confab_agreement']:.1%} "
              f"(agreement on WRONG edges — penalised)")

    # 3. Decomposed edge entropy
    print("\n[3/5] Computing decomposed edge entropy...")
    entropy_results = compute_decomposed_entropy(
        all_parsed, battery_items,
        correct_edges_by_model, incorrect_edges_by_model,
        kg2_enhanced_data)

    for model, er in entropy_results.items():
        m = metrics_by_model[model]
        m.veridical_entropy = er["veridical_mean_entropy"]
        m.veridical_flip_rate = er["veridical_flip_rate"]
        m.veridical_n_edges = er["veridical_n"]
        m.confab_entropy = er["confab_mean_entropy"]
        m.confab_n_edges = er["confab_n"]

        print(f"  {model}:")
        print(f"    Veridical entropy: {er['veridical_mean_entropy']:.3f} "
              f"(n={er['veridical_n']}, flip={er['veridical_flip_rate']:.1%})")
        print(f"    Confab entropy:    {er['confab_mean_entropy']:.3f} "
              f"(n={er['confab_n']}, flip={er['confab_flip_rate']:.1%})")
        print(f"    LOW confab entropy = RIGID wrongness (bad)")

    # 4. SNR
    print("\n[4/5] Computing signal-to-noise ratio...")
    snr_results = compute_snr(edge_tests)
    for model, snr in snr_results.items():
        m = metrics_by_model[model]
        m.snr = snr["snr"]
        m.mean_causal_jsd = snr["mean_causal_jsd"]
        m.mean_null_jsd = snr["mean_null_jsd"]
        m.null_jsd_95 = snr["null_jsd_95"]
        m.detection_power = snr["detection_power"]

        print(f"  {model}: SNR = {snr['snr']:.2f} "
              f"(causal={snr['mean_causal_jsd']:.4f}, "
              f"null={snr['mean_null_jsd']:.4f}), "
              f"detection power = {snr['detection_power']:.1%}")

    # 5. Composite WMS
    print("\n[5/5] Computing World Model Score (WMS)...")
    for model, m in metrics_by_model.items():
        wms = compute_composite(m)

        print(f"\n  {'='*60}")
        print(f"  {model}")
        print(f"  {'='*60}")
        print(f"  COVERAGE           = {m.coverage_score:.3f}  (w=0.25)")
        print(f"    Soft recall       = {m.soft_recall:.1%}")
        print(f"  FIDELITY           = {m.fidelity_score:.3f}  (w=0.25)")
        print(f"    Direction acc     = {m.direction_accuracy:.1%}")
        print(f"    SID              = {m.sid}/{m.sid_total} ({m.sid_normalised:.1%})")
        print(f"  VERIDICAL STABILITY= {m.stability_score:.3f}  (w=0.20)")
        print(f"    Veridical split  = {m.veridical_split_half:.1%}")
        print(f"    Veridical entropy= {m.veridical_entropy:.3f}")
        print(f"    Veridical n_edges= {m.veridical_n_edges}")
        print(f"  DISCRIMINABILITY   = {m.discriminability_score:.3f}  (w=0.15)")
        print(f"    SNR              = {m.snr:.2f}")
        print(f"    Detection power  = {m.detection_power:.1%}")
        print(f"  CONFAB PENALTY     = {m.rigidity_penalty:.3f}  (w=0.15, SUBTRACTED)")
        print(f"    Confab split-half= {m.confab_split_half:.1%}")
        print(f"    Confab entropy   = {m.confab_entropy:.3f}")
        print(f"    Confab n_edges   = {m.confab_n_edges}")
        print(f"  ──────────────────────────────────")
        print(f"  WMS = {m.wms:.3f} — {m.wms_label}")

        # Compare to v1

    # Save outputs
    if output_dir:
        out = Path(output_dir)
        out.mkdir(parents=True, exist_ok=True)

        serial = {}
        for model, m in metrics_by_model.items():
            serial[model] = asdict(m)

        dump_json(out / "world_model_metrics_v2.json", serial, default=str)

        # Generate report
        _generate_report_v2(metrics_by_model, split_results, entropy_results,
                           snr_results, out / "world_model_report_v2.md")

        print(f"\n  Outputs saved to {out}/")

    return metrics_by_model


# =====================================================================
# 7. REPORT GENERATION
# =====================================================================

def _generate_report_v2(metrics, split_results, entropy_results,
                        snr_results, out_path):
    """Generate markdown report for v2 evaluation."""
    L = []
    L.append("# World Model Evaluation Report (v2 — Corrected)")
    L.append("")
    L.append("## Key Correction from v1")
    L.append("")
    L.append("v1 treated split-half reliability as unconditionally positive, rewarding")
    L.append("models that were *consistently wrong*. A model missing 51/55 gold-standard")
    L.append("edges could score 85.7% split-half agreement by reliably failing to detect")
    L.append("the same edges every time.")
    L.append("")
    L.append("v2 decomposes consistency into:")
    L.append("")
    L.append("- **Veridical consistency**: agreement on *correctly* detected edges (rewarded)")
    L.append("- **Confabulatory rigidity**: agreement on *incorrectly* missed edges (penalised)")
    L.append("")

    # Summary table
    L.append("## Summary")
    L.append("")
    models = sorted(metrics.keys())
    L.append("| Model | WMS | Label | Coverage | Fidelity | Stability | Discrim. | "
             "Confab Penalty | Raw Split-Half |")
    L.append("|---|---|---|---|---|---|---|---|---|")
    for m_name in models:
        m = metrics[m_name]
        L.append(
            f"| {m_name} | **{m.wms:.3f}** | {m.wms_label} | {m.coverage_score:.3f} "
            f"| {m.fidelity_score:.3f} | {m.stability_score:.3f} "
            f"| {m.discriminability_score:.3f} | {m.rigidity_penalty:.3f} "
            f"| {m.raw_split_half:.1%} |"
        )

    L.append("")
    L.append("## Split-Half Decomposition")
    L.append("")
    L.append("| Model | Raw Agreement | Veridical Agreement | Confab Agreement |")
    L.append("|---|---|---|---|")
    for m_name in models:
        sr = split_results.get(m_name, {})
        L.append(f"| {m_name} | {sr.get('raw_agreement', 0):.1%} "
                 f"| {sr.get('veridical_agreement', 0):.1%} "
                 f"| {sr.get('confab_agreement', 0):.1%} |")

    L.append("")
    L.append("## Edge Entropy Decomposition")
    L.append("")
    L.append("| Model | Veridical Entropy | Confab Entropy | Veridical n | Confab n |")
    L.append("|---|---|---|---|---|")
    for m_name in models:
        er = entropy_results.get(m_name, {})
        L.append(f"| {m_name} | {er.get('veridical_mean_entropy', 0):.3f} "
                 f"| {er.get('confab_mean_entropy', 0):.3f} "
                 f"| {er.get('veridical_n', 0)} "
                 f"| {er.get('confab_n', 0)} |")

    L.append("")
    L.append("## Interpretation")
    L.append("")
    for m_name in models:
        m = metrics[m_name]
        L.append(f"### {m_name}: {m.wms_label} (WMS = {m.wms:.3f})")
        L.append("")

        # Diagnosis
        issues = []
        if m.soft_recall < 0.2:
            issues.append("critically low edge coverage (< 20%)")
        elif m.soft_recall < 0.5:
            issues.append("low edge coverage")
        if m.snr < 1.0:
            issues.append(f"pathological SNR ({m.snr:.2f}) — responds more to noise than signal")
        elif m.snr < 2.0:
            issues.append(f"weak SNR ({m.snr:.2f})")
        if m.confab_split_half > 0.8:
            issues.append(f"high confabulatory rigidity ({m.confab_split_half:.0%}) — "
                         "systematically and consistently wrong")
        if m.rigidity_penalty > 0.3:
            issues.append(f"large rigidity penalty ({m.rigidity_penalty:.2f})")

        if issues:
            L.append("Key issues: " + "; ".join(issues) + ".")
        else:
            L.append("No critical issues identified.")
        L.append("")

    report = "\n".join(L)
    with open(out_path, "w") as f:
        f.write(report)
    return report


# =====================================================================
# CLI
# =====================================================================

def main():
    p = argparse.ArgumentParser(description="World Model Metrics v2")
    p.add_argument("--results", required=True)
    p.add_argument("--battery", required=True)
    p.add_argument("--kg2-enhanced", required=True)
    p.add_argument("--outdir", default="analysis_world_model_v2")
    args = p.parse_args()

    from causal_llm_eval.response_parser import parse_result, detect_edges

    with open(args.battery) as f:
        bat = json.load(f)
    battery_items = {}
    for b in bat["baselines"]:
        battery_items[b["id"]] = b
    for p_item in bat["perturbations"]:
        battery_items[p_item["id"]] = p_item

    results = []
    with open(args.results) as f:
        for line in f:
            if line.strip():
                try:
                    results.append(json.loads(line))
                except:
                    pass

    all_parsed = [p for p in (parse_result(r) for r in results) if p]
    edge_tests = detect_edges(all_parsed, battery_items)

    with open(args.kg2_enhanced) as f:
        kg2_data = json.load(f)

    compute_world_model_metrics_v2(
        all_parsed, edge_tests, battery_items,
        kg2_enhanced_data=kg2_data,
        output_dir=args.outdir
    )


if __name__ == "__main__":
    main()
