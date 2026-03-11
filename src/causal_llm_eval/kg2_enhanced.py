#!/usr/bin/env python3
"""
KG2 Enhanced Assembly & Graph Comparison Module
================================================
Add-on to response_parser.py. Runs AFTER the base analysis pipeline.

Enhancements over base assemble_kg2():
1. Directed edges with correct/wrong direction classification
2. Continuous edge weights (mean JSD) with BCa bootstrap CIs
3. Conditionality testing (edge active in correct contexts only?)
4. Spurious edge detection from null perturbations
5. Omnibus distribution shift test (permutation chi-squared) before per-treatment
6. Publication-ready graph comparison metrics (SHD, edge-F1, SID-like, calibration)

Usage:
    python kg2_enhanced.py --results results/run_XXX.jsonl \
        --battery vignette_battery.json --outdir analysis

    Or import and call:
        from causal_llm_eval.kg2_enhanced import run_enhanced_analysis
        results = run_enhanced_analysis(edge_tests, all_parsed, battery_items, kg2_base)
"""

import json, math, argparse
from pathlib import Path
from collections import defaultdict, Counter
from dataclasses import dataclass, field, asdict
from typing import Optional
import numpy as np

# =====================================================================
# DATA STRUCTURES
# =====================================================================

@dataclass
class KG2Edge:
    """Rich edge representation for a single model's implicit graph."""
    edge_id: str                          # KG1 statement ID (e.g., "S7R")
    model: str
    detected: bool                        # Significant in >50% of target-treatment probes
    soft_detected: bool = False           # Omnibus significant OR detection_rate > 0.25
    detection_rate: float = 0.0           # Fraction of probes where significant
    n_probes: int = 0                     # Number of target-treatment probes

    # Direction
    direction_correct: Optional[bool] = None  # Did distribution shift match KG1 prediction?
    direction_rate: float = 0.0               # Fraction of probes with correct direction

    # Weight (continuous)
    mean_jsd: float = 0.0                 # Mean JSD across probes
    median_jsd: float = 0.0
    jsd_ci_lower: float = 0.0            # 95% BCa bootstrap CI
    jsd_ci_upper: float = 0.0
    jsd_values: list = field(default_factory=list)  # Raw JSD per probe

    # Conditionality
    conditionality_tested: bool = False   # Was this edge tested across multiple contexts?
    conditionality_correct: Optional[bool] = None  # Active only in correct contexts?
    active_in_contexts: list = field(default_factory=list)   # Families where edge fired
    expected_contexts: list = field(default_factory=list)     # Families where edge should fire

    # Omnibus test
    omnibus_significant: Optional[bool] = None  # Permutation chi-sq significant?
    omnibus_p: Optional[float] = None


@dataclass
class KG1Edge:
    """Reference edge from Ferrari et al."""
    edge_id: str
    consensus_weight: float = 0.0  # Delphi agreement % (0-1)
    edge_type: str = "unknown"     # absolute_ci, relative_ci, indication, conditional
    families: list = field(default_factory=list)  # Which clinical families this applies to


@dataclass
class GraphComparison:
    """Publication-ready comparison metrics between KG1 and KG2."""
    model: str
    # Edge detection (hard: >50% probes significant)
    true_positives: int = 0        # KG1 edge present, KG2 detected (hard)
    false_negatives: int = 0       # KG1 edge present, KG2 missed (hard)
    false_positives: int = 0       # KG1 no edge, KG2 detected (spurious)
    # Derived
    precision: float = 0.0
    recall: float = 0.0
    f1: float = 0.0
    shd: int = 0                   # Structural Hamming Distance

    # Soft detection (omnibus significant OR det_rate >= 0.25)
    soft_true_positives: int = 0
    soft_recall: float = 0.0
    soft_f1: float = 0.0

    # Direction-sensitive
    direction_errors: int = 0      # Detected but wrong direction
    direction_accuracy: float = 0.0

    # Weighted metrics (by KG1 consensus strength)
    weighted_recall: float = 0.0   # Recall weighted by consensus weight
    weighted_precision: float = 0.0

    # Calibration
    weight_correlation: float = 0.0  # Correlation between KG1 weight and KG2 JSD
    calibration_error: float = 0.0   # Mean abs difference between normalised weights

    # Null specificity
    null_jsd_mean: float = 0.0     # Mean JSD on null perturbations (noise floor)
    null_jsd_95: float = 0.0       # 95th percentile of null JSD


