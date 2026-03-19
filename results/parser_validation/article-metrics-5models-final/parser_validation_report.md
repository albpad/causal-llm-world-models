# Parser Validation Report

## Overview
- Results file: `results/raw/article_models_5_h15/run_20260316_h15_5models.jsonl`
- Battery file: `data/vignettes/vignette_battery.json`
- Annotations file: `none`

## 1. Battery Alignment on Real Model Outputs
This section is **not** pure parser accuracy. It measures alignment between parsed model outputs and battery expectations, so disagreement can come from query-space gaps, model omissions, or true parser misses.
- Rows evaluated: `6600`
- Exact match rate: `1.0%`
- `recommended`: precision `59.1%` recall `62.2%` f1 `60.6%`
- `excluded`: precision `19.7%` recall `49.8%` f1 `28.2%`
- `relative_ci`: insufficient support
- `uncertain`: insufficient support

## 2. Consensus Alignment Across Runs
- Case/model groups: `440`
- Exact match rate: `0.2%`
- `recommended`: precision `50.2%` recall `72.6%` f1 `59.4%`
- `excluded`: precision `15.1%` recall `55.1%` f1 `23.7%`
- `relative_ci`: insufficient support
- `uncertain`: insufficient support

## 3. Deterministic Gold-Template Validation
- Cases evaluated: `88`
- Exact match rate: `98.9%`
- `recommended`: precision `100.0%` recall `100.0%` f1 `100.0%`
- `excluded`: precision `100.0%` recall `100.0%` f1 `100.0%`
- `relative_ci`: insufficient support
- `uncertain`: insufficient support

## 4. Structured Label Validation
- Snippets evaluated: `68`
- Exact match rate: `100.0%`
- `recommended`: precision `100.0%` recall `100.0%` f1 `100.0%`
- `excluded`: precision `100.0%` recall `100.0%` f1 `100.0%`
- `relative_ci`: precision `100.0%` recall `100.0%` f1 `100.0%`
- `uncertain`: precision `100.0%` recall `100.0%` f1 `100.0%`

## 5. Real-Output Mismatch Audit
These counts separate benchmark/query issues from model behavior and candidate parser misses.
- `not_in_query_space`: `2293`
- `aggregate_label_mismatch`: `9234`
- `model_omission`: `21`
- `candidate_parser_miss`: `551`
- `model_stance_disagreement`: `20757`

## 6. Completeness
- `rows`: `6600`
- `parsed_rows`: `6600`
- `unparsed_rows`: `0`
- `blank_phase1`: `0`
- `blank_phase2`: `0`
- `zero_stance_rows`: `0`
- `error_rows`: `0`

## 7. Gold Sources
- `battery_expectation`: `6600` rows

