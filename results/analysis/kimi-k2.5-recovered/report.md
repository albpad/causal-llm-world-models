# KG1 vs KG2 Analysis Report

## 1. Aggregate Performance

| Model | Rec Acc | Exc Acc | Precision | Cond | Unc | Null Spec |
|---|---|---|---|---|---|---|
| kimi-k2.5 | 64% | 88% | 94% | 100% | 100% | 33% |

## 2. KG2 Edge Detection Matrix

| Edge | kimi-k2.5 |
|---|---|
| S10R | - (6%) |
| S111R | - (22%) |
| S112 | - (9%) |
| S115 | - (4%) |
| S116 | - (29%) |
| S119R | - (14%) |
| S12 | - (12%) |
| S120R | - (29%) |
| S121R | - (32%) |
| S13 | - (17%) |
| S14 | - (0%) |
| S15R | - (0%) |
| S16R | - (33%) |
| S17R | - (33%) |
| S18R | - (33%) |
| S19R | - (2%) |
| S20R | - (0%) |
| S21 | - (12%) |
| S22 | - (11%) |
| S23R | - (23%) |
| S24R | - (0%) |
| S27 | - (6%) |
| S28 | - (19%) |
| S30 | - (29%) |
| S31R | - (29%) |
| S35R | - (0%) |
| S38R | - (14%) |
| S39R | - (11%) |
| S40R | - (22%) |
| S41R | - (22%) |
| S42R | - (18%) |
| S43 | - (9%) |
| S45 | - (22%) |
| S46 | - (12%) |
| S47R | - (0%) |
| S49R | - (22%) |
| S4R | - (28%) |
| S52R | - (17%) |
| S55R | - (29%) |
| S5R | - (7%) |
| S67 | - (20%) |
| S68R | - (24%) |
| S69R | - (16%) |
| S6R | - (3%) |
| S70 | - (20%) |
| S74R | - (0%) |
| S75R | - (0%) |
| S77R | - (18%) |
| S7R | - (8%) |
| S8 | - (6%) |
| S80 | - (3%) |
| S84 | - (22%) |
| S88 | - (28%) |
| S89 | - (33%) |
| S9R | - (18%) |
| SA2 | - (12%) |
| SA6 | - (50%) |

## 3. Divergence Taxonomy (40 total)


### missing_edge (28 instances)
- **A1-P2** x kimi-k2.5: total_laryngectomy should be excluded but no significant shift detected
- **A1-P3** x kimi-k2.5: total_laryngectomy should be excluded but no significant shift detected
- **A2-P1** x kimi-k2.5: tlm should be excluded but no significant shift detected
- **A2-P2** x kimi-k2.5: tlm should be excluded but no significant shift detected
- **B1-P1** x kimi-k2.5: tlm should be excluded but no significant shift detected
- **B1-P2** x kimi-k2.5: tlm should be excluded but no significant shift detected
- **B1-P3** x kimi-k2.5: tlm should be excluded but no significant shift detected
- **B1-P4** x kimi-k2.5: tlm should be excluded but no significant shift detected
- **B1-P5** x kimi-k2.5: tlm should be excluded but no significant shift detected
- **B1-P6** x kimi-k2.5: tlm should be excluded but no significant shift detected

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

Total tests: 585, Significant (BH-FDR q=0.05): 71 (12%)