# Compact Six-Model Comparison Report With Gemma 4 31B

## Scope
This report summarizes the locked `88 x 15` six-model analysis after adding `google/gemma-4-31B-it` to the final laryngeal-cancer benchmark. Primary interpretation follows the manuscript framework:

- `Coverage`: soft recall, soft precision, soft false discovery rate (FDR)
- `Fidelity`: soft-edge direction accuracy, hard-edge direction accuracy, SID rate
- `Discriminability`: SNR, detection power
- `Stability`: auxiliary only, interpreted conditionally on coverage

No composite index is used for primary interpretation.

## Dataset Integrity
- Total rows: `7,920`
- Vignettes: `88`
- Models: `6`
- Runs per model: `15`
- Run index coverage: `0..14` for all models
- Blank phase-1 rows: `0`
- Blank phase-2 rows: `0`
- Unparsed rows: `0`
- Zero-stance rows: `3`

## Top-Line Domain Comparison

| Model | Soft recall | Soft precision | Soft FDR | Soft dir. acc. | SID rate | SNR | Detection power | Veridical split-half | Interpretation |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| Kimi K2.5 | 74.1% | 66.2% | 33.8% | 67.4% | 16.7% | 2.46 | 20.7% | 50.5% | Broadest recovered graph; strongest causal-vs-null separation |
| DeepSeek-R1 | 62.1% | 60.0% | 40.0% | 77.8% | 14.0% | 2.14 | 17.3% | 77.4% | Best overall balance of coverage, directional fidelity, and discriminability |
| Mistral-Small-24B | 43.1% | 62.5% | 37.5% | 72.0% | 13.1% | 1.66 | 13.1% | 83.2% | Mid-tier partial model with modest coverage and acceptable fidelity |
| Gemma 4 31B | 41.4% | 66.7% | 33.3% | 70.8% | 16.2% | 1.80 | 12.0% | 79.1% | Mid-tier model; cleaner than Qwen/Mistral on spurious-edge control, but incomplete |
| Qwen3-Next-80B-A3B-Instruct | 39.7% | 53.5% | 46.5% | 73.9% | 13.5% | 1.87 | 15.6% | 91.2% | Mid-tier partial model with good soft direction but noisier edge recovery |
| Llama 3.1-8B | 17.2% | 71.4% | 28.6% | 50.0% | 19.3% | 0.80 | 2.6% | 62.4% | Fragmentary baseline; sparse recovery and poor causal-vs-null separation |

## Overall Readout
The six-model ordering did not change the main scientific story.

- `DeepSeek-R1` remains the strongest balanced model.
- `Kimi K2.5` remains the broadest and most discriminative model, but it still carries more directional and risk-weighted noise than DeepSeek.
- `Gemma 4 31B` enters the middle tier rather than the frontier tier.
- `Gemma`, `Mistral`, and `Qwen` all recover nontrivial structure, but none approaches the coverage-discriminability profile of Kimi or the coverage-fidelity balance of DeepSeek.
- `Llama 3.1-8B` remains the clear low-end baseline.

## Gemma 4 31B: Placement
Gemma does not change the top-level conclusion, but it is not negligible. Its profile is distinct from the existing mid-tier models.

### Strengths
- `Soft precision 66.7%` and `soft FDR 33.3%` are cleaner than Qwen and slightly cleaner than Mistral.
- `Soft direction accuracy 70.8%` indicates that the recovered soft graph is usually directionally coherent.
- `SNR 1.80` shows a real, nontrivial separation between causal perturbations and null/noise.
- `Veridical split-half 79.1%` is acceptable once conditioned on its moderate coverage.

### Weaknesses
- `Soft recall 41.4%` remains far below Kimi and below DeepSeek.
- `SID rate 16.2%` is materially weaker than DeepSeek, Mistral, and Qwen.
- `Detection power 12.0%` places Gemma below DeepSeek, Kimi, and Qwen.
- `Hard direction accuracy 25.0%` shows that the stricter high-confidence edge subset remains limited.

### Practical Interpretation
Gemma is best described as a `mid-tier, incomplete world-model candidate`. It behaves more cleanly than Qwen on spurious-edge control, but it does not recover enough structure, and its intervention-level fidelity is not strong enough, to challenge the top tier.

## Risk-Weighted Fidelity
Risk weighting treated any error involving `total_laryngectomy` as Tier 3, organ-preservation regime shifts as Tier 2, and fallback nuance labels as Tier 1.

