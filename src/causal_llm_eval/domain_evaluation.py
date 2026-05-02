#!/usr/bin/env python3
"""Primary domain evaluation and supplementary manuscript analyses."""

from __future__ import annotations

import csv
import json
from collections import defaultdict
from pathlib import Path

import numpy as np

from .benchmark_audit import build_traceability_rows, load_battery
from .json_utils import dump_json
from .kg2_enhanced import KG2Edge, compute_graph_comparison, generate_enhanced_report


MODEL_ORDER = [
    "deepseek-r1",
    "kimi-k2.5",
    "qwen3-next-80b-instruct",
    "mistral-small-24b",
    "gemma-4-31b-it",
    "llama-3.1-8b",
]

MODEL_LABELS = {
    "deepseek-r1": "DeepSeek-R1",
    "kimi-k2.5": "Kimi K2.5",
    "qwen3-next-80b-instruct": "Qwen3-Next-80B-A3B-Instruct",
    "mistral-small-24b": "Mistral-Small-24B",
    "gemma-4-31b-it": "Gemma 4 31B",
    "llama-3.1-8b": "Llama 3.1-8B",
}

MODEL_COLORS = {
    "deepseek-r1": "#1D3557",
    "kimi-k2.5": "#0B7285",
    "qwen3-next-80b-instruct": "#3A7D44",
    "mistral-small-24b": "#7C5CFF",
    "gemma-4-31b-it": "#C27C0E",
    "llama-3.1-8b": "#B42318",
}

FAILURE_REGIMES = {
    "deepseek-r1": "balanced",
    "kimi-k2.5": "broad but noisy",
    "qwen3-next-80b-instruct": "partial and brittle",
    "mistral-small-24b": "partial and brittle",
    "gemma-4-31b-it": "partial and brittle",
    "llama-3.1-8b": "fragmentary",
}

SOFT_SWEEP_VALUES = [0.15, 0.25, 0.35]
HARD_RATE_VALUES = [0.40, 0.50, 0.60]
HARD_JSD_VALUES = [0.05, 0.10, 0.15]

_FALLBACK_COLORS = [
    "#1D4ED8",
    "#047857",
    "#7C3AED",
    "#B45309",
    "#BE123C",
    "#0F766E",
]

TIER3_TREATMENTS = {"total_laryngectomy"}
TIER2_TREATMENTS = {
    "tlm",
    "tors",
    "ophl_any",
    "ophl_type_i",
    "ophl_type_iib",
    "ophl_type_ii",
    "ophl_type_iii",
    "surgical_lp",
    "nonsurgical_lp",
    "concurrent_crt",
    "ict_rt",
    "rt_alone",
    "rt_accelerated",
}


def load_json(path: str | Path) -> dict:
    with open(path) as f:
        return json.load(f)


def ordered_models(models) -> list[str]:
    model_set = set(models.keys() if hasattr(models, "keys") else models)
    preferred = [model for model in MODEL_ORDER if model in model_set]
    extras = sorted(model_set - set(MODEL_ORDER))
    return preferred + extras


def model_label(model: str) -> str:
    return MODEL_LABELS.get(model, model)


def model_color(model: str) -> str:
    if model in MODEL_COLORS:
        return MODEL_COLORS[model]
    return _FALLBACK_COLORS[sum(ord(ch) for ch in model) % len(_FALLBACK_COLORS)]


def failure_regime(model: str) -> str:
    return FAILURE_REGIMES.get(model, "unclassified")


def pct(value: float | None) -> str:
    if value is None:
        return "NA"
    return f"{value * 100:.1f}%"


def fmt_ci(metric: dict) -> str:
    return f"{pct(metric['estimate'])} ({pct(metric['ci_low'])} to {pct(metric['ci_high'])})"


def fmt_num_ci(metric: dict, digits: int = 2) -> str:
    return (
        f"{metric['estimate']:.{digits}f} "
        f"({metric['ci_low']:.{digits}f} to {metric['ci_high']:.{digits}f})"
    )