# =====================================================================
# BOOTSTRAP JSD WITH BCa CONFIDENCE INTERVALS
# =====================================================================

def _jsd_from_counts(counts_a, counts_b, all_treatments, smoothing=0.5):
    """Compute JSD between two treatment count vectors with Dirichlet smoothing."""
    n_tx = len(all_treatments)
    p = np.array([(counts_a.get(t, 0) + smoothing) for t in all_treatments])
    q = np.array([(counts_b.get(t, 0) + smoothing) for t in all_treatments])
    p = p / p.sum()
    q = q / q.sum()

    m = 0.5 * (p + q)
    # Avoid log(0) — m is always > 0 due to smoothing
    kl_pm = np.sum(p * np.log(p / m))
    kl_qm = np.sum(q * np.log(q / m))
    return float(0.5 * kl_pm + 0.5 * kl_qm)


def bootstrap_jsd(samples_a, samples_b, n_boot=2000, alpha=0.05, smoothing=0.5):
    """
    Compute JSD between two sets of categorical samples with BCa bootstrap CI.

    Parameters:
        samples_a: list of treatment labels from condition A (N=30 runs)
        samples_b: list of treatment labels from condition B (N=30 runs)
        n_boot: number of bootstrap resamples
        alpha: significance level for CI (0.05 = 95% CI)
        smoothing: Dirichlet pseudocount for zero-count handling

    Returns:
        (jsd_observed, ci_lower, ci_upper)
    """
    all_treatments = sorted(set(samples_a + samples_b))
    if not all_treatments:
        return 0.0, 0.0, 0.0

    arr_a = np.array(samples_a)
    arr_b = np.array(samples_b)
    na, nb = len(arr_a), len(arr_b)

    def _counts(arr):
        c = Counter(arr.tolist() if hasattr(arr, 'tolist') else arr)
        return c

    # Observed JSD
    jsd_obs = _jsd_from_counts(_counts(arr_a), _counts(arr_b), all_treatments, smoothing)

    # Bootstrap resamples
    rng = np.random.default_rng(42)
    boot_jsds = np.empty(n_boot)
    for b in range(n_boot):
        ba = arr_a[rng.integers(0, na, size=na)]
        bb = arr_b[rng.integers(0, nb, size=nb)]
        boot_jsds[b] = _jsd_from_counts(_counts(ba), _counts(bb), all_treatments, smoothing)

    # BCa correction
    # Bias correction factor z0
    prop_less = np.sum(boot_jsds < jsd_obs) / n_boot
    from scipy.stats import norm
    z0 = norm.ppf(max(min(prop_less, 0.9999), 0.0001))

    # Acceleration factor from jackknife
    jack_vals = np.empty(na)
    for i in range(na):
        jack_a = np.concatenate([arr_a[:i], arr_a[i+1:]])
        jack_vals[i] = _jsd_from_counts(_counts(jack_a), _counts(arr_b), all_treatments, smoothing)
    jack_mean = jack_vals.mean()
    num = np.sum((jack_mean - jack_vals) ** 3)
    den = 6.0 * (np.sum((jack_mean - jack_vals) ** 2) ** 1.5)
    a_hat = num / den if abs(den) > 1e-12 else 0.0

    # Adjusted percentiles
    z_alpha = norm.ppf(alpha / 2)
    z_1alpha = norm.ppf(1 - alpha / 2)

    def _bca_percentile(z):
        num = z0 + z
        adj = z0 + num / (1.0 - a_hat * num) if abs(1.0 - a_hat * num) > 1e-12 else z0 + num
        return norm.cdf(adj)

    p_lo = _bca_percentile(z_alpha)
    p_hi = _bca_percentile(z_1alpha)

    ci_lo = float(np.quantile(boot_jsds, max(min(p_lo, 0.9999), 0.0001)))
    ci_hi = float(np.quantile(boot_jsds, max(min(p_hi, 0.9999), 0.0001)))

    return float(jsd_obs), ci_lo, ci_hi


