# World Model Evaluation Report (v2 — Corrected)

## Key Correction from v1

v1 treated split-half reliability as unconditionally positive, rewarding
models that were *consistently wrong*. A model missing 51/55 gold-standard
edges could score 85.7% split-half agreement by reliably failing to detect
the same edges every time.

v2 decomposes consistency into:

- **Veridical consistency**: agreement on *correctly* detected edges (rewarded)
- **Confabulatory rigidity**: agreement on *incorrectly* missed edges (penalised)

## Summary

| Model | WMS | Label | Coverage | Fidelity | Stability | Discrim. | Confab Penalty | Raw Split-Half |
|---|---|---|---|---|---|---|---|---|
| deepseek-r1 | **0.393** | Weak world model | 0.621 | 0.819 | 0.670 | 0.326 | 1.000 | 79.5% |
| kimi-k2.5 | **0.378** | Weak world model | 0.741 | 0.754 | 0.488 | 0.378 | 1.000 | 63.0% |
| llama-3.1-8b | **0.188** | Fragmentary world model | 0.172 | 0.653 | 0.579 | 0.106 | 1.000 | 89.0% |
| mistral-small-24b | **0.331** | Weak world model | 0.431 | 0.794 | 0.684 | 0.252 | 1.000 | 82.1% |
| qwen3-next-80b-instruct | **0.347** | Weak world model | 0.397 | 0.802 | 0.769 | 0.287 | 1.000 | 89.3% |

## Split-Half Decomposition

| Model | Raw Agreement | Veridical Agreement | Confab Agreement |
|---|---|---|---|
| deepseek-r1 | 79.5% | 78.2% | 80.7% |
| kimi-k2.5 | 63.0% | 49.2% | 76.9% |
| llama-3.1-8b | 89.0% | 62.4% | 91.5% |
| mistral-small-24b | 82.1% | 83.1% | 81.6% |
| qwen3-next-80b-instruct | 89.3% | 90.9% | 88.6% |

## Edge Entropy Decomposition

| Model | Veridical Entropy | Confab Entropy | Veridical n | Confab n |
|---|---|---|---|---|
| deepseek-r1 | 0.498 | 0.535 | 143 | 227 |
| kimi-k2.5 | 0.518 | 0.511 | 157 | 215 |
| llama-3.1-8b | 0.489 | 0.328 | 35 | 326 |
| mistral-small-24b | 0.536 | 0.524 | 94 | 269 |
| qwen3-next-80b-instruct | 0.440 | 0.396 | 91 | 275 |

## Interpretation

### deepseek-r1: Weak world model (WMS = 0.393)

Key issues: high confabulatory rigidity (81%) — systematically and consistently wrong; large rigidity penalty (1.00).

### kimi-k2.5: Weak world model (WMS = 0.378)

Key issues: large rigidity penalty (1.00).

### llama-3.1-8b: Fragmentary world model (WMS = 0.188)

Key issues: critically low edge coverage (< 20%); pathological SNR (0.80) — responds more to noise than signal; high confabulatory rigidity (91%) — systematically and consistently wrong; large rigidity penalty (1.00).

### mistral-small-24b: Weak world model (WMS = 0.331)

Key issues: low edge coverage; weak SNR (1.66); high confabulatory rigidity (82%) — systematically and consistently wrong; large rigidity penalty (1.00).

### qwen3-next-80b-instruct: Weak world model (WMS = 0.347)

Key issues: low edge coverage; weak SNR (1.87); high confabulatory rigidity (89%) — systematically and consistently wrong; large rigidity penalty (1.00).
