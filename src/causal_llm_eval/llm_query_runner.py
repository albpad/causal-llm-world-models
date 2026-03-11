#!/usr/bin/env python3
"""
KG1 LLM Query Runner -- Together.ai Edition
=============================================
88 vignettes x 7 models x 30 runs x 2 phases = 36,960 API calls
Checkpoints after every response. Safe to interrupt and resume.

Usage:
    python llm_query_runner.py --battery vignette_battery.json --runs 30
    python llm_query_runner.py --battery vignette_battery.json --runs 1 --models llama-3.1-8b --items B1-BASE,B1-P1
    python llm_query_runner.py --list-models

Environment: TOGETHER_API_KEY
"""

import json, os, sys, time, hashlib, argparse, re
from pathlib import Path
from datetime import datetime, timezone

MODEL_REGISTRY = {
    "deepseek-r1": {
        "model_id": "deepseek-ai/DeepSeek-R1",
        "max_tokens": 8192, "temperature": 0.6,
        "tier": "reasoning", "price_in": 3.00, "price_out": 7.00,
    },
    "qwen3-235b-thinking": {
        "model_id": "Qwen/Qwen3-235B-A22B-Thinking-2507",
        "max_tokens": 8192, "temperature": 0.6,
        "tier": "reasoning", "price_in": 0.65, "price_out": 3.00,
    },
    "qwen3-235b-instruct": {
        "model_id": "Qwen/Qwen3-235B-A22B-Instruct-2507-tput",
        "max_tokens": 4096, "temperature": 0.6,
        "tier": "general_large", "price_in": 0.20, "price_out": 0.60,
    },
    "llama-4-maverick": {
        "model_id": "meta-llama/Llama-4-Maverick-17B-128E-Instruct-FP8",
        "max_tokens": 4096, "temperature": 0.6,
        "tier": "general_large", "price_in": 0.27, "price_out": 0.85,
    },
    "deepseek-v3.1": {
        "model_id": "deepseek-ai/DeepSeek-V3.1",
        "max_tokens": 4096, "temperature": 0.6,
        "tier": "general_large", "price_in": 0.60, "price_out": 1.70,
    },
    "llama-3.3-70b": {
        "model_id": "meta-llama/Llama-3.3-70B-Instruct-Turbo",
        "max_tokens": 4096, "temperature": 0.6,
        "tier": "scaling", "price_in": 0.88, "price_out": 0.88,
    },
    "llama-3.1-8b": {
        "model_id": "meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo",
        "max_tokens": 4096, "temperature": 0.6,
        "tier": "scaling", "price_in": 0.18, "price_out": 0.18,
    },
    "qwq-32b": {
        "model_id": "Qwen/QwQ-32B",
        "max_tokens": 16384, "temperature": 0.6,
        "tier": "reasoning_small", "price_in": 0.50, "price_out": 1.50,
    },
    "kimi-k2.5": {
        "model_id": "moonshotai/Kimi-K2.5",
        "max_tokens": 4096, "temperature": 1.0,
        "tier": "reasoning_small", "price_in": 0.50, "price_out": 2.80,
    },
    "kimi-k2.5-thinking": {
        "model_id": "moonshotai/Kimi-K2.5",
        "max_tokens": 16384, "temperature": 1.0,
        "tier": "reasoning_small", "price_in": 0.50, "price_out": 2.80,
        "reasoning_effort": "high",
    },
}

ALL_MODELS = list(MODEL_REGISTRY.keys())

SYSTEM_PROMPT = """You are an expert head and neck surgical oncologist participating in a multidisciplinary tumor board. You have extensive experience with laryngeal and hypopharyngeal cancer management, including transoral laser microsurgery (TLM), open partial horizontal laryngectomies (OPHL), total laryngectomy (TL), concurrent chemoradiotherapy (CRT), and induction chemotherapy (ICT) protocols.

When making treatment recommendations, you should:
- Consider all relevant clinical variables including tumor staging, anatomical extent, functional status, patient fitness, and comorbidities
- Distinguish between absolute contraindications, relative contraindications, and preferences
- Explain your reasoning, specifically which clinical findings drive your recommendations
- When uncertain, express that uncertainty rather than committing to a definitive answer
- Consider both surgical and non-surgical larynx preservation options where appropriate

Respond as you would in a real clinical discussion -- thorough but focused on the specific question asked."""

OPEN_ENDED_TEMPLATE = """Here is a clinical case for multidisciplinary discussion:

{clinical_text}

**Clinical Question**: {question}

Please provide your treatment recommendation with detailed reasoning. For each option you recommend or exclude, explain which specific clinical findings support that decision."""