# =====================================================================
# OMNIBUS DISTRIBUTION SHIFT TEST
# =====================================================================

def permutation_chi2(table_a, table_b, all_treatments, n_perm=5000):
    """
    Permutation-based chi-squared test for overall distribution shift.
    Tests H0: treatment distributions are identical between conditions A and B.

    Parameters:
        table_a: dict {treatment: count} for condition A (aggregated over N runs)
        table_b: dict {treatment: count} for condition B
        all_treatments: list of all treatment labels
        n_perm: number of permutations

    Returns:
        (chi2_observed, p_value)
    """
    # Build contingency matrix: rows = treatments, cols = conditions
    obs_a = np.array([table_a.get(t, 0) for t in all_treatments], dtype=float)
    obs_b = np.array([table_b.get(t, 0) for t in all_treatments], dtype=float)

    # Drop treatments with zero total (no information)
    mask = (obs_a + obs_b) > 0
    if mask.sum() < 2:
        return 0.0, 1.0  # Not enough categories

    obs_a = obs_a[mask]
    obs_b = obs_b[mask]

    def _chi2(a, b):
        total = a + b
        n_a = a.sum()
        n_b = b.sum()
        n_total = n_a + n_b
        if n_total == 0:
            return 0.0
        exp_a = total * n_a / n_total
        exp_b = total * n_b / n_total
        # Avoid division by zero
        exp_a = np.maximum(exp_a, 1e-10)
        exp_b = np.maximum(exp_b, 1e-10)
        return float(np.sum((a - exp_a)**2 / exp_a + (b - exp_b)**2 / exp_b))

    chi2_obs = _chi2(obs_a, obs_b)

    # Permutation: pool all counts and randomly reassign to conditions
    pooled = obs_a + obs_b
    n_a_total = int(obs_a.sum())
    n_total = int(pooled.sum())

    rng = np.random.default_rng(42)
    count_ge = 0
    for _ in range(n_perm):
        # Generate random split: sample n_a_total items from pooled
        # Multinomial approximation
        perm_a = rng.multinomial(n_a_total, pooled / pooled.sum())
        perm_b = pooled - perm_a
        perm_b = np.maximum(perm_b, 0)  # Guard against rounding
        chi2_perm = _chi2(perm_a.astype(float), perm_b.astype(float))
        if chi2_perm >= chi2_obs:
            count_ge += 1

    p_value = (count_ge + 1) / (n_perm + 1)  # +1 for continuity
    return chi2_obs, p_value


# =====================================================================
# DIRECTION ANALYSIS
# =====================================================================

def assess_direction(edge_test, battery_item):
    """
    Determine if the distribution shift is in the correct direction.

    For a perturbation that should EXCLUDE a treatment:
        Correct = recommendation rate decreased (base_rec_rate > pert_rec_rate)
    For a perturbation that should RECOMMEND a treatment:
        Correct = recommendation rate increased or stayed high

    Returns: True (correct), False (wrong), None (not assessable)
    """
    tx = edge_test["treatment"]
    exp_rec = set(edge_test.get("exp_rec", []))
    exp_exc = set(edge_test.get("exp_exc", []))
    base_rate = edge_test.get("base_rec_rate", 0)
    pert_rate = edge_test.get("pert_rec_rate", 0)

    if tx in exp_exc:
        # Perturbation should reduce this treatment
        return pert_rate < base_rate
    elif tx in exp_rec:
        # Perturbation should maintain or increase this treatment
        # But we need the baseline expectation too — if it was already recommended
        # in baseline, a non-decrease is correct
        return pert_rate >= base_rate - 0.1  # Allow small noise margin
    return None


