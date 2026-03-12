#!/usr/bin/env python3
"""Research application entrypoint for experiment orchestration."""

from __future__ import annotations

import argparse
import json
import os
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable

os.environ.setdefault("MPLCONFIGDIR", "/tmp/causal-llm-mpl-cache")
os.environ.setdefault("XDG_CACHE_HOME", "/tmp/causal-llm-cache")

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from .kg2_enhanced import run_enhanced_analysis
from .llm_query_runner import MODEL_REGISTRY, load_battery, run_battery
from .response_parser import parse_result, run_analysis
from .world_model_metrics_v2 import compute_world_model_metrics_v2


@dataclass(frozen=True)
class ResearchPreset:
    name: str
    models: tuple[str, ...]
    n_runs: int
    item_filter: tuple[str, ...] | None
    results_subdir: str
    analysis_subdir: str
    world_model_subdir: str | None


PRESETS: dict[str, ResearchPreset] = {
    "single-model": ResearchPreset(
        name="single-model",
        models=("llama-3.1-8b",),
        n_runs=30,
        item_filter=None,
        results_subdir="results",
        analysis_subdir="analysis",
        world_model_subdir="world_model/v2",
    ),
    "full-study": ResearchPreset(
        name="full-study",
        models=(
            "llama-3.1-8b",
            "qwen3-235b-instruct",
            "llama-4-maverick",
            "llama-3.3-70b",
            "deepseek-v3.1",
            "qwen3-235b-thinking",
            "deepseek-r1",
        ),
        n_runs=30,
        item_filter=None,
        results_subdir="results",
        analysis_subdir="analysis",
        world_model_subdir="world_model/v2",
    ),
    "kimi-k25": ResearchPreset(
        name="kimi-k25",
        models=("kimi-k2.5",),
        n_runs=30,
        item_filter=None,
        results_subdir="results_kimi_k25",
        analysis_subdir="analysis_kimi_k25",
        world_model_subdir="world_model/kimi-k25-v2",
    ),
    "kimi-k25-thinking": ResearchPreset(
        name="kimi-k25-thinking",
        models=("kimi-k2.5-thinking",),
        n_runs=30,
        item_filter=None,
        results_subdir="results_kimi_k25_thinking",
        analysis_subdir="analysis_kimi_k25_thinking",
        world_model_subdir="world_model/kimi-k25-thinking-v2",
    ),
    "qwq32b": ResearchPreset(
        name="qwq32b",
        models=("qwq-32b",),
        n_runs=30,
        item_filter=None,
        results_subdir="results_qwq32b",
        analysis_subdir="analysis_qwq32b",
        world_model_subdir="world_model/qwq32b-v2",
    ),
}


def _battery_items_map(battery_path: str | Path) -> dict[str, dict]:
    with open(battery_path) as f:
        battery = json.load(f)
    items = {}
    for baseline in battery["baselines"]:
        items[baseline["id"]] = baseline
    for pert in battery["perturbations"]:
        items[pert["id"]] = pert
    return items


def _load_results(results_path: str | Path) -> list[dict]:
    rows = []
    with open(results_path) as f:
        for line in f:
            if not line.strip():
                continue
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return rows


def _parse_results(rows: Iterable[dict]) -> list[dict]:
    return [parsed for parsed in (parse_result(row) for row in rows) if parsed]


def _latest_results_file(results_dir: str | Path) -> Path:
    files = sorted(Path(results_dir).glob("run_*.jsonl"))
    if not files:
        raise FileNotFoundError(f"No run_*.jsonl files found in {results_dir}")
    return files[-1]


def serialize_enhanced_kg2(kg2_enhanced: dict[str, dict]) -> dict[str, dict]:
    serial = {}
    for model, edges in kg2_enhanced.items():
        serial[model] = {}
        for edge_id, edge in edges.items():
            data = asdict(edge)
            data.pop("jsd_values", None)
            serial[model][edge_id] = data
    return serial


def estimate_run_cost(models: Iterable[str], n_items: int, n_runs: int) -> float:
    total = 0.0
    for model_name in models:
        cfg = MODEL_REGISTRY[model_name]
        est_in = 600
        est_out = 3000 if "reasoning" in cfg.get("tier", "") else 1500
        total += n_items * n_runs * 2 * (est_in * cfg["price_in"] + est_out * cfg["price_out"]) / 1e6
    return total


