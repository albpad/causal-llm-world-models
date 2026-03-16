# Parser Validation Report

## Overview
- Results file: `results/raw/article_models_h15_repaired/run_20260315_h15_harmonized.jsonl`
- Battery file: `data/vignettes/vignette_battery.json`
- Annotations file: `none`

## Row-Level Performance
- Rows evaluated: `2640`
- Exact match rate: `2.4%`
- `recommended`: precision `60.1%` recall `66.2%` f1 `63.0%`
- `excluded`: precision `21.1%` recall `34.5%` f1 `26.2%`
- `relative_ci`: insufficient support
- `uncertain`: insufficient support

## Consensus-Level Performance
- Case/model groups: `176`
- Exact match rate: `0.0%`
- `recommended`: insufficient support
- `excluded`: insufficient support
- `relative_ci`: insufficient support
- `uncertain`: insufficient support

## Completeness
- `rows`: `2640`
- `parsed_rows`: `2640`
- `unparsed_rows`: `0`
- `blank_phase1`: `0`
- `blank_phase2`: `0`
- `zero_stance_rows`: `0`
- `error_rows`: `0`

## Gold Sources
- `battery_expectation`: `2640` rows

## Frequent Treatment Errors
- `ophl_type_iii`: accuracy `0.0%`; top errors `recommended->absent x29, absent->excluded x12, absent->recommended x8, absent->relative_ci x5, recommended->excluded x1`
- `carboplatin_5fu`: accuracy `1.9%`; top errors `recommended->absent x321, excluded->absent x89, absent->recommended x2, recommended->excluded x1, absent->excluded x1`
- `tors`: accuracy `9.1%`; top errors `absent->excluded x78, absent->recommended x73, absent->relative_ci x39, recommended->relative_ci x7, recommended->excluded x2`
- `ophl_type_iib`: accuracy `13.7%`; top errors `absent->recommended x78, absent->excluded x33, recommended->excluded x4, absent->relative_ci x3, recommended->relative_ci x3`
- `ophl_type_i`: accuracy `20.8%`; top errors `absent->recommended x59, absent->excluded x45, excluded->absent x29, absent->relative_ci x13, recommended->relative_ci x12`
- `ict_rt`: accuracy `31.3%`; top errors `absent->recommended x406, absent->excluded x227, recommended->absent x141, recommended->relative_ci x129, absent->relative_ci x103`
- `ophl_any`: accuracy `31.5%`; top errors `absent->recommended x457, absent->excluded x302, absent->relative_ci x143, recommended->relative_ci x112, recommended->excluded x108`
- `tlm`: accuracy `32.7%`; top errors `excluded->recommended x386, absent->excluded x269, absent->recommended x184, excluded->relative_ci x122, recommended->relative_ci x85`
- `ophl_type_ii`: accuracy `33.1%`; top errors `recommended->absent x320, absent->recommended x125, absent->excluded x74, recommended->relative_ci x54, recommended->excluded x45`
- `rt_accelerated`: accuracy `33.7%`; top errors `absent->recommended x54, recommended->relative_ci x50, absent->relative_ci x45, recommended->uncertain x18, recommended->excluded x13`

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
