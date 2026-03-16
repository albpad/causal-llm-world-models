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
| kimi-k2.5 | **0.379** | Weak world model | 0.741 | 0.756 | 0.488 | 0.378 | 1.000 | 63.0% |
| llama-3.1-8b | **0.188** | Fragmentary world model | 0.172 | 0.653 | 0.579 | 0.106 | 1.000 | 88.5% |

## Split-Half Decomposition

| Model | Raw Agreement | Veridical Agreement | Confab Agreement |
|---|---|---|---|
| kimi-k2.5 | 63.0% | 49.2% | 76.9% |
| llama-3.1-8b | 88.5% | 62.4% | 91.0% |

## Edge Entropy Decomposition

| Model | Veridical Entropy | Confab Entropy | Veridical n | Confab n |
|---|---|---|---|---|
| kimi-k2.5 | 0.518 | 0.511 | 157 | 215 |
| llama-3.1-8b | 0.489 | 0.328 | 35 | 326 |

## Interpretation

### kimi-k2.5: Weak world model (WMS = 0.379)

Key issues: large rigidity penalty (1.00).

### llama-3.1-8b: Fragmentary world model (WMS = 0.188)

Key issues: critically low edge coverage (< 20%); pathological SNR (0.80) — responds more to noise than signal; high confabulatory rigidity (91%) — systematically and consistently wrong; large rigidity penalty (1.00).
