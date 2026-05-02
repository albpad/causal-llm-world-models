#!/usr/bin/env python3
"""Combine raw JSONL result files deterministically with hash deduplication."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--inputs", nargs="+", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument(
        "--sort",
        choices=["input", "model_item_run"],
        default="model_item_run",
        help="Deterministic output ordering.",
    )
    return parser.parse_args()


def sort_key(row: dict) -> tuple:
    return (
        row.get("model_name", ""),
        row.get("item_id", ""),
        int(row.get("run_idx", 0)),
        row.get("timestamp", ""),
        row.get("hash", ""),
    )


def main() -> int:
    args = parse_args()
    rows: list[dict] = []
    seen = set()

    for input_path in args.inputs:
        with input_path.open() as f:
            for line in f:
                if not line.strip():
                    continue
                row = json.loads(line)
                dedupe_key = row.get("hash") or (
                    row.get("item_id"),
                    row.get("model_name"),
                    row.get("run_idx"),
                )
                if dedupe_key in seen:
                    continue
                seen.add(dedupe_key)
                rows.append(row)

    if args.sort == "model_item_run":
        rows.sort(key=sort_key)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w") as f:
        for row in rows:
            f.write(json.dumps(row) + "\n")

    print(f"Wrote {len(rows)} rows to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
