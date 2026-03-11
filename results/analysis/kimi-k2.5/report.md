# KG1 vs KG2 Analysis Report

## 1. Aggregate Performance

| Model | Rec Acc | Exc Acc | Precision | Cond | Unc | Null Spec |
|---|---|---|---|---|---|---|
| kimi-k2.5 | 59% | 87% | 94% | 96% | 67% | 25% |

## 2. KG2 Edge Detection Matrix

| Edge | kimi-k2.5 |
|---|---|
| S10R | - (0%) |
| S111R | - (11%) |
| S112 | - (0%) |
| S115 | - (0%) |
| S116 | - (14%) |
| S119R | - (7%) |
| S12 | - (0%) |
| S120R | - (14%) |
| S121R | - (25%) |
| S13 | - (19%) |
| S14 | - (0%) |
| S15R | - (0%) |
| S16R | - (0%) |
| S17R | - (0%) |
| S18R | - (0%) |
| S19R | - (0%) |
| S20R | - (0%) |
| S21 | - (0%) |
| S22 | - (14%) |
| S23R | - (24%) |
| S24R | - (0%) |
| S27 | - (8%) |
| S28 | - (21%) |
| S30 | - (14%) |
| S31R | - (14%) |
| S35R | - (0%) |
| S38R | - (0%) |
| S39R | - (0%) |
| S40R | - (0%) |
| S41R | - (0%) |
| S42R | - (0%) |
| S43 | - (0%) |
| S45 | - (0%) |
| S46 | - (0%) |
| S47R | - (0%) |
| S49R | - (0%) |
| S4R | - (29%) |
| S52R | - (0%) |
| S55R | - (14%) |
| S5R | - (5%) |
| S67 | - (25%) |
| S68R | - (17%) |
| S69R | - (3%) |
| S6R | - (0%) |
| S70 | - (0%) |
| S74R | - (0%) |
| S75R | - (0%) |
| S77R | - (0%) |
| S7R | - (0%) |
| S8 | - (6%) |
| S80 | - (0%) |
| S84 | - (11%) |
| S88 | - (22%) |
| S89 | - (33%) |
| S9R | - (0%) |
| SA2 | - (12%) |
| SA6 | - (33%) |

## 3. Divergence Taxonomy (37 total)


### missing_edge (33 instances)
- **A1-P2** x kimi-k2.5: total_laryngectomy should be excluded but no significant shift detected
- **A1-P3** x kimi-k2.5: total_laryngectomy should be excluded but no significant shift detected
- **A2-P1** x kimi-k2.5: tlm should be excluded but no significant shift detected
- **A2-P2** x kimi-k2.5: tlm should be excluded but no significant shift detected
- **B1-P1** x kimi-k2.5: tlm should be excluded but no significant shift detected
- **B1-P2** x kimi-k2.5: tlm should be excluded but no significant shift detected
- **B1-P3** x kimi-k2.5: tlm should be excluded but no significant shift detected
- **B1-P5** x kimi-k2.5: tlm should be excluded but no significant shift detected
- **B1-P6** x kimi-k2.5: tlm should be excluded but no significant shift detected
- **B1-P7** x kimi-k2.5: tlm should be excluded but no significant shift detected

### wrong_direction (4 instances)
- **A1-P2** x kimi-k2.5: tlm should remain viable but dropped (100%->45%)
- **A1-P3** x kimi-k2.5: tlm should remain viable but dropped (100%->43%)
- **B1-NULL2** x kimi-k2.5: concurrent_crt should remain viable but dropped (93%->10%)
- **G1-REL01** x kimi-k2.5: cisplatin_high_dose should remain viable but dropped (73%->0%)

### wrong_conditionality (0 instances)

### magnitude_misalignment (0 instances)

### spurious_edge (0 instances)

## 4. Statistical Tests Summary

Total tests: 498, Significant (BH-FDR q=0.05): 33 (7%)