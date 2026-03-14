# Parser Validation Report

## Overview
- Results file: `results/raw/kimi-k2.5_recovered/run_20260309_1924_merged.jsonl`
- Battery file: `data/vignettes/vignette_battery.json`
- Annotations file: `none`

## Row-Level Performance
- Rows evaluated: `1349`
- Exact match rate: `0.1%`
- `recommended`: precision `55.5%` recall `51.5%` f1 `53.4%`
- `excluded`: precision `22.9%` recall `45.6%` f1 `30.5%`
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
- `rows`: `1349`
- `parsed_rows`: `1347`
- `unparsed_rows`: `2`
- `blank_phase1`: `2`
- `blank_phase2`: `2`
- `zero_stance_rows`: `0`
- `error_rows`: `2`

## Gold Sources
- `battery_expectation`: `1349` rows

## Frequent Treatment Errors
- `nonsurgical_lp`: accuracy `0.0%`; top errors `excluded->absent x165, recommended->absent x30`
- `ophl_type_iii`: accuracy `0.0%`; top errors `recommended->absent x14, absent->excluded x9, absent->recommended x9, absent->relative_ci x5, recommended->excluded x1`
- `surgical_lp`: accuracy `0.0%`; top errors `excluded->absent x60, recommended->absent x30`
- `carboplatin_5fu`: accuracy `1.1%`; top errors `recommended->absent x162, excluded->absent x15, absent->recommended x2, recommended->excluded x1, absent->excluded x1`
- `rt_accelerated`: accuracy `3.6%`; top errors `absent->relative_ci x85, recommended->relative_ci x50, recommended->excluded x15, recommended->uncertain x12, absent->recommended x10`
- `tors`: accuracy `4.1%`; top errors `absent->excluded x84, absent->relative_ci x43, recommended->relative_ci x6, absent->recommended x3, recommended->excluded x2`
- `ophl_type_iib`: accuracy `7.0%`; top errors `absent->excluded x42, absent->recommended x25, absent->relative_ci x4, recommended->excluded x4, recommended->relative_ci x2`
- `ophl_any`: accuracy `8.2%`; top errors `absent->recommended x339, absent->excluded x327, absent->relative_ci x151, recommended->excluded x12, excluded->recommended x11`
- `ophl_type_i`: accuracy `12.7%`; top errors `absent->excluded x62, absent->recommended x15, excluded->absent x14, absent->relative_ci x12, recommended->relative_ci x9`
- `ict_rt`: accuracy `19.8%`; top errors `absent->excluded x163, absent->recommended x136, recommended->relative_ci x117, recommended->absent x114, absent->relative_ci x91`

## Example Mismatches
- `A1-BASE` / `kimi-k2.5` / `ophl_any`: gold `absent` vs predicted `recommended`
- `A1-BASE` / `kimi-k2.5` / `ophl_type_ii`: gold `recommended` vs predicted `absent`
- `A1-BASE` / `kimi-k2.5` / `rt_accelerated`: gold `absent` vs predicted `relative_ci`
- `A1-BASE` / `kimi-k2.5` / `total_laryngectomy`: gold `excluded` vs predicted `absent`
- `A1-BASE` / `kimi-k2.5` / `ophl_type_ii`: gold `recommended` vs predicted `absent`
- `A1-BASE` / `kimi-k2.5` / `rt_accelerated`: gold `absent` vs predicted `relative_ci`
- `A1-BASE` / `kimi-k2.5` / `ophl_any`: gold `absent` vs predicted `excluded`
- `A1-BASE` / `kimi-k2.5` / `ophl_type_ii`: gold `recommended` vs predicted `absent`
- `A1-BASE` / `kimi-k2.5` / `rt_accelerated`: gold `absent` vs predicted `relative_ci`
- `A1-BASE` / `kimi-k2.5` / `ophl_type_ii`: gold `recommended` vs predicted `absent`
- `A1-BASE` / `kimi-k2.5` / `rt_accelerated`: gold `absent` vs predicted `recommended`
- `A1-BASE` / `kimi-k2.5` / `total_laryngectomy`: gold `excluded` vs predicted `absent`
- `A1-BASE` / `kimi-k2.5` / `ophl_any`: gold `absent` vs predicted `recommended`
- `A1-BASE` / `kimi-k2.5` / `ophl_type_ii`: gold `recommended` vs predicted `absent`
- `A1-BASE` / `kimi-k2.5` / `rt_accelerated`: gold `absent` vs predicted `relative_ci`
