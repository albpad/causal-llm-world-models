# KG1 vs KG2 Analysis Report

## 1. Aggregate Performance

| Model | Rec Acc | Exc Acc | Precision | Cond | Unc | Null Spec |
|---|---|---|---|---|---|---|
| deepseek-r1 | 66% | 81% | 94% | 92% | 67% | 17% |
| gemma-4-31b-it | 77% | 72% | 93% | 100% | 100% | 33% |
| kimi-k2.5 | 73% | 86% | 96% | 100% | 100% | 17% |
| llama-3.1-8b | 86% | 19% | 84% | 100% | 100% | 25% |
| mistral-small-24b | 79% | 70% | 92% | 100% | 100% | 25% |
| qwen3-next-80b-instruct | 61% | 71% | 91% | 100% | 67% | 17% |

## 2. KG2 Edge Detection Matrix

| Edge | deepseek-r1 | gemma-4-31b-it | kimi-k2.5 | llama-3.1-8b | mistral-small-24b | qwen3-next-80b-instruct |
|---|---|---|---|---|---|---|
| S10R | - (7%) | - (0%) | - (5%) | - (10%) | - (10%) | - (3%) |
| S111R | - (11%) | - (40%) | - (18%) | - (0%) | - (12%) | - (12%) |
| S112 | - (0%) | - (0%) | - (8%) | - (0%) | - (0%) | - (15%) |
| S115 | - (8%) | - (0%) | - (0%) | - (0%) | - (0%) | - (7%) |
| S116 | - (0%) | - (33%) | - (22%) | - (0%) | - (0%) | - (0%) |
| S119R | - (0%) | - (33%) | - (11%) | - (0%) | - (0%) | - (0%) |
| S12 | - (0%) | - (0%) | - (3%) | - (0%) | - (0%) | - (7%) |
| S120R | - (0%) | - (33%) | - (22%) | - (0%) | - (0%) | - (0%) |
| S121R | - (36%) | - (20%) | - (36%) | - (9%) | - (4%) | - (15%) |
| S129 | + (62%) | + (67%) | + (56%) | - (25%) | - (38%) | - (50%) |
| S13 | - (21%) | - (25%) | - (18%) | - (0%) | - (19%) | - (6%) |
| S14 | - (0%) | - (0%) | - (0%) | - (0%) | - (0%) | - (0%) |
| S15R | - (0%) | - (0%) | - (0%) | - (0%) | - (0%) | - (0%) |
| S16R | - (33%) | - (25%) | - (27%) | - (0%) | - (11%) | - (10%) |
| S17R | - (30%) | - (25%) | - (36%) | - (0%) | - (12%) | - (10%) |
| S18R | - (30%) | - (25%) | - (36%) | - (0%) | - (12%) | - (10%) |
| S19R | - (6%) | - (0%) | - (4%) | - (5%) | - (11%) | - (4%) |
| S20R | - (11%) | - (0%) | - (12%) | - (0%) | - (0%) | - (0%) |
| S21 | - (0%) | - (0%) | - (0%) | - (0%) | - (0%) | - (0%) |
| S22 | - (10%) | - (33%) | - (10%) | - (0%) | - (0%) | - (0%) |
| S23R | - (14%) | - (17%) | - (13%) | - (4%) | - (8%) | - (12%) |
| S24R | - (0%) | - (0%) | - (0%) | - (0%) | - (0%) | - (0%) |
| S27 | - (5%) | - (0%) | - (5%) | - (0%) | - (0%) | - (15%) |
| S28 | - (15%) | - (18%) | - (10%) | - (4%) | - (8%) | - (11%) |
| S30 | - (0%) | - (33%) | - (22%) | - (0%) | - (0%) | - (0%) |
| S31R | - (0%) | - (33%) | - (22%) | - (0%) | - (0%) | - (0%) |
| S35R | - (0%) | - (0%) | - (0%) | - (0%) | - (12%) | - (43%) |
| S38R | - (11%) | - (0%) | - (0%) | - (0%) | - (0%) | - (12%) |
| S39R | - (19%) | - (6%) | - (6%) | - (0%) | - (2%) | - (21%) |
| S40R | - (9%) | - (12%) | - (18%) | - (0%) | - (10%) | - (10%) |
| S41R | - (9%) | - (12%) | - (18%) | - (0%) | - (10%) | - (10%) |
| S42R | - (29%) | - (13%) | - (14%) | - (0%) | - (6%) | - (6%) |
| S43 | - (0%) | - (0%) | - (2%) | - (3%) | - (0%) | - (5%) |
| S45 | - (9%) | - (12%) | - (18%) | - (0%) | - (10%) | - (10%) |
| S46 | - (5%) | - (6%) | - (10%) | - (0%) | - (6%) | - (6%) |
| S47R | - (0%) | - (0%) | - (0%) | - (0%) | - (12%) | - (43%) |
| S49R | - (9%) | - (12%) | - (18%) | - (0%) | - (10%) | - (10%) |
| S4R | - (22%) | - (29%) | - (15%) | - (6%) | - (12%) | - (18%) |
| S52R | - (31%) | - (8%) | - (15%) | - (0%) | - (12%) | - (13%) |
| S55R | - (0%) | - (33%) | - (22%) | - (0%) | - (0%) | - (0%) |
| S5R | - (13%) | - (19%) | - (6%) | - (0%) | - (7%) | - (10%) |
| S67 | - (14%) | - (0%) | - (10%) | - (25%) | - (12%) | - (9%) |
| S68R | - (34%) | - (9%) | - (16%) | - (0%) | - (13%) | - (14%) |
| S69R | - (9%) | - (2%) | - (11%) | - (0%) | - (4%) | - (4%) |
| S6R | - (0%) | - (0%) | - (2%) | - (0%) | - (0%) | - (0%) |
| S70 | - (14%) | - (0%) | - (14%) | - (0%) | - (14%) | - (10%) |
| S72R | - (34%) | - (9%) | - (16%) | - (0%) | - (13%) | - (14%) |
| S73R | - (14%) | - (0%) | - (10%) | - (25%) | - (12%) | - (9%) |
| S74R | - (0%) | - (0%) | - (0%) | - (0%) | - (0%) | - (0%) |
| S75R | - (10%) | - (0%) | - (0%) | - (0%) | - (0%) | - (0%) |
| S77R | - (14%) | - (7%) | - (13%) | - (0%) | - (6%) | - (5%) |
| S7R | - (4%) | - (0%) | - (8%) | - (0%) | - (0%) | - (0%) |
| S8 | - (0%) | - (0%) | - (5%) | - (0%) | - (0%) | - (0%) |
| S80 | - (0%) | - (0%) | - (1%) | - (0%) | - (0%) | - (0%) |
| S84 | - (11%) | - (40%) | - (18%) | - (0%) | - (12%) | - (12%) |
| S88 | - (22%) | - (45%) | - (27%) | - (0%) | - (25%) | - (12%) |
| S89 | - (33%) | - (50%) | - (36%) | - (0%) | - (38%) | - (11%) |
| S9R | - (0%) | - (0%) | - (18%) | - (43%) | - (12%) | - (10%) |
| SA2 | - (0%) | - (0%) | - (10%) | - (0%) | - (0%) | - (0%) |
| SA6 | + (62%) | - (25%) | - (50%) | - (25%) | - (0%) | - (0%) |

