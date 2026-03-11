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

## Current included artifacts

The repository preserves the original project outputs, including:
- Kimi K2.5 raw runs and parsed analyses
- Llama 3.1 8B raw runs and parsed analyses
- v1 and v2 world-model reports
- the draft manuscript and a plain-text export for quick browsing

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
