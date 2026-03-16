# Parser Validation Report

## Overview
- Results file: `results/raw/article_models_5_h15/run_20260316_h15_5models.jsonl`
- Battery file: `data/vignettes/vignette_battery.json`
- Annotations file: `none`

## Row-Level Performance
- Rows evaluated: `6600`
- Exact match rate: `1.0%`
- `recommended`: precision `59.1%` recall `62.2%` f1 `60.6%`
- `excluded`: precision `19.7%` recall `49.8%` f1 `28.2%`
- `relative_ci`: insufficient support
- `uncertain`: insufficient support

## Consensus-Level Performance
- Case/model groups: `440`
- Exact match rate: `0.0%`
- `recommended`: insufficient support
- `excluded`: insufficient support
- `relative_ci`: insufficient support
- `uncertain`: insufficient support

## Completeness
- `rows`: `6600`
- `parsed_rows`: `6600`
- `unparsed_rows`: `0`
- `blank_phase1`: `0`
- `blank_phase2`: `0`
- `zero_stance_rows`: `0`
- `error_rows`: `0`

## Gold Sources
- `battery_expectation`: `6600` rows

## Frequent Treatment Errors
- `ophl_type_iii`: accuracy `0.0%`; top errors `recommended->absent x74, absent->recommended x28, absent->excluded x17, absent->relative_ci x7, recommended->excluded x1`
- `carboplatin_5fu`: accuracy `1.5%`; top errors `recommended->absent x802, excluded->absent x220, absent->excluded x10, recommended->excluded x9, absent->recommended x4`
- `ophl_type_iib`: accuracy `9.4%`; top errors `absent->excluded x137, absent->recommended x127, absent->relative_ci x30, recommended->excluded x26, recommended->relative_ci x9`
- `rt_accelerated`: accuracy `10.2%`; top errors `absent->recommended x456, absent->relative_ci x401, recommended->relative_ci x155, absent->uncertain x127, absent->excluded x106`
- `tors`: accuracy `12.1%`; top errors `absent->excluded x189, absent->recommended x163, absent->relative_ci x59, recommended->relative_ci x9, recommended->excluded x6`
- `ophl_type_i`: accuracy `15.4%`; top errors `absent->excluded x152, absent->recommended x77, excluded->absent x74, recommended->excluded x47, absent->relative_ci x34`
- `ict_rt`: accuracy `20.5%`; top errors `absent->excluded x1289, absent->recommended x848, recommended->excluded x636, recommended->relative_ci x370, absent->relative_ci x261`
- `rt_alone`: accuracy `25.0%`; top errors `absent->excluded x795, absent->recommended x739, absent->relative_ci x480, absent->uncertain x121, recommended->excluded x121`
- `ophl_any`: accuracy `25.2%`; top errors `absent->recommended x1092, absent->excluded x1033, recommended->excluded x475, recommended->relative_ci x356, absent->relative_ci x346`
- `ophl_type_ii`: accuracy `27.5%`; top errors `recommended->absent x861, absent->recommended x270, recommended->relative_ci x196, absent->excluded x177, recommended->excluded x164`

## Example Mismatches
- `A1-BASE` / `kimi-k2.5` / `ophl_type_ii`: gold `recommended` vs predicted `absent`
- `A1-BASE` / `kimi-k2.5` / `rt_accelerated`: gold `absent` vs predicted `relative_ci`
- `A1-BASE` / `kimi-k2.5` / `total_laryngectomy`: gold `excluded` vs predicted `absent`
- `A1-BASE` / `kimi-k2.5` / `ophl_any`: gold `recommended` vs predicted `absent`
- `A1-BASE` / `kimi-k2.5` / `ophl_type_ii`: gold `recommended` vs predicted `absent`
- `A1-BASE` / `kimi-k2.5` / `rt_accelerated`: gold `absent` vs predicted `relative_ci`
- `A1-BASE` / `kimi-k2.5` / `ophl_any`: gold `recommended` vs predicted `excluded`
- `A1-BASE` / `kimi-k2.5` / `ophl_type_ii`: gold `recommended` vs predicted `absent`
- `A1-BASE` / `kimi-k2.5` / `rt_accelerated`: gold `absent` vs predicted `relative_ci`
- `A1-BASE` / `kimi-k2.5` / `ophl_any`: gold `recommended` vs predicted `absent`
- `A1-BASE` / `kimi-k2.5` / `ophl_type_ii`: gold `recommended` vs predicted `absent`
- `A1-BASE` / `kimi-k2.5` / `rt_accelerated`: gold `absent` vs predicted `recommended`
- `A1-BASE` / `kimi-k2.5` / `total_laryngectomy`: gold `excluded` vs predicted `absent`
- `A1-BASE` / `kimi-k2.5` / `ophl_type_ii`: gold `recommended` vs predicted `absent`
- `A1-BASE` / `kimi-k2.5` / `rt_accelerated`: gold `absent` vs predicted `relative_ci`
