#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
KG1 Single-Model Run — Colab Runner
====================================
Full battery (88 vignettes x 30 runs x 2 phases) on llama-3.1-8b.
Estimated cost: ~$1.33 | Estimated time: 30-60 minutes.

Setup:
1. Upload to Google Drive /KG1_study/:
   - vignette_battery.json
   - llm_query_runner.py
   - response_parser.py
2. Add TOGETHER_API_KEY to Colab Secrets (Settings > Secrets)
3. Run cells in order. Safe to interrupt and resume.

## In Colab: File -> Upload notebook -> select this .py file
"""

# %% [markdown]
# # KG1 Single-Model Pilot: llama-3.1-8b
# **Full battery**: 88 vignettes x 30 runs x 2 phases = 5,280 API calls
# **Estimated cost**: ~$1.33 | **Estimated time**: 30-60 min
#
# Checkpoints after every response — safe to interrupt and resume.

# %% Cell 1: Setup & File Loading
import os, sys, json, shutil
from pathlib import Path

# Mount Google Drive
from google.colab import drive, userdata
drive.mount('/content/drive')

# Project paths
PROJECT = Path('/content/drive/MyDrive/KG1_study')
PROJECT.mkdir(parents=True, exist_ok=True)
WORK = Path('/content/kg1_work')
WORK.mkdir(exist_ok=True)

# Copy pipeline files from Drive to working directory
required_files = ['vignette_battery.json', 'llm_query_runner.py', 'response_parser.py']
for f in required_files:
    src = PROJECT / f
    if src.exists():
        shutil.copy2(src, WORK / f)
        print(f"  + {f}")
    else:
        print(f"  MISSING: {f} — upload it to Google Drive /KG1_study/")

sys.path.insert(0, str(WORK))

# Load API key from Colab Secrets
os.environ['TOGETHER_API_KEY'] = userdata.get('TOGETHER_API_KEY')
print("  + API key loaded")

# Install scipy (needed for Fisher's exact test in analysis)
import subprocess
subprocess.check_call([sys.executable, "-m", "pip", "install", "-q", "scipy"])
print("  + scipy installed")

# %% Cell 2: Verify Battery
from causal_llm_eval.llm_query_runner import load_battery, MODEL_REGISTRY

BATTERY = str(WORK / 'vignette_battery.json')
items = load_battery(BATTERY)
baselines = [i for i in items if i['type'] == 'baseline']
perts = [i for i in items if i['type'] != 'baseline']
print(f"Battery: {len(items)} items ({len(baselines)} baselines, {len(perts)} perturbations)")
print(f"Families: {len(set(i['family'] for i in items))}")

cfg = MODEL_REGISTRY['llama-3.1-8b']
print(f"\nModel: llama-3.1-8b")
print(f"  API ID: {cfg['model_id']}")
print(f"  Temperature: {cfg['temperature']}")
print(f"  Max tokens: {cfg['max_tokens']}")
print(f"  Price: ${cfg['price_in']}/M in, ${cfg['price_out']}/M out")
print(f"\n88 items x 30 runs x 2 phases = 5,280 API calls")
print(f"Estimated cost: ~$1.33")

# %% Cell 3: Run Full Battery
from causal_llm_eval.llm_query_runner import run_battery

RESULTS_DIR = str(PROJECT / 'results')
print("Starting full battery run...")
print("=" * 60)

checkpoint = run_battery(
    battery_path=BATTERY,
    model_names=["llama-3.1-8b"],
    n_runs=30,
    item_filter=None,       # all 88 items
    output_dir=RESULTS_DIR,
    dry_run=False,
)

print(f"\nCheckpoint file: {checkpoint}")

# %% Cell 4: Parse & Analyse
from causal_llm_eval.response_parser import run_analysis

# Find the latest results file
results_dir = Path(RESULTS_DIR)
results_files = sorted(results_dir.glob('run_*.jsonl'))
if not results_files:
    print("ERROR: No results files found. Run Cell 3 first.")
else:
    latest = str(results_files[-1])
    print(f"Analysing: {latest}")

    ANALYSIS_DIR = str(PROJECT / 'analysis')
    metrics, kg2, edge_tests, divergences = run_analysis(latest, BATTERY, ANALYSIS_DIR)

    print("\n" + "=" * 60)
    print("RESULTS SUMMARY")
    print("=" * 60)
    for mn, m in sorted(metrics.items()):
        print(f"\n  {mn}:")
        print(f"    Recommendation accuracy: {m['rec_accuracy']:.1%}")
        print(f"    Exclusion accuracy:      {m['exc_accuracy']:.1%}")
        print(f"    Recommendation precision: {m['rec_precision']:.1%}")
        if m.get('cond_rate') is not None:
            print(f"    Conditionality rate:     {m['cond_rate']:.1%}")
        if m.get('unc_rate') is not None:
            print(f"    Uncertainty rate:         {m['unc_rate']:.1%}")
        if m.get('null_spec') is not None:
            print(f"    Null specificity:         {m['null_spec']:.1%}")

    if edge_tests:
        sig = sum(1 for t in edge_tests if t.get('significant'))
        print(f"\n  Edge tests: {len(edge_tests)} total, {sig} significant (BH-FDR q=0.05)")

    from collections import Counter
    if divergences:
        by_type = Counter(d['divergence_type'] for d in divergences)
        print(f"\n  Divergences: {dict(by_type)}")

# %% Cell 5: Visualise
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

if 'metrics' in dir() and metrics:
    models = sorted(metrics.keys())

    # Plot 1: Aggregate Performance Bar Chart
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    for idx, (key, label) in enumerate([
        ('rec_accuracy', 'Recommendation\nAccuracy'),
        ('exc_accuracy', 'Exclusion\nAccuracy'),
        ('rec_precision', 'Recommendation\nPrecision'),
    ]):
        ax = axes[idx]
        vals = [metrics[m][key] for m in models]
        colors = ['#4C72B0']
        bars = ax.bar(range(len(models)), vals, color=colors)
        ax.set_xticks(range(len(models)))
        ax.set_xticklabels(models, rotation=45, ha='right', fontsize=9)
        ax.set_ylabel(label)
        ax.set_ylim(0, 1.05)
        ax.axhline(1.0, color='gray', ls='--', alpha=0.3)
        for b, v in zip(bars, vals):
            ax.text(b.get_x() + b.get_width()/2, v + 0.02, f'{v:.0%}', ha='center', fontsize=10)
    fig.suptitle('llama-3.1-8b: Aggregate Performance on KG1 Battery', fontweight='bold')
    plt.tight_layout()
    plt.savefig(str(Path(ANALYSIS_DIR) / 'agg_perf.png'), dpi=150, bbox_inches='tight')
    plt.show()
    print("Saved: agg_perf.png")

    # Plot 2: Edge Detection Heatmap
    if kg2:
        all_e = sorted(set(e for me in kg2.values() for e in me))
        ms = sorted(kg2.keys())
        if all_e and ms:
            mat = np.zeros((len(all_e), len(ms)))
            for j, m in enumerate(ms):
                for i, e in enumerate(all_e):
                    if e in kg2[m]:
                        mat[i, j] = kg2[m][e]['detection_rate']

            fig, ax = plt.subplots(figsize=(6, max(8, len(all_e) * 0.35)))
            im = ax.imshow(mat, cmap='RdYlGn', aspect='auto', vmin=0, vmax=1)
            ax.set_xticks(range(len(ms)))
            ax.set_xticklabels(ms, rotation=45, ha='right', fontsize=9)
            ax.set_yticks(range(len(all_e)))
            ax.set_yticklabels(all_e, fontsize=7)
            ax.set_title('KG2 Edge Detection Rate: llama-3.1-8b', fontweight='bold')
            plt.colorbar(im, ax=ax, label='Detection Rate', shrink=0.6)
            for i in range(len(all_e)):
                for j in range(len(ms)):
                    v = mat[i, j]
                    c = 'white' if v < 0.4 or v > 0.8 else 'black'
                    ax.text(j, i, f'{v:.0%}', ha='center', va='center', fontsize=7, color=c)
            plt.tight_layout()
            plt.savefig(str(Path(ANALYSIS_DIR) / 'edge_heatmap.png'), dpi=150, bbox_inches='tight')
            plt.show()
            print("Saved: edge_heatmap.png")

    # Plot 3: JSD Distribution
    if edge_tests:
        fig, ax = plt.subplots(figsize=(10, 5))
        jsds = [t['jsd'] for t in edge_tests if t.get('jsd', 0) > 0]
        if jsds:
            ax.hist(jsds, bins=30, color='#4C72B0', alpha=0.8, edgecolor='white')
            ax.axvline(np.median(jsds), color='red', ls='--', label=f'Median: {np.median(jsds):.3f}')
            ax.set_xlabel('Jensen-Shannon Divergence')
            ax.set_ylabel('Count')
            ax.set_title('Edge Weight Distribution (JSD: baseline vs perturbation)', fontweight='bold')
            ax.legend()
        plt.tight_layout()
        plt.savefig(str(Path(ANALYSIS_DIR) / 'jsd_dist.png'), dpi=150, bbox_inches='tight')
        plt.show()
        print("Saved: jsd_dist.png")

    print(f"\nAll outputs saved to: {ANALYSIS_DIR}")
else:
    print("No metrics available. Run Cell 4 first.")

# %% Cell 6: Detailed Divergence Report
from collections import defaultdict

if 'divergences' in dir() and divergences:
    print("=" * 60)
    print("DIVERGENCE TAXONOMY — llama-3.1-8b")
    print("=" * 60)

    by_type = Counter(d['divergence_type'] for d in divergences)
    for dt, n in by_type.most_common():
        print(f"\n  {dt}: {n} instances")
        for d in [x for x in divergences if x['divergence_type'] == dt][:5]:
            print(f"    - {d['pert_id']}: {d['detail']}")

    if edge_tests:
        print("\n\nMost-missed edges:")
        missed = defaultdict(int)
        tested = defaultdict(int)
        for t in edge_tests:
            for e in t['edges']:
                tested[e] += 1
                if not t.get('significant', False):
                    missed[e] += 1
        for e, n in sorted(missed.items(), key=lambda x: -x[1])[:15]:
            print(f"    {e}: missed {n}/{tested[e]} ({n/tested[e]:.0%})")
else:
    print("No divergence data. Run Cell 4 first.")

# %% Cell 7: Quick Sanity Check — Sample Responses
if 'latest' in dir():
    print("=" * 60)
    print("SAMPLE RESPONSES (first 3 items)")
    print("=" * 60)
    with open(latest) as f:
        seen_items = set()
        for line in f:
            if line.strip():
                r = json.loads(line)
                if r['item_id'] not in seen_items and r.get('error') is None and r['run_idx'] == 0:
                    seen_items.add(r['item_id'])
                    print(f"\n--- {r['item_id']} (run 0) ---")
                    p1 = (r.get('phase1_response') or '')[:500]
                    print(f"Phase 1 (first 500 chars):\n{p1}")
                    if len(seen_items) >= 3:
                        break