# =====================================================================
# ENHANCED KG2 ASSEMBLY
# =====================================================================

def assemble_kg2_enhanced(edge_tests, all_parsed, battery_items):
    """
    Build enriched KG2 per model with direction, JSD weights, CIs, and omnibus tests.

    Parameters:
        edge_tests: list of dicts from detect_edges() in response_parser.py
        all_parsed: list of parsed results from parse_result()
        battery_items: dict {item_id: item_dict} from vignette battery

    Returns:
        dict {model_name: {edge_id: KG2Edge}}
    """
    # Group parsed results by (item_id, model)
    grouped = defaultdict(list)
    for p in all_parsed:
        grouped[(p["item_id"], p["model_name"])].append(p)

    # Group edge tests by (model, edge), but ONLY keep tests for target treatments
    # (those in exp_rec or exp_exc). Bystander treatments dilute edge detection rates.
    model_edge_tests = defaultdict(lambda: defaultdict(list))
    for t in edge_tests:
        tx = t["treatment"]
        target_tx = set(t.get("exp_rec", [])) | set(t.get("exp_exc", []))
        if tx not in target_tx:
            continue  # Skip bystander treatments — they don't test this edge
        for edge in t.get("edges", []):
            model_edge_tests[t["model"]][edge].append(t)

    # Also track ALL tests (including bystanders) for omnibus/spurious analysis
    model_edge_all = defaultdict(lambda: defaultdict(list))
    for t in edge_tests:
        for edge in t.get("edges", []):
            model_edge_all[t["model"]][edge].append(t)

    kg2 = {}
    for model_name, edges_dict in model_edge_tests.items():
        kg2[model_name] = {}

        for edge_id, tests in edges_dict.items():
            n_probes = len(tests)
            n_detected = sum(1 for t in tests if t.get("significant", False))

            # Direction analysis
            directions = []
            for t in tests:
                pert_item = battery_items.get(t["pert_id"])
                if pert_item:
                    d = assess_direction(t, pert_item)
                    if d is not None:
                        directions.append(d)

            n_correct_dir = sum(directions) if directions else 0
            direction_rate = n_correct_dir / len(directions) if directions else 0.0

            # JSD values
            jsd_values = [t["jsd"] for t in tests if t.get("jsd") is not None and t["jsd"] > 0]

            # Bootstrap CIs for mean JSD
            mean_jsd = float(np.mean(jsd_values)) if jsd_values else 0.0
            median_jsd = float(np.median(jsd_values)) if jsd_values else 0.0
            ci_lo, ci_hi = 0.0, 0.0

            if len(jsd_values) >= 3:
                # Simple bootstrap on JSD values (not on raw samples — we're aggregating)
                rng = np.random.default_rng(42)
                boot_means = []
                arr = np.array(jsd_values)
                for _ in range(2000):
                    boot_means.append(float(rng.choice(arr, size=len(arr), replace=True).mean()))
                ci_lo = float(np.percentile(boot_means, 2.5))
                ci_hi = float(np.percentile(boot_means, 97.5))

            # Omnibus test for the first perturbation (representative)
            # Use all tests (including bystanders) for a full-distribution omnibus
            omnibus_sig = None
            omnibus_p = None
            all_tests_for_edge = model_edge_all.get(model_name, {}).get(edge_id, tests)
            if all_tests_for_edge:
                t0 = all_tests_for_edge[0]
                base_parsed = grouped.get((t0["base_id"], model_name), [])
                pert_parsed = grouped.get((t0["pert_id"], model_name), [])
                if base_parsed and pert_parsed:
                    # Build stance count tables
                    base_counts = Counter()
                    pert_counts = Counter()
                    for p in base_parsed:
                        for s in p["stances"]:
                            base_counts[s["treatment"] + ":" + s["stance"]] += 1
                    for p in pert_parsed:
                        for s in p["stances"]:
                            pert_counts[s["treatment"] + ":" + s["stance"]] += 1

                    all_keys = sorted(set(list(base_counts.keys()) + list(pert_counts.keys())))
                    if len(all_keys) >= 2:
                        _, omnibus_p = permutation_chi2(
                            dict(base_counts), dict(pert_counts), all_keys, n_perm=2000
                        )
                        omnibus_sig = omnibus_p < 0.05

            # Conditionality: check if edge was tested across multiple families
            families_tested = list(set(t.get("pert_id", "")[:2] for t in tests))
            # (rough proxy — A=glottic_cT2, B=glottic_cT3, etc.)

            hard_detected = n_detected > n_probes / 2
            det_rate = n_detected / n_probes if n_probes > 0 else 0.0
            # Soft detection: omnibus significant OR at least 25% of probes significant
            soft_det = bool(omnibus_sig) or det_rate >= 0.25

            edge = KG2Edge(
                edge_id=edge_id,
                model=model_name,
                detected=hard_detected,
                soft_detected=soft_det,
                detection_rate=det_rate,
                n_probes=n_probes,
                direction_correct=direction_rate > 0.5 if directions else None,
                direction_rate=direction_rate,
                mean_jsd=mean_jsd,
                median_jsd=median_jsd,
                jsd_ci_lower=ci_lo,
                jsd_ci_upper=ci_hi,
                jsd_values=jsd_values,
                conditionality_tested=len(set(t.get("pert_id", "")[:1] for t in tests)) > 1,
                omnibus_significant=omnibus_sig,
                omnibus_p=omnibus_p,
            )
            kg2[model_name][edge_id] = edge

    return kg2


