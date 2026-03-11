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
| kimi-k2.5 | **0.371** | Weak world model | 0.400 | 0.798 | 0.615 | 0.320 | 0.661 | 66.9% |
| llama-3.1-8b | **0.101** | No coherent world model | 0.073 | 0.351 | 0.684 | 0.055 | 1.000 | 85.7% |

## Split-Half Decomposition

| Model | Raw Agreement | Veridical Agreement | Confab Agreement |
|---|---|---|---|
| kimi-k2.5 | 66.9% | 68.6% | 66.1% |
| llama-3.1-8b | 85.7% | 97.0% | 85.5% |

## Edge Entropy Decomposition

| Model | Veridical Entropy | Confab Entropy | Veridical n | Confab n |
|---|---|---|---|---|
| kimi-k2.5 | 0.490 | 0.592 | 61 | 135 |
| llama-3.1-8b | 0.745 | 0.335 | 6 | 223 |

## Interpretation

### kimi-k2.5: Weak world model (WMS = 0.371)

Key issues: low edge coverage; large rigidity penalty (0.66).

### llama-3.1-8b: No coherent world model (WMS = 0.101)

Key issues: critically low edge coverage (< 20%); pathological SNR (0.46) — responds more to noise than signal; high confabulatory rigidity (86%) — systematically and consistently wrong; large rigidity penalty (1.00).
