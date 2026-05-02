#!/usr/bin/env python3
"""Build compact source tables for the public six-model figure assets."""

from __future__ import annotations

import csv
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from causal_llm_eval.domain_evaluation import failure_regime, model_label, ordered_models


ANALYSIS_DIR = ROOT / "results" / "analysis" / "article-metrics-6models-gemma4"
DOMAIN_DIR = ROOT / "results" / "world_model" / "domain-metrics-6models-gemma4"
FIGURE_DATA_DIR = ROOT / "publication" / "figure_data"


def load_json(path: Path):
    with path.open() as f:
        return json.load(f)


def write_csv(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("")
        return
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def build_domain_summary_rows(domain_summary: dict) -> list[dict]:
    rows = []
    for model in ordered_models(domain_summary):
        payload = domain_summary[model]
        rows.append(
            {
                "model": model,
                "model_label": model_label(model),
                "failure_regime": payload.get("failure_regime") or failure_regime(model),
                "soft_recall": payload.get("soft_recall"),
                "soft_precision": payload.get("soft_precision"),
                "soft_fdr": payload.get("soft_fdr"),
                "soft_direction_accuracy": payload.get("soft_direction_accuracy"),
                "hard_direction_accuracy": payload.get("hard_direction_accuracy"),
                "sid_rate": payload.get("sid_rate"),
                "snr": payload.get("snr"),
                "detection_power": payload.get("detection_power"),
            }
        )
    return rows


def build_recovery_profile_rows(kg2_enhanced: dict) -> list[dict]:
    rows = []
    for model in ordered_models(kg2_enhanced):
        edges = kg2_enhanced[model].values()
        soft_correct = 0
        soft_wrong = 0
        soft_undetected = 0
        hard_correct = 0
        hard_wrong = 0
        total = 0
        for edge in edges:
            total += 1
            soft_detected = bool(edge.get("soft_detected"))
            hard_detected = bool(edge.get("detected"))
            direction_correct = edge.get("direction_correct")
            if soft_detected and direction_correct is True:
                soft_correct += 1
            elif soft_detected and direction_correct is False:
                soft_wrong += 1
            else:
                soft_undetected += 1
            if hard_detected and direction_correct is True:
                hard_correct += 1
            elif hard_detected and direction_correct is False:
                hard_wrong += 1
        rows.append(
            {
                "model": model,
                "model_label": model_label(model),
                "total_edges": total,
                "soft_correct": soft_correct,
                "soft_wrong": soft_wrong,
                "soft_undetected": soft_undetected,
                "hard_correct": hard_correct,
                "hard_wrong": hard_wrong,
            }
        )
    return rows


def copy_source_table(src_name: str, dest_name: str) -> None:
    source = DOMAIN_DIR / src_name
    if source.exists():
        (FIGURE_DATA_DIR / dest_name).write_text(source.read_text())


def main() -> int:
    FIGURE_DATA_DIR.mkdir(parents=True, exist_ok=True)

    domain_summary = load_json(DOMAIN_DIR / "domain_summary.json")
    kg2_enhanced = load_json(ANALYSIS_DIR / "kg2_enhanced.json")

    write_csv(FIGURE_DATA_DIR / "figure2_domain_summary.csv", build_domain_summary_rows(domain_summary))
    write_csv(FIGURE_DATA_DIR / "figure3_recovery_profile.csv", build_recovery_profile_rows(kg2_enhanced))
    copy_source_table("family_stratified_summary.csv", "figure4_family_heatmap.csv")
    copy_source_table("threshold_sensitivity.csv", "supplementary_threshold_sensitivity.csv")
    copy_source_table("run_count_sensitivity_summary.csv", "supplementary_run_count_sensitivity_summary.csv")
    copy_source_table("bootstrap_ci_summary.csv", "supplementary_bootstrap_ci_summary.csv")
    copy_source_table("risk_weighted_fidelity.csv", "supplementary_risk_weighted_fidelity.csv")

    print(f"Wrote public figure source tables to {FIGURE_DATA_DIR}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
