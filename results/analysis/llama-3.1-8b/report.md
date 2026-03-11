# KG1 vs KG2 Analysis Report

## 1. Aggregate Performance

| Model | Rec Acc | Exc Acc | Precision | Cond | Unc | Null Spec |
|---|---|---|---|---|---|---|
| llama-3.1-8b | 79% | 20% | 76% | 100% | 100% | 33% |

## 2. KG2 Edge Detection Matrix

| Edge | llama-3.1-8b |
|---|---|
| S10R | - (0%) |
| S111R | - (20%) |
| S112 | - (0%) |
| S115 | - (0%) |
| S116 | - (0%) |
| S119R | - (0%) |
| S12 | - (0%) |
| S120R | - (0%) |
| S121R | - (39%) |
| S13 | - (0%) |
| S14 | - (0%) |
| S15R | - (0%) |
| S16R | - (0%) |
| S17R | - (0%) |
| S18R | - (0%) |
| S19R | - (6%) |
| S20R | - (0%) |
| S21 | - (0%) |
| S22 | - (14%) |
| S23R | - (0%) |
| S24R | - (0%) |
| S27 | - (0%) |
| S28 | - (0%) |
| S30 | - (0%) |
| S31R | - (0%) |
| S35R | - (0%) |
| S38R | - (0%) |
| S39R | - (7%) |
| S40R | - (0%) |
| S41R | - (0%) |
| S42R | - (0%) |
| S43 | - (4%) |
| S45 | - (0%) |
| S46 | - (0%) |
| S47R | - (0%) |
| S49R | - (0%) |
| S4R | - (0%) |
| S52R | - (0%) |
| S55R | - (0%) |
| S5R | - (5%) |
| S67 | - (0%) |
| S68R | - (0%) |
| S69R | - (0%) |
| S6R | - (0%) |
| S70 | - (0%) |
| S74R | - (30%) |
| S75R | - (0%) |
| S77R | - (0%) |
| S7R | - (0%) |
| S8 | - (0%) |
| S80 | - (0%) |
| S84 | - (20%) |
| S88 | - (9%) |
| S89 | - (0%) |
| S9R | - (0%) |
| SA2 | - (0%) |
| SA6 | - (33%) |

## 3. Divergence Taxonomy (46 total)


### missing_edge (45 instances)
- **A1-P1** x llama-3.1-8b: tlm should be excluded but no significant shift detected
- **A1-P2** x llama-3.1-8b: total_laryngectomy should be excluded but no significant shift detected
- **A1-P3** x llama-3.1-8b: total_laryngectomy should be excluded but no significant shift detected
- **A2-P1** x llama-3.1-8b: tlm should be excluded but no significant shift detected
- **A2-P2** x llama-3.1-8b: tlm should be excluded but no significant shift detected
- **B1-P1** x llama-3.1-8b: tlm should be excluded but no significant shift detected
- **B1-P2** x llama-3.1-8b: tlm should be excluded but no significant shift detected
- **B1-P3** x llama-3.1-8b: tlm should be excluded but no significant shift detected
- **B1-P4** x llama-3.1-8b: tlm should be excluded but no significant shift detected
- **B1-P5** x llama-3.1-8b: tlm should be excluded but no significant shift detected

### wrong_direction (1 instances)
- **J1-P6** x llama-3.1-8b: total_laryngectomy should remain viable but dropped (87%->45%)

### wrong_conditionality (0 instances)

### magnitude_misalignment (0 instances)

### spurious_edge (0 instances)

## 4. Statistical Tests Summary

Total tests: 419, Significant (BH-FDR q=0.05): 19 (5%)