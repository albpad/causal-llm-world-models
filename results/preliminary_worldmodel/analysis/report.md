# KG1 vs KG2 Analysis Report

## 1. Aggregate Performance

| Model | Rec Acc | Exc Acc | Precision | Cond | Unc | Null Spec |
|---|---|---|---|---|---|---|
| deepseek-r1 | 69% | 77% | 93% | 95% | 0% | 14% |
| mistral-small-24b | 80% | 67% | 92% | 100% | 100% | 43% |
| qwen3-next-80b-instruct | 63% | 59% | 88% | 100% | 100% | 14% |

## 2. KG2 Edge Detection Matrix

| Edge | deepseek-r1 | mistral-small-24b | qwen3-next-80b-instruct |
|---|---|---|---|
| S10R | - (7%) | - (10%) | - (3%) |
| S112 | - (0%) | - (0%) | - (15%) |
| S115 | - (0%) | - (0%) | - (0%) |
| S12 | - (0%) | - (0%) | - (7%) |
| S14 | - (0%) | - (0%) | - (0%) |
| S15R | - (0%) | - (0%) | - (0%) |
| S16R | - (33%) | - (11%) | - (10%) |
| S17R | - (30%) | - (12%) | - (10%) |
| S18R | - (30%) | - (12%) | - (10%) |
| S19R | - (0%) | - (29%) | - (0%) |
| S22 | - (10%) | - (0%) | - (0%) |
| S23R | - (14%) | - (8%) | - (12%) |
| S24R | - (0%) | - (0%) | - (0%) |
| S27 | - (5%) | - (0%) | - (15%) |
| S28 | - (15%) | - (8%) | - (11%) |
| S35R | - (0%) | - (12%) | - (43%) |
| S38R | - (11%) | - (0%) | - (12%) |
| S39R | - (23%) | - (4%) | - (8%) |
| S40R | - (9%) | - (10%) | - (10%) |
| S41R | - (9%) | - (10%) | - (10%) |
| S42R | - (29%) | - (6%) | - (6%) |
| S43 | - (0%) | - (0%) | - (7%) |
| S45 | - (9%) | - (10%) | - (10%) |
| S46 | - (5%) | - (6%) | - (6%) |
| S47R | - (0%) | - (12%) | - (43%) |
| S49R | - (9%) | - (10%) | - (10%) |
| S4R | - (22%) | - (12%) | - (18%) |
| S52R | - (29%) | - (14%) | - (17%) |
| S5R | - (13%) | - (7%) | - (10%) |
| S68R | - (29%) | - (14%) | - (17%) |
| S6R | - (0%) | - (0%) | - (0%) |
| S72R | - (29%) | - (14%) | - (17%) |
| S7R | - (4%) | - (0%) | - (0%) |
| S8 | - (0%) | - (0%) | - (0%) |
| S80 | - (0%) | - (0%) | - (0%) |
| S9R | - (0%) | - (12%) | - (10%) |
| SA2 | - (0%) | - (0%) | - (0%) |

## 3. Divergence Taxonomy (84 total)


### missing_edge (75 instances)
- **A1-P1** x mistral-small-24b: tlm should be excluded but no significant shift detected
- **A1-P1** x qwen3-next-80b-instruct: tlm should be excluded but no significant shift detected
- **A1-P2** x mistral-small-24b: total_laryngectomy should be excluded but no significant shift detected
- **A1-P2** x qwen3-next-80b-instruct: total_laryngectomy should be excluded but no significant shift detected
- **A1-P2** x deepseek-r1: total_laryngectomy should be excluded but no significant shift detected
- **A1-P3** x mistral-small-24b: total_laryngectomy should be excluded but no significant shift detected
- **A1-P3** x qwen3-next-80b-instruct: total_laryngectomy should be excluded but no significant shift detected
- **A1-P3** x deepseek-r1: total_laryngectomy should be excluded but no significant shift detected
- **A1-NULL** x mistral-small-24b: total_laryngectomy should be excluded but no significant shift detected
- **A1-NULL** x mistral-small-24b: concurrent_crt should be excluded but no significant shift detected

### wrong_direction (9 instances)
- **A2-P2** x qwen3-next-80b-instruct: rt_alone should remain viable but dropped (73%->7%)
- **A2-P2** x deepseek-r1: rt_alone should remain viable but dropped (87%->20%)
- **A2-P3** x mistral-small-24b: tlm should remain viable but dropped (100%->13%)
- **A2-P3** x deepseek-r1: tlm should remain viable but dropped (93%->7%)
- **B1-P4** x deepseek-r1: surgical_lp should remain viable but dropped (100%->45%)
- **B1-P9** x deepseek-r1: ophl_any should remain viable but dropped (73%->0%)
- **B1-NULL2** x qwen3-next-80b-instruct: tlm should remain viable but dropped (100%->33%)
- **B1-NULL2** x deepseek-r1: tlm should remain viable but dropped (80%->13%)
- **C1-P5** x qwen3-next-80b-instruct: total_laryngectomy should remain viable but dropped (53%->0%)

### wrong_conditionality (0 instances)

### magnitude_misalignment (0 instances)

### spurious_edge (0 instances)

## 4. Statistical Tests Summary

Total tests: 1051, Significant (BH-FDR q=0.05): 66 (6%)