TARGETED_TEMPLATE = """Based on the same clinical case presented above, please evaluate each treatment option listed below.

For EACH treatment, you MUST use this exact format:

**[Treatment name]**: [APPROPRIATE / CONTRAINDICATED / RELATIVELY CONTRAINDICATED / UNCERTAIN]
Reasoning: [1-2 sentences explaining which clinical findings drive this assessment]

Use ONLY one of these four labels — do not paraphrase or hedge the label itself. If a treatment is conditionally appropriate (e.g., depends on surgical expertise or exposure), state APPROPRIATE and note the conditions in your reasoning.

{targeted_questions}"""

TARGETED_QUESTIONS_BY_FAMILY = {
    "glottic_cT2": [
        "1. Is transoral laser microsurgery (TLM) appropriate for this patient?",
        "2. Is conventional radiotherapy alone appropriate?",
        "3. Is accelerated or hyperfractionated radiotherapy indicated?",
        "4. Is concurrent chemoradiotherapy warranted?",
    ],
    "glottic_cT3": [
        "1. Is transoral laser microsurgery (TLM) appropriate for this patient?",
        "2. Is open partial horizontal laryngectomy (OPHL type II) appropriate?",
        "3. Is concurrent chemoradiotherapy (CRT) appropriate?",
        "4. Is induction chemotherapy followed by response-adapted treatment appropriate?",
        "5. Is total laryngectomy necessary?",
    ],
    "supraglottic_cT3": [
        "1. Is transoral laser microsurgery (TLM) or transoral robotic surgery (TORS) appropriate?",
        "2. Is supraglottic laryngectomy (OPHL type I) appropriate?",
        "3. Is OPHL type IIB indicated?",
        "4. Is concurrent chemoradiotherapy appropriate?",
        "5. Should partial laryngectomy be avoided given the nodal status?",
    ],
    "hypopharyngeal": [
        "1. Is transoral laser microsurgery (TLM) appropriate for this hypopharyngeal cancer?",
        "2. Is partial laryngectomy appropriate given the tumor extent and nodal disease?",
        "3. Is non-surgical larynx preservation (CRT or ICT+RT) appropriate?",
        "4. Is total laryngectomy the preferred treatment?",
    ],
    "cT4a_unselected": [
        "1. Is total laryngectomy the appropriate treatment?",
        "2. Is any form of larynx preservation viable?",
        "3. Could non-surgical LP (CRT) be considered?",
    ],
    "cT4a_selected": [
        "1. Is total laryngectomy mandatory for this cT4a patient?",
        "2. Is open partial horizontal laryngectomy (OPHL) a viable option?",
        "3. Is non-surgical larynx preservation (CRT) a viable option?",
        "4. Is TLM appropriate?",
    ],
    "cisplatin_eligibility": [
        "1. Is high-dose cisplatin (100 mg/m2 q3w) appropriate for this patient?",
        "2. If not, what is the specific contraindication?",
        "3. Is the contraindication absolute or relative?",
        "4. What alternative concurrent systemic agent would you recommend?",
    ],
    "post_ict_response": [
        "1. Is radiotherapy alone (without concurrent chemotherapy) the appropriate definitive treatment?",
        "2. Is concurrent chemoradiotherapy (CRT) indicated?",
        "3. Should total laryngectomy be recommended?",
        "4. Is continued non-surgical larynx preservation justified based on the ICT response?",
    ],
    "elderly_frail": [
        "1. Does this patient's age affect eligibility for TLM?",
        "2. Does this patient's age affect eligibility for OPHL?",
        "3. Does this patient's age affect eligibility for concurrent CRT?",
        "4. Should treatment be de-escalated or adapted based on age/frailty?",
    ],
    "pretreatment_function": [
        "1. Is non-surgical larynx preservation (CRT or ICT) contraindicated?",
        "2. If contraindicated, is it an absolute or relative contraindication?",
        "3. What specific functional findings drive this assessment?",
        "4. Is total laryngectomy indicated?",
    ],
}

def build_targeted_questions(family):
    qs = TARGETED_QUESTIONS_BY_FAMILY.get(family, [
        "1. Which treatments are appropriate for this patient?",
        "2. Which treatments are contraindicated?",
        "3. Are any contraindications absolute vs. relative?",
    ])
    return "\n".join(qs)


