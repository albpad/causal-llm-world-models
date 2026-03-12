#!/usr/bin/env python3
"""Build a rerun manifest for incomplete query rows."""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from causal_llm_eval.llm_query_runner import is_complete_result, load_battery


def parse_args():
    parser = argparse.ArgumentParser(description="Create a manifest of incomplete query hashes for rerun.")
    parser.add_argument("--results", required=True, help="Path to run_*.jsonl")
    parser.add_argument("--battery", default="data/vignettes/vignette_battery.json")
    parser.add_argument("--model", required=True, help="Short model name to filter on, e.g. kimi-k2.5")
    parser.add_argument("--max-run-idx", type=int, default=None,
                        help="Only include runs with run_idx <= this value. Useful to isolate the main study.")
    parser.add_argument("--out", required=True, help="Output JSON manifest path")
    parser.add_argument("--allow-empty-phase1", action="store_true")
    parser.add_argument("--allow-empty-phase2", action="store_true")
    return parser.parse_args()


def main():
    args = parse_args()
    rows = [json.loads(line) for line in open(args.results) if line.strip()]
    items_by_id = {item["id"]: item for item in load_battery(args.battery)}

    manifest_rows = []
    for row in rows:
        if row.get("model_name") != args.model:
            continue
        if args.max_run_idx is not None and row.get("run_idx", -1) > args.max_run_idx:
            continue
        if is_complete_result(
            row,
            require_phase1=not args.allow_empty_phase1,
            require_phase2=not args.allow_empty_phase2,
        ):
            continue
        item = items_by_id.get(row["item_id"], {})
        manifest_rows.append(
            {
                "hash": row["hash"],
                "item_id": row["item_id"],
                "model_name": row["model_name"],
                "run_idx": row["run_idx"],
                "family": item.get("family", row.get("family")),
                "item_type": item.get("type", row.get("item_type")),
                "error": row.get("error"),
                "phase1_blank": not bool((row.get("phase1_response") or "").strip()),
                "phase2_blank": not bool((row.get("phase2_response") or "").strip()),
            }
        )

    unique = {}
    for row in manifest_rows:
        unique[row["hash"]] = row
    payload = {
        "results_path": args.results,
        "battery_path": args.battery,
        "model_name": args.model,
        "max_run_idx": args.max_run_idx,
        "require_phase1": not args.allow_empty_phase1,
        "require_phase2": not args.allow_empty_phase2,
        "n_incomplete": len(unique),
        "rows": list(sorted(unique.values(), key=lambda row: (row["item_id"], row["run_idx"]))),
    }
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(payload, indent=2))
    print(f"Wrote {payload['n_incomplete']} incomplete hashes to {out_path}")


if __name__ == "__main__":
    raise SystemExit(main())
