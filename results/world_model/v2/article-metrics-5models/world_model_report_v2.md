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
| deepseek-r1 | **0.393** | Weak world model | 0.621 | 0.819 | 0.669 | 0.326 | 1.000 | 79.1% |
| kimi-k2.5 | **0.379** | Weak world model | 0.741 | 0.754 | 0.495 | 0.378 | 1.000 | 62.9% |
| llama-3.1-8b | **0.183** | Fragmentary world model | 0.172 | 0.653 | 0.555 | 0.106 | 1.000 | 88.8% |
| mistral-small-24b | **0.331** | Weak world model | 0.431 | 0.794 | 0.685 | 0.252 | 1.000 | 81.6% |
| qwen3-next-80b-instruct | **0.347** | Weak world model | 0.397 | 0.802 | 0.771 | 0.287 | 1.000 | 90.3% |

## Split-Half Decomposition

| Model | Raw Agreement | Veridical Agreement | Confab Agreement |
|---|---|---|---|
| deepseek-r1 | 79.1% | 78.1% | 80.1% |
| kimi-k2.5 | 62.9% | 50.3% | 75.5% |
| llama-3.1-8b | 88.8% | 58.4% | 91.7% |
| mistral-small-24b | 81.6% | 83.2% | 80.8% |
| qwen3-next-80b-instruct | 90.3% | 91.2% | 89.9% |

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

Key issues: high confabulatory rigidity (80%) — systematically and consistently wrong; large rigidity penalty (1.00).

### kimi-k2.5: Weak world model (WMS = 0.379)

Key issues: large rigidity penalty (1.00).

### llama-3.1-8b: Fragmentary world model (WMS = 0.183)

Key issues: critically low edge coverage (< 20%); pathological SNR (0.80) — responds more to noise than signal; high confabulatory rigidity (92%) — systematically and consistently wrong; large rigidity penalty (1.00).

### mistral-small-24b: Weak world model (WMS = 0.331)

Key issues: low edge coverage; weak SNR (1.66); high confabulatory rigidity (81%) — systematically and consistently wrong; large rigidity penalty (1.00).

### qwen3-next-80b-instruct: Weak world model (WMS = 0.347)

Key issues: low edge coverage; weak SNR (1.87); high confabulatory rigidity (90%) — systematically and consistently wrong; large rigidity penalty (1.00).
