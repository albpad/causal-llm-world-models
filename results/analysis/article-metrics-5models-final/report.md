# KG1 vs KG2 Analysis Report

## 1. Aggregate Performance

| Model | Rec Acc | Exc Acc | Precision | Cond | Unc | Null Spec |
|---|---|---|---|---|---|---|
| deepseek-r1 | 66% | 81% | 94% | 92% | 67% | 17% |
| kimi-k2.5 | 73% | 87% | 96% | 100% | 100% | 17% |
| llama-3.1-8b | 86% | 19% | 84% | 100% | 100% | 25% |
| mistral-small-24b | 79% | 70% | 92% | 100% | 100% | 25% |
| qwen3-next-80b-instruct | 61% | 71% | 91% | 100% | 67% | 17% |

## 2. KG2 Edge Detection Matrix

| Edge | deepseek-r1 | kimi-k2.5 | llama-3.1-8b | mistral-small-24b | qwen3-next-80b-instruct |
|---|---|---|---|---|---|
| S10R | - (7%) | - (5%) | - (10%) | - (10%) | - (3%) |
| S111R | - (11%) | - (18%) | - (0%) | - (12%) | - (12%) |
| S112 | - (0%) | - (8%) | - (0%) | - (0%) | - (15%) |
| S115 | - (8%) | - (0%) | - (0%) | - (0%) | - (7%) |
| S116 | - (0%) | - (22%) | - (0%) | - (0%) | - (0%) |
| S119R | - (0%) | - (11%) | - (0%) | - (0%) | - (0%) |
| S12 | - (0%) | - (3%) | - (0%) | - (0%) | - (7%) |
| S120R | - (0%) | - (22%) | - (0%) | - (0%) | - (0%) |
| S121R | - (36%) | - (36%) | - (9%) | - (4%) | - (15%) |
| S129 | + (62%) | + (56%) | - (25%) | - (38%) | - (50%) |
| S13 | - (21%) | - (18%) | - (0%) | - (19%) | - (6%) |
| S14 | - (0%) | - (0%) | - (0%) | - (0%) | - (0%) |
| S15R | - (0%) | - (0%) | - (0%) | - (0%) | - (0%) |
| S16R | - (33%) | - (27%) | - (0%) | - (11%) | - (10%) |
| S17R | - (30%) | - (36%) | - (0%) | - (12%) | - (10%) |
| S18R | - (30%) | - (36%) | - (0%) | - (12%) | - (10%) |
| S19R | - (6%) | - (4%) | - (5%) | - (11%) | - (4%) |
| S20R | - (11%) | - (12%) | - (0%) | - (0%) | - (0%) |
| S21 | - (0%) | - (0%) | - (0%) | - (0%) | - (0%) |
| S22 | - (10%) | - (10%) | - (0%) | - (0%) | - (0%) |
| S23R | - (14%) | - (13%) | - (4%) | - (8%) | - (12%) |
| S24R | - (0%) | - (0%) | - (0%) | - (0%) | - (0%) |
| S27 | - (5%) | - (5%) | - (0%) | - (0%) | - (15%) |
| S28 | - (15%) | - (10%) | - (4%) | - (8%) | - (11%) |
| S30 | - (0%) | - (22%) | - (0%) | - (0%) | - (0%) |
| S31R | - (0%) | - (22%) | - (0%) | - (0%) | - (0%) |
| S35R | - (0%) | - (0%) | - (0%) | - (12%) | - (43%) |
| S38R | - (11%) | - (0%) | - (0%) | - (0%) | - (12%) |
| S39R | - (19%) | - (6%) | - (0%) | - (2%) | - (21%) |
| S40R | - (9%) | - (18%) | - (0%) | - (10%) | - (10%) |
| S41R | - (9%) | - (18%) | - (0%) | - (10%) | - (10%) |
| S42R | - (29%) | - (14%) | - (0%) | - (6%) | - (6%) |
| S43 | - (0%) | - (2%) | - (3%) | - (0%) | - (5%) |
| S45 | - (9%) | - (18%) | - (0%) | - (10%) | - (10%) |
| S46 | - (5%) | - (10%) | - (0%) | - (6%) | - (6%) |
| S47R | - (0%) | - (0%) | - (0%) | - (12%) | - (43%) |
| S49R | - (9%) | - (18%) | - (0%) | - (10%) | - (10%) |
| S4R | - (22%) | - (15%) | - (6%) | - (12%) | - (18%) |
| S52R | - (31%) | - (15%) | - (0%) | - (12%) | - (13%) |
| S55R | - (0%) | - (22%) | - (0%) | - (0%) | - (0%) |
| S5R | - (13%) | - (6%) | - (0%) | - (7%) | - (10%) |
| S67 | - (14%) | - (10%) | - (25%) | - (12%) | - (9%) |
| S68R | - (34%) | - (16%) | - (0%) | - (13%) | - (14%) |
| S69R | - (9%) | - (11%) | - (0%) | - (4%) | - (4%) |
| S6R | - (0%) | - (2%) | - (0%) | - (0%) | - (0%) |
| S70 | - (14%) | - (14%) | - (0%) | - (14%) | - (10%) |
| S72R | - (34%) | - (16%) | - (0%) | - (13%) | - (14%) |
| S73R | - (14%) | - (10%) | - (25%) | - (12%) | - (9%) |
| S74R | - (0%) | - (0%) | - (0%) | - (0%) | - (0%) |
| S75R | - (10%) | - (0%) | - (0%) | - (0%) | - (0%) |
| S77R | - (14%) | - (13%) | - (0%) | - (6%) | - (5%) |
| S7R | - (4%) | - (8%) | - (0%) | - (0%) | - (0%) |
| S8 | - (0%) | - (5%) | - (0%) | - (0%) | - (0%) |
| S80 | - (0%) | - (1%) | - (0%) | - (0%) | - (0%) |
| S84 | - (11%) | - (18%) | - (0%) | - (12%) | - (12%) |
| S88 | - (22%) | - (27%) | - (0%) | - (25%) | - (12%) |
| S89 | - (33%) | - (36%) | - (0%) | - (38%) | - (11%) |
| S9R | - (0%) | - (18%) | - (43%) | - (12%) | - (10%) |
| SA2 | - (0%) | - (10%) | - (0%) | - (0%) | - (0%) |
| SA6 | + (62%) | - (50%) | - (25%) | - (0%) | - (0%) |

