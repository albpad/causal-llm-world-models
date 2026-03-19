# Vignette Integrity Report

## Benchmark Summary
- Baselines: `12`
- Perturbations: `76`
- Total items: `88`
- Statement-linked rules: `60`
- Evaluation edges in article metrics: `58`

## Integrity Checks
- Non-null perturbations missing traceability: `0`
- Null controls drifting from baseline expectations: `0`
- Items with staging warnings: `0`

## Query-Space Audit by Family
- `cT4a_selected`: concrete labels missing from targeted query space: `ophl_type_i, ophl_type_ii`
- `cT4a_unselected`: concrete labels missing from targeted query space: `tlm`
- `cisplatin_eligibility`: concrete labels missing from targeted query space: `carboplatin_5fu, cetuximab_concurrent, concurrent_crt, ict_rt`
- `elderly_frail`: concrete labels missing from targeted query space: `ict_rt, ophl_type_ii, rt_alone, total_laryngectomy`
- `glottic_cT2`: concrete labels missing from targeted query space: `ophl_type_ii, total_laryngectomy`
- `glottic_cT3`: concrete labels missing from targeted query space: `ophl_type_iii`
- `hypopharyngeal`: concrete labels missing from targeted query space: `ophl_type_ii`
- `post_ict_response`: concrete labels missing from targeted query space: `none`
- `pretreatment_function`: concrete labels missing from targeted query space: `none`
- `supraglottic_cT3`: concrete labels missing from targeted query space: `ict_rt`

## Traceability Matrix Preview
| Edge ID | Family | Item ID | Type | Baseline |
|---|---|---|---|---|
| `S10R` | `glottic_cT3` | `C1-P3` | `flip` | `C1-BASE` |
| `S10R` | `supraglottic_cT3` | `C1-P1` | `escalate` | `C1-BASE` |
| `S10R` | `supraglottic_cT3` | `C1-P2` | `escalate` | `C1-BASE` |
| `S111R` | `elderly_frail` | `I1-P1` | `flip` | `I1-BASE` |
| `S112` | `supraglottic_cT3` | `C1-P5` | `flip` | `C1-BASE` |
| `S115` | `hypopharyngeal` | `D1-P3` | `escalate` | `D1-BASE` |
| `S115` | `pretreatment_function` | `J1-P1` | `escalate` | `J1-BASE` |
| `S115` | `pretreatment_function` | `J1-P5` | `multi` | `J1-BASE` |
| `S116` | `post_ict_response` | `H1-P1` | `flip` | `H1-BASE` |
| `S119R` | `post_ict_response` | `H1-P1` | `flip` | `H1-BASE` |
| `S119R` | `post_ict_response` | `H2-NULL` | `null` | `H2-BASE` |
| `S12` | `cT4a_selected` | `F1-P5` | `flip` | `F1-BASE` |
| `S12` | `hypopharyngeal` | `D1-P1` | `flip` | `D1-BASE` |
| `S12` | `supraglottic_cT3` | `C1-P5` | `flip` | `C1-BASE` |
| `S120R` | `post_ict_response` | `H1-P1` | `flip` | `H1-BASE` |
| `S121R` | `post_ict_response` | `H1-P2` | `grey_zone` | `H1-BASE` |
| `S121R` | `post_ict_response` | `H1-P3` | `flip` | `H1-BASE` |
| `S121R` | `post_ict_response` | `H2-P1` | `flip` | `H2-BASE` |
| `S129` | `post_ict_response` | `H1-P4` | `flip` | `H1-BASE` |
| `S13` | `elderly_frail` | `I1-P2` | `escalate` | `I1-BASE` |
| `S13` | `elderly_frail` | `I1-P3` | `flip` | `I1-BASE` |
| `S14` | `glottic_cT3` | `B1-P1` | `flip` | `B1-BASE` |
| `S15R` | `cT4a_selected` | `F1-P2` | `flip` | `F1-BASE` |
| `S16R` | `glottic_cT3` | `B1-P8` | `flip` | `B1-BASE` |
| `S17R` | `glottic_cT3` | `B1-P9` | `flip` | `B1-BASE` |

## Null Drift Details
- None

## Staging Warnings
- None
