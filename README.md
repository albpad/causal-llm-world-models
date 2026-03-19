# Behavioural Causal Discovery for LLM Evaluation

This repository is the **clean publication package** for the final NEJM AI submission. It contains only the benchmark, code, figures, tests, and audited result artifacts needed to inspect or reproduce the analyses reported in the manuscript. It intentionally **does not** include the manuscript files or prior manuscript versions.

## Included scope

- final benchmark battery and KG1 traceability materials
- canonical five-model raw dataset used for the paper
- final parser-validation package
- final graph-comparison outputs
- final domain-based evaluation outputs
- final publication figure assets and figure source tables
- analysis code and focused tests required to audit the published results

## Repository layout

```text
causal-llm-world-models/
├── data/vignettes/
│   ├── vignette_battery.json
│   └── vignette_battery.md
├── docs/review/final_benchmark_lock/
│   ├── benchmark_audit_summary.json
│   ├── kg1_traceability_matrix.csv
│   ├── vignette_integrity_report.md
│   └── kg1_final_benchmark_review.html
├── publication/
│   ├── figure_data/
│   └── figures/
├── results/
│   ├── raw/article_models_5_h15/
│   ├── analysis/article-metrics-5models-final/
│   ├── parser_validation/article-metrics-5models-final/
│   ├── world_model/domain-metrics-5models-final/
│   └── world_model/v2/article-metrics-5models-final/
├── scripts/
│   ├── run_analysis.py
│   └── build_supplementary_evaluation.py
├── src/causal_llm_eval/
└── tests/
```

## Audit map

The manuscript-referenced artifacts map to the repository as follows:

- **Final vignette battery:** [data/vignettes/vignette_battery.json](/Users/albertopaderno/Desktop/github%20LLM/causal-llm-world-models/data/vignettes/vignette_battery.json)
- **Final benchmark audit:** [docs/review/final_benchmark_lock](/Users/albertopaderno/Desktop/github%20LLM/causal-llm-world-models/docs/review/final_benchmark_lock)
- **Canonical five-model raw dataset:** [results/raw/article_models_5_h15/run_20260316_h15_5models.jsonl](/Users/albertopaderno/Desktop/github%20LLM/causal-llm-world-models/results/raw/article_models_5_h15/run_20260316_h15_5models.jsonl)
- **Final graph analysis:** [results/analysis/article-metrics-5models-final](/Users/albertopaderno/Desktop/github%20LLM/causal-llm-world-models/results/analysis/article-metrics-5models-final)
- **Final parser validation:** [results/parser_validation/article-metrics-5models-final](/Users/albertopaderno/Desktop/github%20LLM/causal-llm-world-models/results/parser_validation/article-metrics-5models-final)
- **Primary domain-based evaluation:** [results/world_model/domain-metrics-5models-final](/Users/albertopaderno/Desktop/github%20LLM/causal-llm-world-models/results/world_model/domain-metrics-5models-final)
- **Auxiliary corrected stability decomposition:** [results/world_model/v2/article-metrics-5models-final](/Users/albertopaderno/Desktop/github%20LLM/causal-llm-world-models/results/world_model/v2/article-metrics-5models-final)
- **Publication figures and source tables:** [publication](/Users/albertopaderno/Desktop/github%20LLM/causal-llm-world-models/publication)

## Reproducing the published analyses

Create an environment:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -U pip
pip install -e .
```

Run the retained tests:

```bash
pytest -q
```

Rebuild the final graph analysis from the canonical raw dataset:

```bash
python scripts/run_analysis.py \
  --results results/raw/article_models_5_h15/run_20260316_h15_5models.jsonl \
  --battery data/vignettes/vignette_battery.json \
  --outdir results/analysis/article-metrics-5models-final
```

The cleaned repository already retains the frozen supplementary outputs under [results/world_model/domain-metrics-5models-final](/Users/albertopaderno/Desktop/github%20LLM/causal-llm-world-models/results/world_model/domain-metrics-5models-final) and the publication-ready figures under [publication/figures](/Users/albertopaderno/Desktop/github%20LLM/causal-llm-world-models/publication/figures).

## Final study summary

- `12` baselines and `76` perturbations (`88` total items)
- `60` statement-linked treatment rules and `58` evaluation edges
- `5` models, `15` runs per model, `6,600` vignette-run combinations
- primary interpretation based on **Coverage**, **Fidelity**, and **Discriminability**
- **Stability** retained only as an auxiliary reproducibility domain

No composite manuscript index is used in this publication package. The intended primary readout is [domain_summary.md](/Users/albertopaderno/Desktop/github%20LLM/causal-llm-world-models/results/world_model/domain-metrics-5models-final/domain_summary.md), with threshold sensitivity, family-stratified analysis, bootstrap confidence intervals, and risk-weighted fidelity reported as supplementary analyses in the same directory.
