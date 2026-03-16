#!/usr/bin/env python3
"""Rerun incomplete queries from a recovery manifest."""

import argparse
import json
import os
import sys
import time
import threading
from concurrent.futures import FIRST_COMPLETED, ThreadPoolExecutor, wait
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from causal_llm_eval.llm_query_runner import (  # noqa: E402
    MODEL_REGISTRY,
    OPEN_ENDED_TEMPLATE,
    SYSTEM_PROMPT,
    TARGETED_TEMPLATE,
    RateLimiter,
    build_targeted_questions,
    call_together,
    load_battery,
    make_hash,
)


def parse_args():
    parser = argparse.ArgumentParser(description="Rerun incomplete manifest entries.")
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--battery", default="data/vignettes/vignette_battery.json")
    parser.add_argument("--outdir", required=True)
    parser.add_argument("--model-override", default=None,
                        help="Override manifest model, e.g. kimi-k2.5-thinking")
    parser.add_argument("--preserve-manifest-identity", action="store_true",
                        help="When used with --model-override, keep the original manifest model_name/hash "
                             "in saved rows so reruns can merge back into the original study arm.")
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--rpm", type=int, default=20)
    parser.add_argument("--max-retries", type=int, default=3)
    parser.add_argument("--workers", type=int, default=1,
                        help="Number of manifest entries to process concurrently.")
    parser.add_argument("--phase2-context-mode", choices=["full", "truncate", "none"], default="none",
                        help="How much of phase 1 to include before the structured phase 2 prompt.")
    parser.add_argument("--phase1-char-limit", type=int, default=1200,
                        help="Used when --phase2-context-mode=truncate.")
    parser.add_argument("--force-max-tokens", type=int, default=None,
                        help="Override model max_tokens during recovery while keeping the original model name.")
    parser.add_argument("--force-reasoning-effort", default=None,
                        help="Override reasoning_effort during recovery, e.g. high.")
    return parser.parse_args()


class ThreadSafeRateLimiter:
    """Serialize API pacing across worker threads."""

    def __init__(self, rpm: int):
        self._limiter = RateLimiter(rpm=rpm)
        self._lock = threading.Lock()

    def wait(self):
        with self._lock:
            self._limiter.wait()


def load_completed_hashes(outdir: Path) -> set[str]:
    done = set()
    for file_path in outdir.glob("run_*.jsonl"):
        with open(file_path) as f:
            for line in f:
                if not line.strip():
                    continue
                try:
                    row = json.loads(line)
                except json.JSONDecodeError:
                    continue
                p1 = (row.get("phase1_response") or "").strip()
                p2 = (row.get("phase2_response") or "").strip()
                if row.get("error") is None and p1 and p2:
                    done.add(row["hash"])
    return done


def build_phase2_messages(item: dict, phase1_text: str, context_mode: str, phase1_char_limit: int):
    msgs = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": OPEN_ENDED_TEMPLATE.format(
            clinical_text=item["clinical_text"].strip(),
            question=item["question"].strip(),
        )},
    ]
    if context_mode == "full" and phase1_text.strip():
        msgs.append({"role": "assistant", "content": phase1_text})
    elif context_mode == "truncate" and phase1_text.strip():
        msgs.append({"role": "assistant", "content": phase1_text[:phase1_char_limit]})
    msgs.append({"role": "user", "content": TARGETED_TEMPLATE.format(
        targeted_questions=build_targeted_questions(item["family"])
    )})
    return msgs