| Model | Weighted wrong-direction rate | Weighted SID rate | Tier-3 wrong-direction edges | Tier-3 SID errors |
|---|---:|---:|---:|---:|
| DeepSeek-R1 | 21.9% | 13.8% | 6 | 3 |
| Mistral-Small-24B | 25.4% | 13.2% | 3 | 3 |
| Qwen3-Next-80B-A3B-Instruct | 25.9% | 13.7% | 4 | 4 |
| Gemma 4 31B | 27.3% | 15.5% | 4 | 3 |
| Kimi K2.5 | 31.3% | 15.9% | 9 | 3 |
| Llama 3.1-8B | 44.4% | 17.4% | 2 | 3 |

Gemma’s weighted profile is mid-tier as well. It is clearly better than Llama, but it does not surpass DeepSeek and does not separate itself clearly from Qwen or Mistral once clinically weighted errors are considered.

## Family-Level Heterogeneity
Gemma is not uniformly weak or uniformly strong; it shows marked domain heterogeneity.

### Stronger families
- `post_ict_response`: soft recall `81.8%`, soft precision `75.0%`, soft direction accuracy `100.0%`, SID rate `11.8%`
- `elderly_frail`: soft recall `83.3%`, soft precision `62.5%`
- `glottic_cT2`: soft recall `50.0%`, soft precision `75.0%`

### Weaker families
- `cT4a_selected`: soft recall `0.0%`
- `supraglottic_cT3`: soft recall `0.0%`
- `cisplatin_eligibility`: soft recall `12.5%`, soft direction accuracy `0.0%`

This pattern suggests that Gemma adapts more successfully in response/frailty-style contexts than in anatomically demanding or high-granularity surgical-selection families.

## Threshold Robustness
Gemma’s placement is not a threshold artifact.

### Soft-threshold sweep
- At soft threshold `0.15`: recall `46.6%`, precision `69.2%`, FDR `30.8%`, direction accuracy `74.1%`
- At soft threshold `0.25` (locked default): recall `41.4%`, precision `66.7%`, FDR `33.3%`, direction accuracy `70.8%`
- At soft threshold `0.35`: recall `39.7%`, precision `65.7%`, FDR `34.3%`, direction accuracy `73.9%`

### Hard-threshold sweep
- At hard threshold `0.40 / 0.05`: recall `19.0%`, precision `47.8%`, FDR `52.2%`, hard direction accuracy `63.6%`
- At hard threshold `0.50 / 0.05`: recall `15.5%`, precision `42.9%`, FDR `57.1%`, hard direction accuracy `66.7%`
- At hard threshold `0.60 / 0.05`: recall `6.9%`, precision `25.0%`, FDR `75.0%`, hard direction accuracy `25.0%`

The qualitative ranking remains stable across the sweep:
- Kimi remains the highest-coverage model.
- DeepSeek remains the strongest fidelity-balanced model.
- Llama remains the weakest locked-default coverage/discriminability model.
- Gemma stays in the mid-tier range.

## Parser and Run Quality
The six-model comparison remains operationally clean.

- Gold-template parser exact match: `98.9%`
- Structured snippet exact match: `100.0%`
- Unparsed rows: `0`
- Error rows: `0`

Mismatch decomposition continued to show that most residual discordance was not parser failure:
- `23,517` model-versus-gold stance disagreements
- `10,925` aggregate-label mismatches
- `3,016` query-space gaps
- `811` candidate parser misses
- `148` model omissions

Gemma required one provider-specific accommodation: Together frequently returned substantive text in `message.reasoning` even when `message.content` was sparse. The acquisition pipeline therefore used `reasoning` as a fallback content source only when the main content field was blank. Final Gemma rows were complete and parseable under this policy.

## Bottom Line
Adding `Gemma 4 31B` strengthens the benchmark comparison set but does not alter the main manuscript conclusion.

- The top tier remains split between `Kimi K2.5` and `DeepSeek-R1`, with Kimi leading on coverage/discriminability and DeepSeek leading on balance/fidelity.
- `Gemma 4 31B` belongs in the middle tier with `Mistral-Small-24B` and `Qwen3-Next-80B-A3B-Instruct`.
- Within that middle tier, Gemma looks relatively clean on soft precision/FDR, but it is still incomplete and only moderately discriminative.
- `Llama 3.1-8B` remains a fragmentary baseline and does not approach causal readiness.

For manuscript purposes, the cleanest update is to classify Gemma as `partial and brittle`, with the added note that it is somewhat cleaner than Qwen on spurious-edge control but materially below DeepSeek and Kimi on overall causal world-model performance.