## 8. Frequent Treatment-Level Error Clusters
- `ophl_type_iii`: accuracy `0.0%`; top errors `recommended->absent x74, absent->recommended x28, absent->excluded x17, absent->relative_ci x7, recommended->excluded x1`; cause mix `candidate_parser_miss x2, model_stance_disagreement x53, not_in_query_space x72`
- `carboplatin_5fu`: accuracy `1.5%`; top errors `recommended->absent x802, excluded->absent x220, absent->excluded x10, recommended->excluded x9, absent->recommended x4`; cause mix `candidate_parser_miss x32, model_stance_disagreement x26, not_in_query_space x990`
- `ophl_type_iib`: accuracy `9.4%`; top errors `absent->excluded x137, absent->recommended x127, absent->relative_ci x30, recommended->excluded x26, recommended->relative_ci x9`; cause mix `model_omission x2, model_stance_disagreement x334`
- `rt_accelerated`: accuracy `10.2%`; top errors `absent->recommended x456, absent->relative_ci x401, recommended->relative_ci x155, absent->uncertain x127, absent->excluded x106`; cause mix `model_omission x3, model_stance_disagreement x1380`
- `tors`: accuracy `12.1%`; top errors `absent->excluded x189, absent->recommended x163, absent->relative_ci x59, recommended->relative_ci x9, recommended->excluded x6`; cause mix `model_stance_disagreement x429`
- `ophl_type_i`: accuracy `15.4%`; top errors `absent->excluded x152, absent->recommended x77, excluded->absent x74, recommended->excluded x47, absent->relative_ci x34`; cause mix `candidate_parser_miss x2, model_stance_disagreement x339, not_in_query_space x72`
- `ict_rt`: accuracy `20.5%`; top errors `absent->excluded x1289, absent->recommended x848, recommended->excluded x636, recommended->relative_ci x370, absent->relative_ci x261`; cause mix `candidate_parser_miss x165, model_omission x5, model_stance_disagreement x3545, not_in_query_space x81`
- `rt_alone`: accuracy `25.0%`; top errors `absent->excluded x795, absent->recommended x739, absent->relative_ci x480, absent->uncertain x121, recommended->excluded x121`; cause mix `candidate_parser_miss x22, model_omission x2, model_stance_disagreement x2440, not_in_query_space x37`
- `ophl_any`: accuracy `25.2%`; top errors `absent->recommended x1092, absent->excluded x1033, recommended->excluded x475, recommended->relative_ci x356, absent->relative_ci x346`; cause mix `aggregate_label_mismatch x3491`
- `ophl_type_ii`: accuracy `27.5%`; top errors `recommended->absent x861, absent->recommended x270, recommended->relative_ci x196, absent->excluded x177, recommended->excluded x164`; cause mix `candidate_parser_miss x63, model_omission x3, model_stance_disagreement x927, not_in_query_space x845`

## 9. Example Real-Output Mismatches
- `A1-BASE` / `kimi-k2.5` / `ophl_type_ii`: gold `recommended` vs predicted `absent` (`not_in_query_space`)
- `A1-BASE` / `kimi-k2.5` / `rt_accelerated`: gold `absent` vs predicted `relative_ci` (`model_stance_disagreement`)
- `A1-BASE` / `kimi-k2.5` / `total_laryngectomy`: gold `excluded` vs predicted `absent` (`candidate_parser_miss`)
- `A1-BASE` / `kimi-k2.5` / `ophl_any`: gold `recommended` vs predicted `absent` (`aggregate_label_mismatch`)
- `A1-BASE` / `kimi-k2.5` / `ophl_type_ii`: gold `recommended` vs predicted `absent` (`not_in_query_space`)
- `A1-BASE` / `kimi-k2.5` / `rt_accelerated`: gold `absent` vs predicted `relative_ci` (`model_stance_disagreement`)
- `A1-BASE` / `kimi-k2.5` / `ophl_any`: gold `recommended` vs predicted `excluded` (`aggregate_label_mismatch`)
- `A1-BASE` / `kimi-k2.5` / `ophl_type_ii`: gold `recommended` vs predicted `absent` (`not_in_query_space`)
- `A1-BASE` / `kimi-k2.5` / `rt_accelerated`: gold `absent` vs predicted `relative_ci` (`model_stance_disagreement`)
- `A1-BASE` / `kimi-k2.5` / `ophl_any`: gold `recommended` vs predicted `absent` (`aggregate_label_mismatch`)
- `A1-BASE` / `kimi-k2.5` / `ophl_type_ii`: gold `recommended` vs predicted `absent` (`not_in_query_space`)
- `A1-BASE` / `kimi-k2.5` / `rt_accelerated`: gold `absent` vs predicted `recommended` (`model_stance_disagreement`)
- `A1-BASE` / `kimi-k2.5` / `total_laryngectomy`: gold `excluded` vs predicted `absent` (`candidate_parser_miss`)
- `A1-BASE` / `kimi-k2.5` / `ophl_type_ii`: gold `recommended` vs predicted `absent` (`not_in_query_space`)
- `A1-BASE` / `kimi-k2.5` / `rt_accelerated`: gold `absent` vs predicted `relative_ci` (`model_stance_disagreement`)
