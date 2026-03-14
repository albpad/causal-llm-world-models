# KG1 vs KG2 Analysis Report

## 1. Aggregate Performance

| Model | Rec Acc | Exc Acc | Precision | Cond | Unc | Null Spec |
|---|---|---|---|---|---|---|
| kimi-k2.5 | 64% | 88% | 94% | 100% | 100% | 33% |
| llama-3.1-8b | 79% | 20% | 76% | 100% | 100% | 33% |

## 2. KG2 Edge Detection Matrix

| Edge | kimi-k2.5 | llama-3.1-8b |
|---|---|---|
| S10R | - (6%) | - (0%) |
| S111R | - (22%) | - (20%) |
| S112 | - (9%) | - (0%) |
| S115 | - (0%) | - (0%) |
| S116 | - (29%) | - (0%) |
| S119R | - (14%) | - (0%) |
| S12 | - (4%) | - (0%) |
| S120R | - (29%) | - (0%) |
| S121R | - (26%) | - (39%) |
| S13 | - (17%) | - (0%) |
| S14 | - (0%) | - (0%) |
| S15R | - (0%) | - (0%) |
| S16R | - (33%) | - (0%) |
| S17R | - (33%) | - (0%) |
| S18R | - (33%) | - (0%) |
| S19R | - (0%) | - (6%) |
| S20R | - (0%) | - (0%) |
| S21 | - (0%) | - (0%) |
| S22 | - (11%) | - (0%) |
| S23R | - (23%) | - (0%) |
| S24R | - (0%) | - (0%) |
| S27 | - (6%) | - (0%) |
| S28 | - (19%) | - (0%) |
| S30 | - (29%) | - (0%) |
| S31R | - (29%) | - (0%) |
| S35R | - (0%) | - (0%) |
| S38R | - (14%) | - (0%) |
| S39R | - (11%) | - (7%) |
| S40R | - (22%) | - (0%) |
| S41R | - (22%) | - (0%) |
| S42R | - (18%) | - (0%) |
| S43 | - (3%) | - (4%) |
| S45 | - (22%) | - (0%) |
| S46 | - (12%) | - (0%) |
| S47R | - (0%) | - (0%) |
| S49R | - (22%) | - (0%) |
| S4R | - (28%) | - (0%) |
| S52R | - (17%) | - (0%) |
| S55R | - (29%) | - (0%) |
| S5R | - (7%) | - (0%) |
| S67 | - (20%) | - (0%) |
| S68R | - (20%) | - (0%) |
| S69R | - (13%) | - (0%) |
| S6R | - (3%) | - (0%) |
| S70 | - (20%) | - (0%) |
| S74R | - (0%) | - (30%) |
| S75R | - (0%) | - (0%) |
| S77R | - (18%) | - (0%) |
| S7R | - (8%) | - (0%) |
| S8 | - (6%) | - (0%) |
| S80 | - (2%) | - (0%) |
| S84 | - (22%) | - (20%) |
| S88 | - (28%) | - (9%) |
| S89 | - (33%) | - (0%) |
| S9R | - (18%) | - (0%) |
| SA2 | - (12%) | - (0%) |
| SA6 | - (33%) | - (33%) |

## 3. Divergence Taxonomy (85 total)


### missing_edge (73 instances)
- **A1-P1** x llama-3.1-8b: tlm should be excluded but no significant shift detected
- **A1-P2** x kimi-k2.5: total_laryngectomy should be excluded but no significant shift detected
- **A1-P2** x llama-3.1-8b: total_laryngectomy should be excluded but no significant shift detected
- **A1-P3** x kimi-k2.5: total_laryngectomy should be excluded but no significant shift detected
- **A1-P3** x llama-3.1-8b: total_laryngectomy should be excluded but no significant shift detected
- **A2-P1** x kimi-k2.5: tlm should be excluded but no significant shift detected
- **A2-P1** x llama-3.1-8b: tlm should be excluded but no significant shift detected
- **A2-P2** x kimi-k2.5: tlm should be excluded but no significant shift detected
- **A2-P2** x llama-3.1-8b: tlm should be excluded but no significant shift detected
- **B1-P1** x kimi-k2.5: tlm should be excluded but no significant shift detected

### wrong_direction (12 instances)
- **A1-P2** x kimi-k2.5: tlm should remain viable but dropped (100%->33%)
- **A1-P3** x kimi-k2.5: tlm should remain viable but dropped (100%->27%)
- **B1-P2** x kimi-k2.5: ophl_any should remain viable but dropped (73%->14%)
- **G1-REL01** x kimi-k2.5: cisplatin_high_dose should remain viable but dropped (100%->0%)
- **G1-REL02** x kimi-k2.5: cisplatin_high_dose should remain viable but dropped (100%->20%)
- **G1-REL03** x kimi-k2.5: cisplatin_high_dose should remain viable but dropped (100%->0%)
- **G1-REL04** x kimi-k2.5: cisplatin_high_dose should remain viable but dropped (100%->0%)
- **G1-ECOG-TUM** x kimi-k2.5: cisplatin_high_dose should remain viable but dropped (100%->40%)
- **G1-GREY-S70** x kimi-k2.5: cisplatin_high_dose should remain viable but dropped (100%->0%)
- **H1-P1** x kimi-k2.5: total_laryngectomy should decrease but increased (0%->53%)

### wrong_conditionality (0 instances)

### magnitude_misalignment (0 instances)

### spurious_edge (0 instances)

## 4. Statistical Tests Summary

Total tests: 1005, Significant (BH-FDR q=0.05): 80 (8%)