#!/usr/bin/env python3
"""
World Model Evaluation Metrics
===============================
Quantifies the quality and solidity of an LLM's implicit causal world model
as recovered through behavioural causal discovery (counterfactual vignette perturbation).

Theoretical grounding:
- Craik (1943): cognition builds "small-scale models" of reality for simulation
- Lake, Ullman, Tenenbaum (2017): causal generative models enable few-shot generalisation
- Peters & Bühlmann (2015): Structural Intervention Distance for causal graph evaluation

Two independent axes:
    QUALITY  = How well does the LLM's implicit KG match the expert consensus (Ferrari et al.)?
    SOLIDITY = How internally consistent and robust is that KG under repeated probing?

Metrics:
    Quality:
        - SID (Structural Intervention Distance): interventional prediction errors
        - Weighted recall: consensus-strength-weighted edge recovery
        - Calibration: Spearman correlation between KG1 weight and KG2 JSD
        - Direction accuracy: fraction of detected edges with correct sign

    Solidity:
        - Split-half reliability: SHD between KG halves built from independent run subsets
        - Edge consistency entropy: mean entropy of per-edge stance distributions
        - Signal-to-noise ratio: mean causal JSD / mean null JSD
        - Null stability: 95th percentile of null perturbation JSD

    Composite:
        - World Model Index (WMI): geometric mean of normalised quality and solidity

Usage:
    python world_model_metrics.py --results results/run_XXX.jsonl \
        --battery vignette_battery.json --outdir analysis

    Or import:
        from causal_llm_eval.world_model_metrics import compute_world_model_metrics
"""

import json, math, argparse
from pathlib import Path
from collections import defaultdict, Counter
from dataclasses import dataclass, field, asdict
from typing import Optional, Dict, List, Tuple
import numpy as np


# =====================================================================
# DATA STRUCTURES
# =====================================================================

@dataclass
class WorldModelQuality:
    """Measures how well the LLM's implicit KG matches expert consensus."""
    model: str = ""

    # Structural Intervention Distance
    sid: int = 0                       # Number of wrong interventional predictions
    sid_normalised: float = 0.0        # SID / total possible interventions
    n_interventions_tested: int = 0    # Total intervention-treatment pairs evaluated

    # Edge-level quality
    hard_tp: int = 0
    hard_fn: int = 0
    hard_fp: int = 0
    soft_tp: int = 0
    precision: float = 0.0
    recall: float = 0.0
    f1: float = 0.0
    soft_recall: float = 0.0
    soft_f1: float = 0.0
    shd: int = 0                       # Structural Hamming Distance

    # Direction
    direction_accuracy: float = 0.0
    direction_errors: int = 0

    # Weighted by consensus strength
    weighted_recall: float = 0.0       # Recall weighted by Delphi consensus %
    weighted_f1: float = 0.0

    # Calibration
    calibration_rho: float = 0.0       # Spearman rho: KG1 weight vs KG2 JSD
    calibration_p: float = 1.0
    calibration_mae: float = 0.0       # Mean absolute error (normalised)

    # Quality composite (0-1 scale, higher = better)
    quality_score: float = 0.0


@dataclass
class WorldModelSolidity:
    """Measures internal consistency and robustness of the LLM's implicit KG."""
    model: str = ""

    # Split-half reliability
    split_half_shd_mean: float = 0.0   # Mean SHD between random half-KGs
    split_half_shd_std: float = 0.0
    split_half_agreement: float = 0.0  # Fraction of edges that agree across halves
    n_splits: int = 0

    # Edge consistency entropy
    mean_edge_entropy: float = 0.0     # Mean Shannon entropy of per-edge stance dists
    median_edge_entropy: float = 0.0
    max_edge_entropy: float = 0.0
    n_edges_measured: int = 0
    edge_entropy_details: list = field(default_factory=list)  # Per-edge entropy

    # Signal-to-noise ratio
    snr: float = 0.0                   # Mean causal JSD / mean null JSD
    mean_causal_jsd: float = 0.0
    mean_null_jsd: float = 0.0
    null_jsd_95: float = 0.0
    n_causal_tests: int = 0
    n_null_tests: int = 0

    # Response consistency (across runs for same item)
    mean_run_agreement: float = 0.0    # Mean pairwise agreement across runs
    stance_flip_rate: float = 0.0      # Fraction of item-treatment pairs that flip stance

    # Solidity composite (0-1 scale, higher = better)
    solidity_score: float = 0.0


