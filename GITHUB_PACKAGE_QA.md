# GitHub Package QA

Date: 2026-05-01

## Scope Check

- Manuscript `.docx` files: excluded.
- Prior manuscript versions: excluded.
- Private submission-package materials: excluded.
- API keys and credentials: excluded.
- Temporary analysis directories: excluded.
- Provider smoke-test outputs: excluded.
- Superseded intermediate result stacks: excluded.

## Canonical Dataset Check

- Raw file: `results/raw/article_models_6_h15/run_20260410_h15_6models.jsonl`
- Rows: `7,920`
- Models: `6`
- Vignettes: `88`
- Runs per vignette per model: `15`
- Model-output errors in retained raw file: `0`

## Benchmark Check

- Baselines: `12`
- Perturbations: `76`
- Total vignette items: `88`
- Statement-linked treatment rules: `60`
- Evaluation edges: `58`

## Public Text Check

The public docs and retained result artifacts were checked for excluded composite-score language, evaluation-layer language, stale model-count framing, and parser-validation wording that was removed from the manuscript. No retained public artifact contains those excluded terms.

## Secret Scan

The repository was scanned for the known Together.ai key patterns used during development and common API-token patterns. No publishable file contained those secrets.

## Test Check

```text
22 passed in 0.64s
```

## Notes

The full analysis stack can regenerate the article-facing outputs from the retained raw JSONL. Legacy composite artifacts are removed by `scripts/run_full_stack.py` after component metrics are generated, because the article interprets Coverage, Fidelity, and Discriminability rather than a composite score.
