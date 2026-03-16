#!/usr/bin/env python3
"""Build a full-study manifest for one or more models and run indices."""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from causal_llm_eval.llm_query_runner import load_battery, make_hash


def parse_args():
    parser = argparse.ArgumentParser(description="Create a manifest for a full study run.")
    parser.add_argument("--battery", default="data/vignettes/vignette_battery.json")
    parser.add_argument("--models", required=True,
                        help="Comma-separated model names as they should appear in the manifest.")
    parser.add_argument("--runs", type=int, required=True, help="Number of runs per item, starting at run_idx=0.")
    parser.add_argument("--items", default=None,
                        help="Optional comma-separated item IDs to include.")
    parser.add_argument("--out", required=True)
    return parser.parse_args()


def main():
    args = parse_args()
    items = load_battery(args.battery)
    item_filter = {item.strip() for item in args.items.split(",")} if args.items else None
    if item_filter:
        items = [item for item in items if item["id"] in item_filter]

    model_names = [model.strip() for model in args.models.split(",") if model.strip()]
    rows = []
    for model_name in model_names:
        for item in items:
            for run_idx in range(args.runs):
                rows.append(
                    {
                        "hash": make_hash(item["id"], model_name, run_idx),
                        "item_id": item["id"],
                        "model_name": model_name,
                        "run_idx": run_idx,
                        "family": item["family"],
                        "item_type": item.get("type"),
                    }
                )

    payload = {
        "battery_path": args.battery,
        "model_names": model_names,
        "runs": args.runs,
        "n_rows": len(rows),
        "rows": rows,
    }
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(payload, indent=2))
    print(f"Wrote {len(rows)} manifest rows to {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