@dataclass
class WorldModelIndex:
    """Composite index combining quality and solidity."""
    model: str = ""
    quality: WorldModelQuality = field(default_factory=WorldModelQuality)
    solidity: WorldModelSolidity = field(default_factory=WorldModelSolidity)
    wmi: float = 0.0                   # Geometric mean of quality_score and solidity_score
    wmi_label: str = ""                # Qualitative label


# =====================================================================
# 1. STRUCTURAL INTERVENTION DISTANCE (SID)
# =====================================================================

def compute_sid(edge_tests, battery_items):
    """
    Compute Structural Intervention Distance between the LLM's implicit graph
    and the expert consensus graph.

    SID counts how many intervention → treatment predictions differ.
    For each perturbation (= an intervention on a clinical variable):
        For each target treatment (in expected_recommendations or expected_excluded):
            Did the model's response shift match the expected direction?

    An intervention prediction is WRONG if:
        - The expert says treatment should be excluded, but the model doesn't shift
        - The expert says treatment should remain, but the model shifts away
        - The shift is in the wrong direction

    Returns:
        (sid_count, n_total, per_intervention_details)
    """
    # Group edge tests by (perturbation, model)
    by_pert_model = defaultdict(list)
    for t in edge_tests:
        by_pert_model[(t["pert_id"], t["model"])].append(t)

    results = {}
    for (pert_id, model), tests in by_pert_model.items():
        if model not in results:
            results[model] = {"wrong": 0, "total": 0, "details": []}

        pert_item = battery_items.get(pert_id)
        if not pert_item or pert_item.get("type") == "baseline":
            continue

        # Only count perturbations, not nulls (nulls test specificity, not SID)
        if pert_item.get("type") == "null":
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

            # Determine if interventional prediction is correct
            wrong = False
            reason = ""

            if tx in exp_exc:
                # Expert says: this intervention should REDUCE this treatment
                if not significant:
                    wrong = True
                    reason = "no_shift_when_expected"
                elif pert_rate >= base_rate:
                    wrong = True
                    reason = "wrong_direction"
            elif tx in exp_rec:
                # Expert says: treatment should remain appropriate after perturbation
                if significant and pert_rate < base_rate - 0.15:
                    wrong = True
                    reason = "unexpected_reduction"

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
# 2. SPLIT-HALF RELIABILITY
# =====================================================================

def compute_split_half_reliability(all_parsed, battery_items, edge_tests,
                                   n_splits=100, seed=42):
    """
    Split runs into two halves, build independent KGs, measure agreement.

    For each random split:
        1. Partition runs into half_A and half_B
        2. For each perturbation-baseline pair, compute Fisher tests independently
        3. Compare which edges are detected in each half
        4. SHD between the two half-KGs

    Returns: dict {model: {shd_mean, shd_std, agreement_rate, n_splits}}
    """
    rng = np.random.default_rng(seed)

    # Group parsed results by (item_id, model, run_idx)
    by_item_model = defaultdict(lambda: defaultdict(list))
    for p in all_parsed:
        key = (p["item_id"], p["model_name"])
        run_idx = p.get("run_idx", 0)
        by_item_model[key][run_idx].append(p)

    # Get all models
    models = set(p["model_name"] for p in all_parsed)

    results = {}
    for model in models:
        # Find all run indices for this model
        all_runs = set()
        for (iid, mn), runs_dict in by_item_model.items():
            if mn == model:
                all_runs.update(runs_dict.keys())
        all_runs = sorted(all_runs)

        if len(all_runs) < 4:
            results[model] = {"shd_mean": 0, "shd_std": 0,
                              "agreement": 0, "n_splits": 0,
                              "note": "Too few runs for split-half"}
            continue

        shd_values = []
        agreement_values = []

        for _ in range(n_splits):
            # Random split
            perm = rng.permutation(len(all_runs))
            half_size = len(all_runs) // 2
            runs_a = set(all_runs[i] for i in perm[:half_size])
            runs_b = set(all_runs[i] for i in perm[half_size:])

            # Build edge detection for each half
            edges_a = _detect_edges_for_runs(
                by_item_model, model, runs_a, battery_items)
            edges_b = _detect_edges_for_runs(
                by_item_model, model, runs_b, battery_items)

            # Compare: which edges are detected in each half?
            all_edges = set(edges_a.keys()) | set(edges_b.keys())
            if not all_edges:
                continue

            shd = 0
            agree = 0
            for edge_id in all_edges:
                det_a = edges_a.get(edge_id, False)
                det_b = edges_b.get(edge_id, False)
                if det_a == det_b:
                    agree += 1
                else:
                    shd += 1

            shd_values.append(shd)
            agreement_values.append(agree / len(all_edges))

        results[model] = {
            "shd_mean": float(np.mean(shd_values)) if shd_values else 0.0,
            "shd_std": float(np.std(shd_values)) if shd_values else 0.0,
            "agreement": float(np.mean(agreement_values)) if agreement_values else 0.0,
            "n_splits": len(shd_values),
        }

    return results


