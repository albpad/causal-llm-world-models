# KG1 vs KG2 Analysis Report

## 1. Aggregate Performance

| Model | Rec Acc | Exc Acc | Precision | Cond | Unc | Null Spec |
|---|---|---|---|---|---|---|
| kimi-k2.5 | 73% | 87% | 96% | 100% | 100% | 17% |
| llama-3.1-8b | 86% | 19% | 84% | 100% | 100% | 25% |

## 2. KG2 Edge Detection Matrix

| Edge | kimi-k2.5 | llama-3.1-8b |
|---|---|---|
| S10R | - (5%) | - (10%) |
| S111R | - (18%) | - (0%) |
| S112 | - (8%) | - (0%) |
| S115 | - (0%) | - (0%) |
| S116 | - (22%) | - (0%) |
| S119R | - (11%) | - (0%) |
| S12 | - (3%) | - (0%) |
| S120R | - (22%) | - (0%) |
| S121R | - (36%) | - (9%) |
| S129 | + (56%) | - (25%) |
| S13 | - (18%) | - (0%) |
| S14 | - (0%) | - (0%) |
| S15R | - (0%) | - (0%) |
| S16R | - (27%) | - (0%) |
| S17R | - (36%) | - (0%) |
| S18R | - (36%) | - (0%) |
| S19R | - (2%) | - (5%) |
| S20R | - (12%) | - (0%) |
| S21 | - (0%) | - (0%) |
| S22 | - (10%) | - (0%) |
| S23R | - (13%) | - (4%) |
| S24R | - (0%) | - (0%) |
| S27 | - (5%) | - (0%) |
| S28 | - (10%) | - (4%) |
| S30 | - (22%) | - (0%) |
| S31R | - (22%) | - (0%) |
| S35R | - (0%) | - (0%) |
| S38R | - (0%) | - (0%) |
| S39R | - (6%) | - (0%) |
| S40R | - (18%) | - (0%) |
| S41R | - (18%) | - (0%) |
| S42R | - (14%) | - (0%) |
| S43 | - (2%) | - (3%) |
| S45 | - (18%) | - (0%) |
| S46 | - (10%) | - (0%) |
| S47R | - (0%) | - (0%) |
| S49R | - (18%) | - (0%) |
| S4R | - (15%) | - (6%) |
| S52R | - (15%) | - (0%) |
| S55R | - (22%) | - (0%) |
| S5R | - (6%) | - (0%) |
| S67 | - (10%) | - (25%) |
| S68R | - (16%) | - (0%) |
| S69R | - (11%) | - (0%) |
| S6R | - (2%) | - (0%) |
| S70 | - (14%) | - (0%) |
| S72R | - (16%) | - (0%) |
| S73R | - (10%) | - (25%) |
| S74R | - (0%) | - (0%) |
| S75R | - (0%) | - (0%) |
| S77R | - (13%) | - (0%) |
| S7R | - (6%) | - (0%) |
| S8 | - (5%) | - (0%) |
| S80 | - (1%) | - (0%) |
| S84 | - (18%) | - (0%) |
| S88 | - (27%) | - (0%) |
| S89 | - (36%) | - (0%) |
| S9R | - (18%) | - (43%) |
| SA2 | - (10%) | - (0%) |
| SA6 | - (50%) | - (25%) |

## 3. Divergence Taxonomy (107 total)


### missing_edge (91 instances)
- **A1-P1** x llama-3.1-8b: tlm should be excluded but no significant shift detected
- **A1-P2** x kimi-k2.5: total_laryngectomy should be excluded but no significant shift detected
- **A1-P2** x llama-3.1-8b: total_laryngectomy should be excluded but no significant shift detected
- **A1-P3** x kimi-k2.5: total_laryngectomy should be excluded but no significant shift detected
- **A1-P3** x llama-3.1-8b: total_laryngectomy should be excluded but no significant shift detected
- **A1-NULL** x kimi-k2.5: total_laryngectomy should be excluded but no significant shift detected
- **A1-NULL** x kimi-k2.5: concurrent_crt should be excluded but no significant shift detected
- **A1-NULL** x llama-3.1-8b: total_laryngectomy should be excluded but no significant shift detected
- **A1-NULL** x llama-3.1-8b: concurrent_crt should be excluded but no significant shift detected
- **A2-P1** x kimi-k2.5: tlm should be excluded but no significant shift detected

### wrong_direction (16 instances)
- **A1-P2** x kimi-k2.5: tlm should remain viable but dropped (100%->40%)
- **A1-P2** x llama-3.1-8b: nonsurgical_lp should remain viable but dropped (100%->47%)
- **A1-P3** x kimi-k2.5: tlm should remain viable but dropped (100%->27%)
- **B1-P9** x kimi-k2.5: surgical_lp should remain viable but dropped (93%->12%)
- **B1-P9** x kimi-k2.5: ophl_any should remain viable but dropped (80%->0%)
- **C1-P3** x llama-3.1-8b: nonsurgical_lp should remain viable but dropped (100%->47%)
- **C1-P3** x llama-3.1-8b: concurrent_crt should remain viable but dropped (100%->40%)
- **G1-REL01** x kimi-k2.5: cisplatin_high_dose should remain viable but dropped (100%->0%)
- **G1-REL02** x kimi-k2.5: cisplatin_high_dose should remain viable but dropped (100%->20%)
- **G1-REL03** x kimi-k2.5: cisplatin_high_dose should remain viable but dropped (100%->0%)

### wrong_conditionality (0 instances)

### magnitude_misalignment (0 instances)

### spurious_edge (0 instances)

## 4. Statistical Tests Summary

Total tests: 1257, Significant (BH-FDR q=0.05): 81 (6%)