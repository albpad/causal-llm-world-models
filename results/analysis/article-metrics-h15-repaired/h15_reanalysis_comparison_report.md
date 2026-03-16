# Harmonized 15-Run Reanalysis Comparison

## Scope

- Canonical dataset: `88` vignettes x `15` runs x `2` models = `2640` rows.
- KG1 is the repaired `58`-edge graph, not the earlier `55`-edge article set.
- Kimi targeted prompt-fix reruns were completed on the original `kimi-k2.5` backend for the `4` changed vignettes.
- Llama targeted prompt-fix reruns were completed by querying `llama-3-8b-lite` while preserving `llama-3.1-8b` row identity for merge (`60` repaired rows).

## Integrity Checks

- Harmonized file: `2640` rows, `88` unique item IDs, models `kimi-k2.5` and `llama-3.1-8b`, exactly `run_idx 0..14` for both models.
- Kimi targeted reruns: `60/60` complete rows.
- Llama targeted reruns: `60/60` complete rows, all tagged with `queried_with_model_name=llama-3-8b-lite`.
- Harmonized parser validation: row exact-match `2.4%`, consensus exact-match `0.0%`, recommended F1 `0.630`, excluded F1 `0.262`.

## Changed Vignette Behaviour

### Kimi

- `A1-P2`: `cisplatin_high_dose`: `None` -> `recommended`; `ict_rt`: `excluded` -> `recommended`; `ophl_type_iii`: `None` -> `excluded`; `rt_accelerated`: `relative_ci` -> `None`; `rt_alone`: `excluded` -> `recommended`; `total_laryngectomy`: `excluded` -> `relative_ci`.
- `A2-P3`: `ophl_type_iii`: `recommended` -> `excluded`; `rt_accelerated`: `relative_ci` -> `recommended`; `rt_alone`: `excluded` -> `recommended`; `total_laryngectomy`: `recommended` -> `relative_ci`.
- `C1-P3`: `ict_rt`: `excluded` -> `recommended`; `ophl_type_i`: `excluded` -> `None`; `ophl_type_iib`: `excluded` -> `None`; `rt_alone`: `recommended` -> `excluded`; `tors`: `excluded` -> `relative_ci`; `total_laryngectomy`: `excluded` -> `relative_ci`.
- `G1-ABS11`: `carboplatin_5fu`: `recommended` -> `None`; `cisplatin_high_dose`: `relative_ci` -> `excluded`; `concurrent_crt`: `recommended` -> `excluded`; `ict_rt`: `None` -> `excluded`; `ophl_any`: `None` -> `excluded`; `ophl_type_ii`: `None` -> `excluded`; `rt_accelerated`: `None` -> `recommended`; `tlm`: `None` -> `excluded`; `tors`: `None` -> `recommended`; `total_laryngectomy`: `relative_ci` -> `excluded`.

### Llama

- `A1-P2`: `concurrent_crt`: `excluded` -> `recommended`; `ict_rt`: `excluded` -> `uncertain`; `ophl_any`: `excluded` -> `recommended`; `ophl_type_ii`: `None` -> `recommended`; `rt_accelerated`: `recommended` -> `None`; `rt_alone`: `recommended` -> `relative_ci`; `tors`: `excluded` -> `None`.
- `A2-P3`: `ict_rt`: `excluded` -> `recommended`; `ophl_type_ii`: `None` -> `recommended`; `rt_accelerated`: `recommended` -> `None`; `total_laryngectomy`: `recommended` -> `excluded`.
- `C1-P3`: `ict_rt`: `recommended` -> `uncertain`; `ophl_type_i`: `recommended` -> `None`; `ophl_type_ii`: `None` -> `recommended`; `ophl_type_iib`: `recommended` -> `None`; `rt_alone`: `recommended` -> `None`; `tors`: `recommended` -> `None`; `total_laryngectomy`: `recommended` -> `excluded`.
- `G1-ABS11`: `cisplatin_high_dose`: `recommended` -> `excluded`; `ict_rt`: `None` -> `recommended`; `ophl_any`: `None` -> `recommended`; `rt_accelerated`: `None` -> `recommended`; `rt_alone`: `None` -> `recommended`; `surgical_lp`: `None` -> `recommended`; `tlm`: `None` -> `recommended`; `total_laryngectomy`: `None` -> `recommended`.

## Article Metrics: Old vs Harmonized

| Model | Dataset | WMI | SID | Soft Recall | SNR | Hard Recall | Direction Accuracy |
|---|---:|---:|---:|---:|---:|---:|---:|
| kimi-k2.5 | old article set | 0.660 | 37/165 | 74.5% | 2.95 | 18.2% | 70.0% |
| kimi-k2.5 | new harmonized 15-run set | 0.610 | 40/246 | 74.1% | 2.46 | 6.9% | 50.0% |
| llama-3.1-8b | old article set | 0.504 | 44/154 | 7.3% | 0.46 | 1.8% | 100.0% |
| llama-3.1-8b | new harmonized 15-run set | 0.522 | 45/233 | 17.2% | 0.80 | 0.0% | 0.0% |

Interpretation: the new harmonized results change both the study design basis and the effective comparator arm. The study is now equal-run (`15/15`) and uses the repaired `58`-edge KG. The Llama arm preserves the original study identity but its four changed vignettes were refreshed via the accessible serverless `llama-3-8b-lite` backend.

## Edge Counts and Coverage Changes

| Model | Dataset | KG Edge Total | Hard Detected | Soft Detected | Phantom Edges |
|---|---:|---:|---:|---:|---:|
| kimi-k2.5 | old article set | 55 | 10 | 41 | 17 |
| kimi-k2.5 | new harmonized 15-run set | 58 | 4 | 43 | 21 |
| llama-3.1-8b | old article set | 55 | 1 | 4 | 9 |
| llama-3.1-8b | new harmonized 15-run set | 58 | 0 | 10 | 4 |