def _detect_edges_for_runs(by_item_model, model, run_set, battery_items):
    """
    Lightweight edge detection using a subset of runs.
    Returns {edge_id: detected_bool} using simple majority vote on rec rate shift.
    """
    # Build count tables from the selected runs only
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

    # For each perturbation, check if distribution shift is notable
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
                if shift > 0.25:  # Threshold for "notable shift"
                    edge_detections[edge_id]["detected_count"] += 1

    # Edge is "detected" if majority of its probes show notable shift
    result = {}
    for edge_id, data in edge_detections.items():
        if data["total_count"] > 0:
            rate = data["detected_count"] / data["total_count"]
            result[edge_id] = rate > 0.5
        else:
            result[edge_id] = False

    return result


# =====================================================================
# 3. EDGE CONSISTENCY ENTROPY
# =====================================================================

def compute_edge_entropy(all_parsed, battery_items):
    """
    For each edge (perturbation × target treatment), compute Shannon entropy
    of the stance distribution across runs.

    Low entropy = model consistently gives the same answer = solid edge.
    High entropy = model flip-flops = fragile edge.

    Returns: dict {model: {mean_entropy, median_entropy, per_edge: [...]}}
    """
    # Group stances by (item_id, model, treatment)
    stance_counts = defaultdict(lambda: Counter())
    for p in all_parsed:
        for s in p["stances"]:
            key = (p["item_id"], p["model_name"], s["treatment"])
            stance_counts[key][s["stance"]] += 1

    # Compute entropy per (item, model, treatment)
    model_entropies = defaultdict(list)
    model_flip_rates = defaultdict(lambda: {"flips": 0, "total": 0})

    for (iid, model, tx), counts in stance_counts.items():
        total = sum(counts.values())
        if total < 3:
            continue  # Need enough samples for meaningful entropy

        # Shannon entropy
        probs = np.array([c / total for c in counts.values()])
        entropy = float(-np.sum(probs * np.log2(probs + 1e-12)))

        # Max possible entropy for this many categories
        n_cats = len(counts)
        max_entropy = math.log2(n_cats) if n_cats > 1 else 1.0
        normalised_entropy = entropy / max_entropy if max_entropy > 0 else 0.0

        model_entropies[model].append({
            "item_id": iid, "treatment": tx,
            "entropy": entropy, "normalised_entropy": normalised_entropy,
            "n_runs": total, "dominant_stance": counts.most_common(1)[0][0],
            "dominant_rate": counts.most_common(1)[0][1] / total,
            "distribution": dict(counts),
        })

        # Flip rate: does the majority stance have < 80% of responses?
        model_flip_rates[model]["total"] += 1
        if counts.most_common(1)[0][1] / total < 0.8:
            model_flip_rates[model]["flips"] += 1

    results = {}
    for model, entries in model_entropies.items():
        ents = [e["normalised_entropy"] for e in entries]
        fr = model_flip_rates[model]
        results[model] = {
            "mean_entropy": float(np.mean(ents)) if ents else 0.0,
            "median_entropy": float(np.median(ents)) if ents else 0.0,
            "max_entropy": float(np.max(ents)) if ents else 0.0,
            "n_edges_measured": len(entries),
            "stance_flip_rate": fr["flips"] / fr["total"] if fr["total"] > 0 else 0.0,
            # Top 10 most entropic edges
            "most_entropic": sorted(entries, key=lambda e: -e["normalised_entropy"])[:10],
            # Top 10 most stable edges
            "most_stable": sorted(entries, key=lambda e: e["normalised_entropy"])[:10],
        }

    return results


# =====================================================================
# 4. SIGNAL-TO-NOISE RATIO
# =====================================================================