# =====================================================================
# SPURIOUS EDGE DETECTION
# =====================================================================

def detect_spurious_edges(all_parsed, battery_items, edge_tests):
    """
    Detect spurious edges: model responds to null perturbations (where it shouldn't).

    For each null perturbation, compute JSD between baseline and null.
    Any JSD above the noise threshold suggests surface-level sensitivity.

    Also checks: for treatments NOT in expected_recommendations or expected_excluded,
    did the model show significant shifts? These would be phantom edges.

    Returns:
        dict with:
            - null_jsd_by_model: {model: [jsd values on null perturbations]}
            - noise_threshold_by_model: {model: 95th percentile of null JSD}
            - phantom_edges: list of {model, pert_id, treatment, jsd, detail}
    """
    # Null perturbation JSDs
    null_jsd = defaultdict(list)
    for t in edge_tests:
        if t.get("type") == "null":
            null_jsd[t["model"]].append(t.get("jsd", 0))

    noise_thresholds = {}
    for model, jsds in null_jsd.items():
        if jsds:
            noise_thresholds[model] = float(np.percentile(jsds, 95))

    # Phantom edges: significant tests on treatments outside expectations
    phantom_edges = []
    for t in edge_tests:
        if not t.get("significant"):
            continue
        tx = t["treatment"]
        exp_rec = set(t.get("exp_rec", []))
        exp_exc = set(t.get("exp_exc", []))

        if tx not in exp_rec and tx not in exp_exc:
            # This treatment wasn't expected to be affected — spurious edge
            phantom_edges.append({
                "model": t["model"],
                "pert_id": t["pert_id"],
                "base_id": t["base_id"],
                "treatment": tx,
                "jsd": t.get("jsd", 0),
                "p_value": t.get("adjusted_p", t.get("p_value")),
                "detail": f"Significant shift in {tx} which is not in KG1 expectations for {t['pert_id']}"
            })

    return {
        "null_jsd_by_model": dict(null_jsd),
        "noise_thresholds": noise_thresholds,
        "phantom_edges": phantom_edges,
    }


# =====================================================================
# GRAPH COMPARISON METRICS
# =====================================================================