## 3. Divergence Taxonomy (291 total)


### missing_edge (244 instances)
- **A1-P1** x llama-3.1-8b: tlm should be excluded but no significant shift detected
- **A1-P1** x mistral-small-24b: tlm should be excluded but no significant shift detected
- **A1-P1** x qwen3-next-80b-instruct: tlm should be excluded but no significant shift detected
- **A1-P2** x deepseek-r1: total_laryngectomy should be excluded but no significant shift detected
- **A1-P2** x llama-3.1-8b: total_laryngectomy should be excluded but no significant shift detected
- **A1-P2** x gemma-4-31b-it: total_laryngectomy should be excluded but no significant shift detected
- **A1-P2** x mistral-small-24b: total_laryngectomy should be excluded but no significant shift detected
- **A1-P2** x kimi-k2.5: total_laryngectomy should be excluded but no significant shift detected
- **A1-P2** x qwen3-next-80b-instruct: total_laryngectomy should be excluded but no significant shift detected
- **A1-P3** x deepseek-r1: total_laryngectomy should be excluded but no significant shift detected

### wrong_direction (47 instances)
- **A1-P1** x gemma-4-31b-it: surgical_lp should remain viable but dropped (100%->7%)
- **A1-P2** x llama-3.1-8b: nonsurgical_lp should remain viable but dropped (100%->47%)
- **A1-P2** x gemma-4-31b-it: tlm should remain viable but dropped (100%->47%)
- **A1-P2** x kimi-k2.5: tlm should remain viable but dropped (100%->40%)
- **A1-P3** x kimi-k2.5: tlm should remain viable but dropped (100%->27%)
- **A2-P2** x deepseek-r1: rt_alone should remain viable but dropped (87%->20%)
- **A2-P2** x gemma-4-31b-it: surgical_lp should remain viable but dropped (100%->0%)
- **A2-P2** x qwen3-next-80b-instruct: rt_alone should remain viable but dropped (73%->7%)
- **A2-P3** x deepseek-r1: tlm should remain viable but dropped (93%->7%)
- **A2-P3** x gemma-4-31b-it: tlm should remain viable but dropped (100%->7%)

### wrong_conditionality (0 instances)

### magnitude_misalignment (0 instances)

### spurious_edge (0 instances)

## 4. Statistical Tests Summary

Total tests: 3823, Significant (BH-FDR q=0.05): 293 (8%)