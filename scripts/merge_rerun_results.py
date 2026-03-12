#!/usr/bin/env python3
"""Merge recovered rerun rows over an existing results file."""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from causal_llm_eval.llm_query_runner import is_complete_result


def parse_args():
    parser = argparse.ArgumentParser(description="Merge rerun outputs, preferring complete rows by hash.")
    parser.add_argument("--base-results", required=True)
    parser.add_argument("--rerun-results", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--allow-empty-phase1", action="store_true")
    parser.add_argument("--allow-empty-phase2", action="store_true")
    return parser.parse_args()


def load_rows(path):
    return [json.loads(line) for line in open(path) if line.strip()]


def score_row(row, require_phase1=True, require_phase2=True):
    complete = is_complete_result(row, require_phase1=require_phase1, require_phase2=require_phase2)
    nonempty_count = int(bool((row.get("phase1_response") or "").strip())) + int(bool((row.get("phase2_response") or "").strip()))
    no_error = row.get("error") is None
    return (int(complete), int(no_error), nonempty_count)


def main():
    args = parse_args()
    require_phase1 = not args.allow_empty_phase1
    require_phase2 = not args.allow_empty_phase2

    merged = {}
    order = []
    for source in [args.base_results, args.rerun_results]:
        for row in load_rows(source):
            key = row["hash"]
            if key not in merged:
                merged[key] = row
                order.append(key)
                continue
            if score_row(row, require_phase1, require_phase2) >= score_row(merged[key], require_phase1, require_phase2):
                merged[key] = row

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w") as f:
        for key in order:
            f.write(json.dumps(merged[key]) + "\n")
    print(f"Wrote {len(order)} merged rows to {out_path}")


if __name__ == "__main__":
    raise SystemExit(main())