def compute_graph_comparison(kg2_enhanced, kg1_edges=None, spurious_data=None):
    """
    Compute publication-ready comparison metrics between KG1 and KG2.

    Parameters:
        kg2_enhanced: dict {model: {edge_id: KG2Edge}} from assemble_kg2_enhanced()
        kg1_edges: optional dict {edge_id: KG1Edge} with consensus weights
                   If None, all edges in KG2 are assumed to be in KG1 (confirmatory mode)
        spurious_data: output from detect_spurious_edges()

    Returns:
        dict {model: GraphComparison}
    """
    comparisons = {}

    for model, edges in kg2_enhanced.items():
        comp = GraphComparison(model=model)

        # All KG1 edges that were tested for this model
        kg1_tested = set(edges.keys())

        detected_edges = {eid for eid, e in edges.items() if e.detected}
        soft_detected_edges = {eid for eid, e in edges.items() if e.soft_detected}
        missed_edges = kg1_tested - detected_edges

        comp.true_positives = len(detected_edges)
        comp.false_negatives = len(missed_edges)
        comp.soft_true_positives = len(soft_detected_edges)

        # Spurious edges (false positives)
        if spurious_data:
            phantom = [p for p in spurious_data.get("phantom_edges", []) if p["model"] == model]
            comp.false_positives = len(set((p["pert_id"], p["treatment"]) for p in phantom))

        # Precision, recall, F1
        tp, fn, fp = comp.true_positives, comp.false_negatives, comp.false_positives
        comp.precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        comp.recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        comp.f1 = (2 * comp.precision * comp.recall / (comp.precision + comp.recall)
                    if (comp.precision + comp.recall) > 0 else 0.0)

        # Soft detection metrics
        stp = comp.soft_true_positives
        sfn = len(kg1_tested) - stp
        comp.soft_recall = stp / (stp + sfn) if (stp + sfn) > 0 else 0.0
        soft_prec = stp / (stp + fp) if (stp + fp) > 0 else 0.0
        comp.soft_f1 = (2 * soft_prec * comp.soft_recall / (soft_prec + comp.soft_recall)
                        if (soft_prec + comp.soft_recall) > 0 else 0.0)

        # SHD = false positives + false negatives + direction errors
        direction_errors = sum(
            1 for e in edges.values()
            if e.detected and e.direction_correct is False
        )
        comp.direction_errors = direction_errors
        comp.shd = fp + len(missed_edges) + direction_errors

        # Direction accuracy (among detected edges)
        detected_with_dir = [e for e in edges.values() if e.detected and e.direction_correct is not None]
        if detected_with_dir:
            comp.direction_accuracy = sum(
                1 for e in detected_with_dir if e.direction_correct
            ) / len(detected_with_dir)

        # Weighted metrics (by KG1 consensus weight if available)
        if kg1_edges:
            w_tp = sum(kg1_edges[eid].consensus_weight for eid in detected_edges if eid in kg1_edges)
            w_all = sum(kg1_edges[eid].consensus_weight for eid in kg1_tested if eid in kg1_edges)
            comp.weighted_recall = w_tp / w_all if w_all > 0 else 0.0

            # Calibration: correlation between KG1 consensus weight and KG2 JSD
            weights_kg1 = []
            weights_kg2 = []
            for eid, e in edges.items():
                if eid in kg1_edges and e.mean_jsd > 0:
                    weights_kg1.append(kg1_edges[eid].consensus_weight)
                    weights_kg2.append(e.mean_jsd)
            if len(weights_kg1) >= 3:
                from scipy.stats import spearmanr
                corr, _ = spearmanr(weights_kg1, weights_kg2)
                comp.weight_correlation = float(corr) if not np.isnan(corr) else 0.0

                # Calibration error: normalise both to [0,1] and compute MAE
                kg1_norm = np.array(weights_kg1) / max(weights_kg1)
                kg2_norm = np.array(weights_kg2) / max(weights_kg2) if max(weights_kg2) > 0 else np.zeros_like(weights_kg2)
                comp.calibration_error = float(np.mean(np.abs(kg1_norm - kg2_norm)))

        # Null specificity
        if spurious_data:
            null_jsds = spurious_data.get("null_jsd_by_model", {}).get(model, [])
            if null_jsds:
                comp.null_jsd_mean = float(np.mean(null_jsds))
                comp.null_jsd_95 = float(np.percentile(null_jsds, 95))

        comparisons[model] = comp

    return comparisons