## 3. Divergence Taxonomy (241 total)


### missing_edge (201 instances)
- **A1-P1** x mistral-small-24b: tlm should be excluded but no significant shift detected
- **A1-P1** x llama-3.1-8b: tlm should be excluded but no significant shift detected
- **A1-P1** x qwen3-next-80b-instruct: tlm should be excluded but no significant shift detected
- **A1-P2** x mistral-small-24b: total_laryngectomy should be excluded but no significant shift detected
- **A1-P2** x llama-3.1-8b: total_laryngectomy should be excluded but no significant shift detected
- **A1-P2** x qwen3-next-80b-instruct: total_laryngectomy should be excluded but no significant shift detected
- **A1-P2** x deepseek-r1: total_laryngectomy should be excluded but no significant shift detected
- **A1-P2** x kimi-k2.5: total_laryngectomy should be excluded but no significant shift detected
- **A1-P3** x mistral-small-24b: total_laryngectomy should be excluded but no significant shift detected
- **A1-P3** x llama-3.1-8b: total_laryngectomy should be excluded but no significant shift detected

### wrong_direction (40 instances)
- **A1-P2** x llama-3.1-8b: nonsurgical_lp should remain viable but dropped (100%->47%)
- **A1-P2** x kimi-k2.5: tlm should remain viable but dropped (100%->40%)
- **A1-P3** x kimi-k2.5: tlm should remain viable but dropped (100%->27%)
- **A2-P2** x qwen3-next-80b-instruct: rt_alone should remain viable but dropped (73%->7%)
- **A2-P2** x deepseek-r1: rt_alone should remain viable but dropped (87%->20%)
- **A2-P3** x mistral-small-24b: tlm should remain viable but dropped (100%->13%)
- **A2-P3** x deepseek-r1: tlm should remain viable but dropped (93%->7%)
- **B1-P4** x deepseek-r1: surgical_lp should remain viable but dropped (100%->45%)
- **B1-P4** x kimi-k2.5: surgical_lp should remain viable but dropped (93%->38%)
- **B1-P9** x deepseek-r1: ophl_any should remain viable but dropped (73%->0%)

### wrong_conditionality (0 instances)

### magnitude_misalignment (0 instances)

### spurious_edge (0 instances)

## 4. Statistical Tests Summary

Total tests: 3261, Significant (BH-FDR q=0.05): 254 (8%)