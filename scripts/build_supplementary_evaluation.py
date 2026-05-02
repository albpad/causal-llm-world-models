#!/usr/bin/env python3
"""Build supplementary evaluation artifacts for the final publication study."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from causal_llm_eval.domain_evaluation import run_supplementary_evaluation, write_figure_summary_csv


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--analysis-dir", type=Path, required=True)
    parser.add_argument("--world-model-dir", type=Path, required=True)
    parser.add_argument("--world-model-v2-dir", type=Path, required=True)
    parser.add_argument("--battery", type=Path, required=True)
    parser.add_argument("--outdir", type=Path, required=True)
    parser.add_argument("--figure-outdir", type=Path)
    parser.add_argument("--figure-summary-csv", type=Path)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    result = run_supplementary_evaluation(
        analysis_dir=args.analysis_dir,
        world_model_dir=args.world_model_dir,
        world_model_v2_dir=args.world_model_v2_dir,
        battery_path=args.battery,
        outdir=args.outdir,
        figure_outdir=args.figure_outdir,
    )
    if args.figure_summary_csv:
        args.figure_summary_csv.parent.mkdir(parents=True, exist_ok=True)
        write_figure_summary_csv(result["domain_summary"], args.figure_summary_csv)
    print(f"Wrote supplementary evaluation artifacts to {args.outdir}")


if __name__ == "__main__":
    main()