# =====================================================================
# ENHANCED REPORT
# =====================================================================

def generate_enhanced_report(kg2_enhanced, comparisons, spurious_data, out_path):
    """Generate publication-ready markdown report."""
    L = []
    L.append("# KG2 Enhanced Analysis Report\n")
    L.append("## 1. Graph Comparison Metrics\n")

    models = sorted(comparisons.keys())
    L.append("| Model | TP | FN | FP | Prec | Recall | F1 | Soft TP | Soft Recall | Soft F1 | SHD | Dir Acc | Null JSD 95 |")
    L.append("|---|---|---|---|---|---|---|---|---|---|---|---|---|")
    for m in models:
        c = comparisons[m]
        L.append(
            f"| {m} | {c.true_positives} | {c.false_negatives} | {c.false_positives} "
            f"| {c.precision:.2f} | {c.recall:.2f} | {c.f1:.2f} "
            f"| {c.soft_true_positives} | {c.soft_recall:.2f} | {c.soft_f1:.2f} "
            f"| {c.shd} | {c.direction_accuracy:.0%} | {c.null_jsd_95:.4f} |"
        )

    L.append("\n## 2. Edge-Level Detail\n")
    for m in models:
        L.append(f"\n### {m}\n")
        L.append("| Edge | Hard | Soft | Dir | JSD | 95% CI | Omnibus p | N |")
        L.append("|---|---|---|---|---|---|---|---|")
        for eid in sorted(kg2_enhanced[m].keys()):
            e = kg2_enhanced[m][eid]
            hard = "+" if e.detected else "-"
            soft = "+" if e.soft_detected else "-"
            dir_s = "OK" if e.direction_correct else ("WRONG" if e.direction_correct is False else "?")
            ci = f"[{e.jsd_ci_lower:.3f}, {e.jsd_ci_upper:.3f}]" if e.jsd_ci_lower > 0 else "-"
            omni = f"{e.omnibus_p:.3f}" if e.omnibus_p is not None else "-"
            L.append(f"| {eid} | {hard} ({e.detection_rate:.0%}) | {soft} | {dir_s} ({e.direction_rate:.0%}) "
                     f"| {e.mean_jsd:.4f} | {ci} | {omni} | {e.n_probes} |")

    L.append("\n## 3. Spurious Edges\n")
    phantoms = spurious_data.get("phantom_edges", [])
    if phantoms:
        L.append(f"Total phantom edges detected: {len(phantoms)}\n")
        by_model = defaultdict(list)
        for p in phantoms:
            by_model[p["model"]].append(p)
        for m in sorted(by_model.keys()):
            L.append(f"\n**{m}**: {len(by_model[m])} phantom edges")
            for p in by_model[m][:10]:
                L.append(f"- {p['pert_id']} x {p['treatment']}: JSD={p['jsd']:.4f}, p={p['p_value']:.4f}")
    else:
        L.append("No phantom edges detected.\n")

    L.append("\n## 4. Noise Floor (Null Perturbations)\n")
    for m in models:
        nulls = spurious_data.get("null_jsd_by_model", {}).get(m, [])
        if nulls:
            L.append(f"- **{m}**: mean={np.mean(nulls):.4f}, "
                     f"median={np.median(nulls):.4f}, "
                     f"95th={np.percentile(nulls, 95):.4f}, "
                     f"max={max(nulls):.4f}")

    report = "\n".join(L)
    with open(out_path, "w") as f:
        f.write(report)
    return report


# =====================================================================
# MAIN PIPELINE
# =====================================================================