def compute_snr(edge_tests):
    """
    Signal-to-noise ratio: how much stronger are causal perturbation responses
    vs null perturbation responses?

    SNR = mean_JSD(causal perturbations) / mean_JSD(null perturbations)

    High SNR (>3): model distinguishes causal from non-causal changes well.
    Low SNR (~1): model responds similarly to causal and irrelevant changes.
    SNR < 1: model responds MORE to irrelevant changes (pathological).

    Returns: dict {model: {snr, mean_causal_jsd, mean_null_jsd, ...}}
    """
    model_data = defaultdict(lambda: {"causal_jsds": [], "null_jsds": []})

    for t in edge_tests:
        model = t["model"]
        jsd = t.get("jsd", 0)

        # Only count target treatments (in exp_rec or exp_exc)
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

        # SNR with floor to avoid division by zero
        snr = mean_causal / max(mean_null, 0.001)

        # Also compute: fraction of causal JSDs that exceed the null 95th percentile
        # This is a "detection power" measure
        if null_95 > 0:
            above_noise = float(np.mean(causal > null_95))
        else:
            above_noise = 0.0

        results[model] = {
            "snr": snr,
            "mean_causal_jsd": mean_causal,
            "mean_null_jsd": float(np.mean(null)),
            "median_causal_jsd": float(np.median(causal)),
            "median_null_jsd": float(np.median(null)),
            "null_jsd_95": null_95,
            "n_causal": len(data["causal_jsds"]),
            "n_null": len(data["null_jsds"]),
            "detection_power": above_noise,  # Fraction of causal signals above noise floor
        }

    return results


# =====================================================================
# 5. WEIGHTED QUALITY (by consensus strength)
# =====================================================================

def compute_weighted_quality(kg2_enhanced_data, kg1_weights=None):
    """
    Compute consensus-weighted recall and calibration.

    If kg1_weights not provided, uses uniform weights (all edges equal).

    Returns: dict {model: {weighted_recall, calibration_rho, calibration_mae}}
    """
    results = {}

    for model, edges in kg2_enhanced_data.items():
        # Default: uniform weights if no KG1 weights provided
        weights = {}
        for eid in edges:
            if kg1_weights and eid in kg1_weights:
                weights[eid] = kg1_weights[eid]
            else:
                weights[eid] = 1.0

        total_weight = sum(weights.values())
        if total_weight == 0:
            continue

        # Weighted recall (soft detection)
        detected_weight = sum(
            weights.get(eid, 0)
            for eid, e in edges.items()
            if e.get("soft_detected", False)
        )
        weighted_recall = detected_weight / total_weight

        # Calibration: Spearman between KG1 weight and KG2 mean JSD
        kg1_vals = []
        kg2_vals = []
        for eid, e in edges.items():
            if eid in weights and e.get("mean_jsd", 0) > 0:
                kg1_vals.append(weights[eid])
                kg2_vals.append(e["mean_jsd"])

        rho, p_val, mae = 0.0, 1.0, 0.0
        if len(kg1_vals) >= 5:
            try:
                from scipy.stats import spearmanr
                rho, p_val = spearmanr(kg1_vals, kg2_vals)
                if np.isnan(rho):
                    rho = 0.0

                # MAE on normalised scales
                kg1_norm = np.array(kg1_vals) / max(kg1_vals)
                kg2_max = max(kg2_vals) if max(kg2_vals) > 0 else 1.0
                kg2_norm = np.array(kg2_vals) / kg2_max
                mae = float(np.mean(np.abs(kg1_norm - kg2_norm)))
            except Exception:
                pass

        results[model] = {
            "weighted_recall": weighted_recall,
            "calibration_rho": float(rho),
            "calibration_p": float(p_val),
            "calibration_mae": mae,
        }

    return results


# =====================================================================
# 6. COMPOSITE SCORES
# =====================================================================

def compute_composite_scores(quality: WorldModelQuality,
                              solidity: WorldModelSolidity) -> float:
    """
    Compute World Model Index (WMI) as geometric mean of quality and solidity.

    Quality score (0-1):
        Weighted combination of soft_recall, direction_accuracy,
        1 - sid_normalised, calibration_rho

    Solidity score (0-1):
        Weighted combination of split_half_agreement, 1 - mean_edge_entropy,
        snr (capped), 1 - null_jsd_95

    WMI = sqrt(quality_score * solidity_score)
    """
    # Quality: weighted sum of sub-metrics
    q_components = [
        (0.35, quality.soft_recall),
        (0.25, quality.direction_accuracy),
        (0.25, max(0, 1.0 - quality.sid_normalised)),
        (0.15, max(0, min(1, (quality.calibration_rho + 1) / 2))),  # Map [-1,1] to [0,1]
    ]
    quality.quality_score = sum(w * v for w, v in q_components)

    # Solidity: weighted sum of sub-metrics
    # Cap SNR contribution at SNR=5 (map to 0-1)
    snr_score = min(solidity.snr / 5.0, 1.0) if solidity.snr > 0 else 0.0

    s_components = [
        (0.30, solidity.split_half_agreement),
        (0.25, max(0, 1.0 - solidity.mean_edge_entropy)),
        (0.25, snr_score),
        (0.20, max(0, 1.0 - solidity.null_jsd_95)),
    ]
    solidity.solidity_score = sum(w * v for w, v in s_components)

    # WMI = geometric mean
    q = max(quality.quality_score, 0.001)
    s = max(solidity.solidity_score, 0.001)
    wmi = math.sqrt(q * s)

    return wmi


