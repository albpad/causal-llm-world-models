#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
KG1 Counterfactual Sensitivity Analysis — Colab Runner
=======================================================
Complete pipeline on Together.ai: query 7 LLMs x 88 vignettes x 30 runs,
then parse, score, detect edges (Fisher + JSD + FDR), classify divergences,
reconstruct KG2, and generate publication-ready analysis.

Setup:
1. Upload to Google Drive /KG1_study/:
   - vignette_battery.json, llm_query_runner.py, response_parser.py
2. Add TOGETHER_API_KEY to Colab Secrets
3. Run cells in order. Safe to interrupt and resume.

## In Colab: File -> Upload notebook -> select this .py file
"""

# %% [markdown]
# # KG1 Counterfactual Sensitivity Analysis
# **Source**: Ferrari et al., Lancet Oncol 2025; 26: e264-81
#
# 88 vignettes × 7 models × 30 runs × 2 phases = 36,960 API calls
# Statistical edge detection: Fisher's exact + JSD + BH-FDR (q=0.05)
# Divergence taxonomy: missing edge / wrong direction / wrong conditionality / magnitude misalignment

# %% Cell 1: Setup
import os, sys, json, shutil
from pathlib import Path
from google.colab import drive, userdata

drive.mount('/content/drive')
PROJECT = Path('/content/drive/MyDrive/KG1_study')
PROJECT.mkdir(parents=True, exist_ok=True)
WORK = Path('/content/kg1_work'); WORK.mkdir(exist_ok=True)

for f in ['vignette_battery.json', 'llm_query_runner.py', 'response_parser.py']:
    src = PROJECT / f
    if src.exists(): shutil.copy2(src, WORK / f); print(f"+ {f}")
    else: print(f"MISSING: {f}")

sys.path.insert(0, str(WORK))
os.environ['TOGETHER_API_KEY'] = userdata.get('TOGETHER_API_KEY')
print("+ API key loaded")

# Install scipy for statistical tests
import subprocess
subprocess.check_call([sys.executable, "-m", "pip", "install", "-q", "scipy"])

# %% Cell 2: Verify Battery & Models
from causal_llm_eval.llm_query_runner import load_battery, MODEL_REGISTRY

BATTERY = str(WORK / 'vignette_battery.json')
items = load_battery(BATTERY)
print(f"Battery: {len(items)} items ({len([i for i in items if i['type']=='baseline'])} baselines)")

print(f"\n{'Model':<25s} {'Tier':<15s} {'$/M in':>7s} {'$/M out':>8s}")
for n, c in sorted(MODEL_REGISTRY.items(), key=lambda x: x[1]['price_in']):
    print(f"{n:<25s} {c['tier']:<15s} ${c['price_in']:>6.2f} ${c['price_out']:>7.2f}")

# %% Cell 3: Configuration
# ===========================================================
# EDIT BEFORE RUNNING
# ===========================================================

MODELS = [
    "llama-3.1-8b",          # $1.62  — small baseline
    "qwen3-235b-instruct",   # $3.27  — large, no thinking
    "llama-4-maverick",      # $4.57  — Meta MoE
    "llama-3.3-70b",         # $7.90  — dense 70B
    "deepseek-v3.1",         # $9.45  — DeepSeek general
    "qwen3-235b-thinking",   # $31.15 — thinking mode (paired with instruct)
    "deepseek-r1",           # $106   — best reasoning
]

N_RUNS = 30          # 30 for distributional testing (Fisher/JSD)
PILOT_ITEMS = None   # Set to ["B1-BASE","B1-P1","B1-P2","B1-NULL1"] for pilot

# ===========================================================
n = len(PILOT_ITEMS) if PILOT_ITEMS else len(items)
calls = n * len(MODELS) * N_RUNS * 2
print(f"\n{n} items x {len(MODELS)} models x {N_RUNS} runs = {n*len(MODELS)*N_RUNS} queries ({calls} API calls)")
if N_RUNS == 1: print("WARNING: N=1 is OK for pilot but Fisher/JSD need N>=10")

# %% Cell 4: Run Query Battery
from causal_llm_eval.llm_query_runner import run_battery

RESULTS_DIR = str(PROJECT / 'results')
checkpoint = run_battery(BATTERY, MODELS, N_RUNS, PILOT_ITEMS, RESULTS_DIR)
print(f"\nCheckpoint: {checkpoint}")

# %% Cell 5: Parse & Score & Statistical Testing
from causal_llm_eval.response_parser import run_analysis

results_dir = Path(RESULTS_DIR)
latest = str(sorted(results_dir.glob('run_*.jsonl'))[-1])
print(f"Using: {latest}")

ANALYSIS_DIR = str(PROJECT / 'analysis')
metrics, kg2, edge_tests, divergences = run_analysis(latest, BATTERY, ANALYSIS_DIR)

# %% Cell 6: Visualise
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

models = sorted(metrics.keys())

# Plot 1: Aggregate Performance
fig, axes = plt.subplots(1, 3, figsize=(18, 6))
for idx, (key, label) in enumerate([
    ('rec_accuracy', 'Recommendation\nAccuracy'),
    ('exc_accuracy', 'Exclusion\nAccuracy'),
    ('rec_precision', 'Recommendation\nPrecision'),
]):
    ax = axes[idx]; vals = [metrics[m][key] for m in models]
    colors = plt.cm.Set2(np.linspace(0, 1, len(models)))
    bars = ax.bar(range(len(models)), vals, color=colors)
    ax.set_xticks(range(len(models))); ax.set_xticklabels(models, rotation=45, ha='right', fontsize=8)
    ax.set_ylabel(label); ax.set_ylim(0, 1.05); ax.axhline(1.0, color='gray', ls='--', alpha=0.3)
    for b, v in zip(bars, vals): ax.text(b.get_x()+b.get_width()/2, v+.02, f'{v:.0%}', ha='center', fontsize=8)
fig.suptitle('KG1 vs KG2: Aggregate Model Performance', fontweight='bold')
plt.tight_layout(); plt.savefig(str(Path(ANALYSIS_DIR)/'agg_perf.png'), dpi=150, bbox_inches='tight'); plt.show()

# Plot 2: Edge Detection Heatmap
if kg2:
    all_e = sorted(set(e for me in kg2.values() for e in me))
    ms = sorted(kg2.keys())
    mat = np.zeros((len(all_e), len(ms)))
    for j, m in enumerate(ms):
        for i, e in enumerate(all_e):
            if e in kg2[m]: mat[i,j] = kg2[m][e]['detection_rate']

    fig, ax = plt.subplots(figsize=(max(8, len(ms)*2.5), max(10, len(all_e)*0.35)))
    im = ax.imshow(mat, cmap='RdYlGn', aspect='auto', vmin=0, vmax=1)
    ax.set_xticks(range(len(ms))); ax.set_xticklabels(ms, rotation=45, ha='right', fontsize=8)
    ax.set_yticks(range(len(all_e))); ax.set_yticklabels(all_e, fontsize=7)
    ax.set_title('KG2 Edge Detection Rate by Model', fontweight='bold')
    plt.colorbar(im, ax=ax, label='Detection Rate', shrink=0.6)
    for i in range(len(all_e)):
        for j in range(len(ms)):
            v = mat[i,j]; c = 'white' if v<0.4 or v>0.8 else 'black'
            ax.text(j, i, f'{v:.0%}', ha='center', va='center', fontsize=6, color=c)
    plt.tight_layout(); plt.savefig(str(Path(ANALYSIS_DIR)/'edge_heatmap.png'), dpi=150, bbox_inches='tight'); plt.show()

# Plot 3: JSD Distribution
if edge_tests:
    fig, ax = plt.subplots(figsize=(10, 6))
    for m in models:
        jsds = [t['jsd'] for t in edge_tests if t['model'] == m and t.get('jsd', 0) > 0]
        if jsds: ax.hist(jsds, bins=20, alpha=0.5, label=m)
    ax.set_xlabel('Jensen-Shannon Divergence'); ax.set_ylabel('Count')
    ax.set_title('Edge Weight Distribution (JSD between baseline/perturbation)', fontweight='bold')
    ax.legend(fontsize=7); plt.tight_layout()
    plt.savefig(str(Path(ANALYSIS_DIR)/'jsd_dist.png'), dpi=150, bbox_inches='tight'); plt.show()

print("Plots saved to analysis/")

# %% Cell 7: Divergence Analysis
from collections import Counter

print("=" * 60)
print("DIVERGENCE TAXONOMY")
print("=" * 60)
by_type = Counter(d['divergence_type'] for d in divergences)
for dt, n in by_type.most_common():
    print(f"  {dt}: {n}")

print(f"\nPer-model breakdown:")
by_model = {}
for d in divergences:
    by_model.setdefault(d['model'], Counter())[d['divergence_type']] += 1
for m in sorted(by_model):
    print(f"  {m}: {dict(by_model[m])}")

print(f"\nMost-missed edges (all models):")
from collections import defaultdict
missed = defaultdict(int); tested = defaultdict(int)
for t in edge_tests:
    for e in t['edges']:
        tested[e] += 1
        if not t.get('significant', False): missed[e] += 1
for e, n in sorted(missed.items(), key=lambda x: -x[1])[:15]:
    print(f"  {e}: missed {n}/{tested[e]} ({n/tested[e]:.0%})")

# %% Cell 8: Thinking vs Non-Thinking Comparison
if 'qwen3-235b-thinking' in metrics and 'qwen3-235b-instruct' in metrics:
    print("=" * 60)
    print("THINKING vs NON-THINKING (Qwen3-235B, same architecture)")
    print("=" * 60)
    t = metrics['qwen3-235b-thinking']; i = metrics['qwen3-235b-instruct']
    for k in ['rec_accuracy', 'exc_accuracy', 'rec_precision', 'cond_rate', 'unc_rate', 'null_spec']:
        tv = t.get(k); iv = i.get(k)
        if tv is not None and iv is not None:
            delta = tv - iv
            print(f"  {k:25s}: thinking={tv:.0%}  instruct={iv:.0%}  delta={delta:+.0%}")

# %% Cell 9: Export
from datetime import datetime
summary = {
    "study": "KG1 Counterfactual Sensitivity Analysis",
    "source": "Ferrari et al., Lancet Oncol 2025",
    "date": datetime.utcnow().isoformat(),
    "design": {"items": len(items), "models": len(MODELS), "runs": N_RUNS,
               "total_api_calls": len(items)*len(MODELS)*N_RUNS*2},
    "models": MODELS,
    "metrics": {m: {k: round(v, 4) if isinstance(v, float) else v
                    for k, v in ms.items()} for m, ms in metrics.items()},
    "n_edge_tests": len(edge_tests),
    "n_significant": sum(1 for t in edge_tests if t.get('significant')),
    "divergences": dict(Counter(d['divergence_type'] for d in divergences)),
}
with open(Path(ANALYSIS_DIR)/'summary.json', 'w') as f: json.dump(summary, f, indent=2)
print(f"Summary saved. Total cost: check Together.ai dashboard.")
print(f"All outputs in: {ANALYSIS_DIR}")