def print_experiment_summary(battery_path: str | Path, models: list[str], n_runs: int,
                             item_filter: list[str] | None) -> None:
    items = load_battery(battery_path)
    if item_filter:
        items = [item for item in items if item["id"] in set(item_filter)]
    baselines = [item for item in items if item["type"] == "baseline"]
    perturbations = [item for item in items if item["type"] != "baseline"]
    families = sorted({item["family"] for item in items})
    queries = len(items) * len(models) * n_runs

    print("=" * 72)
    print("Research Run")
    print("=" * 72)
    print(f"Battery items : {len(items)} ({len(baselines)} baselines, {len(perturbations)} perturbations)")
    print(f"Families      : {len(families)}")
    print(f"Models        : {', '.join(models)}")
    print(f"Runs/model    : {n_runs}")
    print(f"Queries       : {queries} ({queries * 2} API calls)")
    print(f"Est. cost     : ~${estimate_run_cost(models, len(items), n_runs):.2f}")


def save_base_analysis_plots(metrics: dict, kg2: dict, edge_tests: list[dict], outdir: str | Path) -> None:
    out_path = Path(outdir)
    out_path.mkdir(parents=True, exist_ok=True)
    models = sorted(metrics.keys())
    if not models:
        return

    fig, axes = plt.subplots(1, 3, figsize=(16, 5))
    plot_defs = [
        ("rec_accuracy", "Recommendation\nAccuracy"),
        ("exc_accuracy", "Exclusion\nAccuracy"),
        ("rec_precision", "Recommendation\nPrecision"),
    ]
    for idx, (key, label) in enumerate(plot_defs):
        values = [metrics[model][key] for model in models]
        bars = axes[idx].bar(range(len(models)), values, color=plt.cm.Set2(np.linspace(0, 1, len(models))))
        axes[idx].set_xticks(range(len(models)))
        axes[idx].set_xticklabels(models, rotation=45, ha="right", fontsize=8)
        axes[idx].set_ylim(0, 1.05)
        axes[idx].set_ylabel(label)
        axes[idx].axhline(1.0, color="gray", linestyle="--", alpha=0.3)
        for bar, value in zip(bars, values):
            axes[idx].text(bar.get_x() + bar.get_width() / 2, value + 0.02, f"{value:.0%}", ha="center", fontsize=8)
    fig.suptitle("Aggregate Model Performance", fontweight="bold")
    fig.tight_layout()
    fig.savefig(out_path / "agg_perf.png", dpi=150, bbox_inches="tight")
    plt.close(fig)

    if kg2:
        all_edges = sorted({edge for per_model in kg2.values() for edge in per_model})
        if all_edges:
            matrix = np.zeros((len(all_edges), len(models)))
            for col, model in enumerate(models):
                for row, edge in enumerate(all_edges):
                    if edge in kg2.get(model, {}):
                        matrix[row, col] = kg2[model][edge]["detection_rate"]
            fig, ax = plt.subplots(figsize=(max(8, len(models) * 2.5), max(10, len(all_edges) * 0.35)))
            image = ax.imshow(matrix, cmap="RdYlGn", aspect="auto", vmin=0, vmax=1)
            ax.set_xticks(range(len(models)))
            ax.set_xticklabels(models, rotation=45, ha="right", fontsize=8)
            ax.set_yticks(range(len(all_edges)))
            ax.set_yticklabels(all_edges, fontsize=7)
            ax.set_title("KG2 Edge Detection Rate", fontweight="bold")
            plt.colorbar(image, ax=ax, label="Detection Rate", shrink=0.6)
            fig.tight_layout()
            fig.savefig(out_path / "edge_heatmap.png", dpi=150, bbox_inches="tight")
            plt.close(fig)

    jsd_by_model = {model: [t["jsd"] for t in edge_tests if t["model"] == model and t.get("jsd", 0) > 0] for model in models}
    if any(jsd_by_model.values()):
        fig, ax = plt.subplots(figsize=(10, 5))
        multiple_models = sum(1 for values in jsd_by_model.values() if values) > 1
        if multiple_models:
            for model in models:
                if jsd_by_model[model]:
                    ax.hist(jsd_by_model[model], bins=20, alpha=0.5, label=model)
            ax.legend(fontsize=7)
        else:
            only_model = next(model for model, values in jsd_by_model.items() if values)
            ax.hist(jsd_by_model[only_model], bins=30, color="#4C72B0", alpha=0.8, edgecolor="white")
            ax.axvline(np.median(jsd_by_model[only_model]), color="red", linestyle="--",
                       label=f"Median: {np.median(jsd_by_model[only_model]):.3f}")
            ax.legend(fontsize=8)
        ax.set_xlabel("Jensen-Shannon Divergence")
        ax.set_ylabel("Count")
        ax.set_title("Edge Weight Distribution", fontweight="bold")
        fig.tight_layout()
        fig.savefig(out_path / "jsd_dist.png", dpi=150, bbox_inches="tight")
        plt.close(fig)