def label_wmi(wmi: float) -> str:
    """Qualitative label for World Model Index."""
    if wmi >= 0.8:
        return "Strong world model"
    elif wmi >= 0.6:
        return "Moderate world model"
    elif wmi >= 0.4:
        return "Weak world model"
    elif wmi >= 0.2:
        return "Fragmentary world model"
    else:
        return "No coherent world model"


# =====================================================================
# 7. MAIN PIPELINE
# =====================================================================

def compute_world_model_metrics(all_parsed, edge_tests, battery_items,
                                 kg2_enhanced_data=None, kg1_weights=None,
                                 output_dir=None):
    """
    Run the full world model evaluation pipeline.

    Parameters:
        all_parsed: list of parsed results from response_parser.parse_result()
        edge_tests: list from response_parser.detect_edges()
        battery_items: dict {item_id: item_dict}
        kg2_enhanced_data: dict {model: {edge_id: edge_dict}} from kg2_enhanced.json
        kg1_weights: optional dict {edge_id: consensus_weight}
        output_dir: path to save outputs

    Returns:
        dict {model: WorldModelIndex}
    """
    print("=" * 60)
    print("WORLD MODEL EVALUATION")
    print("=" * 60)

    models = set(p["model_name"] for p in all_parsed)

    # 1. SID
    print("\n[1/6] Computing Structural Intervention Distance...")
    sid_results = compute_sid(edge_tests, battery_items)
    for m, data in sid_results.items():
        total = data["total"]
        wrong = data["wrong"]
        pct = wrong / total * 100 if total > 0 else 0
        print(f"  {m}: SID = {wrong}/{total} ({pct:.1f}% interventional predictions wrong)")

    # 2. Split-half reliability
    print("\n[2/6] Computing split-half reliability (100 random splits)...")
    split_results = compute_split_half_reliability(all_parsed, battery_items, edge_tests)
    for m, data in split_results.items():
        print(f"  {m}: SHD = {data['shd_mean']:.1f} ± {data['shd_std']:.1f}, "
              f"agreement = {data['agreement']:.1%}")

    # 3. Edge entropy
    print("\n[3/6] Computing edge consistency entropy...")
    entropy_results = compute_edge_entropy(all_parsed, battery_items)
    for m, data in entropy_results.items():
        print(f"  {m}: mean H = {data['mean_entropy']:.3f}, "
              f"flip rate = {data['stance_flip_rate']:.1%}, "
              f"n = {data['n_edges_measured']}")

    # 4. Signal-to-noise ratio
    print("\n[4/6] Computing signal-to-noise ratio...")
    snr_results = compute_snr(edge_tests)
    for m, data in snr_results.items():
        print(f"  {m}: SNR = {data['snr']:.2f} "
              f"(causal={data['mean_causal_jsd']:.4f}, null={data['mean_null_jsd']:.4f}), "
              f"detection power = {data['detection_power']:.1%}")

    # 5. Weighted quality
    print("\n[5/6] Computing weighted quality metrics...")
    if kg2_enhanced_data:
        weighted_results = compute_weighted_quality(kg2_enhanced_data, kg1_weights)
        for m, data in weighted_results.items():
            print(f"  {m}: weighted recall = {data['weighted_recall']:.1%}, "
                  f"calibration ρ = {data['calibration_rho']:.3f}")
    else:
        weighted_results = {}
        print("  (skipped — no kg2_enhanced data)")

    # 6. Assemble composite indices
    print("\n[6/6] Computing World Model Index...")
    indices = {}

    for model in models:
        # Quality
        q = WorldModelQuality(model=model)
        if model in sid_results:
            sd = sid_results[model]
            q.sid = sd["wrong"]
            q.n_interventions_tested = sd["total"]
            q.sid_normalised = sd["wrong"] / sd["total"] if sd["total"] > 0 else 1.0

        # Pull in existing graph comparison metrics if available
        if kg2_enhanced_data and model in kg2_enhanced_data:
            edges = kg2_enhanced_data[model]
            n_total = len(edges)
            n_soft = sum(1 for e in edges.values()
                         if (e.get("soft_detected") if isinstance(e, dict) else e.soft_detected))
            n_hard = sum(1 for e in edges.values()
                         if (e.get("detected") if isinstance(e, dict) else e.detected))

            q.hard_tp = n_hard
            q.soft_tp = n_soft
            q.hard_fn = n_total - n_hard
            q.recall = n_hard / n_total if n_total > 0 else 0.0
            q.soft_recall = n_soft / n_total if n_total > 0 else 0.0

            # Direction accuracy
            detected_with_dir = [
                e for e in edges.values()
                if (e.get("detected") if isinstance(e, dict) else e.detected)
                and (e.get("direction_correct") if isinstance(e, dict) else e.direction_correct) is not None
            ]
            if detected_with_dir:
                q.direction_accuracy = sum(
                    1 for e in detected_with_dir
                    if (e.get("direction_correct") if isinstance(e, dict) else e.direction_correct)
                ) / len(detected_with_dir)
            else:
                # Use soft-detected direction accuracy as fallback
                soft_with_dir = [
                    e for e in edges.values()
                    if (e.get("soft_detected") if isinstance(e, dict) else e.soft_detected)
                    and (e.get("direction_correct") if isinstance(e, dict) else e.direction_correct) is not None
                ]
                if soft_with_dir:
                    q.direction_accuracy = sum(
                        1 for e in soft_with_dir
                        if (e.get("direction_correct") if isinstance(e, dict) else e.direction_correct)
                    ) / len(soft_with_dir)

        if model in weighted_results:
            wr = weighted_results[model]
            q.weighted_recall = wr["weighted_recall"]
            q.calibration_rho = wr["calibration_rho"]
            q.calibration_p = wr["calibration_p"]
            q.calibration_mae = wr["calibration_mae"]

        # Solidity
        s = WorldModelSolidity(model=model)
        if model in split_results:
            sr = split_results[model]
            s.split_half_shd_mean = sr["shd_mean"]
            s.split_half_shd_std = sr["shd_std"]
            s.split_half_agreement = sr["agreement"]
            s.n_splits = sr.get("n_splits", 0)

        if model in entropy_results:
            er = entropy_results[model]
            s.mean_edge_entropy = er["mean_entropy"]
            s.median_edge_entropy = er["median_entropy"]
            s.max_edge_entropy = er["max_entropy"]
            s.n_edges_measured = er["n_edges_measured"]
            s.stance_flip_rate = er["stance_flip_rate"]

        if model in snr_results:
            snr = snr_results[model]
            s.snr = snr["snr"]
            s.mean_causal_jsd = snr["mean_causal_jsd"]
            s.mean_null_jsd = snr["mean_null_jsd"]
            s.null_jsd_95 = snr["null_jsd_95"]
            s.n_causal_tests = snr["n_causal"]
            s.n_null_tests = snr["n_null"]

        # Composite
        wmi = compute_composite_scores(q, s)
        label = label_wmi(wmi)

        idx = WorldModelIndex(
            model=model, quality=q, solidity=s,
            wmi=wmi, wmi_label=label
        )
        indices[model] = idx

        print(f"\n  {'='*50}")
        print(f"  {model}")
        print(f"  {'='*50}")
        print(f"  QUALITY  = {q.quality_score:.3f}")
        print(f"    SID           = {q.sid}/{q.n_interventions_tested} "
              f"({q.sid_normalised:.1%} wrong)")
        print(f"    Soft recall    = {q.soft_recall:.1%}")
        print(f"    Direction acc  = {q.direction_accuracy:.1%}")
        print(f"    Weighted recall= {q.weighted_recall:.1%}")
        print(f"    Calibration ρ  = {q.calibration_rho:.3f}")
        print(f"  SOLIDITY = {s.solidity_score:.3f}")
        print(f"    Split-half SHD = {s.split_half_shd_mean:.1f} ± {s.split_half_shd_std:.1f}")
        print(f"    Split-half agr = {s.split_half_agreement:.1%}")
        print(f"    Edge entropy   = {s.mean_edge_entropy:.3f}")
        print(f"    Flip rate      = {s.stance_flip_rate:.1%}")
        print(f"    SNR            = {s.snr:.2f}")
        print(f"    Null JSD 95th  = {s.null_jsd_95:.4f}")
        print(f"  WMI = {wmi:.3f} — {label}")

    # Save outputs
    if output_dir:
        out = Path(output_dir)
        out.mkdir(parents=True, exist_ok=True)

        # Full metrics as JSON
        serial = {}
        for model, idx in indices.items():
            serial[model] = {
                "wmi": idx.wmi,
                "wmi_label": idx.wmi_label,
                "quality": asdict(idx.quality),
                "solidity": asdict(idx.solidity),
            }
        with open(out / "world_model_metrics.json", "w") as f:
            json.dump(serial, f, indent=2, default=str)

        # SID details
        sid_serial = {}
        for m, data in sid_results.items():
            sid_serial[m] = {
                "sid": data["wrong"],
                "total": data["total"],
                "sid_normalised": data["wrong"] / data["total"] if data["total"] > 0 else 0,
                "details": data["details"],
            }
        with open(out / "sid_details.json", "w") as f:
            json.dump(sid_serial, f, indent=2)

        # Entropy details
        entropy_serial = {}
        for m, data in entropy_results.items():
            entropy_serial[m] = {
                "mean_entropy": data["mean_entropy"],
                "median_entropy": data["median_entropy"],
                "stance_flip_rate": data["stance_flip_rate"],
                "most_entropic": data["most_entropic"],
                "most_stable": data["most_stable"],
            }
        with open(out / "edge_entropy.json", "w") as f:
            json.dump(entropy_serial, f, indent=2)

        # SNR details
        with open(out / "snr_details.json", "w") as f:
            json.dump(dict(snr_results), f, indent=2)

        # Split-half details
        with open(out / "split_half.json", "w") as f:
            json.dump(dict(split_results), f, indent=2)

        # Markdown report
        _generate_report(indices, sid_results, entropy_results,
                         snr_results, split_results, out / "world_model_report.md")

        print(f"\n  Outputs saved to {out}/")

    return indices