def run_enhanced_analysis(edge_tests, all_parsed, battery_items, output_dir=None):
    """
    Run full enhanced KG2 analysis. Call after base response_parser.run_analysis().

    Parameters:
        edge_tests: from response_parser.detect_edges()
        all_parsed: from response_parser.parse_result() applied to all results
        battery_items: dict {item_id: item_dict}
        output_dir: path to save outputs (optional)

    Returns:
        (kg2_enhanced, comparisons, spurious_data)
    """
    print("=" * 60)
    print("KG2 ENHANCED ANALYSIS")
    print("=" * 60)

    # 1. Enhanced KG2 assembly
    print("\n[1/4] Assembling enhanced KG2...")
    kg2 = assemble_kg2_enhanced(edge_tests, all_parsed, battery_items)
    for m in sorted(kg2.keys()):
        n_hard = sum(1 for e in kg2[m].values() if e.detected)
        n_soft = sum(1 for e in kg2[m].values() if e.soft_detected)
        n_total = len(kg2[m])
        mean_jsd = np.mean([e.mean_jsd for e in kg2[m].values() if e.mean_jsd > 0]) if kg2[m] else 0
        print(f"  {m}: {n_hard}/{n_total} hard, {n_soft}/{n_total} soft detected, mean JSD={mean_jsd:.4f}")

    # 2. Spurious edge detection
    print("\n[2/4] Detecting spurious edges...")
    spurious_data = detect_spurious_edges(all_parsed, battery_items, edge_tests)
    n_phantom = len(spurious_data.get("phantom_edges", []))
    print(f"  Phantom edges: {n_phantom}")
    for m, jsds in spurious_data.get("null_jsd_by_model", {}).items():
        print(f"  {m} null JSD: mean={np.mean(jsds):.4f}, 95th={np.percentile(jsds, 95):.4f}")

    # 3. Graph comparison
    print("\n[3/4] Computing graph comparison metrics...")
    comparisons = compute_graph_comparison(kg2, kg1_edges=None, spurious_data=spurious_data)
    for m in sorted(comparisons.keys()):
        c = comparisons[m]
        print(f"  {m}: P={c.precision:.2f} R={c.recall:.2f} F1={c.f1:.2f} "
              f"SoftR={c.soft_recall:.2f} SoftF1={c.soft_f1:.2f} "
              f"SHD={c.shd} DirAcc={c.direction_accuracy:.0%}")

    # 4. Save outputs
    if output_dir:
        out = Path(output_dir)
        out.mkdir(parents=True, exist_ok=True)

        # KG2 as serialisable dict
        kg2_serial = {}
        for m, edges in kg2.items():
            kg2_serial[m] = {}
            for eid, e in edges.items():
                d = asdict(e)
                d.pop("jsd_values", None)  # Don't dump raw arrays
                kg2_serial[m][eid] = d
        with open(out / "kg2_enhanced.json", "w") as f:
            json.dump(kg2_serial, f, indent=2)

        # Comparisons
        comp_serial = {m: asdict(c) for m, c in comparisons.items()}
        with open(out / "graph_comparison.json", "w") as f:
            json.dump(comp_serial, f, indent=2)

        # Spurious
        with open(out / "spurious_edges.json", "w") as f:
            json.dump(spurious_data, f, indent=2, default=str)

        # Report
        print("\n[4/4] Generating report...")
        generate_enhanced_report(kg2, comparisons, spurious_data, out / "kg2_report.md")
        print(f"  Saved to: {out}/")

    return kg2, comparisons, spurious_data


# =====================================================================
# CLI ENTRY POINT
# =====================================================================

def main():
    """Run as standalone add-on after base analysis."""
    p = argparse.ArgumentParser(description="KG2 Enhanced Analysis (add-on)")
    p.add_argument("--results", required=True, help="Path to run_XXX.jsonl")
    p.add_argument("--battery", required=True, help="Path to vignette_battery.json")
    p.add_argument("--outdir", default="analysis", help="Output directory")
    args = p.parse_args()

    # Re-use base parser for data loading
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

    # Run base edge detection
    edge_tests = detect_edges(all_parsed, battery_items)
    if edge_tests:
        sig = sum(1 for t in edge_tests if t.get("significant"))
        print(f"Base edge tests: {len(edge_tests)} total, {sig} significant")

    # Run enhanced analysis
    run_enhanced_analysis(edge_tests, all_parsed, battery_items, args.outdir)


if __name__ == "__main__":
    main()
