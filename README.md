# Behavioural Causal Discovery for LLM Evaluation

Production-ready repository for a research project that tests whether large language models express a coherent **implicit causal world model** in head-and-neck oncology decision making.

The project builds a structured vignette battery, probes models under controlled perturbations, reconstructs a behavioural graph (KG2), and compares it against an expert-derived reference graph (KG1).

## What is in the repo

- **Vignette battery generation** for baseline and perturbation cases
- **Model querying** through Together.ai-compatible chat completions
- **Response parsing** into treatment stances and exclusions
- **Graph reconstruction** and KG1↔KG2 comparison
- **World-model scoring** with the revised v2 framework
- **Synthetic fine-tuning data generation** from observed failure modes
- **Manuscript materials** and preserved result artifacts

## Repository layout

```text
causal-llm-world-models-production/
├── src/causal_llm_eval/          # installable Python package
├── data/
│   ├── vignettes/                # vignette battery and markdown rendering
│   └── finetuning/               # dataset-generation helpers and templates
├── results/
│   ├── raw/                      # raw JSONL model outputs
│   ├── analysis/                 # parsed and graph-level analyses
│   └── world_model/              # v1/v2 world-model metrics
├── notebooks/                    # original exploratory notebooks
├── scripts/                      # convenience entrypoints and colab helpers
├── tests/                        # smoke and package tests
├── docs/                         # methods, notes, publishing guide
├── manuscript/                   # draft article and text export
├── .github/workflows/            # CI
└── configs/                      # example environment files
```

## Quick start

### 1) Create an environment

```bash
python -m venv .venv
source .venv/bin/activate
pip install -U pip
pip install -e .[dev]
```

### 2) Configure the API key

```bash
cp configs/.env.example .env
export TOGETHER_API_KEY=your_key_here
```

### 3) Run tests

```bash
pytest
```

### 4) Query a model

```bash
python -m causal_llm_eval.llm_query_runner       --battery data/vignettes/vignette_battery.json       --runs 1       --models kimi-k2.5       --outdir results/raw/kimi-k2.5
```

### 5) Parse and score

```bash
python -m causal_llm_eval.response_parser       --results results/raw/kimi-k2.5/run_YYYYMMDD_HHMM.jsonl       --battery data/vignettes/vignette_battery.json       --outdir results/analysis/kimi-k2.5
```

### 6) Compute world-model metrics

```bash
python -m causal_llm_eval.world_model_metrics_v2       --analysis-dir results/analysis/kimi-k2.5       --outdir results/world_model/v2
```

### 7) Run the research app

The notebooks can be replaced by a single application entrypoint with presets for the main experiment variants:

```bash
causal-llm-research --preset full-study
causal-llm-research --preset single-model --items A1-BASE,A1-P1,A1-P2,A1-NULL1
python scripts/colab_kimi_k25.py --skip-query --results-file results_kimi_k25/run_YYYYMMDD_HHMM.jsonl
```

### 8) Launch the clinician review app

This starts a local browser UI for reviewing automatic parsing, graph edges, and model-level evaluation artifacts:

```bash
python scripts/review_app.py
```

Then open `http://127.0.0.1:8765`.

## Current included artifacts

The repository preserves the original project outputs, including:
- Kimi K2.5 raw runs and parsed analyses
- Llama 3.1 8B raw runs and parsed analyses
- v1 and v2 world-model reports
- the draft manuscript and a plain-text export for quick browsing

## Current article-facing results

The final manuscript-facing comparison now uses the harmonised five-model 15-run dataset under:

- `results/raw/article_models_5_h15/run_20260316_h15_5models.jsonl`
- `results/analysis/article-metrics-5models/`
- `results/world_model/article-metrics-5models/world_model_report.md`
- `results/world_model/article-metrics-5models/world_model_metrics.json`

Key metrics used in the article:

| Model | Soft recall | Hard recall | Direction accuracy | SID | Mean causal JSD | Mean null JSD | SNR | Detection power |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Kimi K2.5 | 74.1% (43/58) | 6.9% (4/58) | 50.0% | 41/246 (16.7%) | 0.187 | 0.076 | 2.46 | 20.7% |
| DeepSeek-R1 | 62.1% (36/58) | 10.3% (6/58) | 66.7% | 34/243 (14.0%) | 0.154 | 0.072 | 2.14 | 17.3% |
| Mistral-Small-24B | 43.1% (25/58) | 1.7% (1/58) | 0.0% | 31/236 (13.1%) | 0.116 | 0.070 | 1.66 | 13.1% |
| Qwen3-Next-80B-A3B-Instruct | 39.7% (23/58) | 1.7% (1/58) | 0.0% | 32/237 (13.5%) | 0.103 | 0.055 | 1.87 | 15.6% |
| Llama 3.1-8B | 17.2% (10/58) | 0.0% (0/58) | 0.0% | 45/233 (19.3%) | 0.059 | 0.074 | 0.80 | 2.6% |

Use these article-facing outputs for manuscript text, tables, and figures. The `results/world_model/v2/` artifacts remain useful for the newer composite scoring framework, but they are not the primary results cited in the manuscript.

## Production-readiness improvements in this version

- installable `src/` package structure
- package-relative data path helpers
- CI workflow for smoke tests
- cleaner tests based on `pytest`
- convenience scripts and `.env` example
- improved `README` with reproducible commands
- removed local cache artifacts and macOS metadata

## Notes before public release

- Review whether raw results should remain in Git or move to Git LFS / releases.
- Add your preferred license before publishing publicly.
- Check the manuscript and results for any content you do not want in a public repo.