def serialise_csv(path: Path, rows: list[dict]) -> None:
    if not rows:
        path.write_text("")
        return
    with open(path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def deserialise_kg2(path: str | Path) -> dict[str, dict[str, KG2Edge]]:
    raw = load_json(path)
    kg2 = {}
    for model, edges in raw.items():
        kg2[model] = {}
        for edge_id, payload in edges.items():
            kg2[model][edge_id] = KG2Edge(**payload)
    return kg2


def treatment_risk_weight(treatment: str) -> int:
    if treatment in TIER3_TREATMENTS:
        return 3
    if treatment in TIER2_TREATMENTS:
        return 2
    return 1


def _split_labels(raw: str) -> list[str]:
    if not raw:
        return []
    return [part.strip() for part in raw.split(",") if part.strip()]


def build_edge_risk_map(traceability_rows: list[dict]) -> dict[str, dict]:
    edge_map = defaultdict(lambda: {"weight": 1, "treatments": set()})
    for row in traceability_rows:
        labels = _split_labels(row.get("expected_recommendations", "")) + _split_labels(row.get("expected_excluded", ""))
        if not labels:
            continue
        weights = [treatment_risk_weight(label) for label in labels]
        edge_map[row["edge_id"]]["weight"] = max(edge_map[row["edge_id"]]["weight"], max(weights))
        edge_map[row["edge_id"]]["treatments"].update(labels)
    return {
        edge_id: {"weight": payload["weight"], "treatments": sorted(payload["treatments"])}
        for edge_id, payload in edge_map.items()
    }


def build_family_edge_map(battery: dict) -> dict[str, set[str]]:
    family_edges = defaultdict(set)
    for item in battery.get("perturbations", []):
        if item.get("type") == "null":
            continue
        for edge_id in item.get("edge_justification", []):
            family_edges[item.get("family", "")].add(edge_id)
    for item in battery.get("baselines", []):
        family_edges.setdefault(item.get("family", ""), set())
    return dict(sorted(family_edges.items()))


def compute_threshold_sensitivity(kg2_enhanced: dict, edge_tests: list[dict], spurious_data: dict) -> list[dict]:
    rows = []

    def append_rows(mode: str, comparisons: dict, *, soft_detection_rate=None, hard_detection_rate=None, hard_mean_jsd_threshold=None):
        for model in ordered_models(comparisons):
            comp = comparisons[model]
            rows.append(
                {
                    "mode": mode,
                    "model": model,
                    "model_label": model_label(model),
                    "soft_detection_rate": soft_detection_rate,
                    "hard_detection_rate": hard_detection_rate,
                    "hard_mean_jsd_threshold": hard_mean_jsd_threshold,
                    "soft_recall": comp.soft_recall,
                    "hard_recall": comp.recall,
                    "soft_direction_accuracy": comp.direction_accuracy,
                    "hard_direction_accuracy": comp.hard_direction_accuracy,
                    "soft_precision": comp.soft_precision,
                    "soft_fdr": comp.soft_fdr,
                    "hard_precision": comp.hard_precision,
                    "hard_fdr": comp.hard_fdr,
                }
            )

    append_rows("locked_default", compute_graph_comparison(kg2_enhanced, spurious_data=spurious_data))
    for thr in SOFT_SWEEP_VALUES:
        append_rows(
            "soft_sweep",
            compute_graph_comparison(
                kg2_enhanced,
                spurious_data=spurious_data,
                edge_tests=edge_tests,
                soft_detection_rate=thr,
            ),
            soft_detection_rate=thr,
        )
    for rate in HARD_RATE_VALUES:
        for jsd in HARD_JSD_VALUES:
            append_rows(
                "hard_sweep",
                compute_graph_comparison(
                    kg2_enhanced,
                    spurious_data=spurious_data,
                    edge_tests=edge_tests,
                    hard_detection_rate=rate,
                    hard_mean_jsd_threshold=jsd,
                ),
                hard_detection_rate=rate,
                hard_mean_jsd_threshold=jsd,
            )
    return rows


def write_threshold_report(rows: list[dict], outdir: Path) -> None:
    by_mode = defaultdict(list)
    for row in rows:
        by_mode[row["mode"]].append(row)
    models = ordered_models({row["model"] for row in rows})

    soft_rows = by_mode["soft_sweep"]
    hard_rows = by_mode["hard_sweep"]
    soft_leaders = {}
    for threshold in sorted({row["soft_detection_rate"] for row in soft_rows}):
        configs = [r for r in soft_rows if r["soft_detection_rate"] == threshold]
        soft_leaders[threshold] = max(configs, key=lambda item: item["soft_recall"])["model"]
    hard_leaders = {}
    for row in hard_rows:
        key = (row["hard_detection_rate"], row["hard_mean_jsd_threshold"])
        configs = [r for r in hard_rows if (r["hard_detection_rate"], r["hard_mean_jsd_threshold"]) == key]
        hard_leaders[key] = max(configs, key=lambda item: item["hard_recall"])["model"]
    hard_win_counts = defaultdict(int)
    for leader in hard_leaders.values():
        hard_win_counts[leader] += 1
    soft_dir_means = {
        model: float(np.mean([r["soft_direction_accuracy"] for r in soft_rows if r["model"] == model]))
        for model in models
    }
    strongest_soft_dir = max(soft_dir_means.items(), key=lambda item: item[1])[0]
    weakest_locked_default = min(
        [r for r in rows if r["mode"] == "locked_default"],
        key=lambda item: item["soft_recall"],
    )["model"]

    lines = []
    lines.append("# Threshold Sensitivity Analysis\n")
    lines.append("This supplementary analysis evaluates how the main detection-dependent metrics vary across threshold choices.")
    lines.append("The locked default outputs are preserved; the sweeps are used only as robustness checks.\n")
    lines.append("## Qualitative Summary")
    if len(set(soft_leaders.values())) == 1:
        leader = next(iter(soft_leaders.values()))
        lines.append(f"- Across all soft-threshold settings, the highest soft recall remained with `{model_label(leader)}`.")
    else:
        leader_map = ", ".join(
            f"`{threshold:.2f}`: `{model_label(model)}`" for threshold, model in sorted(soft_leaders.items())
        )
        lines.append(f"- The soft-recall leader varied modestly across thresholds: {leader_map}.")
    strongest_soft_dir_values = [r["soft_direction_accuracy"] for r in soft_rows if r["model"] == strongest_soft_dir]
    lines.append(
        f"- `{model_label(strongest_soft_dir)}` retained the strongest soft-edge direction accuracy across the soft-threshold sweep "
        f"({pct(min(strongest_soft_dir_values))} to {pct(max(strongest_soft_dir_values))})."
    )
    most_common_hard_leader = max(hard_win_counts.items(), key=lambda item: item[1])[0]
    lines.append(
        f"- `{model_label(most_common_hard_leader)}` had the highest hard recall in `{hard_win_counts[most_common_hard_leader]}` of "
        f"`{len(hard_leaders)}` hard-threshold configurations."
    )
    lines.append(
        f"- `{model_label(weakest_locked_default)}` remained the weakest locked-default coverage model; "
        "discriminability is unchanged because SNR and detection power are threshold-independent.\n"
    )

    lines.append("## Soft-Threshold Sweep")
    lines.append("| Model | Threshold | Soft recall | Soft precision | Soft FDR | Soft-edge direction accuracy |")
    lines.append("|---|---:|---:|---:|---:|---:|")
    for model in models:
        for row in sorted((r for r in soft_rows if r["model"] == model), key=lambda item: item["soft_detection_rate"]):
            lines.append(
                f"| {model_label(model)} | {row['soft_detection_rate']:.2f} | {pct(row['soft_recall'])} | "
                f"{pct(row['soft_precision'])} | {pct(row['soft_fdr'])} | {pct(row['soft_direction_accuracy'])} |"
            )

    lines.append("\n## Hard-Threshold Sweep")
    lines.append("| Model | Rate threshold | JSD threshold | Hard recall | Hard precision | Hard FDR | Hard-edge direction accuracy |")
    lines.append("|---|---:|---:|---:|---:|---:|---:|")
    for model in models:
        model_rows = [r for r in hard_rows if r["model"] == model]
        model_rows.sort(key=lambda item: (item["hard_detection_rate"], item["hard_mean_jsd_threshold"]))
        for row in model_rows:
            lines.append(
                f"| {model_label(model)} | {row['hard_detection_rate']:.2f} | {row['hard_mean_jsd_threshold']:.2f} | "
                f"{pct(row['hard_recall'])} | {pct(row['hard_precision'])} | {pct(row['hard_fdr'])} | "
                f"{pct(row['hard_direction_accuracy'])} |"
            )

    (outdir / "threshold_sensitivity_report.md").write_text("\n".join(lines) + "\n")


def plot_threshold_sensitivity(rows: list[dict], outdir: Path) -> None:
    import matplotlib.pyplot as plt

    soft_rows = [r for r in rows if r["mode"] == "soft_sweep"]
    hard_rows = [r for r in rows if r["mode"] == "hard_sweep"]
    hard_labels = [f"{rate:.2f}/{jsd:.2f}" for rate in HARD_RATE_VALUES for jsd in HARD_JSD_VALUES]
    models = ordered_models({row["model"] for row in rows})

    fig, axes = plt.subplots(2, 2, figsize=(14.5, 9))
    fig.subplots_adjust(left=0.08, right=0.98, top=0.9, bottom=0.12, wspace=0.24, hspace=0.32)

    for model in models:
        color = model_color(model)
        model_soft = sorted((r for r in soft_rows if r["model"] == model), key=lambda item: item["soft_detection_rate"])
        axes[0, 0].plot(
            [r["soft_detection_rate"] for r in model_soft],
            [r["soft_recall"] for r in model_soft],
            marker="o",
            linewidth=2,
            color=color,
            label=model_label(model),
        )
        axes[0, 1].plot(
            [r["soft_detection_rate"] for r in model_soft],
            [r["soft_direction_accuracy"] for r in model_soft],
            marker="o",
            linewidth=2,
            color=color,
        )

        model_hard = sorted(
            (r for r in hard_rows if r["model"] == model),
            key=lambda item: (item["hard_detection_rate"], item["hard_mean_jsd_threshold"]),
        )
        axes[1, 0].plot(hard_labels, [r["hard_recall"] for r in model_hard], marker="o", linewidth=2, color=color)
        axes[1, 1].plot(hard_labels, [r["hard_direction_accuracy"] for r in model_hard], marker="o", linewidth=2, color=color)

    titles = [
        ("Soft recall across soft-detection thresholds", axes[0, 0]),
        ("Soft-edge direction accuracy across soft thresholds", axes[0, 1]),
        ("Hard recall across hard-threshold grid", axes[1, 0]),
        ("Hard-edge direction accuracy across hard-threshold grid", axes[1, 1]),
    ]
    for title, ax in titles:
        ax.set_title(title, fontsize=12, fontweight="bold", loc="left")
        ax.set_ylim(0, 1.02)
        ax.grid(axis="y", color="#E5E7EB", linewidth=0.8)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
    axes[0, 0].set_xlabel("Soft detection-rate threshold")
    axes[0, 1].set_xlabel("Soft detection-rate threshold")
    axes[1, 0].set_xlabel("Hard rate / mean-JSD threshold")
    axes[1, 1].set_xlabel("Hard rate / mean-JSD threshold")
    axes[1, 0].tick_params(axis="x", rotation=45)
    axes[1, 1].tick_params(axis="x", rotation=45)
    axes[0, 0].legend(loc="lower left", frameon=False, fontsize=9)
    fig.suptitle("Supplementary Figure S1. Threshold sensitivity of detection-dependent metrics", fontsize=14.5, fontweight="bold")
    outdir.mkdir(parents=True, exist_ok=True)
    fig.savefig(outdir / "supplementary_figureS1_threshold_sensitivity.svg", bbox_inches="tight")
    fig.savefig(outdir / "supplementary_figureS1_threshold_sensitivity.png", dpi=300, bbox_inches="tight")
    plt.close(fig)


def _bootstrap_percentile(values: list[float]) -> tuple[float, float]:
    return float(np.percentile(values, 2.5)), float(np.percentile(values, 97.5))


def _edge_records(kg2_enhanced: dict[str, dict[str, KG2Edge]]) -> dict[str, list[dict]]:
    records = defaultdict(list)
    for model, edges in kg2_enhanced.items():
        for edge_id, edge in edges.items():
            records[model].append(
                {
                    "edge_id": edge_id,
                    "soft_detected": bool(edge.soft_detected),
                    "hard_detected": bool(edge.detected),
                    "direction_correct": edge.direction_correct,
                }
            )
    return dict(records)


def _phantom_candidates(edge_tests: list[dict]) -> dict[str, list[dict]]:
    by_model = defaultdict(list)
    for row in edge_tests:
        tx = row["treatment"]
        exp_rec = set(row.get("exp_rec", []))
        exp_exc = set(row.get("exp_exc", []))
        if tx in exp_rec or tx in exp_exc:
            continue
        by_model[row["model"]].append(
            {
                "soft_positive": bool(row.get("significant")),
                "hard_positive": bool(row.get("significant")),
            }
        )
    return dict(by_model)


def compute_bootstrap_cis(
    kg2_enhanced: dict,
    edge_tests: list[dict],
    sid_details: dict,
    snr_details: dict,
    spurious_data: dict,
    *,
    n_boot: int = 2000,
    seed: int = 42,
) -> dict:
    rng = np.random.default_rng(seed)
    edge_records = _edge_records(kg2_enhanced)
    phantom_records = _phantom_candidates(edge_tests)
    causal_jsd_by_model = defaultdict(list)
    for row in edge_tests:
        if row.get("type") == "null":
            continue
        jsd = row.get("jsd")
        if jsd is not None:
            causal_jsd_by_model[row["model"]].append(float(jsd))

    summary = {}
    for model in ordered_models(kg2_enhanced):
        edges = edge_records[model]
        phantoms = phantom_records.get(model, [])
        sid_rows = sid_details[model]["details"]
        causal_jsd = causal_jsd_by_model[model]
        null_jsd = [float(x) for x in spurious_data.get("null_jsd_by_model", {}).get(model, [])]

        soft_recall_vals = []
        hard_recall_vals = []
        soft_precision_vals = []
        soft_fdr_vals = []
        soft_dir_vals = []
        hard_dir_vals = []
        sid_vals = []
        snr_vals = []
        power_vals = []

        edge_arr = np.array(edges, dtype=object)
        phantom_arr = np.array(phantoms, dtype=object) if phantoms else np.array([], dtype=object)
        sid_arr = np.array(sid_rows, dtype=object)
        causal_arr = np.array(causal_jsd)
        null_arr = np.array(null_jsd)

        for _ in range(n_boot):
            edge_sample = edge_arr[rng.integers(0, len(edge_arr), size=len(edge_arr))]
            soft_tp = sum(1 for row in edge_sample if row["soft_detected"])
            hard_tp = sum(1 for row in edge_sample if row["hard_detected"])
            soft_recall_vals.append(soft_tp / len(edge_sample))
            hard_recall_vals.append(hard_tp / len(edge_sample))

            soft_dir_rows = [row for row in edge_sample if row["soft_detected"] and row["direction_correct"] is not None]
            hard_dir_rows = [row for row in edge_sample if row["hard_detected"] and row["direction_correct"] is not None]
            soft_dir_vals.append(
                sum(1 for row in soft_dir_rows if row["direction_correct"]) / len(soft_dir_rows)
                if soft_dir_rows
                else 0.0
            )
            hard_dir_vals.append(
                sum(1 for row in hard_dir_rows if row["direction_correct"]) / len(hard_dir_rows)
                if hard_dir_rows
                else 0.0
            )

            if len(phantom_arr):
                phantom_sample = phantom_arr[rng.integers(0, len(phantom_arr), size=len(phantom_arr))]
                soft_fp = sum(1 for row in phantom_sample if row["soft_positive"])
            else:
                soft_fp = 0
            soft_precision_vals.append(soft_tp / (soft_tp + soft_fp) if (soft_tp + soft_fp) else 0.0)
            soft_fdr_vals.append(soft_fp / (soft_tp + soft_fp) if (soft_tp + soft_fp) else 0.0)

            sid_sample = sid_arr[rng.integers(0, len(sid_arr), size=len(sid_arr))]
            sid_wrong = sum(1 for row in sid_sample if row["wrong"])
            sid_vals.append(sid_wrong / len(sid_sample))

            causal_sample = causal_arr[rng.integers(0, len(causal_arr), size=len(causal_arr))]
            null_sample = null_arr[rng.integers(0, len(null_arr), size=len(null_arr))]
            snr_vals.append(float(causal_sample.mean() / null_sample.mean()) if null_sample.mean() > 0 else 0.0)
            null_95 = float(np.percentile(null_sample, 95))
            power_vals.append(float(np.mean(causal_sample > null_95)))

        summary[model] = {
            "soft_recall": {
                "estimate": len([row for row in edges if row["soft_detected"]]) / len(edges),
                "ci_low": _bootstrap_percentile(soft_recall_vals)[0],
                "ci_high": _bootstrap_percentile(soft_recall_vals)[1],
            },
            "hard_recall": {
                "estimate": len([row for row in edges if row["hard_detected"]]) / len(edges),
                "ci_low": _bootstrap_percentile(hard_recall_vals)[0],
                "ci_high": _bootstrap_percentile(hard_recall_vals)[1],
            },
            "soft_precision": {
                "estimate": compute_graph_comparison(kg2_enhanced, edge_tests=edge_tests, spurious_data=spurious_data)[model].soft_precision,
                "ci_low": _bootstrap_percentile(soft_precision_vals)[0],
                "ci_high": _bootstrap_percentile(soft_precision_vals)[1],
            },
            "soft_fdr": {
                "estimate": compute_graph_comparison(kg2_enhanced, edge_tests=edge_tests, spurious_data=spurious_data)[model].soft_fdr,
                "ci_low": _bootstrap_percentile(soft_fdr_vals)[0],
                "ci_high": _bootstrap_percentile(soft_fdr_vals)[1],
            },
            "soft_direction_accuracy": {
                "estimate": compute_graph_comparison(kg2_enhanced, spurious_data=spurious_data)[model].direction_accuracy,
                "ci_low": _bootstrap_percentile(soft_dir_vals)[0],
                "ci_high": _bootstrap_percentile(soft_dir_vals)[1],
            },
            "hard_direction_accuracy": {
                "estimate": compute_graph_comparison(kg2_enhanced, spurious_data=spurious_data)[model].hard_direction_accuracy,
                "ci_low": _bootstrap_percentile(hard_dir_vals)[0],
                "ci_high": _bootstrap_percentile(hard_dir_vals)[1],
            },
            "sid_rate": {
                "estimate": sid_details[model]["sid_normalised"],
                "ci_low": _bootstrap_percentile(sid_vals)[0],
                "ci_high": _bootstrap_percentile(sid_vals)[1],
            },
            "snr": {
                "estimate": snr_details[model]["snr"],
                "ci_low": _bootstrap_percentile(snr_vals)[0],
                "ci_high": _bootstrap_percentile(snr_vals)[1],
            },
            "detection_power": {
                "estimate": snr_details[model]["detection_power"],
                "ci_low": _bootstrap_percentile(power_vals)[0],
                "ci_high": _bootstrap_percentile(power_vals)[1],
            },
        }

    return summary


def write_bootstrap_report(summary: dict, outdir: Path) -> None:
    lines = []
    lines.append("# Bootstrap Confidence Intervals for Primary Metrics\n")
    lines.append("| Model | Soft recall | Hard recall | Soft precision | Soft FDR | Soft dir. acc. | Hard dir. acc. | SID rate | SNR | Detection power |")
    lines.append("|---|---|---|---|---|---|---|---|---|---|")
    for model in ordered_models(summary):
        row = summary[model]
        lines.append(
            f"| {model_label(model)} | {fmt_ci(row['soft_recall'])} | {fmt_ci(row['hard_recall'])} | "
            f"{fmt_ci(row['soft_precision'])} | {fmt_ci(row['soft_fdr'])} | "
            f"{fmt_ci(row['soft_direction_accuracy'])} | {fmt_ci(row['hard_direction_accuracy'])} | "
            f"{fmt_ci(row['sid_rate'])} | {fmt_num_ci(row['snr'])} | {fmt_ci(row['detection_power'])} |"
        )
    (outdir / "bootstrap_ci_summary.md").write_text("\n".join(lines) + "\n")


def compute_risk_weighted_fidelity(kg2_enhanced: dict, sid_details: dict, edge_risk_map: dict) -> dict:
    results = {}
    for model, edges in kg2_enhanced.items():
        soft_dir_edges = [
            (edge_id, edge)
            for edge_id, edge in edges.items()
            if edge.soft_detected and edge.direction_correct is not None
        ]
        edge_total_weight = sum(edge_risk_map.get(edge_id, {"weight": 1})["weight"] for edge_id, _ in soft_dir_edges)
        edge_wrong_weight = sum(
            edge_risk_map.get(edge_id, {"weight": 1})["weight"]
            for edge_id, edge in soft_dir_edges
            if edge.direction_correct is False
        )
        tier3_edge_wrong = sum(
            1
            for edge_id, edge in soft_dir_edges
            if edge.direction_correct is False and edge_risk_map.get(edge_id, {"weight": 1})["weight"] == 3
        )

        sid_rows = sid_details[model]["details"]
        sid_total_weight = sum(treatment_risk_weight(row["treatment"]) for row in sid_rows)
        sid_wrong_weight = sum(treatment_risk_weight(row["treatment"]) for row in sid_rows if row["wrong"])
        tier3_sid_wrong = sum(
            1 for row in sid_rows if row["wrong"] and treatment_risk_weight(row["treatment"]) == 3
        )

        results[model] = {
            "weighted_wrong_direction_rate": edge_wrong_weight / edge_total_weight if edge_total_weight else 0.0,
            "weighted_sid_rate": sid_wrong_weight / sid_total_weight if sid_total_weight else 0.0,
            "edge_total_weight": edge_total_weight,
            "edge_wrong_weight": edge_wrong_weight,
            "sid_total_weight": sid_total_weight,
            "sid_wrong_weight": sid_wrong_weight,
            "tier3_wrong_direction_edges": tier3_edge_wrong,
            "tier3_sid_errors": tier3_sid_wrong,
        }
    return results


def write_risk_report(summary: dict, outdir: Path) -> None:
    lines = []
    lines.append("# Risk-Weighted Fidelity Analysis\n")
    lines.append("Weights: Tier 3 = total laryngectomy-related errors; Tier 2 = organ-preservation regime shifts; Tier 1 = fallback nuances.\n")
    lines.append("| Model | Weighted wrong-direction rate | Weighted SID rate | Tier-3 wrong-direction edges | Tier-3 SID errors |")
    lines.append("|---|---:|---:|---:|---:|")
    for model in ordered_models(summary):
        row = summary[model]
        lines.append(
            f"| {model_label(model)} | {pct(row['weighted_wrong_direction_rate'])} | {pct(row['weighted_sid_rate'])} | "
            f"{row['tier3_wrong_direction_edges']} | {row['tier3_sid_errors']} |"
        )
    (outdir / "risk_weighted_fidelity.md").write_text("\n".join(lines) + "\n")


def compute_family_stratified(
    battery: dict,
    kg2_enhanced: dict,
    edge_tests: list[dict],
    sid_details: dict,
    snr_details: dict,
) -> list[dict]:
    family_edges = build_family_edge_map(battery)
    item_map = {item["id"]: item for item in battery.get("baselines", []) + battery.get("perturbations", [])}
    rows = []
    for family, edge_ids in family_edges.items():
        family_tests = [
            row
            for row in edge_tests
            if item_map[row["pert_id"]]["family"] == family and item_map[row["pert_id"]].get("type") != "null"
        ]
        for model in ordered_models(kg2_enhanced):
            edges = kg2_enhanced[model]
            tested_edges = [edges[edge_id] for edge_id in sorted(edge_ids) if edge_id in edges]
            soft_tp = sum(1 for edge in tested_edges if edge.soft_detected)
            soft_dir_rows = [edge for edge in tested_edges if edge.soft_detected and edge.direction_correct is not None]
            phantom_pairs = {
                (row["pert_id"], row["treatment"])
                for row in family_tests
                if row["model"] == model
                and row.get("significant")
                and row["treatment"] not in set(row.get("exp_rec", [])) | set(row.get("exp_exc", []))
            }
            sid_rows = [
                row for row in sid_details[model]["details"] if item_map[row["pert_id"]]["family"] == family
            ]
            causal_jsds = [row["jsd"] for row in family_tests if row["model"] == model and row.get("jsd") is not None]
            null95 = snr_details[model]["null_jsd_95"]
            rows.append(
                {
                    "family": family,
                    "model": model,
                    "model_label": model_label(model),
                    "gold_edges_in_family": len(edge_ids),
                    "soft_recall": soft_tp / len(edge_ids) if edge_ids else None,
                    "soft_precision": soft_tp / (soft_tp + len(phantom_pairs)) if (soft_tp + len(phantom_pairs)) else None,
                    "soft_fdr": len(phantom_pairs) / (soft_tp + len(phantom_pairs)) if (soft_tp + len(phantom_pairs)) else None,
                    "soft_direction_accuracy": (
                        sum(1 for edge in soft_dir_rows if edge.direction_correct) / len(soft_dir_rows)
                        if soft_dir_rows
                        else None
                    ),
                    "sid_rate": (
                        sum(1 for row in sid_rows if row["wrong"]) / len(sid_rows)
                        if sid_rows
                        else None
                    ),
                    "mean_causal_jsd": float(np.mean(causal_jsds)) if causal_jsds else None,
                    "fraction_above_global_null95": (
                        float(np.mean(np.array(causal_jsds) > null95)) if causal_jsds else None
                    ),
                }
            )
    return rows


def write_family_report(rows: list[dict], outdir: Path, family_edge_map: dict) -> None:
    unique_edges = sorted({edge for edges in family_edge_map.values() for edge in edges})
    model_order = ordered_models({row["model"] for row in rows})
    model_rank = {model: idx for idx, model in enumerate(model_order)}
    lines = []
    lines.append("# Family-Stratified Supplementary Analysis\n")
    lines.append(f"- Families represented: `{len(family_edge_map)}`")
    lines.append(f"- Union of family-level gold edges: `{len(unique_edges)}`")
    lines.append("- One additional benchmark edge (`S80`) functions as a shared null-control edge rather than a family-specific directional edge; together these reconcile to the full 58-edge benchmark.")
    lines.append("- Note: `cT4a_unselected` is retained as baseline/null-control context and therefore carries no directional gold-edge denominator.\n")
    lines.append("| Family | Model | Gold edges | Soft recall | Soft precision | Soft FDR | Soft dir. acc. | SID rate | Mean causal JSD | Fraction above global null 95th |")
    lines.append("|---|---|---:|---:|---:|---:|---:|---:|---:|---:|")
    order = sorted(rows, key=lambda row: (row["family"], model_rank[row["model"]]))
    for row in order:
        mean_jsd = "NA" if row["mean_causal_jsd"] is None else f"{row['mean_causal_jsd']:.3f}"
        lines.append(
            f"| {row['family']} | {row['model_label']} | {row['gold_edges_in_family']} | "
            f"{pct(row['soft_recall'])} | {pct(row['soft_precision'])} | {pct(row['soft_fdr'])} | "
            f"{pct(row['soft_direction_accuracy'])} | {pct(row['sid_rate'])} | "
            f"{mean_jsd} | "
            f"{pct(row['fraction_above_global_null95'])} |"
        )
    (outdir / "family_stratified_report.md").write_text("\n".join(lines) + "\n")


def build_domain_summary(
    graph_comparison: dict,
    bootstrap_summary: dict,
    sid_details: dict,
    snr_details: dict,
    v2_metrics: dict,
    risk_metrics: dict,
) -> dict:
    summary = {}
    for model in ordered_models(graph_comparison):
        summary[model] = {
            "label": model_label(model),
            "failure_regime": failure_regime(model),
            "soft_recall": bootstrap_summary[model]["soft_recall"],
            "soft_precision": bootstrap_summary[model]["soft_precision"],
            "soft_fdr": bootstrap_summary[model]["soft_fdr"],
            "hard_recall": bootstrap_summary[model]["hard_recall"],
            "soft_direction_accuracy": bootstrap_summary[model]["soft_direction_accuracy"],
            "hard_direction_accuracy": bootstrap_summary[model]["hard_direction_accuracy"],
            "sid_rate": bootstrap_summary[model]["sid_rate"],
            "snr": bootstrap_summary[model]["snr"],
            "detection_power": bootstrap_summary[model]["detection_power"],
            "soft_true_positives": graph_comparison[model]["soft_true_positives"],
            "hard_true_positives": graph_comparison[model]["true_positives"],
            "soft_false_positives": graph_comparison[model]["soft_false_positives"],
            "veridical_split_half": v2_metrics[model]["veridical_split_half"],
            "raw_split_half": v2_metrics[model]["raw_split_half"],
            "weighted_wrong_direction_rate": risk_metrics[model]["weighted_wrong_direction_rate"],
            "weighted_sid_rate": risk_metrics[model]["weighted_sid_rate"],
            "tier3_wrong_direction_edges": risk_metrics[model]["tier3_wrong_direction_edges"],
            "tier3_sid_errors": risk_metrics[model]["tier3_sid_errors"],
            "sid": sid_details[model]["sid"],
            "sid_total": sid_details[model]["total"],
            "mean_causal_jsd": snr_details[model]["mean_causal_jsd"],
            "mean_null_jsd": snr_details[model]["mean_null_jsd"],
            "null_jsd_95": snr_details[model]["null_jsd_95"],
        }
    return summary


def write_domain_summary(summary: dict, outdir: Path) -> None:
    lines = []
    lines.append("# Domain-Based World-Model Evaluation\n")
    lines.append("Primary interpretation uses Coverage, Fidelity, and Discriminability. Stability is auxiliary and interpreted only conditionally on coverage.\n")
    lines.append("| Model | Soft recall | Soft precision | Soft FDR | Soft dir. acc. | Hard dir. acc. | SID rate | SNR | Detection power | Veridical split-half | Regime |")
    lines.append("|---|---|---|---|---|---|---|---|---|---:|---|")
    for model in ordered_models(summary):
        row = summary[model]
        lines.append(
            f"| {row['label']} | {fmt_ci(row['soft_recall'])} | {fmt_ci(row['soft_precision'])} | "
            f"{fmt_ci(row['soft_fdr'])} | {fmt_ci(row['soft_direction_accuracy'])} | "
            f"{fmt_ci(row['hard_direction_accuracy'])} | {fmt_ci(row['sid_rate'])} | "
            f"{fmt_num_ci(row['snr'])} | {fmt_ci(row['detection_power'])} | "
            f"{pct(row['veridical_split_half'])} | {row['failure_regime']} |"
        )
    lines.append("")
    lines.append("## Interpretation")
    lines.append("- Coverage should be interpreted jointly as broad recovery versus noisy over-coverage; soft precision and soft FDR make that explicit.")
    lines.append("- Fidelity is reported in two views: soft-edge direction accuracy is primary, whereas hard-edge direction accuracy is a stricter secondary sensitivity check.")
    lines.append("- Stability is auxiliary only; sparse models can look stable because consistent non-detection is easy to reproduce.")
    lines.append("- Sparse models can also look superficially precise, because a small denominator can inflate precision even when clinically important edges are missed.")
    lines.append("- No single composite index is used for primary interpretation.")
    (outdir / "domain_summary.md").write_text("\n".join(lines) + "\n")


def write_figure_summary_csv(summary: dict, outpath: Path) -> None:
    rows = [
        {
            "model": model,
            "soft_recall": summary[model]["soft_recall"]["estimate"],
            "hard_recall": summary[model]["hard_recall"]["estimate"],
            "direction_accuracy": summary[model]["soft_direction_accuracy"]["estimate"],
            "sid_normalised": summary[model]["sid_rate"]["estimate"],
            "snr": summary[model]["snr"]["estimate"],
            "detection_power": summary[model]["detection_power"]["estimate"],
        }
        for model in ordered_models(summary)
    ]
    serialise_csv(outpath, rows)


def run_supplementary_evaluation(
    analysis_dir: str | Path,
    world_model_dir: str | Path,
    world_model_v2_dir: str | Path,
    battery_path: str | Path,
    outdir: str | Path,
    figure_outdir: str | Path | None = None,
) -> dict:
    analysis_dir = Path(analysis_dir)
    world_model_dir = Path(world_model_dir)
    world_model_v2_dir = Path(world_model_v2_dir)
    outdir = Path(outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    battery = load_battery(battery_path)
    traceability_rows = build_traceability_rows(battery)
    edge_risk_map = build_edge_risk_map(traceability_rows)
    family_edge_map = build_family_edge_map(battery)

    kg2_enhanced = deserialise_kg2(analysis_dir / "kg2_enhanced.json")
    edge_tests = load_json(analysis_dir / "edge_tests.json")
    spurious_data = load_json(analysis_dir / "spurious_edges.json")
    sid_details = load_json(world_model_dir / "sid_details.json")
    snr_details = load_json(world_model_dir / "snr_details.json")
    v2_metrics = load_json(world_model_v2_dir / "world_model_metrics_v2.json")

    comparison_objects = compute_graph_comparison(kg2_enhanced, spurious_data=spurious_data)
    graph_comparison = {model: vars(comp) for model, comp in comparison_objects.items()}
    dump_json(analysis_dir / "graph_comparison.json", graph_comparison)
    generate_enhanced_report(kg2_enhanced, comparison_objects, spurious_data, analysis_dir / "kg2_report.md")

    threshold_rows = compute_threshold_sensitivity(kg2_enhanced, edge_tests, spurious_data)
    bootstrap_summary = compute_bootstrap_cis(kg2_enhanced, edge_tests, sid_details, snr_details, spurious_data)
    risk_metrics = compute_risk_weighted_fidelity(kg2_enhanced, sid_details, edge_risk_map)
    family_rows = compute_family_stratified(battery, kg2_enhanced, edge_tests, sid_details, snr_details)
    domain_summary = build_domain_summary(graph_comparison, bootstrap_summary, sid_details, snr_details, v2_metrics, risk_metrics)

    dump_json(outdir / "threshold_sensitivity.json", threshold_rows)
    serialise_csv(outdir / "threshold_sensitivity.csv", threshold_rows)
    write_threshold_report(threshold_rows, outdir)

    dump_json(outdir / "bootstrap_ci_summary.json", bootstrap_summary)
    serialise_csv(
        outdir / "bootstrap_ci_summary.csv",
        [
            {
                "model": model,
                "metric": metric_name,
                **metric,
            }
            for model, metrics in bootstrap_summary.items()
            for metric_name, metric in metrics.items()
        ],
    )
    write_bootstrap_report(bootstrap_summary, outdir)

    dump_json(outdir / "risk_weighted_fidelity.json", risk_metrics)
    serialise_csv(outdir / "risk_weighted_fidelity.csv", [{"model": model, **values} for model, values in risk_metrics.items()])
    write_risk_report(risk_metrics, outdir)

    dump_json(outdir / "family_stratified_summary.json", family_rows)
    serialise_csv(outdir / "family_stratified_summary.csv", family_rows)
    write_family_report(family_rows, outdir, family_edge_map)

    dump_json(outdir / "domain_summary.json", domain_summary)
    write_domain_summary(domain_summary, outdir)

    if figure_outdir is not None:
        plot_threshold_sensitivity(threshold_rows, Path(figure_outdir))

    return {
        "threshold_rows": threshold_rows,
        "bootstrap_summary": bootstrap_summary,
        "risk_metrics": risk_metrics,
        "family_rows": family_rows,
        "domain_summary": domain_summary,
    }