# =====================================================================
# 8. REPORT GENERATION
# =====================================================================

def _generate_report(indices, sid_results, entropy_results,
                     snr_results, split_results, out_path):
    """Generate markdown report for the world model evaluation."""
    L = []
    L.append("# World Model Evaluation Report\n")
    L.append("Behavioural causal discovery assessment of LLM implicit causal graphs.\n")
    L.append("**Framework**: Quality (alignment with expert consensus) × "
             "Solidity (internal consistency under repeated probing).\n")

    # Summary table
    L.append("## 1. Summary\n")
    models = sorted(indices.keys())
    L.append("| Model | WMI | Label | Quality | Solidity | SID | Soft Recall | SNR | "
             "Split-Half Agr | Edge Entropy | Flip Rate |")
    L.append("|---|---|---|---|---|---|---|---|---|---|---|")
    for m in models:
        idx = indices[m]
        q, s = idx.quality, idx.solidity
        L.append(
            f"| {m} | **{idx.wmi:.3f}** | {idx.wmi_label} | {q.quality_score:.3f} "
            f"| {s.solidity_score:.3f} | {q.sid}/{q.n_interventions_tested} "
            f"| {q.soft_recall:.1%} | {s.snr:.2f} | {s.split_half_agreement:.1%} "
            f"| {s.mean_edge_entropy:.3f} | {s.stance_flip_rate:.1%} |"
        )

    # SID breakdown
    L.append("\n## 2. Structural Intervention Distance (Quality)\n")
    L.append("SID counts how many intervention → treatment predictions the model gets wrong "
             "compared to expert consensus. Each perturbation is an intervention on a clinical "
             "variable; we check whether the model's response shifts match expert expectations.\n")

    for m in models:
        if m in sid_results:
            sd = sid_results[m]
            L.append(f"\n### {m}\n")
            L.append(f"- **SID**: {sd['wrong']}/{sd['total']} "
                     f"({sd['wrong']/sd['total']*100:.1f}% wrong)\n")

            # Breakdown by error type
            wrong_details = [d for d in sd["details"] if d["wrong"]]
            by_reason = defaultdict(list)
            for d in wrong_details:
                by_reason[d["reason"]].append(d)

            if by_reason:
                L.append("Error breakdown:\n")
                for reason, items in sorted(by_reason.items()):
                    L.append(f"- **{reason}**: {len(items)} cases")
                    for item in items[:3]:
                        L.append(f"  - {item['pert_id']} × {item['treatment']}: "
                                 f"base={item['base_rate']:.0%} → pert={item['pert_rate']:.0%}")

    # Solidity details
    L.append("\n## 3. Split-Half Reliability (Solidity)\n")
    L.append("Randomly split runs into two halves (100 times), build independent KGs, "
             "measure edge agreement. High agreement = stable internal structure.\n")

    for m in models:
        if m in split_results:
            sr = split_results[m]
            L.append(f"- **{m}**: agreement = {sr['agreement']:.1%}, "
                     f"SHD = {sr['shd_mean']:.1f} ± {sr['shd_std']:.1f}")

    L.append("\n## 4. Edge Consistency Entropy (Solidity)\n")
    L.append("Shannon entropy of per-edge stance distributions. Low = consistent, high = noisy.\n")

    for m in models:
        if m in entropy_results:
            er = entropy_results[m]
            L.append(f"\n### {m} (mean H = {er['mean_entropy']:.3f}, "
                     f"flip rate = {er['stance_flip_rate']:.1%})\n")

            L.append("**Most unstable edges** (highest entropy):\n")
            for e in er["most_entropic"][:5]:
                L.append(f"- {e['item_id']} × {e['treatment']}: H={e['normalised_entropy']:.3f}, "
                         f"dominant={e['dominant_stance']} ({e['dominant_rate']:.0%}), "
                         f"dist={e['distribution']}")

            L.append("\n**Most stable edges** (lowest entropy):\n")
            for e in er["most_stable"][:5]:
                L.append(f"- {e['item_id']} × {e['treatment']}: H={e['normalised_entropy']:.3f}, "
                         f"dominant={e['dominant_stance']} ({e['dominant_rate']:.0%})")

    L.append("\n## 5. Signal-to-Noise Ratio (Solidity)\n")
    L.append("Ratio of mean JSD on causal perturbations vs null perturbations. "
             "SNR > 3 = good discrimination. SNR ~1 = no discrimination.\n")

    for m in models:
        if m in snr_results:
            snr = snr_results[m]
            L.append(f"- **{m}**: SNR = {snr['snr']:.2f} "
                     f"(causal μ={snr['mean_causal_jsd']:.4f}, "
                     f"null μ={snr['mean_null_jsd']:.4f}), "
                     f"detection power = {snr['detection_power']:.1%}")

    L.append("\n## 6. Interpretation\n")
    for m in models:
        idx = indices[m]
        q, s = idx.quality, idx.solidity
        L.append(f"\n### {m}: {idx.wmi_label} (WMI = {idx.wmi:.3f})\n")

        if idx.wmi < 0.2:
            L.append("The model shows no coherent causal graph in this domain. "
                     "Responses are largely stochastic with respect to the clinical "
                     "variables that experts identify as causally relevant.")
        elif idx.wmi < 0.4:
            L.append("The model shows fragmentary causal knowledge — some edges are "
                     "present but the overall structure is too sparse and inconsistent "
                     "to constitute a functional world model for clinical reasoning.")
        elif idx.wmi < 0.6:
            L.append("The model has a partial world model with moderate coverage but "
                     "significant gaps. Some causal pathways are represented but the "
                     "model cannot reliably generalise across novel variable combinations.")
        elif idx.wmi < 0.8:
            L.append("The model has a moderately complete world model with good coverage "
                     "of the major causal pathways. Gaps remain in specific areas.")
        else:
            L.append("The model has a strong internal world model that closely matches "
                     "expert consensus in both structure and stability.")

    report = "\n".join(L)
    with open(out_path, "w") as f:
        f.write(report)
    return report


