#!/usr/bin/env python3
"""Materialize deterministic JSONL subsets from one or more raw result files."""

import argparse
import json
from pathlib import Path


def parse_args():
    parser = argparse.ArgumentParser(description="Filter one or more run_*.jsonl files into a deterministic subset.")
    parser.add_argument("--results", required=True, nargs="+", help="Input JSONL files in the order to process them.")
    parser.add_argument("--out", required=True, help="Output JSONL file")
    parser.add_argument("--model", action="append", default=None,
                        help="Restrict to one or more model_name values. Repeat the flag to allow multiple models.")
    parser.add_argument("--max-run-idx", type=int, default=None,
                        help="Only include rows with run_idx <= this value.")
    parser.add_argument("--items", default=None,
                        help="Comma-separated list of item IDs to include.")
    parser.add_argument("--dedupe-hash", action="store_true",
                        help="Keep only the first occurrence of each hash across all inputs.")
    return parser.parse_args()


def iter_rows(paths):
    for path in paths:
        with open(path) as f:
            for line in f:
                if not line.strip():
                    continue
                yield json.loads(line)


def main():
    args = parse_args()
    models = set(args.model or [])
    items = {item.strip() for item in args.items.split(",")} if args.items else None
    seen = set()
    kept = 0
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    with open(out_path, "w") as out_f:
        for row in iter_rows(args.results):
            if models and row.get("model_name") not in models:
                continue
            if args.max_run_idx is not None and row.get("run_idx", -1) > args.max_run_idx:
                continue
            if items and row.get("item_id") not in items:
                continue
            if args.dedupe_hash:
                row_hash = row.get("hash")
                if row_hash in seen:
                    continue
                seen.add(row_hash)
            out_f.write(json.dumps(row) + "\n")
            kept += 1

    print(f"Wrote {kept} rows to {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
