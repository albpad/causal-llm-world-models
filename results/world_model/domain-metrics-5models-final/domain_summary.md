# Domain-Based World-Model Evaluation

Primary interpretation uses Coverage, Fidelity, and Discriminability. Stability is auxiliary and interpreted only conditionally on coverage.

| Model | Soft recall | Soft precision | Soft FDR | Soft dir. acc. | Hard dir. acc. | SID rate | SNR | Detection power | Veridical split-half | Regime |
|---|---|---|---|---|---|---|---|---|---:|---|
| DeepSeek-R1 | 62.1% (50.0% to 74.1%) | 60.0% (50.0% to 70.6%) | 40.0% (29.4% to 50.0%) | 77.8% (63.2% to 90.2%) | 66.7% (20.0% to 100.0%) | 14.0% (9.9% to 18.5%) | 2.14 (1.41 to 2.80) | 17.3% (3.5% to 29.3%) | 78.2% | balanced |
| Kimi K2.5 | 74.1% (62.1% to 84.5%) | 66.2% (56.2% to 76.3%) | 33.8% (23.7% to 43.8%) | 67.4% (53.1% to 80.0%) | 50.0% (0.0% to 100.0%) | 16.7% (12.2% to 21.5%) | 2.46 (1.80 to 3.23) | 20.7% (12.7% to 29.9%) | 49.2% | broad but noisy |
| Qwen3-Next-80B-A3B-Instruct | 39.7% (27.6% to 53.4%) | 53.5% (40.0% to 67.6%) | 46.5% (32.4% to 60.0%) | 73.9% (55.0% to 91.3%) | 0.0% (0.0% to 0.0%) | 13.5% (9.3% to 18.1%) | 1.87 (1.47 to 2.89) | 15.6% (10.5% to 20.3%) | 90.9% | partial and brittle |
| Mistral-Small-24B | 43.1% (31.0% to 55.2%) | 62.5% (50.0% to 75.7%) | 37.5% (24.3% to 50.0%) | 72.0% (53.6% to 88.9%) | 0.0% (0.0% to 0.0%) | 13.1% (8.9% to 17.4%) | 1.66 (1.36 to 2.44) | 13.1% (8.5% to 27.3%) | 83.1% | partial and brittle |
| Llama 3.1-8B | 17.2% (8.6% to 27.6%) | 71.4% (46.2% to 93.3%) | 28.6% (6.7% to 53.8%) | 50.0% (16.7% to 83.3%) | 0.0% (0.0% to 0.0%) | 19.3% (14.2% to 24.5%) | 0.80 (0.71 to 1.74) | 2.6% (0.0% to 25.6%) | 62.4% | fragmentary |

## Interpretation
- Coverage should be interpreted jointly as broad recovery versus noisy over-coverage; soft precision and soft FDR make that explicit.
- Fidelity is reported in two views: soft-edge direction accuracy is primary, whereas hard-edge direction accuracy is a stricter secondary sensitivity check.
- Stability is auxiliary only; sparse models can look stable because consistent non-detection is easy to reproduce.
- Sparse models can also look superficially precise, because a small denominator can inflate precision even when clinically important edges are missed.
- No single composite index is used for primary interpretation.
