# Parser Validation Report

## Overview
- Results file: `results/raw/kimi-k2.5/run_20260309_1924.jsonl`
- Battery file: `data/vignettes/vignette_battery.json`
- Annotations file: `none`

## Row-Level Performance
- Rows evaluated: `1386`
- Exact match rate: `1.3%`
- `recommended`: precision `57.5%` recall `30.5%` f1 `39.9%`
- `excluded`: precision `26.0%` recall `31.8%` f1 `28.6%`
- `relative_ci`: insufficient support
- `uncertain`: insufficient support

## Consensus-Level Performance
- Case/model groups: `88`
- Exact match rate: `0.0%`
- `recommended`: insufficient support
- `excluded`: insufficient support
- `relative_ci`: insufficient support
- `uncertain`: insufficient support

## Completeness
- `rows`: `1386`
- `parsed_rows`: `1372`
- `unparsed_rows`: `14`
- `blank_phase1`: `305`
- `blank_phase2`: `768`
- `zero_stance_rows`: `329`
- `error_rows`: `14`

## Gold Sources
- `battery_expectation`: `1386` rows

## Frequent Treatment Errors
- `nonsurgical_lp`: accuracy `0.0%`; top errors `excluded->absent x169, recommended->absent x30`
- `ophl_type_iib`: accuracy `0.0%`; top errors `recommended->absent x15, absent->excluded x13, absent->recommended x5, absent->relative_ci x1`
- `ophl_type_iii`: accuracy `0.0%`; top errors `recommended->absent x15, absent->excluded x3, absent->relative_ci x2, absent->recommended x1`
- `surgical_lp`: accuracy `0.0%`; top errors `excluded->absent x60, recommended->absent x30`
- `carboplatin_5fu`: accuracy `0.6%`; top errors `recommended->absent x163, excluded->absent x15, recommended->excluded x1, absent->excluded x1`
- `rt_accelerated`: accuracy `1.6%`; top errors `absent->relative_ci x79, recommended->relative_ci x58, recommended->absent x27, recommended->excluded x10, absent->recommended x7`
- `ict_rt`: accuracy `4.6%`; top errors `recommended->absent x329, absent->excluded x117, absent->recommended x69, recommended->relative_ci x64, absent->relative_ci x52`
- `ophl_any`: accuracy `8.0%`; top errors `absent->recommended x216, absent->excluded x206, absent->relative_ci x73, excluded->absent x41, recommended->absent x30`
- `tors`: accuracy `10.9%`; top errors `absent->excluded x31, absent->relative_ci x9, recommended->relative_ci x6, recommended->excluded x2, recommended->uncertain x1`
- `ophl_type_ii`: accuracy `16.0%`; top errors `recommended->absent x316, absent->recommended x37, absent->excluded x31, excluded->absent x24, recommended->relative_ci x10`

## Example Mismatches
- `A1-BASE` / `kimi-k2.5` / `ophl_any`: gold `absent` vs predicted `recommended`
- `A1-BASE` / `kimi-k2.5` / `ophl_type_ii`: gold `recommended` vs predicted `relative_ci`
- `A1-BASE` / `kimi-k2.5` / `rt_accelerated`: gold `absent` vs predicted `relative_ci`
- `A1-BASE` / `kimi-k2.5` / `ophl_type_ii`: gold `recommended` vs predicted `absent`
- `A1-BASE` / `kimi-k2.5` / `rt_accelerated`: gold `absent` vs predicted `relative_ci`
- `A1-BASE` / `kimi-k2.5` / `ophl_any`: gold `absent` vs predicted `recommended`
- `A1-BASE` / `kimi-k2.5` / `ophl_type_ii`: gold `recommended` vs predicted `absent`
- `A1-BASE` / `kimi-k2.5` / `rt_accelerated`: gold `absent` vs predicted `relative_ci`
- `A1-BASE` / `kimi-k2.5` / `total_laryngectomy`: gold `excluded` vs predicted `recommended`
- `A1-BASE` / `kimi-k2.5` / `ophl_type_ii`: gold `recommended` vs predicted `absent`
- `A1-BASE` / `kimi-k2.5` / `rt_accelerated`: gold `absent` vs predicted `recommended`
- `A1-BASE` / `kimi-k2.5` / `total_laryngectomy`: gold `excluded` vs predicted `absent`
- `A1-BASE` / `kimi-k2.5` / `ophl_any`: gold `absent` vs predicted `recommended`
- `A1-BASE` / `kimi-k2.5` / `ophl_type_ii`: gold `recommended` vs predicted `absent`
- `A1-BASE` / `kimi-k2.5` / `rt_accelerated`: gold `absent` vs predicted `relative_ci`