def run_entry(item: dict, query_model_name: str, run_idx: int, api_key: str, rl: RateLimiter,
              context_mode: str, phase1_char_limit: int,
              force_max_tokens: int | None = None,
              force_reasoning_effort: str | None = None,
              output_model_name: str | None = None,
              output_hash: str | None = None,
              progress=None):
    cfg = MODEL_REGISTRY[query_model_name]
    max_tokens = force_max_tokens or cfg["max_tokens"]
    reasoning_effort = force_reasoning_effort if force_reasoning_effort is not None else cfg.get("reasoning_effort")
    stored_model_name = output_model_name or query_model_name
    result = {
        "item_id": item["id"],
        "model_name": stored_model_name,
        "model_id": cfg["model_id"],
        "run_idx": run_idx,
        "hash": output_hash or make_hash(item["id"], stored_model_name, run_idx),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "temperature": cfg["temperature"],
        "family": item["family"],
        "item_type": item.get("type", "baseline"),
        "tier": cfg["tier"],
        "phase1_response": None,
        "phase1_reasoning": None,
        "phase2_response": None,
        "phase2_reasoning": None,
        "phase1_usage": None,
        "phase2_usage": None,
        "error": None,
    }
    if stored_model_name != query_model_name:
        result["queried_with_model_name"] = query_model_name

    try:
        msgs1 = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": OPEN_ENDED_TEMPLATE.format(
                clinical_text=item["clinical_text"].strip(),
                question=item["question"].strip(),
            )},
        ]
        if progress:
            progress("phase1:start")
        rl.wait()
        timeout = 600 if "reasoning" in cfg.get("tier", "") else 300
        r1 = call_together(cfg["model_id"], msgs1, cfg["temperature"], max_tokens, api_key, reasoning_effort, timeout)
        result["phase1_response"] = r1["content"]
        result["phase1_reasoning"] = r1["reasoning"]
        result["phase1_usage"] = r1["usage"]
        if progress:
            progress(f"phase1:done len={len(r1['content'] or '')}")

        msgs2 = build_phase2_messages(item, r1["content"] or "", context_mode, phase1_char_limit)
        if progress:
            progress("phase2:start")
        rl.wait()
        r2 = call_together(cfg["model_id"], msgs2, cfg["temperature"], max_tokens, api_key, reasoning_effort, timeout)
        result["phase2_response"] = r2["content"]
        result["phase2_reasoning"] = r2["reasoning"]
        result["phase2_usage"] = r2["usage"]
        if progress:
            progress(f"phase2:done len={len(r2['content'] or '')}")
    except Exception as exc:  # noqa: BLE001
        result["error"] = f"{type(exc).__name__}: {exc}"
        if progress:
            progress(f"error:{result['error']}")

    return result


def main():
    args = parse_args()
    api_key = os.environ.get("TOGETHER_API_KEY", "")
    if not api_key:
        print("ERROR: TOGETHER_API_KEY not set")
        return 1

    manifest = json.load(open(args.manifest))
    rows = manifest["rows"]
    if args.limit is not None:
        rows = rows[: args.limit]

    battery_items = {item["id"]: item for item in load_battery(args.battery)}
    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    done = load_completed_hashes(outdir)

    work = []
    for row in rows:
        query_model_name = args.model_override or row["model_name"]
        output_model_name = row["model_name"] if args.preserve_manifest_identity else query_model_name
        item = battery_items[row["item_id"]]
        rerun_hash = row["hash"] if args.preserve_manifest_identity else make_hash(item["id"], output_model_name, row["run_idx"])
        if rerun_hash in done:
            continue
        work.append((item, query_model_name, output_model_name, row["run_idx"], row["hash"], rerun_hash))

    if not work:
        print("No remaining manifest entries to rerun.")
        return 0

    checkpoint = outdir / f"run_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M')}.jsonl"
    rl = ThreadSafeRateLimiter(rpm=args.rpm)
    print(f"Rerunning {len(work)} manifest entries")
    print(f"Output: {checkpoint}")
    print(f"Phase 2 context mode: {args.phase2_context_mode}")
    print(f"Workers: {args.workers}")

    file_lock = threading.Lock()
    print_lock = threading.Lock()

    def process_one(index, item, query_model_name, output_model_name, run_idx, original_hash, output_hash):
        line_prefix = f"[{index}/{len(work)}] {item['id']} {output_model_name} via {query_model_name} run={run_idx}"

        def log(message):
            with print_lock:
                print(f"{line_prefix} {message}", flush=True)

        result = None
        for attempt in range(args.max_retries):
            result = run_entry(
                item,
                query_model_name,
                run_idx,
                api_key,
                rl,
                args.phase2_context_mode,
                args.phase1_char_limit,
                args.force_max_tokens,
                args.force_reasoning_effort,
                output_model_name,
                output_hash,
                log,
            )
            if (
                result["error"] is None
                and (result.get("phase1_response") or "").strip()
                and (result.get("phase2_response") or "").strip()
            ):
                break
            if attempt < args.max_retries - 1:
                wait_seconds = 2 ** attempt * 5
                log(f"retry in {wait_seconds}s")
                time.sleep(wait_seconds)

        result["recovery_of_hash"] = original_hash
        with file_lock:
            with open(checkpoint, "a") as f:
                f.write(json.dumps(result) + "\n")
                f.flush()

        p1 = bool((result.get("phase1_response") or "").strip())
        p2 = bool((result.get("phase2_response") or "").strip())
        status = "ok" if result.get("error") is None and p1 and p2 else f"incomplete error={result.get('error')}"
        log(status)
        return result

    with ThreadPoolExecutor(max_workers=max(1, args.workers)) as executor:
        pending = set()
        work_iter = iter(enumerate(work, 1))

        while True:
            while len(pending) < max(1, args.workers):
                try:
                    idx, work_row = next(work_iter)
                except StopIteration:
                    break
                pending.add(executor.submit(process_one, idx, *work_row))

            if not pending:
                break

            done_futures, pending = wait(pending, return_when=FIRST_COMPLETED)
            for future in done_futures:
                future.result()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