def save_enhanced_plots(kg2_enhanced: dict[str, dict], outdir: str | Path) -> None:
    out_path = Path(outdir)
    out_path.mkdir(parents=True, exist_ok=True)
    for model_name, edges in sorted(kg2_enhanced.items()):
        all_edges = sorted(edges.keys())
        if not all_edges:
            continue

        detection_rates = [edges[edge].detection_rate for edge in all_edges]
        colors = ["#2ecc71" if edges[edge].soft_detected else "#95a5a6" for edge in all_edges]
        means = [edges[edge].mean_jsd for edge in all_edges]
        lower = [max(0.0, means[idx] - edges[edge].jsd_ci_lower) for idx, edge in enumerate(all_edges)]
        upper = [max(0.0, edges[edge].jsd_ci_upper - means[idx]) for idx, edge in enumerate(all_edges)]

        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, max(6, len(all_edges) * 0.28)))
        y_pos = np.arange(len(all_edges))
        ax1.barh(y_pos, detection_rates, color=colors, alpha=0.85)
        ax1.axvline(0.5, color="red", linestyle="--", alpha=0.5, label="Hard")
        ax1.axvline(0.25, color="orange", linestyle="--", alpha=0.5, label="Soft")
        ax1.set_yticks(y_pos)
        ax1.set_yticklabels(all_edges, fontsize=8)
        ax1.set_xlim(0, 1.05)
        ax1.set_xlabel("Detection Rate")
        ax1.set_title(f"{model_name}: Edge Detection", fontweight="bold", fontsize=10)
        ax1.legend(fontsize=8)

        ax2.barh(y_pos, means, color="#3498db", alpha=0.8)
        ax2.errorbar(means, y_pos, xerr=[lower, upper], fmt="none", ecolor="black", capsize=3)
        ax2.set_yticks(y_pos)
        ax2.set_yticklabels(all_edges, fontsize=8)
        ax2.set_xlabel("Mean JSD")
        ax2.set_title(f"{model_name}: Edge Weight", fontweight="bold", fontsize=10)
        fig.tight_layout()
        fig.savefig(out_path / f"{model_name}_enhanced_edge_detail.png", dpi=150, bbox_inches="tight")
        plt.close(fig)

        direction_rates = [edges[edge].direction_rate for edge in all_edges]
        direction_colors = ["#2ecc71" if rate > 0.5 else "#e74c3c" for rate in direction_rates]
        fig, ax = plt.subplots(figsize=(10, max(6, len(all_edges) * 0.3)))
        ax.barh(range(len(all_edges)), direction_rates, color=direction_colors, alpha=0.85)
        ax.axvline(0.5, color="gray", linestyle="--", alpha=0.5, label="Chance")
        ax.set_yticks(range(len(all_edges)))
        ax.set_yticklabels(all_edges, fontsize=8)
        ax.set_xlim(0, 1.05)
        ax.set_xlabel("Direction Accuracy")
        ax.set_title(f"{model_name}: Direction Accuracy", fontweight="bold")
        ax.legend(fontsize=8)
        fig.tight_layout()
        fig.savefig(out_path / f"{model_name}_direction_accuracy.png", dpi=150, bbox_inches="tight")
        plt.close(fig)


def save_summary(output_dir: str | Path, preset: str | None, models: list[str], n_runs: int,
                 battery_size: int, metrics: dict, edge_tests: list[dict]) -> None:
    summary = {
        "preset": preset,
        "models": models,
        "runs": n_runs,
        "battery_items": battery_size,
        "queries": battery_size * len(models) * n_runs,
        "metrics": {
            model: {key: round(value, 4) if isinstance(value, float) else value for key, value in model_metrics.items()}
            for model, model_metrics in metrics.items()
        },
        "n_edge_tests": len(edge_tests),
        "n_significant": sum(1 for test in edge_tests if test.get("significant")),
    }
    with open(Path(output_dir) / "summary.json", "w") as f:
        json.dump(summary, f, indent=2)


