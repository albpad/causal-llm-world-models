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
| kimi-k2.5 | **0.428** | Weak world model | 0.745 | 0.787 | 0.606 | 0.468 | 0.975 | 75.5% |

## Split-Half Decomposition

| Model | Raw Agreement | Veridical Agreement | Confab Agreement |
|---|---|---|---|
| kimi-k2.5 | 75.5% | 71.7% | 81.0% |

## Edge Entropy Decomposition

| Model | Veridical Entropy | Confab Entropy | Veridical n | Confab n |
|---|---|---|---|---|
| kimi-k2.5 | 0.561 | 0.487 | 112 | 129 |

## Interpretation

### kimi-k2.5: Weak world model (WMS = 0.428)

Key issues: high confabulatory rigidity (81%) — systematically and consistently wrong; large rigidity penalty (0.97).