def call_together(model_id, messages, temperature, max_tokens, api_key,
                   reasoning_effort=None, timeout=300, max_retries=5):
    import requests, random
    payload = {"model": model_id, "messages": messages,
               "temperature": temperature, "max_tokens": max_tokens}
    if reasoning_effort:
        payload["reasoning_effort"] = reasoning_effort

    for attempt in range(max_retries):
        try:
            resp = requests.post(
                "https://api.together.xyz/v1/chat/completions",
                headers={"Authorization": f"Bearer {api_key}",
                         "Content-Type": "application/json"},
                json=payload,
                timeout=timeout,
            )
            if resp.status_code == 503 or resp.status_code == 429:
                wait = min(2 ** attempt * 10 + random.uniform(0, 5), 120)
                time.sleep(wait)
                continue
            resp.raise_for_status()
            break
        except requests.exceptions.ReadTimeout:
            if attempt < max_retries - 1:
                wait = min(2 ** attempt * 15 + random.uniform(0, 10), 180)
                time.sleep(wait)
                continue
            raise
        except requests.exceptions.HTTPError:
            raise
    data = resp.json()
    msg = data["choices"][0]["message"]
    content = msg.get("content", "") or ""
    reasoning = ""

    # Method 1: reasoning_content field (some providers return this)
    if msg.get("reasoning_content"):
        reasoning = msg["reasoning_content"].strip()
    # Method 2: <think> tags (Together.ai standard for reasoning models)
    if not reasoning and "<think>" in content:
        m = re.search(r"<think>(.*?)</think>", content, re.DOTALL)
        if m:
            reasoning = m.group(1).strip()
            content = re.sub(r"<think>.*?</think>", "", content, flags=re.DOTALL).strip()

    return {"content": content, "reasoning": reasoning,
            "usage": data.get("usage", {}),
            "finish_reason": data["choices"][0].get("finish_reason", "unknown")}


class RateLimiter:
    def __init__(self, rpm=50):
        self._interval = 60.0 / rpm
        self._last = 0
    def wait(self):
        w = max(0, self._interval - (time.time() - self._last))
        if w > 0: time.sleep(w)
        self._last = time.time()


def make_hash(item_id, model, run):
    return hashlib.md5(f"{item_id}:{model}:{run}".encode()).hexdigest()[:12]


def load_battery(path):
    with open(path) as f:
        bat = json.load(f)
    items = []
    for b in bat["baselines"]:
        items.append({"id": b["id"], "family": b["family"], "type": "baseline",
                       "clinical_text": b["clinical_text"], "question": b["question"],
                       "expected_recommendations": b["expected_recommendations"],
                       "expected_excluded": b["expected_excluded"]})
    for p in bat["perturbations"]:
        items.append({"id": p["id"], "family": p["family"], "type": p["type"],
                       "baseline_id": p["baseline_id"],
                       "clinical_text": p["clinical_text"], "question": p["question"],
                       "expected_recommendations": p["expected_recommendations"],
                       "expected_excluded": p["expected_excluded"],
                       "edge_justification": p.get("edge_justification", []),
                       "grey_zone_statement": p.get("grey_zone_statement")})
    return items


def run_single_query(item, model_name, run_idx, rl, api_key, dry_run=False):
    cfg = MODEL_REGISTRY[model_name]
    result = {
        "item_id": item["id"], "model_name": model_name,
        "model_id": cfg["model_id"], "run_idx": run_idx,
        "hash": make_hash(item["id"], model_name, run_idx),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "temperature": cfg["temperature"], "family": item["family"],
        "item_type": item.get("type", "baseline"), "tier": cfg["tier"],
        "phase1_response": None, "phase1_reasoning": None,
        "phase2_response": None, "phase2_reasoning": None,
        "phase1_usage": None, "phase2_usage": None, "error": None,
    }
    if dry_run:
        result["phase1_response"] = result["phase2_response"] = "[DRY RUN]"
        return result
    try:
        msgs1 = [{"role": "system", "content": SYSTEM_PROMPT},
                 {"role": "user", "content": OPEN_ENDED_TEMPLATE.format(
                     clinical_text=item["clinical_text"].strip(),
                     question=item["question"].strip())}]
        rl.wait()
        re_effort = cfg.get("reasoning_effort")
        # Reasoning models need longer timeouts (up to 10 min per call)
        tout = 600 if "reasoning" in cfg.get("tier", "") else 300
        r1 = call_together(cfg["model_id"], msgs1, cfg["temperature"], cfg["max_tokens"], api_key, re_effort, tout)
        result["phase1_response"] = r1["content"]
        result["phase1_reasoning"] = r1["reasoning"]
        result["phase1_usage"] = r1["usage"]

        msgs2 = msgs1 + [
            {"role": "assistant", "content": r1["content"]},
            {"role": "user", "content": TARGETED_TEMPLATE.format(
                targeted_questions=build_targeted_questions(item["family"]))}]
        rl.wait()
        r2 = call_together(cfg["model_id"], msgs2, cfg["temperature"], cfg["max_tokens"], api_key, re_effort, tout)
        result["phase2_response"] = r2["content"]
        result["phase2_reasoning"] = r2["reasoning"]
        result["phase2_usage"] = r2["usage"]
    except Exception as e:
        result["error"] = f"{type(e).__name__}: {str(e)}"
    return result