def run_pipeline(
    battery_path: str | Path,
    models: list[str],
    n_runs: int,
    results_dir: str | Path,
    analysis_dir: str | Path,
    item_filter: list[str] | None = None,
    results_file: str | Path | None = None,
    skip_query: bool = False,
    skip_enhanced: bool = False,
    skip_world_model: bool = False,
    skip_plots: bool = False,
    world_model_dir: str | Path | None = None,
    preset_name: str | None = None,
) -> dict:
    print_experiment_summary(battery_path, models, n_runs, item_filter)

    if skip_query:
        checkpoint = Path(results_file) if results_file else _latest_results_file(results_dir)
        print(f"Using existing results file: {checkpoint}")
    else:
        checkpoint = Path(
            run_battery(
                battery_path=str(battery_path),
                model_names=models,
                n_runs=n_runs,
                item_filter=item_filter,
                output_dir=str(results_dir),
            )
        )

    metrics, kg2, edge_tests, divergences = run_analysis(str(checkpoint), str(battery_path), str(analysis_dir))

    rows = _load_results(checkpoint)
    all_parsed = _parse_results(rows)
    battery_items = _battery_items_map(battery_path)

    enhanced_serial = None
    if not skip_enhanced:
        kg2_enhanced, comparisons, spurious = run_enhanced_analysis(edge_tests, all_parsed, battery_items, str(analysis_dir))
        enhanced_serial = serialize_enhanced_kg2(kg2_enhanced)
        if not skip_plots:
            save_enhanced_plots(kg2_enhanced, analysis_dir)
    else:
        comparisons = {}
        spurious = {}

    world_model_metrics = None
    if not skip_world_model and enhanced_serial is not None:
        target_dir = Path(world_model_dir) if world_model_dir else Path(analysis_dir) / "world_model_v2"
        world_model_metrics = compute_world_model_metrics_v2(
            all_parsed,
            edge_tests,
            battery_items,
            kg2_enhanced_data=enhanced_serial,
            output_dir=str(target_dir),
        )

    if not skip_plots:
        save_base_analysis_plots(metrics, kg2, edge_tests, analysis_dir)

    battery_items_count = len(load_battery(battery_path) if item_filter is None else [item for item in load_battery(battery_path) if item["id"] in set(item_filter)])
    save_summary(analysis_dir, preset_name, models, n_runs, battery_items_count, metrics, edge_tests)

    return {
        "checkpoint": str(checkpoint),
        "metrics": metrics,
        "kg2": kg2,
        "edge_tests": edge_tests,
        "divergences": divergences,
        "comparisons": comparisons,
        "spurious": spurious,
        "world_model_metrics": world_model_metrics,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run the full research pipeline from Python scripts.")
    parser.add_argument("--preset", choices=sorted(PRESETS.keys()))
    parser.add_argument("--battery", default="data/vignettes/vignette_battery.json")
    parser.add_argument("--models", help="Comma-separated model names. Overrides preset.")
    parser.add_argument("--runs", type=int, help="Runs per item. Overrides preset.")
    parser.add_argument("--items", help="Comma-separated item ids to run.")
    parser.add_argument("--results-dir", help="Directory for raw run_*.jsonl outputs.")
    parser.add_argument("--analysis-dir", help="Directory for analysis artifacts.")
    parser.add_argument("--world-model-dir", help="Directory for v2 world-model outputs.")
    parser.add_argument("--results-file", help="Existing JSONL file to analyze when using --skip-query.")
    parser.add_argument("--skip-query", action="store_true")
    parser.add_argument("--skip-enhanced", action="store_true")
    parser.add_argument("--skip-world-model", action="store_true")
    parser.add_argument("--skip-plots", action="store_true")
    return parser


def _resolve_args(args: argparse.Namespace) -> dict:
    preset = PRESETS.get(args.preset) if args.preset else None
    models = [model.strip() for model in args.models.split(",")] if args.models else list(preset.models if preset else [])
    if not models:
        raise SystemExit("Provide --models or choose a --preset.")

    runs = args.runs if args.runs is not None else (preset.n_runs if preset else 30)
    item_filter = [item.strip() for item in args.items.split(",")] if args.items else list(preset.item_filter) if preset and preset.item_filter else None
    results_dir = args.results_dir or (preset.results_subdir if preset else "results")
    analysis_dir = args.analysis_dir or (preset.analysis_subdir if preset else "analysis")
    world_model_dir = args.world_model_dir or (preset.world_model_subdir if preset else None)

    return {
        "battery_path": args.battery,
        "models": models,
        "n_runs": runs,
        "results_dir": results_dir,
        "analysis_dir": analysis_dir,
        "item_filter": item_filter,
        "results_file": args.results_file,
        "skip_query": args.skip_query,
        "skip_enhanced": args.skip_enhanced,
        "skip_world_model": args.skip_world_model,
        "skip_plots": args.skip_plots,
        "world_model_dir": world_model_dir,
        "preset_name": preset.name if preset else None,
    }


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    resolved = _resolve_args(args)
    run_pipeline(**resolved)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
