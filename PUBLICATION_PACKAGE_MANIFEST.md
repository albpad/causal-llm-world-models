# Public GitHub Package Manifest

This manifest defines the intended public repository contents for the NEJM AI replication package.

## Retained for Replication

- `README.md`: repository overview and reproduction commands.
- `DATA_AND_CODE_AVAILABILITY.md`: data/code availability and compliance boundary.
- `GITHUB_PACKAGE_QA.md`: final public-package QA checks.
- `pyproject.toml`, `requirements.txt`: minimal runtime and test dependencies.
- `.github/workflows/tests.yml`: public CI smoke-test workflow.
- `data/vignettes/`: locked vignette battery.
- `docs/review/final_benchmark_lock/`: benchmark integrity and traceability artifacts.
- `docs/review/kg1_full_review/`: KG1 edge, family, treatment-rule, baseline, and perturbation review tables.
- `docs/review/ontology_validation_sheet/`: clinician-readable ontology validation sheet.
- `results/raw/article_models_6_h15/run_20260410_h15_6models.jsonl`: canonical six-model raw output dataset.
- `results/kg1_extraction/ferrari_pdf/`: deterministic KG1 extraction and benchmark-alignment outputs.
- `results/analysis/article-metrics-6models-gemma4/`: parsed responses, edge tests, KG2 outputs, and graph-comparison artifacts.
- `results/parser_validation/article-metrics-6models-gemma4/`: parser-validation report and examples.
- `results/world_model/article-metrics-6models-gemma4/`: base world-model metric components used by supplementary analyses.
- `results/world_model/v2/article-metrics-6models-gemma4/`: auxiliary corrected stability outputs.
- `results/world_model/domain-metrics-6models-gemma4/`: final article-facing Coverage, Fidelity, Discriminability, sensitivity, uncertainty, family, and risk-weighted outputs.
- `publication/`: final non-manuscript figure assets and figure source tables.
- `scripts/`: analysis, figure, benchmark-review, and reproducibility builders.
- `src/causal_llm_eval/`: importable analysis package.
- `tests/`: focused reproducibility and regression tests.

## Excluded from Public GitHub

- Manuscript `.docx` files and historical manuscript versions.
- Private submission-package materials.
- API keys, `.env` files, and local credentials.
- Temporary result directories.
- Superseded intermediate result stacks.
- Provider smoke-test outputs.
- Python bytecode, pytest caches, and OS metadata files.
- Manuscript-editing utility scripts that modify local Word documents.

## Canonical Article Dataset

- Vignettes: `88`
- Models: `6`
- Runs per vignette per model: `15`
- Raw rows: `7,920`
- Raw file: `results/raw/article_models_6_h15/run_20260410_h15_6models.jsonl`

## Required Reproduction Entry Point

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