# =====================================================================
# CLI ENTRY POINT
# =====================================================================

def main():
    """Run as standalone or add-on after base analysis."""
    p = argparse.ArgumentParser(description="World Model Evaluation Metrics")
    p.add_argument("--results", required=True, help="Path to run_XXX.jsonl")
    p.add_argument("--battery", required=True, help="Path to vignette_battery.json")
    p.add_argument("--kg2-enhanced", default=None,
                   help="Path to kg2_enhanced.json (optional)")
    p.add_argument("--outdir", default="analysis", help="Output directory")
    args = p.parse_args()

    from causal_llm_eval.response_parser import parse_result, detect_edges

    # Load battery
    with open(args.battery) as f:
        bat = json.load(f)
    battery_items = {}
    for b in bat["baselines"]:
        battery_items[b["id"]] = b
    for p_item in bat["perturbations"]:
        battery_items[p_item["id"]] = p_item

    # Load and parse results
    results = []
    with open(args.results) as f:
        for line in f:
            if line.strip():
                try:
                    results.append(json.loads(line))
                except:
                    pass
    print(f"Loaded {len(results)} results")

    all_parsed = [p for p in (parse_result(r) for r in results) if p]
    print(f"Parsed {len(all_parsed)} responses")

    edge_tests = detect_edges(all_parsed, battery_items)

    # Load KG2 enhanced if provided
    kg2_data = None
    if args.kg2_enhanced:
        with open(args.kg2_enhanced) as f:
            kg2_data = json.load(f)

    compute_world_model_metrics(
        all_parsed, edge_tests, battery_items,
        kg2_enhanced_data=kg2_data,
        output_dir=args.outdir
    )


if __name__ == "__main__":
    main()
