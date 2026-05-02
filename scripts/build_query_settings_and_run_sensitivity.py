#!/usr/bin/env python3
"""Build reproducibility artifacts for query settings and run-count sensitivity."""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter, defaultdict
from pathlib import Path
import sys

import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from causal_llm_eval.domain_evaluation import model_color, model_label, ordered_models
from causal_llm_eval.llm_query_runner import MODEL_REGISTRY
from causal_llm_eval.response_parser import detect_edges
from causal_llm_eval.world_model_metrics import compute_snr


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--raw-results", type=Path, required=True)
    parser.add_argument("--parsed", type=Path, required=True)
    parser.add_argument("--battery", type=Path, required=True)
    parser.add_argument("--outdir", type=Path, required=True)
    parser.add_argument("--figure-outdir", type=Path, required=True)
    parser.add_argument("--n-resamples", type=int, default=50)
    parser.add_argument("--seed", type=int, default=42)
    return parser.parse_args()


def load_battery_items(path: Path) -> dict:
    with path.open() as f:
        battery = json.load(f)
    battery_items = {row["id"]: row for row in battery["baselines"]}
    for row in battery["perturbations"]:
        battery_items[row["id"]] = row
    return battery_items


def write_csv(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("")
        return
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def fmt_float(value: float | None, digits: int = 3) -> str:
    if value is None:
        return "NA"
    return f"{value:.{digits}f}"


def build_query_settings_rows(raw_results_path: Path) -> list[dict]:
    observed = defaultdict(lambda: {"model_ids": Counter(), "temperatures": Counter(), "run_indices": set(), "records": 0})
    with raw_results_path.open() as f:
        for line in f:
            if not line.strip():
                continue
            row = json.loads(line)
            model = row["model_name"]
            if model not in MODEL_REGISTRY:
                continue
            observed[model]["model_ids"][row["model_id"]] += 1
            observed[model]["temperatures"][str(row["temperature"])] += 1
            observed[model]["run_indices"].add(int(row["run_idx"]))
            observed[model]["records"] += 1

    rows = []
    for model in ordered_models(observed):
        cfg = MODEL_REGISTRY[model]
        obs = observed[model]
        rows.append(
            {
                "model": model,
                "model_label": model_label(model),
                "provider_endpoint": "Together.ai chat-completions API",
                "registry_model_id": cfg["model_id"],
                "observed_model_ids": "; ".join(
                    f"{model_id} ({count})" for model_id, count in sorted(obs["model_ids"].items())
                ),
                "temperature": cfg["temperature"],
                "observed_temperature_values": "; ".join(
                    f"{temp} ({count})" for temp, count in sorted(obs["temperatures"].items())
                ),
                "max_tokens": cfg["max_tokens"],
                "reasoning_effort": cfg.get("reasoning_effort", ""),
                "tier": cfg["tier"],
                "runs_per_item": len(obs["run_indices"]),
                "retained_records": obs["records"],
            }
        )
    return rows


def write_query_settings_report(rows: list[dict], outdir: Path) -> None:
    lines = []
    lines.append("# Supplementary Table S1. Query Settings for the Canonical Analysis Dataset\n")
    lines.append("| Model | Provider endpoint | Registry model ID | Observed model ID(s) in retained dataset | Temperature | Max tokens | Reasoning effort | Runs per item |")
    lines.append("|---|---|---|---|---:|---:|---|---:|")
    for row in rows:
        reasoning_effort = row["reasoning_effort"] or "default"
        lines.append(
            f"| {row['model_label']} | {row['provider_endpoint']} | {row['registry_model_id']} | "
            f"{row['observed_model_ids']} | {row['temperature']} | {row['max_tokens']} | "
            f"{reasoning_effort} | {row['runs_per_item']} |"
        )
    lines.append("")
    lines.append("Temperatures were fixed within model and were not tuned per vignette or per family.")
    (outdir / "supplementary_table_s1_query_settings.md").write_text("\n".join(lines) + "\n")


def compute_run_count_sensitivity(
    parsed_path: Path,
    battery_path: Path,
    *,
    n_resamples: int = 50,
    seed: int = 42,
) -> tuple[list[dict], list[dict]]:
    parsed = json.loads(parsed_path.read_text())
    battery_items = load_battery_items(battery_path)

    parsed_by_run = defaultdict(list)
    for row in parsed:
        parsed_by_run[int(row["run_idx"])].append(row)
    run_ids = sorted(parsed_by_run)

    rng = np.random.default_rng(seed)
    raw_rows: list[dict] = []

    for run_count in range(1, len(run_ids) + 1):
        n_draws = 1 if run_count == len(run_ids) else n_resamples
        for replicate in range(n_draws):
            if run_count == len(run_ids):
                chosen_runs = tuple(run_ids)
            else:
                chosen_runs = tuple(sorted(int(x) for x in rng.choice(run_ids, size=run_count, replace=False)))

            subset_parsed = []
            for run_idx in chosen_runs:
                subset_parsed.extend(parsed_by_run[run_idx])

            edge_tests = detect_edges(subset_parsed, battery_items)
            snr_summary = compute_snr(edge_tests)

            for model in ordered_models(snr_summary):
                metrics = snr_summary.get(model, {})
                raw_rows.append(
                    {
                        "run_count": run_count,
                        "replicate": replicate,
                        "model": model,
                        "model_label": model_label(model),
                        "selected_runs": ",".join(str(x) for x in chosen_runs),
                        "mean_causal_jsd": metrics.get("mean_causal_jsd"),
                        "mean_null_jsd": metrics.get("mean_null_jsd"),
                        "snr": metrics.get("snr"),
                        "detection_power": metrics.get("detection_power"),
                    }
                )

    summary_rows: list[dict] = []
    grouped = defaultdict(list)
    for row in raw_rows:
        grouped[(row["model"], row["run_count"])].append(row)

    for model in ordered_models({row["model"] for row in raw_rows}):
        for run_count in range(1, len(run_ids) + 1):
            rows = grouped[(model, run_count)]
            causal = np.array([float(row["mean_causal_jsd"]) for row in rows], dtype=float)
            null = np.array([float(row["mean_null_jsd"]) for row in rows], dtype=float)
            snr = np.array([float(row["snr"]) for row in rows], dtype=float)
            power = np.array([float(row["detection_power"]) for row in rows], dtype=float)
            summary_rows.append(
                {
                    "model": model,
                    "model_label": model_label(model),
                    "run_count": run_count,
                    "n_subsamples": len(rows),
                    "mean_causal_jsd_median": float(np.median(causal)),
                    "mean_causal_jsd_q10": float(np.percentile(causal, 10)),
                    "mean_causal_jsd_q90": float(np.percentile(causal, 90)),
                    "mean_null_jsd_median": float(np.median(null)),
                    "snr_median": float(np.median(snr)),
                    "detection_power_median": float(np.median(power)),
                }
            )

    return raw_rows, summary_rows


def write_run_count_report(summary_rows: list[dict], outdir: Path) -> None:
    by_model = defaultdict(list)
    for row in summary_rows:
        by_model[row["model"]].append(row)

    lines = []
    lines.append("# Supplementary Figure S2 Source Summary. Run-Count Sensitivity of Mean Causal JSD\n")
    lines.append(
        "For each run count from 1 to 15, we repeatedly subsampled the retained runs without replacement "
        "and recomputed mean causal JSD. The table reports the median and 10th to 90th percentile band "
        "across subsamples."
    )
    lines.append("")
    lines.append("| Model | Run count | Median mean causal JSD | 10th percentile | 90th percentile | Median SNR |")
    lines.append("|---|---:|---:|---:|---:|---:|")
    models = ordered_models({row["model"] for row in summary_rows})
    for model in models:
        for row in sorted(by_model[model], key=lambda item: item["run_count"]):
            lines.append(
                f"| {row['model_label']} | {row['run_count']} | "
                f"{fmt_float(row['mean_causal_jsd_median'])} | {fmt_float(row['mean_causal_jsd_q10'])} | "
                f"{fmt_float(row['mean_causal_jsd_q90'])} | {fmt_float(row['snr_median'])} |"
            )

    lines.append("")
    lines.append("## Plateau Check")
    lines.append("| Model | Median JSD at 11 runs | Full-data JSD at 15 runs | Absolute difference |")
    lines.append("|---|---:|---:|---:|")
    for model in models:
        row11 = next(row for row in by_model[model] if row["run_count"] == 11)
        row15 = next(row for row in by_model[model] if row["run_count"] == 15)
        diff = abs(row15["mean_causal_jsd_median"] - row11["mean_causal_jsd_median"])
        lines.append(
            f"| {model_label(model)} | {fmt_float(row11['mean_causal_jsd_median'])} | "
            f"{fmt_float(row15['mean_causal_jsd_median'])} | {fmt_float(diff)} |"
        )

    (outdir / "run_count_sensitivity_report.md").write_text("\n".join(lines) + "\n")


def plot_run_count_sensitivity(summary_rows: list[dict], figure_outdir: Path) -> None:
    figure_outdir.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(figsize=(10.5, 6.2))
    fig.subplots_adjust(left=0.10, right=0.98, top=0.88, bottom=0.14)

    models = ordered_models({row["model"] for row in summary_rows})
    for model in models:
        rows = sorted((row for row in summary_rows if row["model"] == model), key=lambda item: item["run_count"])
        x = [row["run_count"] for row in rows]
        y = [row["mean_causal_jsd_median"] for row in rows]
        ylo = [row["mean_causal_jsd_q10"] for row in rows]
        yhi = [row["mean_causal_jsd_q90"] for row in rows]
        color = model_color(model)
        ax.plot(x, y, color=color, linewidth=2.2, marker="o", markersize=4.5, label=model_label(model))
        ax.fill_between(x, ylo, yhi, color=color, alpha=0.12)

    ax.set_title("Supplementary Figure S2. Run-count sensitivity of mean causal JSD", fontsize=13.5, fontweight="bold", loc="left")
    ax.set_xlabel("Retained runs per vignette")
    ax.set_ylabel("Mean causal JSD")
    ax.set_xlim(1, 15)
    ax.set_xticks(range(1, 16))
    ax.grid(axis="y", color="#E5E7EB", linewidth=0.8)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.legend(frameon=False, ncol=2, fontsize=9, loc="upper right")
    fig.savefig(figure_outdir / "supplementary_figureS2_run_count_sensitivity.png", dpi=300, bbox_inches="tight")
    fig.savefig(figure_outdir / "supplementary_figureS2_run_count_sensitivity.svg", bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    args = parse_args()
    args.outdir.mkdir(parents=True, exist_ok=True)
    args.figure_outdir.mkdir(parents=True, exist_ok=True)

    settings_rows = build_query_settings_rows(args.raw_results)
    write_csv(args.outdir / "supplementary_table_s1_query_settings.csv", settings_rows)
    write_query_settings_report(settings_rows, args.outdir)

    raw_rows, summary_rows = compute_run_count_sensitivity(
        args.parsed,
        args.battery,
        n_resamples=args.n_resamples,
        seed=args.seed,
    )
    write_csv(args.outdir / "run_count_sensitivity_raw.csv", raw_rows)
    write_csv(args.outdir / "run_count_sensitivity_summary.csv", summary_rows)
    write_run_count_report(summary_rows, args.outdir)
    plot_run_count_sensitivity(summary_rows, args.figure_outdir)

    print(f"Wrote query settings table and run-count sensitivity outputs to {args.outdir}")


if __name__ == "__main__":
    main()
