# Domain-Based World-Model Evaluation

Primary interpretation uses Coverage, Fidelity, and Discriminability. Stability is auxiliary and interpreted only conditionally on coverage.

| Model | Soft recall | Soft precision | Soft FDR | Soft dir. acc. | Hard dir. acc. | SID rate | SNR | Detection power | Veridical split-half | Regime |
|---|---|---|---|---|---|---|---|---|---:|---|
| DeepSeek-R1 | 62.1% (50.0% to 74.1%) | 60.0% (50.0% to 71.1%) | 40.0% (28.9% to 50.0%) | 77.8% (63.2% to 90.2%) | 66.7% (20.0% to 100.0%) | 14.0% (9.9% to 18.5%) | 2.14 (1.42 to 2.82) | 17.3% (3.6% to 30.1%) | 78.6% | balanced |
| Kimi K2.5 | 74.1% (62.1% to 84.5%) | 66.2% (56.9% to 76.3%) | 33.8% (23.7% to 43.1%) | 67.4% (53.1% to 80.0%) | 50.0% (0.0% to 100.0%) | 16.7% (12.2% to 21.1%) | 2.46 (1.81 to 3.17) | 20.7% (12.5% to 29.1%) | 49.5% | broad but noisy |
| Qwen3-Next-80B-A3B-Instruct | 39.7% (27.6% to 53.4%) | 53.5% (40.6% to 67.5%) | 46.5% (32.5% to 59.4%) | 73.9% (55.0% to 91.3%) | 0.0% (0.0% to 0.0%) | 13.5% (9.3% to 18.1%) | 1.87 (1.49 to 2.94) | 15.6% (10.6% to 20.8%) | 91.4% | partial and brittle |
| Mistral-Small-24B | 43.1% (31.0% to 55.2%) | 62.5% (49.1% to 75.8%) | 37.5% (24.2% to 50.9%) | 72.0% (53.6% to 88.9%) | 0.0% (0.0% to 0.0%) | 13.1% (8.9% to 17.4%) | 1.66 (1.32 to 2.51) | 13.1% (8.0% to 28.3%) | 83.2% | partial and brittle |
| Gemma 4 31B | 41.4% (29.3% to 53.4%) | 66.7% (53.1% to 81.5%) | 33.3% (18.5% to 46.9%) | 70.8% (52.2% to 88.0%) | 25.0% (0.0% to 100.0%) | 16.2% (11.5% to 20.9%) | 1.80 (1.20 to 2.88) | 12.0% (2.1% to 29.3%) | 77.8% | partial and brittle |
| Llama 3.1-8B | 17.2% (8.6% to 27.6%) | 71.4% (46.7% to 92.9%) | 28.6% (7.1% to 53.3%) | 50.0% (16.7% to 80.0%) | 0.0% (0.0% to 0.0%) | 19.3% (14.6% to 24.9%) | 0.80 (0.72 to 1.70) | 2.6% (0.0% to 25.9%) | 62.4% | fragmentary |

## Interpretation
- Coverage should be interpreted jointly as broad recovery versus noisy over-coverage; soft precision and soft FDR make that explicit.
- Fidelity is reported in two views: soft-edge direction accuracy is primary, whereas hard-edge direction accuracy is a stricter secondary sensitivity check.
- Stability is auxiliary only; sparse models can look stable because consistent non-detection is easy to reproduce.
- Sparse models can also look superficially precise, because a small denominator can inflate precision even when clinically important edges are missed.
- No single composite index is used for primary interpretation.
