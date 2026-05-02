#!/usr/bin/env python3
"""Run the full analysis stack on a raw results JSONL file."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from causal_llm_eval.domain_evaluation import run_supplementary_evaluation
from causal_llm_eval.kg2_enhanced import run_enhanced_analysis
from causal_llm_eval.parser_validation import validate_parser, write_report as write_parser_report
from causal_llm_eval.response_parser import detect_edges, parse_result, run_analysis
from causal_llm_eval.world_model_metrics import compute_world_model_metrics
from causal_llm_eval.world_model_metrics_v2 import compute_world_model_metrics_v2


def remove_legacy_composite_outputs(world_model_dir: Path, world_model_v2_dir: Path) -> None:
    """Keep only component metrics used by the manuscript-facing analyses."""
    for path in (
        world_model_dir / "world_model_metrics.json",
        world_model_dir / "world_model_report.md",
        world_model_v2_dir / "world_model_report_v2.md",
    ):
        if path.exists():
            path.unlink()

    v2_path = world_model_v2_dir / "world_model_metrics_v2.json"
    if v2_path.exists():
        with v2_path.open() as f:
            payload = json.load(f)
        for metrics in payload.values():
            metrics.pop("wms", None)
            metrics.pop("wms_label", None)
        with v2_path.open("w") as f:
            json.dump(payload, f, indent=2)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--results", type=Path, required=True)
    parser.add_argument("--battery", type=Path, required=True)
    parser.add_argument("--analysis-outdir", type=Path, required=True)
    parser.add_argument("--parser-outdir", type=Path, required=True)
    parser.add_argument("--world-model-outdir", type=Path, required=True)
    parser.add_argument("--world-model-v2-outdir", type=Path, required=True)
    parser.add_argument("--domain-outdir", type=Path, required=True)
    parser.add_argument("--figure-outdir", type=Path)
    return parser.parse_args()


def load_battery_map(path: Path) -> dict[str, dict]:
    with path.open() as f:
        battery = json.load(f)
    items = {}
    for row in battery["baselines"]:
        items[row["id"]] = row
    for row in battery["perturbations"]:
        items[row["id"]] = row
    return items


def load_results(path: Path) -> list[dict]:
    rows = []
    with path.open() as f:
        for line in f:
            if not line.strip():
                continue
            rows.append(json.loads(line))
    return rows


def main() -> int:
    args = parse_args()

    run_analysis(args.results, args.battery, args.analysis_outdir)

    parser_summary = validate_parser(args.results, args.battery)
    write_parser_report(parser_summary, args.parser_outdir)

    battery_items = load_battery_map(args.battery)
    results = load_results(args.results)
    all_parsed = [parsed for parsed in (parse_result(row) for row in results) if parsed]
    edge_tests = detect_edges(all_parsed, battery_items)

    kg2_enhanced, _, _ = run_enhanced_analysis(
        edge_tests,
        all_parsed,
        battery_items,
        output_dir=args.analysis_outdir,
    )

    with (args.analysis_outdir / "kg2_enhanced.json").open() as f:
        kg2_serial = json.load(f)

    compute_world_model_metrics(
        all_parsed,
        edge_tests,
        battery_items,
        kg2_enhanced_data=kg2_serial,
        output_dir=args.world_model_outdir,
    )

    compute_world_model_metrics_v2(
        all_parsed,
        edge_tests,
        battery_items,
        kg2_enhanced_data=kg2_serial,
        output_dir=args.world_model_v2_outdir,
    )

    remove_legacy_composite_outputs(args.world_model_outdir, args.world_model_v2_outdir)

    run_supplementary_evaluation(
        analysis_dir=args.analysis_outdir,
        world_model_dir=args.world_model_outdir,
        world_model_v2_dir=args.world_model_v2_outdir,
        battery_path=args.battery,
        outdir=args.domain_outdir,
        figure_outdir=args.figure_outdir,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