def load_completed(path):
    done = set()
    if Path(path).exists():
        with open(path) as f:
            for line in f:
                if line.strip():
                    try:
                        r = json.loads(line)
                        if r.get("error") is None: done.add(r["hash"])
                    except: pass
    return done


def run_battery(battery_path, model_names, n_runs=30, item_filter=None,
                output_dir="results", dry_run=False, max_retries=3):
    items = load_battery(battery_path)
    if item_filter:
        items = [i for i in items if i["id"] in item_filter]

    for m in model_names:
        if m not in MODEL_REGISTRY:
            print(f"ERROR: Unknown model '{m}'. Use --list-models"); return

    api_key = os.environ.get("TOGETHER_API_KEY", "")
    if not api_key and not dry_run:
        print("ERROR: TOGETHER_API_KEY not set"); return

    n_q = len(items) * len(model_names) * n_runs
    print(f"{len(items)} items x {len(model_names)} models x {n_runs} runs = {n_q} queries ({n_q*2} API calls)")

    out = Path(output_dir); out.mkdir(parents=True, exist_ok=True)

    # Resume: reuse existing checkpoint, or create new one
    existing = sorted(out.glob("run_*.jsonl"))
    if existing:
        cp = existing[-1]
        print(f"Found existing checkpoint: {cp}")
    else:
        cp = out / f"run_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M')}.jsonl"
    print(f"Checkpoint: {cp}")

    # Scan ALL .jsonl files in results dir (in case of multiple checkpoint files)
    done = set()
    for jf in out.glob("run_*.jsonl"):
        done |= load_completed(str(jf))
    if done: print(f"Resuming: {len(done)} completed across all checkpoint files")

    work = [(i, m, r) for i in items for m in model_names for r in range(n_runs)
            if make_hash(i["id"], m, r) not in done]
    print(f"Remaining: {len(work)}\n")
    if not work: print("All done!"); return str(cp)

    rl = RateLimiter()
    n_done = n_err = 0; t0 = time.time()

    for item, mn, ri in work:
        n_done += 1
        eta = (len(work)-n_done) / (n_done/(time.time()-t0)) / 60 if n_done > 0 and time.time() > t0 else 0
        print(f"[{n_done}/{len(work)}] {item['id']} x {mn} r{ri} | ETA {eta:.0f}m", end="")

        res = None
        for att in range(max_retries):
            res = run_single_query(item, mn, ri, rl, api_key, dry_run)
            if res["error"] is None: break
            w = 2**att * 5; print(f" [retry {att+1} in {w}s]", end=""); time.sleep(w)

        with open(cp, "a") as f: f.write(json.dumps(res, default=str) + "\n")
        if res["error"]: n_err += 1; print(f" X {res['error'][:60]}")
        else: print(f" ok ({len(res['phase1_response'] or '')}+{len(res['phase2_response'] or '')}c)")

    print(f"\nDone: {n_done} in {(time.time()-t0)/60:.1f}m, {n_err} errors")
    return str(cp)


def main():
    p = argparse.ArgumentParser(description="KG1 Query Runner - Together.ai")
    p.add_argument("--battery", help="Path to vignette_battery.json")
    p.add_argument("--models", default=",".join(ALL_MODELS))
    p.add_argument("--runs", type=int, default=30)
    p.add_argument("--items", default=None)
    p.add_argument("--outdir", default="results")
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--list-models", action="store_true")
    args = p.parse_args()

    if args.list_models:
        print(f"{'Name':<25s} {'Tier':<15s} {'$/M in':>7s} {'$/M out':>8s} Model ID")
        for n, c in sorted(MODEL_REGISTRY.items(), key=lambda x: x[1]["price_in"]):
            print(f"{n:<25s} {c['tier']:<15s} ${c['price_in']:>6.2f} ${c['price_out']:>7.2f} {c['model_id']}")
        return

    if not args.battery: p.error("--battery required")
    models = [m.strip() for m in args.models.split(",")]
    filt = [i.strip() for i in args.items.split(",")] if args.items else None
    run_battery(args.battery, models, args.runs, filt, args.outdir, args.dry_run)

if __name__ == "__main__":
    main()
