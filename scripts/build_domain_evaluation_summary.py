#!/usr/bin/env python3
"""Build a primary domain-based evaluation summary from final analysis outputs."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


MODEL_ORDER = [
    "deepseek-r1",
    "kimi-k2.5",
    "qwen3-next-80b-instruct",
    "mistral-small-24b",
    "llama-3.1-8b",
]

MODEL_LABELS = {
    "deepseek-r1": "DeepSeek-R1",
    "kimi-k2.5": "Kimi K2.5",
    "qwen3-next-80b-instruct": "Qwen3-Next-80B-A3B-Instruct",
    "mistral-small-24b": "Mistral-Small-24B",
    "llama-3.1-8b": "Llama 3.1-8B",
}


def load_json(path: Path) -> dict:
    return json.loads(path.read_text())


def pct(value: float) -> str:
    return f"{value * 100:.1f}%"


def build_summary(graph: dict, sid: dict, snr: dict, split_half: dict, v2: dict) -> dict:
    summary = {}
    for model in MODEL_ORDER:
        gc = graph[model]
        sd = sid[model]
        sn = snr[model]
        sp = split_half[model]
        vv = v2[model]
        summary[model] = {
            "label": MODEL_LABELS[model],
            "raw_metrics": {
                "soft_recall": gc["soft_recall"],
                "hard_recall": gc["recall"],
                "soft_true_positives": gc["soft_true_positives"],
                "hard_true_positives": gc["true_positives"],
                "direction_accuracy": gc["direction_accuracy"],
                "sid": sd["sid"],
                "sid_total": sd["total"],
                "sid_normalised": sd["sid_normalised"],
                "snr": sn["snr"],
                "detection_power": sn["detection_power"],
                "mean_causal_jsd": sn["mean_causal_jsd"],
                "mean_null_jsd": sn["mean_null_jsd"],
                "null_jsd_95": sn["null_jsd_95"],
                "split_half_agreement": sp["agreement"],
                "split_half_shd_mean": sp["shd_mean"],
            },
            "primary_domains": {
                "coverage": vv["coverage_score"],
                "fidelity": vv["fidelity_score"],
                "discriminability": vv["discriminability_score"],
                "stability_aux": vv["stability_score"],
            },
            "interpretation": {
                "coverage_profile": (
                    "broad"
                    if gc["soft_recall"] >= 0.6
                    else "intermediate"
                    if gc["soft_recall"] >= 0.3
                    else "sparse"
                ),
                "noise_profile": (
                    "separates signal from noise"
                    if sn["snr"] >= 2.0
                    else "weakly separates signal from noise"
                    if sn["snr"] >= 1.0
                    else "fails to separate signal from noise"
                ),
                "stability_caveat": (
                    "stability should be interpreted conditionally because sparse graphs can look reproducible"
                ),
            },
        }
    return summary


def build_markdown(summary: dict) -> str:
    lines = []
    lines.append("# Domain-Based World-Model Evaluation")
    lines.append("")
    lines.append("This summary is the primary interpretation layer for the final five-model study.")
    lines.append("It intentionally avoids `WMI` and instead foregrounds interpretable domains:")
    lines.append("Coverage, Fidelity, Discriminability, and auxiliary Stability.")
    lines.append("")
    lines.append("## Raw Domain Metrics")
    lines.append("")
    lines.append("| Model | Soft recall | Hard recall | Direction accuracy (soft edges) | SID | SNR | Detection power | Split-half agreement |")
    lines.append("|---|---:|---:|---:|---:|---:|---:|---:|")
    for model in MODEL_ORDER:
        item = summary[model]
        raw = item["raw_metrics"]
        lines.append(
            f"| {item['label']} | {pct(raw['soft_recall'])} ({raw['soft_true_positives']}/58) "
            f"| {pct(raw['hard_recall'])} ({raw['hard_true_positives']}/58) "
            f"| {pct(raw['direction_accuracy'])} "
            f"| {raw['sid']}/{raw['sid_total']} ({pct(raw['sid_normalised'])}) "
            f"| {raw['snr']:.2f} "
            f"| {pct(raw['detection_power'])} "
            f"| {pct(raw['split_half_agreement'])} |"
        )
    lines.append("")
    lines.append("## Four-Domain Profile")
    lines.append("")
    lines.append("| Model | Coverage | Fidelity | Discriminability | Stability (aux.) |")
    lines.append("|---|---:|---:|---:|---:|")
    for model in MODEL_ORDER:
        item = summary[model]
        dom = item["primary_domains"]
        lines.append(
            f"| {item['label']} | {dom['coverage']:.3f} | {dom['fidelity']:.3f} | {dom['discriminability']:.3f} | {dom['stability_aux']:.3f} |"
        )
    lines.append("")
    lines.append("## Interpretation")
    lines.append("")
    lines.append("- Kimi K2.5 has the broadest recovered graph and the strongest causal-versus-noise separation.")
    lines.append("- DeepSeek-R1 has the strongest overall balance once coverage, fidelity, discriminability, and stability are interpreted jointly.")
    lines.append("- Qwen3-Next-80B-A3B-Instruct and Mistral-Small-24B recover partial structure but remain directionally brittle.")
    lines.append("- Llama 3.1-8B remains fragmentary, with very low coverage and SNR below 1.0.")
    lines.append("- Stability is auxiliary, not primary: sparse graphs can appear stable because they consistently recover little structure.")
    lines.append("")
    lines.append("## Note on Legacy Composites")
    lines.append("")
    lines.append("`WMI` is retained only as a legacy exploratory artifact. It is not recommended for interpretation because it can over-reward sparse but reproducible failure modes.")
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--graph-comparison", type=Path, required=True)
    parser.add_argument("--sid-details", type=Path, required=True)
    parser.add_argument("--snr-details", type=Path, required=True)
    parser.add_argument("--split-half", type=Path, required=True)
    parser.add_argument("--v2-metrics", type=Path, required=True)
    parser.add_argument("--outdir", type=Path, required=True)
    args = parser.parse_args()

    summary = build_summary(
        load_json(args.graph_comparison),
        load_json(args.sid_details),
        load_json(args.snr_details),
        load_json(args.split_half),
        load_json(args.v2_metrics),
    )

    args.outdir.mkdir(parents=True, exist_ok=True)
    (args.outdir / "domain_summary.json").write_text(json.dumps(summary, indent=2))
    (args.outdir / "domain_summary.md").write_text(build_markdown(summary))
    print(f"Wrote domain summary to {args.outdir}")


if __name__ == "__main__":
    main()
