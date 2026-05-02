# Parser Validation Report

## Overview
- Results file: `results/raw/article_models_6_h15/run_20260410_h15_6models.jsonl`
- Battery file: `data/vignettes/vignette_battery.json`
- Annotations file: `none`

## 1. Battery Alignment on Real Model Outputs
This section is **not** pure parser accuracy. It measures alignment between parsed model outputs and battery expectations, so disagreement can come from query-space gaps, model omissions, or true parser misses.
- Rows evaluated: `7920`
- Exact match rate: `1.0%`
- `recommended`: precision `59.6%` recall `61.4%` f1 `60.5%`
- `excluded`: precision `20.1%` recall `48.1%` f1 `28.4%`
- `relative_ci`: insufficient support
- `uncertain`: insufficient support

## 2. Consensus Alignment Across Runs
- Case/model groups: `528`
- Exact match rate: `0.6%`
- `recommended`: precision `51.0%` recall `73.4%` f1 `60.2%`
- `excluded`: precision `16.0%` recall `54.3%` f1 `24.8%`
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
- `not_in_query_space`: `3016`
- `aggregate_label_mismatch`: `10925`
- `model_omission`: `148`
- `candidate_parser_miss`: `811`
- `model_stance_disagreement`: `23517`

## 6. Completeness
- `rows`: `7920`
- `parsed_rows`: `7920`
- `unparsed_rows`: `0`
- `blank_phase1`: `0`
- `blank_phase2`: `0`
- `zero_stance_rows`: `3`
- `error_rows`: `0`

## 7. Gold Sources
- `battery_expectation`: `7920` rows

## 8. Frequent Treatment-Level Error Clusters
- `ophl_type_iii`: accuracy `0.0%`; top errors `recommended->absent x89, absent->recommended x28, absent->excluded x17, absent->relative_ci x7, recommended->excluded x1`; cause mix `candidate_parser_miss x2, model_stance_disagreement x53, not_in_query_space x87`
- `carboplatin_5fu`: accuracy `1.6%`; top errors `recommended->absent x961, excluded->absent x259, absent->excluded x14, recommended->excluded x12, absent->recommended x7`; cause mix `candidate_parser_miss x49, model_stance_disagreement x41, not_in_query_space x1171`
- `rt_accelerated`: accuracy `10.4%`; top errors `absent->recommended x568, absent->relative_ci x438, recommended->relative_ci x191, absent->uncertain x127, absent->excluded x109`; cause mix `candidate_parser_miss x5, model_omission x13, model_stance_disagreement x1578`
- `ophl_type_iib`: accuracy `10.6%`; top errors `absent->recommended x155, absent->excluded x148, absent->relative_ci x39, recommended->excluded x27, recommended->relative_ci x10`; cause mix `candidate_parser_miss x1, model_omission x3, model_stance_disagreement x384`
- `tors`: accuracy `12.1%`; top errors `absent->excluded x202, absent->recommended x179, absent->relative_ci x73, recommended->excluded x10, recommended->relative_ci x9`; cause mix `candidate_parser_miss x4, model_stance_disagreement x477`
- `ophl_type_i`: accuracy `15.9%`; top errors `absent->excluded x163, absent->recommended x101, excluded->absent x89, recommended->excluded x55, absent->relative_ci x37`; cause mix `candidate_parser_miss x3, model_omission x1, model_stance_disagreement x389, not_in_query_space x87`
- `ict_rt`: accuracy `21.0%`; top errors `absent->excluded x1428, absent->recommended x969, recommended->excluded x718, recommended->relative_ci x394, recommended->absent x376`; cause mix `candidate_parser_miss x218, model_omission x27, model_stance_disagreement x3957, not_in_query_space x178`
- `ophl_any`: accuracy `26.0%`; top errors `absent->recommended x1259, absent->excluded x1129, recommended->excluded x533, absent->relative_ci x384, recommended->relative_ci x379`; cause mix `aggregate_label_mismatch x3997`
- `rt_alone`: accuracy `26.8%`; top errors `absent->recommended x901, absent->excluded x874, absent->relative_ci x501, recommended->excluded x127, absent->uncertain x121`; cause mix `candidate_parser_miss x22, model_omission x4, model_stance_disagreement x2733, not_in_query_space x50`
- `ophl_type_ii`: accuracy `26.9%`; top errors `recommended->absent x1118, absent->recommended x278, recommended->relative_ci x204, absent->excluded x191, recommended->excluded x183`; cause mix `candidate_parser_miss x103, model_omission x27, model_stance_disagreement x979, not_in_query_space x1055`

## 9. Example Real-Output Mismatches
- `A1-BASE` / `deepseek-r1` / `ophl_any`: gold `recommended` vs predicted `excluded` (`aggregate_label_mismatch`)
- `A1-BASE` / `deepseek-r1` / `ophl_type_i`: gold `absent` vs predicted `excluded` (`model_stance_disagreement`)
- `A1-BASE` / `deepseek-r1` / `ophl_type_ii`: gold `recommended` vs predicted `absent` (`not_in_query_space`)
- `A1-BASE` / `deepseek-r1` / `rt_accelerated`: gold `absent` vs predicted `excluded` (`model_stance_disagreement`)
- `A1-BASE` / `deepseek-r1` / `total_laryngectomy`: gold `excluded` vs predicted `absent` (`candidate_parser_miss`)
- `A1-BASE` / `deepseek-r1` / `ict_rt`: gold `absent` vs predicted `excluded` (`model_stance_disagreement`)
- `A1-BASE` / `deepseek-r1` / `ophl_type_ii`: gold `recommended` vs predicted `absent` (`not_in_query_space`)
- `A1-BASE` / `deepseek-r1` / `rt_accelerated`: gold `absent` vs predicted `relative_ci` (`model_stance_disagreement`)
- `A1-BASE` / `deepseek-r1` / `ict_rt`: gold `absent` vs predicted `excluded` (`model_stance_disagreement`)
- `A1-BASE` / `deepseek-r1` / `ophl_any`: gold `recommended` vs predicted `excluded` (`aggregate_label_mismatch`)
- `A1-BASE` / `deepseek-r1` / `ophl_type_ii`: gold `recommended` vs predicted `absent` (`not_in_query_space`)
- `A1-BASE` / `deepseek-r1` / `rt_accelerated`: gold `absent` vs predicted `excluded` (`model_stance_disagreement`)
- `A1-BASE` / `deepseek-r1` / `ict_rt`: gold `absent` vs predicted `excluded` (`model_stance_disagreement`)
- `A1-BASE` / `deepseek-r1` / `ophl_any`: gold `recommended` vs predicted `excluded` (`aggregate_label_mismatch`)
- `A1-BASE` / `deepseek-r1` / `ophl_type_ii`: gold `recommended` vs predicted `excluded` (`model_stance_disagreement`)
