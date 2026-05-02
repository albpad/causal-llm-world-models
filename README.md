# Behavioral Causal Discovery for LLM Clinical Adaptation

This repository is the public replication package for the NEJM AI submission:

**Do Large Language Models Adapt Treatment Recommendations When Clinical Cases Change? A Behavioral Causal Discovery Study in Laryngeal Cancer**

It contains the benchmark, raw model outputs, analysis code, parser, validation artifacts, final result tables, and publication figure assets needed to reproduce the analyses reported in the article. It intentionally excludes manuscript `.docx` files, prior manuscript versions, private submission-package materials, API keys, and ad hoc development outputs.

## Public Scope

Included:

- Final counterfactual vignette battery: `88` items (`12` baselines and `76` perturbations).
- Locked KG1 benchmark artifacts: `60` statement-linked treatment rules represented as `58` evaluation edges.
- Canonical six-model raw output dataset: `7,920` rows (`88` vignettes x `15` runs/model x `6` models).
- Deterministic parser and parser-validation artifacts.
- KG2 graph-recovery, domain-metric, threshold-sensitivity, bootstrap-CI, family-stratified, and risk-weighted-fidelity outputs.
- Publication figures and source tables.
- Minimal scripts and tests required to rerun the analysis stack.

Excluded:

- Manuscript files, tracked edits, and prior manuscript versions.
- API keys, local environment files, and user-specific credentials.
- Provider smoke tests, temporary analysis directories, and superseded intermediate outputs.
- Private editorial notes and submission-package-only documents.

## Repository Layout

```text
causal-llm-world-models/
├── data/vignettes/
│   ├── vignette_battery.json
│   └── vignette_battery.md
├── docs/review/
│   ├── final_benchmark_lock/
│   ├── kg1_full_review/
│   └── ontology_validation_sheet/
├── publication/
│   ├── figure_data/
│   └── figures/
├── results/
│   ├── raw/article_models_6_h15/
│   ├── kg1_extraction/ferrari_pdf/
│   ├── analysis/article-metrics-6models-gemma4/
│   ├── parser_validation/article-metrics-6models-gemma4/
│   └── world_model/
│       ├── article-metrics-6models-gemma4/
│       ├── domain-metrics-6models-gemma4/
│       └── v2/article-metrics-6models-gemma4/
├── scripts/
├── src/causal_llm_eval/
└── tests/
```

## Primary Artifacts

- Vignette battery: `data/vignettes/vignette_battery.json`
- Benchmark lock: `docs/review/final_benchmark_lock/`
- KG1 review tables: `docs/review/kg1_full_review/`
- KG1 ontology validation sheet: `docs/review/ontology_validation_sheet/`
- Canonical raw model outputs: `results/raw/article_models_6_h15/run_20260410_h15_6models.jsonl`
- Parsed outputs and graph recovery: `results/analysis/article-metrics-6models-gemma4/`
- Parser validation: `results/parser_validation/article-metrics-6models-gemma4/`
- Primary domain metrics: `results/world_model/domain-metrics-6models-gemma4/`
- Auxiliary graph/stability metrics: `results/world_model/article-metrics-6models-gemma4/` and `results/world_model/v2/article-metrics-6models-gemma4/`
- Publication figure assets: `publication/figures/`
- Figure source tables: `publication/figure_data/`

## Reproducing the Article Analyses

Create an environment:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -e .[dev]
```

Run the tests:

```bash
pytest -q
```

Rebuild the full six-model analysis stack from the canonical raw outputs:

```bash
python scripts/run_full_stack.py \
  --results results/raw/article_models_6_h15/run_20260410_h15_6models.jsonl \
  --battery data/vignettes/vignette_battery.json \
  --analysis-outdir results/analysis/article-metrics-6models-gemma4 \
  --parser-outdir results/parser_validation/article-metrics-6models-gemma4 \
  --world-model-outdir results/world_model/article-metrics-6models-gemma4 \
  --world-model-v2-outdir results/world_model/v2/article-metrics-6models-gemma4 \
  --domain-outdir results/world_model/domain-metrics-6models-gemma4 \
  --figure-outdir publication/figures/supplementary
```

Rebuild query-setting and run-count sensitivity outputs:

```bash
python scripts/build_query_settings_and_run_sensitivity.py \
  --raw-results results/raw/article_models_6_h15/run_20260410_h15_6models.jsonl \
  --parsed results/analysis/article-metrics-6models-gemma4/parsed.json \
  --battery data/vignettes/vignette_battery.json \
  --outdir results/world_model/domain-metrics-6models-gemma4 \
  --figure-outdir publication/figures/supplementary
```

Regenerate compact source tables for the public figure assets:

```bash
python scripts/build_publication_figures_6models.py
```

The deterministic KG1 extraction utility is retained for auditability. The source article PDF is not redistributed in this repository; users should obtain it from the publisher or institutional access if they wish to rerun PDF extraction:

```bash
causal-llm-extract-kg1 \
  --pdf /path/to/ferrari_delphi_consensus.pdf \
  --outdir results/kg1_extraction/ferrari_pdf
```

## Study Summary

- Vignettes: `88`
- Baselines: `12`
- Perturbations: `76`
- Statement-linked treatment rules: `60`
- Evaluation edges: `58`
- Models: `6`
- Runs per vignette per model: `15`
- Canonical rows: `7,920`
- Primary domains: Coverage, Fidelity, Discriminability
- Auxiliary domain: Stability, interpreted conditionally on coverage

No composite score is used for primary interpretation.

## Data and Compliance Notes

The dataset is semi-synthetic and contains no patient-level records or protected health information. Raw model outputs are retained because they are required for exact replication of the parser, graph-recovery, and domain-metric analyses. Rerunning model inference requires the user's own Together.ai-compatible API credentials and may not reproduce identical outputs if provider endpoints change.

NEJM AI emphasizes freely available benchmark datasets and protocols for medical-AI evaluation. The repository therefore prioritizes the data, code, and audit artifacts needed to inspect and reproduce the reported benchmark rather than manuscript drafting files.
