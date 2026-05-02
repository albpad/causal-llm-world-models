# Data and Code Availability

This repository provides the data and code needed to reproduce the analyses reported in the article.

## Available Data

- Counterfactual vignette battery: `data/vignettes/vignette_battery.json`
- Benchmark review and traceability artifacts: `docs/review/`
- Canonical raw model outputs: `results/raw/article_models_6_h15/run_20260410_h15_6models.jsonl`
- Parsed responses, edge tests, and recovered graphs: `results/analysis/article-metrics-6models-gemma4/`
- Parser-validation outputs: `results/parser_validation/article-metrics-6models-gemma4/`
- Domain metrics, threshold sensitivity, bootstrap confidence intervals, family-stratified analysis, and risk-weighted fidelity: `results/world_model/domain-metrics-6models-gemma4/`
- Publication figure assets and source tables: `publication/`

## Data Not Included

- No patient-level data are included.
- No protected health information is included.
- No manuscript `.docx` files, prior manuscript versions, private editorial notes, or submission-system materials are included.
- No Together.ai API keys or other credentials are included.
- The Ferrari et al. source PDF used for deterministic KG1 extraction is not redistributed; users should obtain the source article through the publisher or institutional access.

## Reuse Boundary

The retained raw model outputs are sufficient for exact replication of the parser, graph-recovery, and article-facing metric analyses. Rerunning model inference is possible with the included query runner, but endpoint behavior may change over time and may not reproduce identical text outputs.

## Compliance Statement

The study used semi-synthetic vignettes and model-generated text. It did not enroll patients, use patient records, or process protected health information. The repository is designed to support transparent computational replication of the reported benchmark while excluding private manuscript files and credentials.
