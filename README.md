# Behavioural Causal Discovery for LLM Evaluation

Production-ready repository for a research project that tests whether large language models express a coherent **implicit causal world model** in head-and-neck oncology decision making.

The project builds a structured vignette battery, probes models under controlled perturbations, reconstructs a behavioural graph (KG2), and compares it against an expert-derived reference graph (KG1).

## What is in the repo

- **Vignette battery generation** for baseline and perturbation cases
- **Model querying** through Together.ai-compatible chat completions
- **Response parsing** into treatment stances and exclusions
- **Graph reconstruction** and KG1↔KG2 comparison
- **Domain-based evaluation** using Coverage, Fidelity, Discriminability, and auxiliary Stability
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
│   └── world_model/              # domain metrics and auxiliary legacy outputs
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

### 6) Build the domain-based evaluation package

```bash
python -m causal_llm_eval.world_model_metrics       --analysis-dir results/analysis/kimi-k2.5       --outdir results/world_model/kimi-k2.5
python -m causal_llm_eval.world_model_metrics_v2       --analysis-dir results/analysis/kimi-k2.5       --outdir results/world_model/v2/kimi-k2.5
PYTHONPATH=src python scripts/build_supplementary_evaluation.py       --analysis-dir results/analysis/kimi-k2.5       --world-model-dir results/world_model/kimi-k2.5       --world-model-v2-dir results/world_model/v2/kimi-k2.5       --battery data/vignettes/vignette_battery.json       --outdir results/world_model/domain-metrics/kimi-k2.5
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

The repository preserves the original exploratory outputs and the final locked study package, including:
- benchmark review artifacts for the final KG1/vignette battery
- parser-validation artifacts for the final five-model study
- harmonised raw outputs for the canonical 15-run comparison
- base and enhanced graph analyses
- article-facing domain-metric summaries plus auxiliary stability decomposition
- the manuscript draft and plain-text export

## Current article-facing results

The final manuscript-facing comparison uses the harmonised five-model 15-run dataset under:

- `results/raw/article_models_5_h15/run_20260316_h15_5models.jsonl`
- `docs/review/final_benchmark_lock/`
- `results/parser_validation/article-metrics-5models-final/`
- `results/analysis/article-metrics-5models-final/`
- `results/world_model/domain-metrics-5models-final/domain_summary.md`
- `results/world_model/domain-metrics-5models-final/threshold_sensitivity_report.md`
- `results/world_model/domain-metrics-5models-final/family_stratified_report.md`
- `results/world_model/domain-metrics-5models-final/risk_weighted_fidelity.md`

The final benchmark audit confirms:
- `12` baselines and `76` perturbations (`88` total items)
- `60` statement-linked treatment rules and `58` evaluation edges
- `0` missing non-null source traceability items
- `0` null-control drift items
- `0` staging inconsistency warnings

The remaining benchmark caveat is query-space undercoverage in some family-specific structured menus. The benchmark is source-clean and clinically coherent, but certain concrete labels are under-probed in the Phase 2 menus, so the final interpretation relies on both Phase 1 open-ended recommendations and deterministic aggregate-label derivation.

The final parser-validation package shows:
- deterministic gold-template validation: `98.9%` exact match
- structured snippet validation: `100%` exact match
- real-output mismatch audit dominated by model disagreement and query-space effects, not widespread parser failure

Primary manuscript-facing metrics:

| Model | Soft recall | Soft precision | Soft FDR | Soft dir. acc. | SID rate | SNR | Detection power | Veridical split-half | Regime |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| DeepSeek-R1 | 62.1% | 60.0% | 40.0% | 77.8% | 14.0% | 2.14 | 17.3% | 78.2% | balanced |
| Kimi K2.5 | 74.1% | 66.2% | 33.8% | 67.4% | 16.7% | 2.46 | 20.7% | 49.2% | broad but noisy |
| Qwen3-Next-80B-A3B-Instruct | 39.7% | 53.5% | 46.5% | 73.9% | 13.5% | 1.87 | 15.6% | 90.9% | partial and brittle |
| Mistral-Small-24B | 43.1% | 62.5% | 37.5% | 72.0% | 13.1% | 1.66 | 13.1% | 83.1% | partial and brittle |
| Llama 3.1-8B | 17.2% | 71.4% | 28.6% | 50.0% | 19.3% | 0.80 | 2.6% | 62.4% | fragmentary |

Primary interpretation should rely on the domain metrics above, not on a single composite index. In particular:

- Kimi K2.5 has the broadest recovered graph and the strongest signal-to-noise separation.
- DeepSeek-R1 has the strongest fidelity-balanced profile once direction control, SID, and auxiliary stability are interpreted jointly.
- Qwen3-Next-80B-A3B-Instruct and Mistral-Small-24B recover partial but brittle structure.
- Llama 3.1-8B remains fragmentary despite superficially favorable conditional precision on a sparse graph.

The main supplementary upgrades now included in the repo are:
- threshold sensitivity for soft and hard detection thresholds
- bootstrap confidence intervals for the primary manuscript metrics
- family-stratified analysis across the 10 clinical families
- clinically weighted fidelity analyses that treat total-laryngectomy-related errors as highest risk

Use the `article-metrics-5models-final` directories for manuscript text, tables, and figures. The earlier `article-metrics-5models` outputs remain preserved as intermediate artifacts and should not be treated as the final manuscript lock.

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
