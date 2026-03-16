# KG₁ Clinical Vignette Battery for LLM Causal Reasoning Evaluation

> Source: Ferrari et al., Lancet Oncol 2025; 26: e264-81
> Generated test battery: **12** baselines, **76** perturbations, **88** total items
> Unique KG₁ edges tested: **60**
> Perturbation types: {'flip': 48, 'escalate': 12, 'null': 12, 'grey_zone': 3, 'multi': 1}

---

## A1-BASE — glottic_cT2 / favorable_TLM_eligible

**Question**: What are the appropriate treatment options for this patient?

### Baseline

```
Patient: 54-year-old male, retired teacher, ECOG 0. Non-smoker for 8 years (former 20 pack-year history). Moderate alcohol intake. No significant comorbidities.

Tumor: cT2N0 glottic squamous cell carcinoma of the left true vocal cord. The lesion involves the middle and anterior third of the left vocal cord with impaired mobility but no fixation.

Imaging: CT and MRI show no cartilage involvement, no paraglottic space invasion, no subglottic extension, and no pre-epiglottic space involvement. No suspicious lymph nodes.

Function: Mild dysphonia (VHI-10: 18). No dysphagia. No airway compromise. Adequate laryngeal exposure confirmed on clinic suspension laryngoscopy simulation.

Labs: Normal blood panel, CrCl 102 mL/min.
```

**Expected recommendations**: nonsurgical_lp, ophl_any, ophl_type_ii, rt_alone, surgical_lp, tlm
**Expected excluded**: concurrent_crt, total_laryngectomy
**Reasoning**: Favorable cT2N0: TLM viable (adequate exposure, no blocking features). RT alone adequate per S22. No indication for chemo at cT2N0.

### 🔄 A1-P1 — Laryngeal exposure insufficient

**Type**: flip
**Variables changed**: `laryngeal_exposure`: adequate → insufficient

```
Patient: 54-year-old male, retired teacher, ECOG 0. Non-smoker for 8 years (former 20 pack-year history). Moderate alcohol intake. No significant comorbidities.

Tumor: cT2N0 glottic squamous cell carcinoma of the left true vocal cord. The lesion involves the middle and anterior third of the left vocal cord with impaired mobility but no fixation.

Imaging: CT and MRI show no cartilage involvement, no paraglottic space invasion, no subglottic extension, and no pre-epiglottic space involvement. No suspicious lymph nodes.

Function: Mild dysphonia (VHI-10: 18). No dysphagia. No airway compromise. Laryngeal exposure assessed as insufficient on preoperative suspension laryngoscopy simulation — limited visualisation of the posterior glottis due to anatomy.

Labs: Normal blood panel, CrCl 102 mL/min.
```

**Expected recommendations**: nonsurgical_lp, ophl_any, ophl_type_ii, rt_alone, surgical_lp
**Expected excluded**: tlm
**Edge justification**: S5R, S22
**Predicted failure mode**: Correctly blocks TLM while preserving other options

### ⬆️ A1-P2 — Vocal cord fixed → upstages to cT3 (STAGING PROPAGATION)

**Type**: escalate
**Variables changed**: `vocal_cord_mobility`: partially_impaired → fixed; `t_stage`: cT2 → cT3
**Staging impact**: cT2 → cT3 (vocal cord fixation defines T3 by AJCC)

```
Patient: 54-year-old male, retired teacher, ECOG 0. Non-smoker for 8 years (former 20 pack-year history). Moderate alcohol intake. No significant comorbidities.

Tumor: cT3N0 glottic squamous cell carcinoma of the left true vocal cord. The lesion involves the middle and anterior third of the left vocal cord with complete fixation of the left vocal cord.

Imaging: CT and MRI show no cartilage involvement, no paraglottic space invasion, no subglottic extension, and no pre-epiglottic space involvement. No suspicious lymph nodes.

Function: Severe dysphonia (VHI-10: 32). No dysphagia. No airway compromise. Adequate laryngeal exposure confirmed on clinic suspension laryngoscopy simulation.

Labs: Normal blood panel, CrCl 102 mL/min.
```

**Expected recommendations**: concurrent_crt, ict_rt, nonsurgical_lp, ophl_any, ophl_type_ii, surgical_lp, tlm
**Expected excluded**: total_laryngectomy
**Edge justification**: S23R, S4R, S28
**Predicted failure mode**: Must recognize that fixed cord upstages to cT3 and open the full cT3 decision landscape including CRT and ICT, not just escalate RT

### 🔄 A1-P3 — Add unfavorable cT2 features without fixation (SA2)

**Type**: flip
**Variables changed**: `unfavorable_ct2`: false → true; `tumor_volume`: low → high; `anterior_commissure`: none → present_good_exposure; `subglottic_extension`: none → under_10mm_anterior

```
Patient: 54-year-old male, retired teacher, ECOG 0. Non-smoker for 8 years (former 20 pack-year history). Moderate alcohol intake. No significant comorbidities.

Tumor: cT2N0 glottic squamous cell carcinoma of the left true vocal cord. The lesion is bulky, involving the entire left vocal cord with extension to the anterior commissure and minor anterior subglottic extension (approximately 7mm). Cord mobility is impaired but not fixed.

Imaging: CT and MRI show no cartilage involvement, no paraglottic space invasion, minor anterior subglottic extension, and no pre-epiglottic space involvement. No suspicious lymph nodes.

Function: Moderate dysphonia (VHI-10: 24). No dysphagia. No airway compromise. Adequate laryngeal exposure confirmed on clinic suspension laryngoscopy simulation.

Labs: Normal blood panel, CrCl 102 mL/min.
```

**Expected recommendations**: nonsurgical_lp, ophl_any, ophl_type_ii, rt_accelerated, rt_alone, surgical_lp, tlm
**Expected excluded**: total_laryngectomy
**Edge justification**: SA2, S23R, S8
**Predicted failure mode**: Should recognise unfavorable cT2 features (bulky, AC, subglottic, impaired mobility) warrant consideration of accelerated RT (S23R) even though still staged cT2

### ⊘ A1-NULL — Age 74, fit — should NOT change options

**Type**: null
**Variables changed**: `age`: under_70 → 70_plus

```
Patient: 74-year-old male, retired teacher, ECOG 0. Comprehensive Geriatric Assessment: fit. G8 score 15/17. Non-smoker for 8 years (former 20 pack-year history). Moderate alcohol intake. No significant comorbidities.

Tumor: cT2N0 glottic squamous cell carcinoma of the left true vocal cord. The lesion involves the middle and anterior third of the left vocal cord with impaired mobility but no fixation.

Imaging: CT and MRI show no cartilage involvement, no paraglottic space invasion, no subglottic extension, and no pre-epiglottic space involvement. No suspicious lymph nodes.

Function: Mild dysphonia (VHI-10: 18). No dysphagia. No airway compromise. Adequate laryngeal exposure confirmed on clinic suspension laryngoscopy simulation.

Labs: Normal blood panel, CrCl 102 mL/min.
```

**Expected recommendations**: nonsurgical_lp, ophl_any, ophl_type_ii, rt_alone, surgical_lp, tlm
**Expected excluded**: concurrent_crt, total_laryngectomy
**Edge justification**: S6R, S80
**Predicted failure mode**: Over-sensitivity to age in fit patient
---

## A2-BASE — glottic_cT2 / unfavorable_reduced_mobility

**Question**: What are the appropriate treatment options for this patient?

### Baseline

```
Patient: 61-year-old male, ECOG 0. Active smoker (35 pack-years). No significant comorbidities apart from mild COPD (GOLD I).

Tumor: cT2N0 glottic SCC. The lesion is bulky, involving the entire left vocal cord with extension to the anterior commissure. Left vocal cord mobility is reduced. The right cord is normal. Arytenoids bilaterally mobile.

Imaging: MRI shows anterior commissure involvement with adequate visualisation on office endoscopy. There is minor anterior subglottic extension (approximately 7mm). No paraglottic space invasion. No cartilage involvement. No suspicious lymph nodes.

Function: Moderate dysphonia. No dysphagia, no airway compromise. Laryngeal exposure assessed as adequate.

Labs: CrCl 89 mL/min, albumin 4.0, Hb 13.8.
```

**Expected recommendations**: nonsurgical_lp, ophl_any, ophl_type_ii, rt_accelerated, rt_alone, surgical_lp, tlm
**Expected excluded**: total_laryngectomy
**Reasoning**: Unfavorable cT2 (SA2): bulky, AC involvement, reduced cord, anterior subglottic. TLM technically feasible (exposure adequate, AC with good exposure per S8). Accelerated RT warranted given reduced cord (S23R).

### 🔄 A2-P1 — AC difficult exposure → TLM relative CI

**Type**: flip
**Variables changed**: `anterior_commissure`: present_good_exposure → present_difficult_exposure

```
Patient: 61-year-old male, ECOG 0. Active smoker (35 pack-years). No significant comorbidities apart from mild COPD (GOLD I).

Tumor: cT2N0 glottic SCC. The lesion is bulky, involving the entire left vocal cord with extension to the anterior commissure. Left vocal cord mobility is reduced. The right cord is normal. Arytenoids bilaterally mobile.

Imaging: MRI shows anterior commissure involvement with difficult visualisation — office endoscopy shows limited access to the anterior commissure region. There is minor anterior subglottic extension (approximately 7mm). No paraglottic space invasion. No cartilage involvement. No suspicious lymph nodes.

Function: Moderate dysphonia. No dysphagia, no airway compromise. Laryngeal exposure assessed as adequate.

Labs: CrCl 89 mL/min, albumin 4.0, Hb 13.8.
```

**Expected recommendations**: nonsurgical_lp, ophl_any, ophl_type_ii, rt_accelerated, rt_alone, surgical_lp
**Expected excluded**: tlm
**Edge justification**: S7R, S8
**Predicted failure mode**: Should block TLM due to AC with difficult exposure (S7R absolute CI)

### 🔄 A2-P2 — Laryngeal exposure insufficient

**Type**: flip
**Variables changed**: `laryngeal_exposure`: adequate → insufficient

```
Patient: 61-year-old male, ECOG 0. Active smoker (35 pack-years). No significant comorbidities apart from mild COPD (GOLD I).

Tumor: cT2N0 glottic SCC. The lesion is bulky, involving the entire left vocal cord with extension to the anterior commissure. Left vocal cord mobility is reduced. The right cord is normal. Arytenoids bilaterally mobile.

Imaging: MRI shows anterior commissure involvement with adequate visualisation on office endoscopy. There is minor anterior subglottic extension (approximately 7mm). No paraglottic space invasion. No cartilage involvement. No suspicious lymph nodes.

Function: Moderate dysphonia. No dysphagia, no airway compromise. Laryngeal exposure assessed as insufficient on preoperative evaluation — Cormack-Lehane grade III.

Labs: CrCl 89 mL/min, albumin 4.0, Hb 13.8.
```

**Expected recommendations**: nonsurgical_lp, ophl_any, ophl_type_ii, rt_accelerated, rt_alone, surgical_lp
**Expected excluded**: tlm
**Edge justification**: S5R
**Predicted failure mode**: Absolute CI TLM (S5R, 100%)

### ⬆️ A2-P3 — Vocal cord fixed → upstages to cT3

**Type**: escalate
**Variables changed**: `vocal_cord_mobility`: partially_impaired → fixed; `t_stage`: cT2 → cT3
**Staging impact**: cT2 → cT3 (vocal cord fixation defines T3 by AJCC)

```
Patient: 61-year-old male, ECOG 0. Active smoker (35 pack-years). No significant comorbidities apart from mild COPD (GOLD I).

Tumor: cT3N0 glottic SCC. The lesion is bulky, involving the entire left vocal cord with extension to the anterior commissure. Left vocal cord is fixed. The right cord is normal. Arytenoids bilaterally mobile.

Imaging: MRI shows anterior commissure involvement with adequate visualisation on office endoscopy. There is minor anterior subglottic extension (approximately 7mm). No paraglottic space invasion. No cartilage involvement. No suspicious lymph nodes.

Function: Moderate dysphonia. No dysphagia, no airway compromise. Laryngeal exposure assessed as adequate.

Labs: CrCl 89 mL/min, albumin 4.0, Hb 13.8.
```

**Expected recommendations**: concurrent_crt, ict_rt, nonsurgical_lp, ophl_any, ophl_type_ii, surgical_lp, tlm
**Edge justification**: S23R, S4R, S28
**Predicted failure mode**: Fixed cord = T3 by definition. Must upstage and offer full cT3 options including CRT/ICT.

### ⊘ A2-NULL — Age 73, fit

**Type**: null
**Variables changed**: `age`: under_70 → 70_plus

```
Patient: 73-year-old male, ECOG 0. Comprehensive Geriatric Assessment: fit. G8 15/17. Active smoker (35 pack-years). No significant comorbidities apart from mild COPD (GOLD I).

Tumor: cT2N0 glottic SCC. The lesion is bulky, involving the entire left vocal cord with extension to the anterior commissure. Left vocal cord mobility is reduced. The right cord is normal. Arytenoids bilaterally mobile.

Imaging: MRI shows anterior commissure involvement with adequate visualisation on office endoscopy. There is minor anterior subglottic extension (approximately 7mm). No paraglottic space invasion. No cartilage involvement. No suspicious lymph nodes.

Function: Moderate dysphonia. No dysphagia, no airway compromise. Laryngeal exposure assessed as adequate.

Labs: CrCl 89 mL/min, albumin 4.0, Hb 13.8.
```

**Expected recommendations**: nonsurgical_lp, ophl_any, ophl_type_ii, rt_accelerated, rt_alone, surgical_lp, tlm
**Expected excluded**: total_laryngectomy
**Edge justification**: S6R, S80
**Predicted failure mode**: Age alone should not change any recommendation
---

## B1-BASE — glottic_cT3 / TLM_eligible_clean

**Question**: What larynx-preservation treatment options are appropriate for this patient?

### Baseline

```
Patient: 58-year-old male, ECOG 0. Former smoker (quit 3 years ago, 25 pack-years). Social drinker. No significant comorbidities.

Tumor: cT3N0 glottic SCC. Left vocal cord fixed, right cord fully mobile. Arytenoids bilaterally mobile. The lesion involves the left vocal cord with extension into the anterior paraglottic space on the left side only.

Imaging: MRI shows paraglottic space invasion confined to the anterior compartment on the left. No posterior paraglottic involvement. No thyroid cartilage involvement (inner or outer cortex intact). No cricoid involvement. No pre-epiglottic space invasion. No subglottic extension. No suspicious lymph nodes.

Function: Moderate-to-severe dysphonia. No dysphagia, no aspiration. No airway obstruction. No tracheostomy. Laryngeal exposure assessed as adequate on preoperative evaluation (Cormack-Lehane grade I).

Labs: CrCl 98 mL/min, NYHA I, no neuropathy, normal hearing. Albumin 4.2, Hb 14.5.
```

**Expected recommendations**: concurrent_crt, ict_rt, nonsurgical_lp, ophl_any, ophl_type_ii, surgical_lp, tlm
**Expected excluded**: total_laryngectomy
**Reasoning**: Clean cT3N0: TLM viable (adequate exposure, no S7R blockers). OPHL-II viable (no S15R/S16R/S17R blockers). CRT highest LP rate (S28). ICT viable (S30, LoE I).

### 🔄 B1-P1 — Focal TC inner cortex (TREATMENT-CONDITIONAL)

**Type**: flip
**Variables changed**: `thyroid_cartilage_inner_cortex`: none → focal

```
Patient: 58-year-old male, ECOG 0. Former smoker (quit 3 years ago, 25 pack-years). Social drinker. No significant comorbidities.

Tumor: cT3N0 glottic SCC. Left vocal cord fixed, right cord fully mobile. Arytenoids bilaterally mobile. The lesion involves the left vocal cord with extension into the anterior paraglottic space on the left side only.

Imaging: MRI shows paraglottic space invasion confined to the anterior compartment on the left. No posterior paraglottic involvement. MRI shows focal inner cortex involvement of the thyroid cartilage on the left, without outer cortex or full-thickness invasion. Outer cortex intact. No cricoid involvement. No pre-epiglottic space invasion. No subglottic extension. No suspicious lymph nodes.

Function: Moderate-to-severe dysphonia. No dysphagia, no aspiration. No airway obstruction. No tracheostomy. Laryngeal exposure assessed as adequate on preoperative evaluation (Cormack-Lehane grade I).

Labs: CrCl 98 mL/min, NYHA I, no neuropathy, normal hearing. Albumin 4.2, Hb 14.5.
```

**Expected recommendations**: concurrent_crt, ict_rt, nonsurgical_lp, ophl_any, ophl_type_ii, surgical_lp
**Expected excluded**: tlm
**Edge justification**: S7R, S14, S27, S28
**Predicted failure mode**: Over-generalisation: 'cartilage = no surgery' without distinguishing TLM from OPHL
**Notes**: KEY TEST: TC inner cortex is absolute CI for TLM (S7R) but NOT CI for OPHL-II (S14) and NOT CI for CRT (S27)

### ⬆️ B1-P2 — Outer cortex → cT4a (STAGING PROPAGATION)

**Type**: escalate
**Variables changed**: `thyroid_cartilage_outer_cortex`: false → true; `extralaryngeal_extension`: none → minimal_anterior; `t_stage`: cT3 → cT4a
**Staging impact**: cT3 → cT4a (outer cortex invasion by AJCC definition)

```
Patient: 58-year-old male, ECOG 0. Former smoker (quit 3 years ago, 25 pack-years). Social drinker. No significant comorbidities.

Tumor: cT4aN0 glottic SCC. Left vocal cord fixed, right cord fully mobile. Arytenoids bilaterally mobile. The lesion involves the left vocal cord with extension into the anterior paraglottic space on the left side only.

Imaging: MRI shows paraglottic space invasion confined to the anterior compartment on the left. No posterior paraglottic involvement. CT shows focal outer cortex invasion of the thyroid cartilage anteriorly with minimal anterior extralaryngeal soft tissue extension confined to the strap muscles. No deep muscle invasion, no magic plane crossing. No cricoid involvement. No pre-epiglottic space invasion. No subglottic extension. No suspicious lymph nodes.

Function: Moderate-to-severe dysphonia. No dysphagia, no aspiration. No airway obstruction. No tracheostomy. Laryngeal exposure assessed as adequate on preoperative evaluation (Cormack-Lehane grade I).

Labs: CrCl 98 mL/min, NYHA I, no neuropathy, normal hearing. Albumin 4.2, Hb 14.5.
```

**Expected recommendations**: concurrent_crt, nonsurgical_lp, total_laryngectomy
**Expected excluded**: tlm
**Edge justification**: S45, S46, S40R, S41R, S49R
**Predicted failure mode**: Binary: 'cT4a = TL always' (misses selected LP exception per S46, S40R second clause)

### 🔄 B1-P3 — Posterior paraglottic space → TLM blocked

**Type**: flip
**Variables changed**: `posterior_paraglottic_space`: false → true

```
Patient: 58-year-old male, ECOG 0. Former smoker (quit 3 years ago, 25 pack-years). Social drinker. No significant comorbidities.

Tumor: cT3N0 glottic SCC. Left vocal cord fixed, right cord fully mobile. Arytenoids bilaterally mobile. The lesion involves the left vocal cord with extension into the anterior paraglottic space on the left side only.

Imaging: MRI shows paraglottic space invasion confined to the anterior compartment on the left. Posterior paraglottic space involvement on the left, extending to the posterior compartment. No thyroid cartilage involvement (inner or outer cortex intact). No cricoid involvement. No pre-epiglottic space invasion. No subglottic extension. No suspicious lymph nodes.

Function: Moderate-to-severe dysphonia. No dysphagia, no aspiration. No airway obstruction. No tracheostomy. Laryngeal exposure assessed as adequate on preoperative evaluation (Cormack-Lehane grade I).

Labs: CrCl 98 mL/min, NYHA I, no neuropathy, normal hearing. Albumin 4.2, Hb 14.5.
```

**Expected recommendations**: concurrent_crt, ict_rt, nonsurgical_lp, ophl_any, ophl_type_ii, surgical_lp
**Expected excluded**: tlm
**Edge justification**: S7R
**Predicted failure mode**: Should block TLM specifically, not all surgery

### 🔄 B1-P4 — Massive PES abutting membrane → TLM blocked

**Type**: flip
**Variables changed**: `pre_epiglottic_space`: none → massive_abutting_membrane

```
Patient: 58-year-old male, ECOG 0. Former smoker (quit 3 years ago, 25 pack-years). Social drinker. No significant comorbidities.

Tumor: cT3N0 glottic SCC. Left vocal cord fixed, right cord fully mobile. Arytenoids bilaterally mobile. The lesion involves the left vocal cord with extension into the anterior paraglottic space on the left side only.

Imaging: MRI shows paraglottic space invasion confined to the anterior compartment on the left. No posterior paraglottic involvement. No thyroid cartilage involvement (inner or outer cortex intact). No cricoid involvement. Massive pre-epiglottic space invasion with tumor abutting the thyrohyoid membrane. No subglottic extension. No suspicious lymph nodes.

Function: Moderate-to-severe dysphonia. No dysphagia, no aspiration. No airway obstruction. No tracheostomy. Laryngeal exposure assessed as adequate on preoperative evaluation (Cormack-Lehane grade I).

Labs: CrCl 98 mL/min, NYHA I, no neuropathy, normal hearing. Albumin 4.2, Hb 14.5.
```

**Expected recommendations**: concurrent_crt, ict_rt, nonsurgical_lp, ophl_any, ophl_type_ii, surgical_lp
**Expected excluded**: tlm
**Edge justification**: S7R
**Predicted failure mode**: TLM absolute CI; OPHL/CRT remain viable

### 🔄 B1-P5 — Posterior subglottic <10mm → TLM blocked

**Type**: flip
**Variables changed**: `subglottic_extension`: none → under_10mm_posterior

```
Patient: 58-year-old male, ECOG 0. Former smoker (quit 3 years ago, 25 pack-years). Social drinker. No significant comorbidities.

Tumor: cT3N0 glottic SCC. Left vocal cord fixed, right cord fully mobile. Arytenoids bilaterally mobile. The lesion involves the left vocal cord with extension into the anterior paraglottic space on the left side only.

Imaging: MRI shows paraglottic space invasion confined to the anterior compartment on the left. No posterior paraglottic involvement. No thyroid cartilage involvement (inner or outer cortex intact). No cricoid involvement. No pre-epiglottic space invasion. Subglottic extension of approximately 8mm posteriorly. No suspicious lymph nodes.

Function: Moderate-to-severe dysphonia. No dysphagia, no aspiration. No airway obstruction. No tracheostomy. Laryngeal exposure assessed as adequate on preoperative evaluation (Cormack-Lehane grade I).

Labs: CrCl 98 mL/min, NYHA I, no neuropathy, normal hearing. Albumin 4.2, Hb 14.5.
```

**Expected recommendations**: concurrent_crt, ict_rt, nonsurgical_lp, ophl_any, ophl_type_ii, surgical_lp
**Expected excluded**: tlm
**Edge justification**: S7R
**Predicted failure mode**: Subtle: posterior <10mm blocks TLM but anterior <10mm does not

### 🔄 B1-P6 — Laryngeal exposure insufficient

**Type**: flip
**Variables changed**: `laryngeal_exposure`: adequate → insufficient

```
Patient: 58-year-old male, ECOG 0. Former smoker (quit 3 years ago, 25 pack-years). Social drinker. No significant comorbidities.

Tumor: cT3N0 glottic SCC. Left vocal cord fixed, right cord fully mobile. Arytenoids bilaterally mobile. The lesion involves the left vocal cord with extension into the anterior paraglottic space on the left side only.

Imaging: MRI shows paraglottic space invasion confined to the anterior compartment on the left. No posterior paraglottic involvement. No thyroid cartilage involvement (inner or outer cortex intact). No cricoid involvement. No pre-epiglottic space invasion. No subglottic extension. No suspicious lymph nodes.

Function: Moderate-to-severe dysphonia. No dysphagia, no aspiration. No airway obstruction. No tracheostomy. Laryngeal exposure assessed as insufficient on preoperative evaluation (Cormack-Lehane grade III) — limited visualisation due to anatomy.

Labs: CrCl 98 mL/min, NYHA I, no neuropathy, normal hearing. Albumin 4.2, Hb 14.5.
```

**Expected recommendations**: concurrent_crt, ict_rt, nonsurgical_lp, ophl_any, ophl_type_ii, surgical_lp
**Expected excluded**: tlm
**Edge justification**: S5R
**Predicted failure mode**: Absolute CI TLM (S5R, 100%)

### 🔄 B1-P7 — AC difficult exposure → TLM blocked

**Type**: flip
**Variables changed**: `anterior_commissure`: none → present_difficult_exposure

```
Patient: 58-year-old male, ECOG 0. Former smoker (quit 3 years ago, 25 pack-years). Social drinker. No significant comorbidities.

Tumor: cT3N0 glottic SCC. Left vocal cord fixed, right cord fully mobile. Arytenoids bilaterally mobile. The lesion involves the left vocal cord with extension to the anterior commissure and into the anterior paraglottic space on the left side. Anterior commissure exposure is assessed as difficult on preoperative evaluation.

Imaging: MRI shows paraglottic space invasion confined to the anterior compartment on the left. No posterior paraglottic involvement. No thyroid cartilage involvement (inner or outer cortex intact). No cricoid involvement. No pre-epiglottic space invasion. No subglottic extension. No suspicious lymph nodes.

Function: Moderate-to-severe dysphonia. No dysphagia, no aspiration. No airway obstruction. No tracheostomy. Laryngeal exposure assessed as adequate on preoperative evaluation (Cormack-Lehane grade I).

Labs: CrCl 98 mL/min, NYHA I, no neuropathy, normal hearing. Albumin 4.2, Hb 14.5.
```

**Expected recommendations**: concurrent_crt, ict_rt, nonsurgical_lp, ophl_any, ophl_type_ii, surgical_lp
**Expected excluded**: tlm
**Edge justification**: S7R
**Predicted failure mode**: AC with difficult exposure = absolute CI TLM

### 🔄 B1-P8 — Bilateral arytenoid → CI ALL conservative surgery (S16R)

**Type**: flip
**Variables changed**: `posterior_laryngeal_involvement`: none → bilateral_arytenoid; `arytenoid_mobility`: bilateral_mobile → bilateral_fixed; `baseline_laryngeal_function`: functional → dysfunctional

```
Patient: 58-year-old male, ECOG 0. Former smoker (quit 3 years ago, 25 pack-years). Social drinker. No significant comorbidities.

Tumor: cT3N0 glottic SCC. Left vocal cord fixed, right cord fully mobile. Both arytenoids fixed with bilateral posterior involvement. The lesion involves the left vocal cord with extension into the anterior paraglottic space on the left side only.

Imaging: MRI shows paraglottic space invasion confined to the anterior compartment on the left. Bilateral posterior involvement with both arytenoids fixed. No thyroid cartilage involvement (inner or outer cortex intact). No cricoid involvement. No pre-epiglottic space invasion. No subglottic extension. No suspicious lymph nodes.

Function: Severe dysphonia with emerging aspiration risk due to bilateral arytenoid fixation. No airway obstruction. No tracheostomy. Laryngeal exposure assessed as adequate on preoperative evaluation (Cormack-Lehane grade I).

Labs: CrCl 98 mL/min, NYHA I, no neuropathy, normal hearing. Albumin 4.2, Hb 14.5.
```

**Expected recommendations**: concurrent_crt, nonsurgical_lp, total_laryngectomy
**Expected excluded**: tlm
**Edge justification**: S16R, S39R, S42R
**Predicted failure mode**: Bilateral arytenoid = CI ALL conservative surgery (S16R, 98%). Must block OPHL too, not just TLM.

### 🔄 B1-P9 — Subglottic >10mm + CAJ invasion → CI OPHL-II (S17R)

**Type**: flip
**Variables changed**: `subglottic_extension`: none → over_10mm; `cricoarytenoid_joint_invasion`: false → true

```
Patient: 58-year-old male, ECOG 0. Former smoker (quit 3 years ago, 25 pack-years). Social drinker. No significant comorbidities.

Tumor: cT3N0 glottic SCC. Left vocal cord fixed, right cord fully mobile. Arytenoids bilaterally mobile. The lesion involves the left vocal cord with extension into the anterior paraglottic space on the left side only.

Imaging: MRI shows paraglottic space invasion confined to the anterior compartment on the left. No posterior paraglottic involvement. No thyroid cartilage involvement (inner or outer cortex intact). Cricoid involvement with CAJ invasion. No pre-epiglottic space invasion. Subglottic extension >10mm with cricoarytenoid joint invasion on the left. No suspicious lymph nodes.

Function: Moderate-to-severe dysphonia. No dysphagia, no aspiration. No airway obstruction. No tracheostomy. Laryngeal exposure assessed as adequate on preoperative evaluation (Cormack-Lehane grade I).

Labs: CrCl 98 mL/min, NYHA I, no neuropathy, normal hearing. Albumin 4.2, Hb 14.5.
```

**Expected recommendations**: concurrent_crt, ict_rt, nonsurgical_lp, ophl_any, ophl_type_iii, surgical_lp
**Expected excluded**: ophl_type_ii, tlm
**Edge justification**: S17R, S18R
**Predicted failure mode**: >10mm subglottic + CAJ = absolute CI OPHL-II (S17R). But >10mm anterior subglottic may allow OPHL-III in expert centers (S18R).

### ⊘ B1-NULL1 — Age 73, fit — should NOT change

**Type**: null
**Variables changed**: `age`: under_70 → 70_plus; `frailty_status`: fit → fit

```
Patient: 73-year-old male, ECOG 0. Comprehensive Geriatric Assessment: fit. G8 score 15/17. Former smoker (quit 3 years ago, 25 pack-years). Social drinker. No significant comorbidities.

Tumor: cT3N0 glottic SCC. Left vocal cord fixed, right cord fully mobile. Arytenoids bilaterally mobile. The lesion involves the left vocal cord with extension into the anterior paraglottic space on the left side only.

Imaging: MRI shows paraglottic space invasion confined to the anterior compartment on the left. No posterior paraglottic involvement. No thyroid cartilage involvement (inner or outer cortex intact). No cricoid involvement. No pre-epiglottic space invasion. No subglottic extension. No suspicious lymph nodes.

Function: Moderate-to-severe dysphonia. No dysphagia, no aspiration. No airway obstruction. No tracheostomy. Laryngeal exposure assessed as adequate on preoperative evaluation (Cormack-Lehane grade I).

Labs: CrCl 98 mL/min, NYHA I, no neuropathy, normal hearing. Albumin 4.2, Hb 14.5.
```

**Expected recommendations**: concurrent_crt, ict_rt, nonsurgical_lp, ophl_any, ophl_type_ii, surgical_lp, tlm
**Expected excluded**: total_laryngectomy
**Edge justification**: S6R, S80
**Predicted failure mode**: Over-sensitivity to age in fit elderly

### ⊘ B1-NULL2 — Focal TC inner cortex — CRT should NOT be blocked

**Type**: null
**Variables changed**: `thyroid_cartilage_inner_cortex`: none → focal

```
Patient: 58-year-old male, ECOG 0. Former smoker (quit 3 years ago, 25 pack-years). Social drinker. No significant comorbidities.

Tumor: cT3N0 glottic SCC. Left vocal cord fixed, right cord fully mobile. Arytenoids bilaterally mobile. The lesion involves the left vocal cord with extension into the anterior paraglottic space on the left side only.

Imaging: MRI shows paraglottic space invasion confined to the anterior compartment on the left. No posterior paraglottic involvement. MRI shows focal inner cortex involvement of the thyroid cartilage on the left, without outer cortex or full-thickness invasion. No cricoid involvement. No pre-epiglottic space invasion. No subglottic extension. No suspicious lymph nodes.

Function: Moderate-to-severe dysphonia. No dysphagia, no aspiration. No airway obstruction. No tracheostomy. Laryngeal exposure assessed as adequate on preoperative evaluation (Cormack-Lehane grade I).

Labs: CrCl 98 mL/min, NYHA I, no neuropathy, normal hearing. Albumin 4.2, Hb 14.5.
```

**Expected recommendations**: concurrent_crt, ict_rt, nonsurgical_lp, ophl_any, ophl_type_ii, surgical_lp, tlm
**Expected excluded**: total_laryngectomy
**Edge justification**: S27
**Predicted failure mode**: Tests S27 specifically: TC inner cortex is NOT CI for CRT. Ask targeted: 'Is CRT contraindicated by the cartilage finding?'
**Notes**: TARGETED QUESTION VARIANT: 'Given the focal inner cortex thyroid cartilage involvement, is concurrent chemoradiotherapy contraindicated?'
---

## C1-BASE — supraglottic_cT3 / limited_PES

**Question**: What larynx-preservation treatment options are appropriate for this patient?

### Baseline

```
Patient: 56-year-old male, ECOG 0. Former smoker (quit 6 years, 30 pack-years). No significant comorbidities.

Tumor: cT3N1 supraglottic SCC arising from the epiglottis. There is a single ipsilateral level II lymph node (2.2cm, no extranodal extension on imaging).

Imaging: MRI shows limited pre-epiglottic space invasion — the tumor extends into the anterior portion of the PES without reaching the thyroid cartilage. No thyroid cartilage erosion or involvement. No paraglottic space invasion posteriorly. Vocal cord mobility mildly reduced on the left but not fixed. Arytenoids bilaterally mobile. No subglottic extension.

Function: Mild dysphagia to solids (no aspiration on FEES). Voice mildly altered. No airway obstruction. No tracheostomy. Laryngeal exposure adequate.

Labs: CrCl 94, NYHA I, normal hearing. Albumin 3.9, Hb 13.6.
```

**Expected recommendations**: concurrent_crt, ict_rt, nonsurgical_lp, ophl_any, ophl_type_i, surgical_lp, tlm, tors
**Expected excluded**: total_laryngectomy
**Reasoning**: Supraglottic cT3 with limited PES: TLM/TORS viable per S10R. OPHL-I viable. CRT + ICT viable. N1 does not contraindicate surgical LP (S24R only for N2+).

### ⬆️ C1-P1 — PES pronounced → OPHL type I preferred

**Type**: escalate
**Variables changed**: `pre_epiglottic_space`: limited → massive_not_abutting_membrane

```
Patient: 56-year-old male, ECOG 0. Former smoker (quit 6 years, 30 pack-years). No significant comorbidities.

Tumor: cT3N1 supraglottic SCC arising from the epiglottis. There is a single ipsilateral level II lymph node (2.2cm, no extranodal extension on imaging).

Imaging: MRI shows pronounced pre-epiglottic space invasion — the tumor fills most of the PES but does not abut the thyrohyoid membrane or thyroid cartilage. No thyroid cartilage erosion or involvement. No paraglottic space invasion posteriorly. Vocal cord mobility mildly reduced on the left but not fixed. Arytenoids bilaterally mobile. No subglottic extension.

Function: Mild dysphagia to solids (no aspiration on FEES). Voice mildly altered. No airway obstruction. No tracheostomy. Laryngeal exposure adequate.

Labs: CrCl 94, NYHA I, normal hearing. Albumin 3.9, Hb 13.6.
```

**Expected recommendations**: concurrent_crt, ict_rt, nonsurgical_lp, ophl_any, ophl_type_i, surgical_lp
**Expected excluded**: tlm
**Edge justification**: S10R
**Predicted failure mode**: Pronounced PES shifts from TLM/TORS toward OPHL-I (S10R-b)

### ⬆️ C1-P2 — PES + TC erosion → OPHL-IIB (SITE-CONDITIONAL)

**Type**: escalate
**Variables changed**: `pre_epiglottic_space`: limited → massive_not_abutting_membrane; `thyroid_cartilage_erosion`: false → true

```
Patient: 56-year-old male, ECOG 0. Former smoker (quit 6 years, 30 pack-years). No significant comorbidities.

Tumor: cT3N1 supraglottic SCC arising from the epiglottis. There is a single ipsilateral level II lymph node (2.2cm, no extranodal extension on imaging).

Imaging: MRI shows pronounced pre-epiglottic space invasion with thyroid cartilage erosion on CT. No full-thickness infiltration, no outer cortex invasion. No paraglottic space invasion posteriorly. Vocal cord mobility mildly reduced on the left but not fixed. Arytenoids bilaterally mobile. No subglottic extension.

Function: Mild dysphagia to solids (no aspiration on FEES). Voice mildly altered. No airway obstruction. No tracheostomy. Laryngeal exposure adequate.

Labs: CrCl 94, NYHA I, normal hearing. Albumin 3.9, Hb 13.6.
```

**Expected recommendations**: concurrent_crt, ict_rt, nonsurgical_lp, ophl_any, ophl_type_iib, surgical_lp
**Expected excluded**: tlm
**Edge justification**: S10R
**Predicted failure mode**: CRITICAL SITE-CONDITIONAL: TC erosion = INDICATION for OPHL-IIB in supraglottic (S10R) but would be CI for TLM in glottic (S9R)
**Notes**: This is the site-conditional pattern: same finding (TC erosion) has opposite meaning at different sites

### 🔄 C1-P3 — Change site to glottic + keep TC erosion (SITE CROSSOVER)

**Type**: flip
**Variables changed**: `primary_site`: supraglottic → glottic; `pre_epiglottic_space`: limited → none; `thyroid_cartilage_erosion`: false → true

```
Patient: 56-year-old male, ECOG 0. Former smoker (quit 6 years, 30 pack-years). No significant comorbidities.

Tumor: cT3N1 glottic SCC. There is a single ipsilateral level II lymph node (2.2cm, no extranodal extension on imaging).

Imaging: MRI shows no pre-epiglottic space involvement. Thyroid cartilage erosion on CT, without full-thickness infiltration or outer cortex invasion. No paraglottic space invasion posteriorly. Vocal cord mobility mildly reduced on the left but not fixed. Arytenoids bilaterally mobile. No subglottic extension.

Function: Mild dysphagia to solids (no aspiration on FEES). Voice mildly altered. No airway obstruction. No tracheostomy. Laryngeal exposure adequate.

Labs: CrCl 94, NYHA I, normal hearing. Albumin 3.9, Hb 13.6.
```

**Expected recommendations**: concurrent_crt, ict_rt, nonsurgical_lp, ophl_any, ophl_type_ii, surgical_lp
**Expected excluded**: tlm
**Edge justification**: S9R, S10R
**Predicted failure mode**: TC erosion now = CI for TLM (S9R) in glottic. NOT an indication for OPHL-IIB (that's supraglottic-specific). Tests site-conditionality.

### 🔄 C1-P4 — N2 → relative CI partial laryngectomy

**Type**: flip
**Variables changed**: `n_stage`: cN1 → cN2

```
Patient: 56-year-old male, ECOG 0. Former smoker (quit 6 years, 30 pack-years). No significant comorbidities.

Tumor: cT3N1 supraglottic SCC arising from the epiglottis. There is bilateral lymphadenopathy — 3.0cm left level II, 2.5cm left level III, 1.8cm right level II. No extranodal extension on imaging.

Imaging: MRI shows limited pre-epiglottic space invasion — the tumor extends into the anterior portion of the PES without reaching the thyroid cartilage. No thyroid cartilage erosion or involvement. No paraglottic space invasion posteriorly. Vocal cord mobility mildly reduced on the left but not fixed. Arytenoids bilaterally mobile. No subglottic extension.

Function: Mild dysphagia to solids (no aspiration on FEES). Voice mildly altered. No airway obstruction. No tracheostomy. Laryngeal exposure adequate.

Labs: CrCl 94, NYHA I, normal hearing. Albumin 3.9, Hb 13.6.
```

**Expected recommendations**: concurrent_crt, ict_rt, nonsurgical_lp
**Expected excluded**: tlm
**Edge justification**: S24R
**Predicted failure mode**: N2+ = relative CI for partial laryngectomy (S24R), preference shifts to CRT

### 🔄 C1-P5 — Site → hypopharyngeal (SITE-CONDITIONAL)

**Type**: flip
**Variables changed**: `primary_site`: supraglottic → hypopharyngeal; `pre_epiglottic_space`: limited → none

```
Patient: 56-year-old male, ECOG 0. Former smoker (quit 6 years, 30 pack-years). No significant comorbidities.

Tumor: cT3N1 SCC of the left piriform sinus. There is a single ipsilateral level II lymph node (2.2cm, no extranodal extension on imaging).

Imaging: MRI shows tumor confined to the piriform sinus with extension to the medial wall. No thyroid cartilage erosion or involvement. No paraglottic space invasion posteriorly. Vocal cord mobility mildly reduced on the left but not fixed. Arytenoids bilaterally mobile. No subglottic extension.

Function: Mild dysphagia to solids (no aspiration on FEES). Voice mildly altered. No airway obstruction. No tracheostomy. Laryngeal exposure adequate.

Labs: CrCl 94, NYHA I, normal hearing. Albumin 3.9, Hb 13.6.
```

**Expected recommendations**: concurrent_crt, ict_rt, nonsurgical_lp, total_laryngectomy
**Expected excluded**: tlm
**Edge justification**: S12, S43, S112
**Predicted failure mode**: Hypopharyngeal: TLM not first-line (S12), worse outcomes with non-surgical (S43)
---

## D1-BASE — hypopharyngeal / cT3_advanced

**Question**: What are the treatment options for this patient, and what is the preferred strategy?

### Baseline

```
Patient: 63-year-old male, ECOG 1. Current smoker (40 pack-years), heavy alcohol use (>14 units/week). Mild malnutrition (albumin 3.3, BMI 19.2, unintentional weight loss 5kg over 3 months).

Tumor: cT3N2b SCC of the left piriform sinus extending to the postcricoid area. Left vocal cord fixed, left arytenoid fixed. Right cord and arytenoid mobile. No cartilage invasion on imaging.

Imaging: CT and MRI show bulky primary with bilateral level II-IV lymphadenopathy (largest 3.5cm left level III, 2.0cm right level II), no extranodal extension. No subglottic extension. No extralaryngeal extension. No carotid artery encasement.

Function: Moderate dysphagia to solids, managing liquids and soft diet. No aspiration on FEES. Voice severely impaired. No airway obstruction, no tracheostomy, no feeding tube.

Labs: CrCl 82, NYHA I, no neuropathy, normal hearing, Hb 12.1.
```

**Expected recommendations**: concurrent_crt, ict_rt, nonsurgical_lp, total_laryngectomy
**Expected excluded**: tlm
**Reasoning**: Hypopharyngeal advanced: TLM not first-line (S12). OPHL limited by unilateral arytenoid + N2 (S24R). ICT → response assessment especially relevant (S30). Hypopharyngeal origin = worse LP outcomes (S43).

### 🔄 D1-P1 — Site → glottic (SITE CROSSOVER)

**Type**: flip
**Variables changed**: `primary_site`: hypopharyngeal → glottic

```
Patient: 63-year-old male, ECOG 1. Current smoker (40 pack-years), heavy alcohol use (>14 units/week). Mild malnutrition (albumin 3.3, BMI 19.2, unintentional weight loss 5kg over 3 months).

Tumor: cT3N2b glottic SCC with transglottic extension. Left vocal cord fixed, left arytenoid fixed. Right cord and arytenoid mobile. No cartilage invasion on imaging.

Imaging: CT and MRI show bulky primary with bilateral level II-IV lymphadenopathy (largest 3.5cm left level III, 2.0cm right level II), no extranodal extension. No subglottic extension. No extralaryngeal extension. No carotid artery encasement.

Function: Moderate dysphagia to solids, managing liquids and soft diet. No aspiration on FEES. Voice severely impaired. No airway obstruction, no tracheostomy, no feeding tube.

Labs: CrCl 82, NYHA I, no neuropathy, normal hearing, Hb 12.1.
```

**Expected recommendations**: concurrent_crt, ict_rt, nonsurgical_lp, ophl_any, ophl_type_ii, surgical_lp, total_laryngectomy
**Edge justification**: S12, S43
**Predicted failure mode**: Removing site-specific penalties: TLM now discussable, non-surgical outcomes not penalised by site

### ⬆️ D1-P2 — Add aspiration pneumonia → absolute CI non-surgical

**Type**: escalate
**Variables changed**: `swallowing_status`: impaired_no_aspiration → recurrent_pneumonia

```
Patient: 63-year-old male, ECOG 1. Current smoker (40 pack-years), heavy alcohol use (>14 units/week). Mild malnutrition (albumin 3.3, BMI 19.2, unintentional weight loss 5kg over 3 months).

Tumor: cT3N2b SCC of the left piriform sinus extending to the postcricoid area. Left vocal cord fixed, left arytenoid fixed. Right cord and arytenoid mobile. No cartilage invasion on imaging.

Imaging: CT and MRI show bulky primary with bilateral level II-IV lymphadenopathy (largest 3.5cm left level III, 2.0cm right level II), no extranodal extension. No subglottic extension. No extralaryngeal extension. No carotid artery encasement.

Function: Severe dysphagia with documented aspiration. Two episodes of aspiration pneumonia in the past 6 weeks requiring hospitalisation. FEES shows penetration and aspiration with thin liquids. Voice severely impaired. No airway obstruction, no tracheostomy, no feeding tube.

Labs: CrCl 82, NYHA I, no neuropathy, normal hearing, Hb 12.1.
```

**Expected recommendations**: total_laryngectomy
**Edge justification**: S19R
**Predicted failure mode**: Recurrent aspiration pneumonia = absolute CI for non-surgical LP (S19R-a)

### ⬆️ D1-P3 — Add tracheostomy

**Type**: escalate
**Variables changed**: `pretreatment_tracheostomy`: false → true; `airway_obstruction`: false → true

```
Patient: 63-year-old male, ECOG 1. Current smoker (40 pack-years), heavy alcohol use (>14 units/week). Mild malnutrition (albumin 3.3, BMI 19.2, unintentional weight loss 5kg over 3 months).

Tumor: cT3N2b SCC of the left piriform sinus extending to the postcricoid area. Left vocal cord fixed, left arytenoid fixed. Right cord and arytenoid mobile. No cartilage invasion on imaging.

Imaging: CT and MRI show bulky primary with bilateral level II-IV lymphadenopathy (largest 3.5cm left level III, 2.0cm right level II), no extranodal extension. No subglottic extension. No extralaryngeal extension. No carotid artery encasement.

Function: Moderate dysphagia to solids, managing liquids and soft diet. No aspiration on FEES. Voice severely impaired. Severe airway obstruction requiring tracheostomy placement 2 weeks ago. No feeding tube.

Labs: CrCl 82, NYHA I, no neuropathy, normal hearing, Hb 12.1.
```

**Expected recommendations**: concurrent_crt, ict_rt, nonsurgical_lp, total_laryngectomy
**Edge justification**: S19R, S115
**Predicted failure mode**: Tracheostomy = relative CI non-surgical (S19R-b) + poor functional prognosis (S115). Non-surgical not excluded but balance shifts.

### ⊘ D1-NULL — Age 73, fit

**Type**: null
**Variables changed**: `age`: under_70 → 70_plus

```
Patient: 73-year-old male, ECOG 1. Comprehensive Geriatric Assessment: fit. G8 14/17. Current smoker (40 pack-years), heavy alcohol use (>14 units/week). Mild malnutrition (albumin 3.3, BMI 19.2, unintentional weight loss 5kg over 3 months).

Tumor: cT3N2b SCC of the left piriform sinus extending to the postcricoid area. Left vocal cord fixed, left arytenoid fixed. Right cord and arytenoid mobile. No cartilage invasion on imaging.

Imaging: CT and MRI show bulky primary with bilateral level II-IV lymphadenopathy (largest 3.5cm left level III, 2.0cm right level II), no extranodal extension. No subglottic extension. No extralaryngeal extension. No carotid artery encasement.

Function: Moderate dysphagia to solids, managing liquids and soft diet. No aspiration on FEES. Voice severely impaired. No airway obstruction, no tracheostomy, no feeding tube.

Labs: CrCl 82, NYHA I, no neuropathy, normal hearing, Hb 12.1.
```

**Expected recommendations**: concurrent_crt, ict_rt, nonsurgical_lp, total_laryngectomy
**Expected excluded**: tlm
**Edge justification**: S80
**Predicted failure mode**: Age alone should not change recommendation
---

## E1-BASE — cT4a_unselected / significant_extralaryngeal

**Question**: What is the recommended treatment for this patient?

### Baseline

```
Patient: 59-year-old male, ECOG 1. Active smoker (45 pack-years). Moderate alcohol intake. Otherwise healthy.

Tumor: cT4aN1 glottic SCC. Bulky transglottic tumor with left vocal cord fixation and left arytenoid fixation. Right cord mobile.

Imaging: CT shows full-thickness thyroid cartilage infiltration with significant extralaryngeal soft tissue extension invading the strap muscles bilaterally. Extensive subglottic extension (>15mm) with cricoid cartilage invasion. The tumor crosses the magic plane. Single ipsilateral level III lymph node (2.5cm).

Function: Severe dysphonia — largely non-communicative by voice. Emergency tracheostomy placed 1 week ago for critical airway obstruction. Moderate dysphagia to solids but tolerating liquids. Laryngeal function is considered globally dysfunctional.

Direct laryngoscopy: Laryngeal exposure is insufficient due to tumor bulk and anatomy.

Labs: CrCl 91, NYHA I, no neuropathy. Albumin 3.4, Hb 12.8.
```

**Expected recommendations**: total_laryngectomy
**Expected excluded**: tlm
**Reasoning**: Unambiguous TL: significant extralaryngeal (S38R), extensive subglottic (S38R), TLM CI (S45/S5R), magic plane (S15R), dysfunctional larynx (S39R), tracheostomy (S19R-b/S115).

### ⊘ E1-NULL — Add age 75, fit — TL still indicated

**Type**: null
**Variables changed**: `age`: under_70 → 70_plus

```
Patient: 75-year-old male, ECOG 1. CGA: fit. G8 14/17. Active smoker (45 pack-years). Moderate alcohol intake. Otherwise healthy.

Tumor: cT4aN1 glottic SCC. Bulky transglottic tumor with left vocal cord fixation and left arytenoid fixation. Right cord mobile.

Imaging: CT shows full-thickness thyroid cartilage infiltration with significant extralaryngeal soft tissue extension invading the strap muscles bilaterally. Extensive subglottic extension (>15mm) with cricoid cartilage invasion. The tumor crosses the magic plane. Single ipsilateral level III lymph node (2.5cm).

Function: Severe dysphonia — largely non-communicative by voice. Emergency tracheostomy placed 1 week ago for critical airway obstruction. Moderate dysphagia to solids but tolerating liquids. Laryngeal function is considered globally dysfunctional.

Direct laryngoscopy: Laryngeal exposure is insufficient due to tumor bulk and anatomy.

Labs: CrCl 91, NYHA I, no neuropathy. Albumin 3.4, Hb 12.8.
```

**Expected recommendations**: total_laryngectomy
**Expected excluded**: tlm
**Edge justification**: S80
**Predicted failure mode**: Age should not change clear TL indication
---

## F1-BASE — cT4a_selected / minimal_anterior_favorable

**Question**: Is larynx preservation a viable option for this cT4a patient?

### Baseline

```
Patient: 55-year-old male, ECOG 0. Former smoker (quit 5 years, 20 pack-years). No comorbidities. Highly motivated for voice preservation.

Tumor: cT4aN0 glottic SCC. Left vocal cord fixed, right mobile. Arytenoids bilaterally mobile.

Imaging: CT shows focal outer cortex thyroid cartilage invasion anteriorly with minimal soft tissue extension confined to the immediate anterior strap muscle plane. No deep muscle invasion. No involvement beyond the anterior compartment. No magic plane crossing. No subglottic extension. No cricoid involvement. No suspicious lymph nodes.

Function: Moderate dysphonia but communicative. No dysphagia, no aspiration. No airway obstruction. No tracheostomy. Baseline laryngeal function considered preserved/functional. Adequate laryngeal exposure.

Labs: CrCl 104, NYHA I, no neuropathy. Albumin 4.3, Hb 14.8.
```

**Expected recommendations**: concurrent_crt, nonsurgical_lp, total_laryngectomy
**Expected excluded**: tlm
**Reasoning**: Favorable cT4a: meets S46 criteria (N0, minimal anterior extralaryngeal, fit). OPHL viable. Non-surgical LP has very few but real indications (S49R). TL preferred for unselected but LP achieves equal outcomes in selected patients (S40R). TLM absolute CI (S45).

### ⬆️ F1-P1 — Extralaryngeal → significant: LP collapses

**Type**: escalate
**Variables changed**: `extralaryngeal_extension`: minimal_anterior → significant

```
Patient: 55-year-old male, ECOG 0. Former smoker (quit 5 years, 20 pack-years). No comorbidities. Highly motivated for voice preservation.

Tumor: cT4aN0 glottic SCC. Left vocal cord fixed, right mobile. Arytenoids bilaterally mobile.

Imaging: CT shows focal outer cortex thyroid cartilage invasion anteriorly with significant extralaryngeal soft tissue extension invading the strap muscles bilaterally with deep muscle involvement. No magic plane crossing. No subglottic extension. No cricoid involvement. No suspicious lymph nodes.

Function: Moderate dysphonia but communicative. No dysphagia, no aspiration. No airway obstruction. No tracheostomy. Baseline laryngeal function considered preserved/functional. Adequate laryngeal exposure.

Labs: CrCl 104, NYHA I, no neuropathy. Albumin 4.3, Hb 14.8.
```

**Expected recommendations**: total_laryngectomy
**Expected excluded**: tlm
**Edge justification**: S38R, S39R
**Predicted failure mode**: Significant extralaryngeal = TL indication (S38R), CI for LP (S39R)

### 🔄 F1-P2 — Magic plane crossing → OPHL-I/II blocked

**Type**: flip
**Variables changed**: `magic_plane_crossing`: false → true

```
Patient: 55-year-old male, ECOG 0. Former smoker (quit 5 years, 20 pack-years). No comorbidities. Highly motivated for voice preservation.

Tumor: cT4aN0 glottic SCC. Left vocal cord fixed, right mobile. Arytenoids bilaterally mobile.

Imaging: CT shows focal outer cortex thyroid cartilage invasion anteriorly with minimal soft tissue extension confined to the immediate anterior strap muscle plane. No deep muscle invasion. No involvement beyond the anterior compartment. The tumor crosses the magic plane. No subglottic extension. No cricoid involvement. No suspicious lymph nodes.

Function: Moderate dysphonia but communicative. No dysphagia, no aspiration. No airway obstruction. No tracheostomy. Baseline laryngeal function considered preserved/functional. Adequate laryngeal exposure.

Labs: CrCl 104, NYHA I, no neuropathy. Albumin 4.3, Hb 14.8.
```

**Expected recommendations**: concurrent_crt, nonsurgical_lp, total_laryngectomy
**Expected excluded**: ophl_type_i, ophl_type_ii, tlm
**Edge justification**: S15R
**Predicted failure mode**: Magic plane = CI for OPHL-I and OPHL-II (S15R). Only OPHL-III or TL remain surgical options.

### 🔄 F1-P3 — Baseline laryngeal function → dysfunctional

**Type**: flip
**Variables changed**: `baseline_laryngeal_function`: functional → dysfunctional

```
Patient: 55-year-old male, ECOG 0. Former smoker (quit 5 years, 20 pack-years). No comorbidities. Highly motivated for voice preservation.

Tumor: cT4aN0 glottic SCC. Left vocal cord fixed, right mobile. Arytenoids bilaterally mobile.

Imaging: CT shows focal outer cortex thyroid cartilage invasion anteriorly with minimal soft tissue extension confined to the immediate anterior strap muscle plane. No deep muscle invasion. No involvement beyond the anterior compartment. No magic plane crossing. No subglottic extension. No cricoid involvement. No suspicious lymph nodes.

Function: Severe dysphonia, largely non-communicative. Emerging dysphagia to solids. No airway obstruction. No tracheostomy. Baseline laryngeal function is considered globally dysfunctional — severe dysphonia, swallowing difficulties emerging. Adequate laryngeal exposure.

Labs: CrCl 104, NYHA I, no neuropathy. Albumin 4.3, Hb 14.8.
```

**Expected recommendations**: total_laryngectomy
**Edge justification**: S39R, S42R
**Predicted failure mode**: Dysfunctional baseline = absolute CI for BOTH surgical and non-surgical LP (S39R). Forces TL.

### 🔄 F1-P4 — N stage → cN2

**Type**: flip
**Variables changed**: `n_stage`: cN0 → cN2

```
Patient: 55-year-old male, ECOG 0. Former smoker (quit 5 years, 20 pack-years). No comorbidities. Highly motivated for voice preservation.

Tumor: cT4aN0 glottic SCC. Left vocal cord fixed, right mobile. Arytenoids bilaterally mobile.

Imaging: CT shows focal outer cortex thyroid cartilage invasion anteriorly with minimal soft tissue extension confined to the immediate anterior strap muscle plane. No deep muscle invasion. No involvement beyond the anterior compartment. No magic plane crossing. No subglottic extension. No cricoid involvement. Bilateral lymphadenopathy — 2.8cm left level III, 2.0cm right level II. No extranodal extension.

Function: Moderate dysphonia but communicative. No dysphagia, no aspiration. No airway obstruction. No tracheostomy. Baseline laryngeal function considered preserved/functional. Adequate laryngeal exposure.

Labs: CrCl 104, NYHA I, no neuropathy. Albumin 4.3, Hb 14.8.
```

**Expected recommendations**: concurrent_crt, nonsurgical_lp, total_laryngectomy
**Edge justification**: S24R, S46
**Predicted failure mode**: N2 = relative CI for partial laryngectomy (S24R). S46 requires N0-1 for OPHL in cT4a.

### 🔄 F1-P5 — Site → hypopharyngeal

**Type**: flip
**Variables changed**: `primary_site`: glottic → hypopharyngeal

```
Patient: 55-year-old male, ECOG 0. Former smoker (quit 5 years, 20 pack-years). No comorbidities. Highly motivated for voice preservation.

Tumor: cT4aN0 SCC of the piriform sinus. Left vocal cord fixed, right mobile. Arytenoids bilaterally mobile.

Imaging: CT shows focal outer cortex thyroid cartilage invasion anteriorly with minimal soft tissue extension confined to the immediate anterior strap muscle plane. No deep muscle invasion. No involvement beyond the anterior compartment. No magic plane crossing. No subglottic extension. No cricoid involvement. No suspicious lymph nodes.

Function: Moderate dysphonia but communicative. No dysphagia, no aspiration. No airway obstruction. No tracheostomy. Baseline laryngeal function considered preserved/functional. Adequate laryngeal exposure.

Labs: CrCl 104, NYHA I, no neuropathy. Albumin 4.3, Hb 14.8.
```

**Expected recommendations**: concurrent_crt, nonsurgical_lp, total_laryngectomy
**Expected excluded**: tlm
**Edge justification**: S12, S43
**Predicted failure mode**: Hypopharynx at cT4a: worse outcomes non-surgical (S43), TLM not first-line (S12)

### 🔘 F1-GREY1 — Post-OPHL: adjuvant RT for pT4aN0 neg margins no PNI/LVI?

**Type**: grey_zone

```
Patient: 55-year-old male, ECOG 0. Former smoker (quit 5 years, 20 pack-years). No comorbidities. Highly motivated for voice preservation.

Tumor: cT4aN0 glottic SCC. Left vocal cord fixed, right mobile. Arytenoids bilaterally mobile.

Imaging: CT shows focal outer cortex thyroid cartilage invasion anteriorly with minimal soft tissue extension confined to the immediate anterior strap muscle plane. No deep muscle invasion. No involvement beyond the anterior compartment. No magic plane crossing. No subglottic extension. No cricoid involvement. No suspicious lymph nodes.

Function: Moderate dysphonia but communicative. No dysphagia, no aspiration. No airway obstruction. No tracheostomy. Baseline laryngeal function considered preserved/functional. Adequate laryngeal exposure.

Labs: CrCl 104, NYHA I, no neuropathy. Albumin 4.3, Hb 14.8.

[FOLLOW-UP SCENARIO]: The patient underwent OPHL. Final pathology: pT4aN0, all margins negative (>5mm), no perineural invasion, no lymphovascular invasion. Should adjuvant radiotherapy be administered?
```

**Expected recommendations**: 
**Edge justification**: S47R, S35R
**Predicted failure mode**: GREY ZONE S47R (61.4%): experts split on omitting adjuvant RT with favorable pathology. Model should express uncertainty.
**Grey zone**: S47R

### ⊘ F1-NULL — Age 74, fit

**Type**: null
**Variables changed**: `age`: under_70 → 70_plus

```
Patient: 74-year-old male, ECOG 0. CGA: fit. G8 15/17. Former smoker (quit 5 years, 20 pack-years). No comorbidities. Highly motivated for voice preservation.

Tumor: cT4aN0 glottic SCC. Left vocal cord fixed, right mobile. Arytenoids bilaterally mobile.

Imaging: CT shows focal outer cortex thyroid cartilage invasion anteriorly with minimal soft tissue extension confined to the immediate anterior strap muscle plane. No deep muscle invasion. No involvement beyond the anterior compartment. No magic plane crossing. No subglottic extension. No cricoid involvement. No suspicious lymph nodes.

Function: Moderate dysphonia but communicative. No dysphagia, no aspiration. No airway obstruction. No tracheostomy. Baseline laryngeal function considered preserved/functional. Adequate laryngeal exposure.

Labs: CrCl 104, NYHA I, no neuropathy. Albumin 4.3, Hb 14.8.
```

**Expected recommendations**: concurrent_crt, nonsurgical_lp, total_laryngectomy
**Expected excluded**: tlm
**Edge justification**: S80
**Predicted failure mode**: Age alone should not change LP eligibility in fit patient
---

## G1-BASE — cisplatin_eligibility / fully_eligible

**Question**: Is high-dose cisplatin (100 mg/m² q3w, up to 300 mg/m² cumulative) appropriate as the concurrent systemic agent?

### Baseline

```
Patient: 60-year-old male, ECOG 0.

Tumor: cT3N1 glottic SCC. The multidisciplinary team has decided that concurrent chemoradiotherapy is the treatment strategy. The clinical question is the choice of concurrent systemic agent.

Renal: CrCl 95 mL/min, normal electrolytes.
Cardiac: NYHA class I, LVEF 65%, normal ECG, no cardiac history.
Hepatic: normal LFTs, no chronic liver disease (Child-Pugh A equivalent).
Neurological: no peripheral neuropathy, no hearing deficit on pure-tone audiometry.
Haematological: Hb 14.2, WBC 7.8, platelets 245, normal differential.
Infectious: HIV negative, HBV surface antigen negative, HCV antibody negative.
Other: no known platinum allergy, no psychiatric history, no diabetes, not pregnant. Good social and family support.
Nutritional status adequate (albumin 4.1, BMI 24).
```

**Expected recommendations**: cisplatin_high_dose
**Expected excluded**: carboplatin_5fu, cetuximab_concurrent
**Reasoning**: No absolute or relative CIs. High-dose cisplatin preferred (S52R, LoE I-II).

### 🔄 G1-ABS01 — CrCl <50 absolute CI

**Type**: flip
**Variables changed**: `renal_function`: normal → under_50_ml_min

```
Patient: 60-year-old male, ECOG 0.

Tumor: cT3N1 glottic SCC. The multidisciplinary team has decided that concurrent chemoradiotherapy is the treatment strategy. The clinical question is the choice of concurrent systemic agent.

Renal: CrCl 38 mL/min (stage 3b CKD), elevated creatinine 2.1 mg/dL.
Cardiac: NYHA class I, LVEF 65%, normal ECG, no cardiac history.
Hepatic: normal LFTs, no chronic liver disease (Child-Pugh A equivalent).
Neurological: no peripheral neuropathy, no hearing deficit on pure-tone audiometry.
Haematological: Hb 14.2, WBC 7.8, platelets 245, normal differential.
Infectious: HIV negative, HBV surface antigen negative, HCV antibody negative.
Other: no known platinum allergy, no psychiatric history, no diabetes, not pregnant. Good social and family support.
Nutritional status adequate (albumin 4.1, BMI 24).
```

**Expected recommendations**: carboplatin_5fu, cetuximab_concurrent, nonsurgical_lp
**Expected excluded**: cisplatin_high_dose
**Edge justification**: S68R, S52R, S72R
**Predicted failure mode**: Should identify renal_function as absolute CI and recommend alternative agent

### 🔄 G1-ABS02 — NYHA III-IV / LVEF ≤50 absolute CI

**Type**: flip
**Variables changed**: `cardiac_function`: normal → nyha_III_IV

```
Patient: 60-year-old male, ECOG 0.

Tumor: cT3N1 glottic SCC. The multidisciplinary team has decided that concurrent chemoradiotherapy is the treatment strategy. The clinical question is the choice of concurrent systemic agent.

Renal: CrCl 95 mL/min, normal electrolytes.
Cardiac: NYHA class III congestive heart failure, LVEF 40%, on furosemide and carvedilol. History of myocardial infarction 2019.
Hepatic: normal LFTs, no chronic liver disease (Child-Pugh A equivalent).
Neurological: no peripheral neuropathy, no hearing deficit on pure-tone audiometry.
Haematological: Hb 14.2, WBC 7.8, platelets 245, normal differential.
Infectious: HIV negative, HBV surface antigen negative, HCV antibody negative.
Other: no known platinum allergy, no psychiatric history, no diabetes, not pregnant. Good social and family support.
Nutritional status adequate (albumin 4.1, BMI 24).
```

**Expected recommendations**: carboplatin_5fu, cetuximab_concurrent, nonsurgical_lp
**Expected excluded**: cisplatin_high_dose
**Edge justification**: S68R, S52R, S72R
**Predicted failure mode**: Should identify cardiac_function as absolute CI and recommend alternative agent

### 🔄 G1-ABS03 — Child-Pugh B/C absolute CI

**Type**: flip
**Variables changed**: `liver_function`: normal → child_pugh_B_C

```
Patient: 60-year-old male, ECOG 0.

Tumor: cT3N1 glottic SCC. The multidisciplinary team has decided that concurrent chemoradiotherapy is the treatment strategy. The clinical question is the choice of concurrent systemic agent.

Renal: CrCl 95 mL/min, normal electrolytes.
Cardiac: NYHA class I, LVEF 65%, normal ECG, no cardiac history.
Hepatic: Child-Pugh B alcoholic cirrhosis (score 8). Albumin 2.8, bilirubin 2.5, mild ascites.
Neurological: no peripheral neuropathy, no hearing deficit on pure-tone audiometry.
Haematological: Hb 14.2, WBC 7.8, platelets 245, normal differential.
Infectious: HIV negative, HBV surface antigen negative, HCV antibody negative.
Other: no known platinum allergy, no psychiatric history, no diabetes, not pregnant. Good social and family support.
Nutritional status adequate (albumin 4.1, BMI 24).
```

**Expected recommendations**: carboplatin_5fu, cetuximab_concurrent, nonsurgical_lp
**Expected excluded**: cisplatin_high_dose
**Edge justification**: S68R, S52R, S72R
**Predicted failure mode**: Should identify liver_function as absolute CI and recommend alternative agent

### 🔄 G1-ABS04 — Grade ≥2 neuropathy absolute CI

**Type**: flip
**Variables changed**: `neuropathy`: none → grade_2_plus

```
Patient: 60-year-old male, ECOG 0.

Tumor: cT3N1 glottic SCC. The multidisciplinary team has decided that concurrent chemoradiotherapy is the treatment strategy. The clinical question is the choice of concurrent systemic agent.

Renal: CrCl 95 mL/min, normal electrolytes.
Cardiac: NYHA class I, LVEF 65%, normal ECG, no cardiac history.
Hepatic: normal LFTs, no chronic liver disease (Child-Pugh A equivalent).
Neurological: grade 2 sensorimotor peripheral neuropathy — numbness and tingling in hands and feet affecting fine motor tasks. Normal hearing.
Haematological: Hb 14.2, WBC 7.8, platelets 245, normal differential.
Infectious: HIV negative, HBV surface antigen negative, HCV antibody negative.
Other: no known platinum allergy, no psychiatric history, no diabetes, not pregnant. Good social and family support.
Nutritional status adequate (albumin 4.1, BMI 24).
```

**Expected recommendations**: carboplatin_5fu, cetuximab_concurrent, nonsurgical_lp
**Expected excluded**: cisplatin_high_dose
**Edge justification**: S68R, S52R, S72R
**Predicted failure mode**: Should identify neuropathy as absolute CI and recommend alternative agent

### 🔄 G1-ABS05 — CD4 <200/AIDS absolute CI

**Type**: flip
**Variables changed**: `hiv_status`: negative → cd4_under_200_or_aids

```
Patient: 60-year-old male, ECOG 0.

Tumor: cT3N1 glottic SCC. The multidisciplinary team has decided that concurrent chemoradiotherapy is the treatment strategy. The clinical question is the choice of concurrent systemic agent.

Renal: CrCl 95 mL/min, normal electrolytes.
Cardiac: NYHA class I, LVEF 65%, normal ECG, no cardiac history.
Hepatic: normal LFTs, no chronic liver disease (Child-Pugh A equivalent).
Neurological: no peripheral neuropathy, no hearing deficit on pure-tone audiometry.
Haematological: Hb 14.2, WBC 7.8, platelets 245, normal differential.
Infectious: HIV positive, CD4 count 180 cells/µL with recent Pneumocystis pneumonia (AIDS-defining). On HAART with poor virological control. HBV/HCV negative.
Other: no known platinum allergy, no psychiatric history, no diabetes, not pregnant. Good social and family support.
Nutritional status adequate (albumin 4.1, BMI 24).
```

**Expected recommendations**: carboplatin_5fu, cetuximab_concurrent, nonsurgical_lp
**Expected excluded**: cisplatin_high_dose
**Edge justification**: S68R, S52R, S72R
**Predicted failure mode**: Should identify hiv_status as absolute CI and recommend alternative agent

### 🔄 G1-ABS06 — Uncontrolled HBV absolute CI

**Type**: flip
**Variables changed**: `hepatitis`: negative → uncontrolled

```
Patient: 60-year-old male, ECOG 0.

Tumor: cT3N1 glottic SCC. The multidisciplinary team has decided that concurrent chemoradiotherapy is the treatment strategy. The clinical question is the choice of concurrent systemic agent.

Renal: CrCl 95 mL/min, normal electrolytes.
Cardiac: NYHA class I, LVEF 65%, normal ECG, no cardiac history.
Hepatic: normal LFTs, no chronic liver disease (Child-Pugh A equivalent).
Neurological: no peripheral neuropathy, no hearing deficit on pure-tone audiometry.
Haematological: Hb 14.2, WBC 7.8, platelets 245, normal differential.
Infectious: HIV negative. Chronic hepatitis B with high viral load (HBV DNA >20,000 IU/mL), not currently on antiviral therapy. HBeAg positive. HCV negative.
Other: no known platinum allergy, no psychiatric history, no diabetes, not pregnant. Good social and family support.
Nutritional status adequate (albumin 4.1, BMI 24).
```

**Expected recommendations**: carboplatin_5fu, cetuximab_concurrent, nonsurgical_lp
**Expected excluded**: cisplatin_high_dose
**Edge justification**: S68R, S52R, S72R
**Predicted failure mode**: Should identify hepatitis as absolute CI and recommend alternative agent

### 🔄 G1-ABS07 — Platinum hypersensitivity absolute CI

**Type**: flip
**Variables changed**: `platinum_hypersensitivity`: false → true

```
Patient: 60-year-old male, ECOG 0.

Tumor: cT3N1 glottic SCC. The multidisciplinary team has decided that concurrent chemoradiotherapy is the treatment strategy. The clinical question is the choice of concurrent systemic agent.

Renal: CrCl 95 mL/min, normal electrolytes.
Cardiac: NYHA class I, LVEF 65%, normal ECG, no cardiac history.
Hepatic: normal LFTs, no chronic liver disease (Child-Pugh A equivalent).
Neurological: no peripheral neuropathy, no hearing deficit on pure-tone audiometry.
Haematological: Hb 14.2, WBC 7.8, platelets 245, normal differential.
Infectious: HIV negative, HBV surface antigen negative, HCV antibody negative.
Other: documented grade 3 anaphylactic reaction to cisplatin during prior treatment (urticaria, bronchospasm, hypotension requiring adrenaline). No psychiatric history, no diabetes, not pregnant. Good social and family support.
Nutritional status adequate (albumin 4.1, BMI 24).
```

**Expected recommendations**: carboplatin_5fu, cetuximab_concurrent, nonsurgical_lp
**Expected excluded**: cisplatin_high_dose
**Edge justification**: S68R, S52R, S72R
**Predicted failure mode**: Should identify platinum_hypersensitivity as absolute CI and recommend alternative agent

### 🔄 G1-ABS08 — Severe psychiatric disorder absolute CI

**Type**: flip
**Variables changed**: `psychiatric_disorders`: false → true

```
Patient: 60-year-old male, ECOG 0.

Tumor: cT3N1 glottic SCC. The multidisciplinary team has decided that concurrent chemoradiotherapy is the treatment strategy. The clinical question is the choice of concurrent systemic agent.

Renal: CrCl 95 mL/min, normal electrolytes.
Cardiac: NYHA class I, LVEF 65%, normal ECG, no cardiac history.
Hepatic: normal LFTs, no chronic liver disease (Child-Pugh A equivalent).
Neurological: no peripheral neuropathy, no hearing deficit on pure-tone audiometry.
Haematological: Hb 14.2, WBC 7.8, platelets 245, normal differential.
Infectious: HIV negative, HBV surface antigen negative, HCV antibody negative.
Other: no platinum allergy. Severe treatment-resistant schizophrenia with limited capacity for informed consent and poor treatment compliance — under psychiatric care with supervised medication. No diabetes, not pregnant. Good social and family support.
Nutritional status adequate (albumin 4.1, BMI 24).
```

**Expected recommendations**: carboplatin_5fu, cetuximab_concurrent, nonsurgical_lp
**Expected excluded**: cisplatin_high_dose
**Edge justification**: S68R, S52R, S72R
**Predicted failure mode**: Should identify psychiatric_disorders as absolute CI and recommend alternative agent

### 🔄 G1-ABS09 — Uncontrolled insulin-dependent DM absolute CI

**Type**: flip
**Variables changed**: `diabetes`: none → uncontrolled_insulin_dependent

```
Patient: 60-year-old male, ECOG 0.

Tumor: cT3N1 glottic SCC. The multidisciplinary team has decided that concurrent chemoradiotherapy is the treatment strategy. The clinical question is the choice of concurrent systemic agent.

Renal: CrCl 95 mL/min, normal electrolytes.
Cardiac: NYHA class I, LVEF 65%, normal ECG, no cardiac history.
Hepatic: normal LFTs, no chronic liver disease (Child-Pugh A equivalent).
Neurological: no peripheral neuropathy, no hearing deficit on pure-tone audiometry.
Haematological: Hb 14.2, WBC 7.8, platelets 245, normal differential.
Infectious: HIV negative, HBV surface antigen negative, HCV antibody negative.
Other: no platinum allergy, no psychiatric history. Uncontrolled type 1 diabetes — HbA1c 12.3%, recurrent diabetic ketoacidosis (3 hospitalisations this year), insulin-dependent with poor glycaemic control despite endocrine follow-up. Not pregnant. Good social and family support.
Nutritional status adequate (albumin 4.1, BMI 24).
```

**Expected recommendations**: carboplatin_5fu, cetuximab_concurrent, nonsurgical_lp
**Expected excluded**: cisplatin_high_dose
**Edge justification**: S68R, S52R, S72R
**Predicted failure mode**: Should identify diabetes as absolute CI and recommend alternative agent

### 🔄 G1-ABS10 — Grade >2 bone marrow absolute CI

**Type**: flip
**Variables changed**: `bone_marrow`: normal → grade_2_plus

```
Patient: 60-year-old male, ECOG 0.

Tumor: cT3N1 glottic SCC. The multidisciplinary team has decided that concurrent chemoradiotherapy is the treatment strategy. The clinical question is the choice of concurrent systemic agent.

Renal: CrCl 95 mL/min, normal electrolytes.
Cardiac: NYHA class I, LVEF 65%, normal ECG, no cardiac history.
Hepatic: normal LFTs, no chronic liver disease (Child-Pugh A equivalent).
Neurological: no peripheral neuropathy, no hearing deficit on pure-tone audiometry.
Haematological: Hb 8.9, WBC 2.1 (ANC 0.8), platelets 62 — grade 3 pancytopenia. Under investigation for myelodysplastic syndrome.
Infectious: HIV negative, HBV surface antigen negative, HCV antibody negative.
Other: no known platinum allergy, no psychiatric history, no diabetes, not pregnant. Good social and family support.
Nutritional status adequate (albumin 4.1, BMI 24).
```

**Expected recommendations**: carboplatin_5fu, cetuximab_concurrent, nonsurgical_lp
**Expected excluded**: cisplatin_high_dose
**Edge justification**: S68R, S52R, S72R
**Predicted failure mode**: Should identify bone_marrow as absolute CI and recommend alternative agent

### 🔄 G1-REL01 — CrCl 50-60 = RELATIVE CI only, not absolute

**Type**: flip
**Variables changed**: `renal_function`: normal → 50_60_ml_min

```
Patient: 60-year-old male, ECOG 0.

Tumor: cT3N1 glottic SCC. The multidisciplinary team has decided that concurrent chemoradiotherapy is the treatment strategy. The clinical question is the choice of concurrent systemic agent.

Renal: CrCl 55 mL/min (mild-moderate renal impairment), creatinine 1.4 mg/dL.
Cardiac: NYHA class I, LVEF 65%, normal ECG, no cardiac history.
Hepatic: normal LFTs, no chronic liver disease (Child-Pugh A equivalent).
Neurological: no peripheral neuropathy, no hearing deficit on pure-tone audiometry.
Haematological: Hb 14.2, WBC 7.8, platelets 245, normal differential.
Infectious: HIV negative, HBV surface antigen negative, HCV antibody negative.
Other: no known platinum allergy, no psychiatric history, no diabetes, not pregnant. Good social and family support.
Nutritional status adequate (albumin 4.1, BMI 24).
```

**Expected recommendations**: cisplatin_high_dose
**Edge justification**: S69R
**Predicted failure mode**: Should identify as RELATIVE CI — cisplatin still possible with monitoring. Must NOT declare absolute CI.

### 🔄 G1-REL02 — Grade 1 hearing = RELATIVE CI only

**Type**: flip
**Variables changed**: `hearing_status`: grade_0 → grade_1

```
Patient: 60-year-old male, ECOG 0.

Tumor: cT3N1 glottic SCC. The multidisciplinary team has decided that concurrent chemoradiotherapy is the treatment strategy. The clinical question is the choice of concurrent systemic agent.

Renal: CrCl 95 mL/min, normal electrolytes.
Cardiac: NYHA class I, LVEF 65%, normal ECG, no cardiac history.
Hepatic: normal LFTs, no chronic liver disease (Child-Pugh A equivalent).
Neurological: no peripheral neuropathy. Grade 1 bilateral sensorineural hearing loss on audiometry — mild high-frequency deficit, functionally adequate.
Haematological: Hb 14.2, WBC 7.8, platelets 245, normal differential.
Infectious: HIV negative, HBV surface antigen negative, HCV antibody negative.
Other: no known platinum allergy, no psychiatric history, no diabetes, not pregnant. Good social and family support.
Nutritional status adequate (albumin 4.1, BMI 24).
```

**Expected recommendations**: cisplatin_high_dose
**Edge justification**: S69R
**Predicted failure mode**: Should identify as RELATIVE CI — cisplatin still possible with monitoring. Must NOT declare absolute CI.

### 🔄 G1-REL03 — Impaired social support = RELATIVE CI only

**Type**: flip
**Variables changed**: `social_support`: adequate → impaired

```
Patient: 60-year-old male, ECOG 0.

Tumor: cT3N1 glottic SCC. The multidisciplinary team has decided that concurrent chemoradiotherapy is the treatment strategy. The clinical question is the choice of concurrent systemic agent.

Renal: CrCl 95 mL/min, normal electrolytes.
Cardiac: NYHA class I, LVEF 65%, normal ECG, no cardiac history.
Hepatic: normal LFTs, no chronic liver disease (Child-Pugh A equivalent).
Neurological: no peripheral neuropathy, no hearing deficit on pure-tone audiometry.
Haematological: Hb 14.2, WBC 7.8, platelets 245, normal differential.
Infectious: HIV negative, HBV surface antigen negative, HCV antibody negative.
Other: no known platinum allergy, no psychiatric history, no diabetes, not pregnant. Limited social support — lives alone, nearest family 200km away. No reliable transport to treatment centre.
Nutritional status adequate (albumin 4.1, BMI 24).
```

**Expected recommendations**: cisplatin_high_dose
**Edge justification**: S69R
**Predicted failure mode**: Should identify as RELATIVE CI — cisplatin still possible with monitoring. Must NOT declare absolute CI.

### 🔄 G1-REL04 — CD4 200-350 = RELATIVE CI only, not absolute

**Type**: flip
**Variables changed**: `hiv_status`: negative → cd4_200_350

```
Patient: 60-year-old male, ECOG 0.

Tumor: cT3N1 glottic SCC. The multidisciplinary team has decided that concurrent chemoradiotherapy is the treatment strategy. The clinical question is the choice of concurrent systemic agent.

Renal: CrCl 95 mL/min, normal electrolytes.
Cardiac: NYHA class I, LVEF 65%, normal ECG, no cardiac history.
Hepatic: normal LFTs, no chronic liver disease (Child-Pugh A equivalent).
Neurological: no peripheral neuropathy, no hearing deficit on pure-tone audiometry.
Haematological: Hb 14.2, WBC 7.8, platelets 245, normal differential.
Infectious: HIV positive, CD4 count 280 cells/µL, on HAART with suppressed viral load. No AIDS-defining illnesses. HBV/HCV negative.
Other: no known platinum allergy, no psychiatric history, no diabetes, not pregnant. Good social and family support.
Nutritional status adequate (albumin 4.1, BMI 24).
```

**Expected recommendations**: cisplatin_high_dose
**Edge justification**: S69R
**Predicted failure mode**: Should identify as RELATIVE CI — cisplatin still possible with monitoring. Must NOT declare absolute CI.

### 🔄 G1-ECOG-TUM — ECOG 2 tumor-driven → cisplatin STILL OK (SOURCE-CONDITIONAL)

**Type**: flip
**Variables changed**: `ecog_ps`: 0 → 2_tumor_related; `ecog_ps_source`: null → tumor_driven

```
Patient: 60-year-old male, ECOG 2. His reduced functional status is entirely attributable to the bulky laryngeal tumor causing severe dysphagia and weight loss. Prior to symptom onset 4 months ago, he was fully active (ECOG 0). No pre-existing functional limitations.

Tumor: cT3N1 glottic SCC. The multidisciplinary team has decided that concurrent chemoradiotherapy is the treatment strategy. The clinical question is the choice of concurrent systemic agent.

Renal: CrCl 95 mL/min, normal electrolytes.
Cardiac: NYHA class I, LVEF 65%, normal ECG, no cardiac history.
Hepatic: normal LFTs, no chronic liver disease (Child-Pugh A equivalent).
Neurological: no peripheral neuropathy, no hearing deficit on pure-tone audiometry.
Haematological: Hb 14.2, WBC 7.8, platelets 245, normal differential.
Infectious: HIV negative, HBV surface antigen negative, HCV antibody negative.
Other: no known platinum allergy, no psychiatric history, no diabetes, not pregnant. Good social and family support.
Nutritional status adequate (albumin 4.1, BMI 24).
```

**Expected recommendations**: cisplatin_high_dose
**Edge justification**: S77R, S52R
**Predicted failure mode**: Blanket 'ECOG 2 = unfit for cisplatin' without evaluating cause. Must distinguish tumor-driven (OK) from comorbidity-driven (CI).

### 🔄 G1-ECOG-COM — ECOG 2 comorbidity-driven → cisplatin ABSOLUTE CI (SOURCE-CONDITIONAL)

**Type**: flip
**Variables changed**: `ecog_ps`: 0 → 2_comorbidity_related; `ecog_ps_source`: null → comorbidity_driven; `cardiopulmonary_function`: good → impaired

```
Patient: 60-year-old male, ECOG 2. He has longstanding COPD (GOLD III) and peripheral vascular disease limiting his mobility. He requires assistance with some daily activities. His functional limitations predate the cancer diagnosis by several years. The tumor itself causes only mild symptoms.

Tumor: cT3N1 glottic SCC. The multidisciplinary team has decided that concurrent chemoradiotherapy is the treatment strategy. The clinical question is the choice of concurrent systemic agent.

Renal: CrCl 95 mL/min, normal electrolytes.
Cardiac: NYHA class II, LVEF 55%. COPD GOLD III, FEV1 35% predicted.
Hepatic: normal LFTs, no chronic liver disease (Child-Pugh A equivalent).
Neurological: no peripheral neuropathy, no hearing deficit on pure-tone audiometry.
Haematological: Hb 14.2, WBC 7.8, platelets 245, normal differential.
Infectious: HIV negative, HBV surface antigen negative, HCV antibody negative.
Other: no known platinum allergy, no psychiatric history, no diabetes, not pregnant. Good social and family support.
Nutritional status adequate (albumin 4.1, BMI 24).
```

**Expected recommendations**: carboplatin_5fu, cetuximab_concurrent, nonsurgical_lp
**Expected excluded**: cisplatin_high_dose
**Edge justification**: S68R, S77R, S52R, S72R
**Predicted failure mode**: Same ECOG 2 as G1-ECOG-TUM but opposite recommendation — tests whether model distinguishes etiology

### 🔘 G1-GREY-S70 — 2 relative CIs — grey zone (ACCUMULATION-NON-PATTERN)

**Type**: grey_zone
**Variables changed**: `renal_function`: normal → 50_60_ml_min; `hearing_status`: grade_0 → grade_1; `cisplatin_relative_ci_count`: 0 → 2_plus

```
Patient: 60-year-old male, ECOG 0.

Tumor: cT3N1 glottic SCC. The multidisciplinary team has decided that concurrent chemoradiotherapy is the treatment strategy. The clinical question is the choice of concurrent systemic agent.

Renal: CrCl 55 mL/min (mild-moderate impairment), creatinine 1.4 mg/dL.
Cardiac: NYHA class I, LVEF 65%, normal ECG, no cardiac history.
Hepatic: normal LFTs, no chronic liver disease (Child-Pugh A equivalent).
Neurological: no peripheral neuropathy. Grade 1 bilateral sensorineural hearing loss on audiometry.
Haematological: Hb 14.2, WBC 7.8, platelets 245, normal differential.
Infectious: HIV negative, HBV surface antigen negative, HCV antibody negative.
Other: no known platinum allergy, no psychiatric history, no diabetes, not pregnant. Good social and family support.
Nutritional status adequate (albumin 4.1, BMI 24).
```

**Expected recommendations**: cisplatin_high_dose
**Edge justification**: S70, S69R
**Predicted failure mode**: Model incorrectly aggregates 2 relative CIs into absolute CI. S70 (75%) failed consensus — experts split on this. Appropriate response is uncertainty.
**Grey zone**: S70

### 🔄 G1-ABS11 — Severe comorbidity burden → unfit for chemo (S67)

**Type**: flip
**Variables changed**: `comorbidity_burden`: none_mild → severe

```
Patient: 60-year-old male, ECOG 0.

Tumor: cT3N1 glottic SCC. The multidisciplinary team has decided that concurrent chemoradiotherapy is the treatment strategy. The clinical question is the choice of concurrent systemic agent.

Renal: CrCl 95 mL/min, normal electrolytes.
Cardiac: NYHA class I, LVEF 65%, normal ECG, no cardiac history.
Hepatic: normal LFTs, no chronic liver disease (Child-Pugh A equivalent).
Neurological: no peripheral neuropathy, no hearing deficit on pure-tone audiometry.
Haematological: Hb 14.2, WBC 7.8, platelets 245, normal differential.
Infectious: HIV negative, HBV surface antigen negative, HCV antibody negative.
Other: no known platinum allergy, no psychiatric history, no diabetes, not pregnant. Good social and family support.
Severe comorbidity burden (ACE-27 score 3): COPD GOLD III, chronic kidney disease stage 3, compensated heart failure. Nutritional status marginal (albumin 3.2, BMI 20).
```

**Expected recommendations**: nonsurgical_lp, rt_accelerated
**Expected excluded**: carboplatin_5fu, cetuximab_concurrent, cisplatin_high_dose, concurrent_crt, ict_rt
**Edge justification**: S67, S73R
**Predicted failure mode**: Severe comorbidity burden = unfit for any chemo-based LP (S67). If TL is declined, accelerated or hyperfractionated RT alone is the fallback (S73R).
**Notes**: TARGETED QUESTION VARIANT: 'If this patient declines total laryngectomy and is unfit for any systemic therapy, what larynx-preservation option, if any, remains appropriate?'

### ⊘ G1-NULL — Controlled T2DM — NOT a CI

**Type**: null
**Variables changed**: `diabetes`: none → controlled

```
Patient: 60-year-old male, ECOG 0.

Tumor: cT3N1 glottic SCC. The multidisciplinary team has decided that concurrent chemoradiotherapy is the treatment strategy. The clinical question is the choice of concurrent systemic agent.

Renal: CrCl 95 mL/min, normal electrolytes.
Cardiac: NYHA class I, LVEF 65%, normal ECG, no cardiac history.
Hepatic: normal LFTs, no chronic liver disease (Child-Pugh A equivalent).
Neurological: no peripheral neuropathy, no hearing deficit on pure-tone audiometry.
Haematological: Hb 14.2, WBC 7.8, platelets 245, normal differential.
Infectious: HIV negative, HBV surface antigen negative, HCV antibody negative.
Other: no known platinum allergy, no psychiatric history. Well-controlled type 2 diabetes on metformin (HbA1c 6.8%, no end-organ damage, no neuropathy). Not pregnant. Good social and family support.
Nutritional status adequate (albumin 4.1, BMI 24).
```

**Expected recommendations**: cisplatin_high_dose
**Expected excluded**: carboplatin_5fu, cetuximab_concurrent
**Edge justification**: 
**Predicted failure mode**: Over-generalises 'diabetes = problem for chemo'
---

## H1-BASE — post_ict_response / complete_response

**Question**: What is the appropriate definitive treatment following this complete response to induction chemotherapy?

### Baseline

```
Patient: 57-year-old male, ECOG 0. Initially presented with cT3N1 glottic SCC with fixed left vocal cord and a 2.5cm level III node.

The patient received 3 cycles of induction chemotherapy (TPF protocol). He tolerated treatment well with manageable toxicity.

Post-ICT reassessment (8 weeks after cycle 3):
- Imaging: CT and MRI show complete radiological response at the primary site. The level III node has resolved completely. No residual tumor visible on imaging.
- Direct laryngoscopy: Complete endoscopic response. The previously fixed left vocal cord has regained normal mobility. Both arytenoids mobile. Mucosa appears normal.
- PET-CT: No FDG-avid disease at the primary site or neck.

Current function: Voice significantly improved. No dysphagia. No airway issues.
```

**Expected recommendations**: nonsurgical_lp, rt_alone
**Expected excluded**: concurrent_crt, total_laryngectomy
**Reasoning**: CR + VC remobilization after ICT → RT alone (S31R, S120R). NOT CRT. VC remobilization predicts functional LP (S119R). ICT CR is favorable factor (S116).

### 🔄 H1-P1 — PR ≥50% — shifts from RT alone to CRT

**Type**: flip
**Variables changed**: `ict_response`: complete_response → partial_response_50plus; `vc_remobilization_post_ict`: true → false; `vocal_cord_mobility`: normal → partially_impaired

```
Patient: 57-year-old male, ECOG 0. Initially presented with cT3N1 glottic SCC with fixed left vocal cord and a 2.5cm level III node.

The patient received 3 cycles of induction chemotherapy (TPF protocol). He tolerated treatment well with manageable toxicity.

Post-ICT reassessment (8 weeks after cycle 3):
- Imaging: CT and MRI show partial response with >50% tumor volume reduction at the primary site. The level III node has decreased from 2.5cm to 1.0cm. Residual tumor visible but significantly reduced.
- Direct laryngoscopy: Significant endoscopic tumor reduction but residual disease visible. The left vocal cord remains partially impaired (improved from fixed but not fully mobile). Arytenoids mobile.
- PET-CT: Reduced but persistent FDG uptake at the primary site (SUVmax 4.2, down from 12.8). Neck nodes show minimal residual uptake.

Current function: Voice improved but still moderately impaired. No dysphagia. No airway issues.
```

**Expected recommendations**: concurrent_crt, nonsurgical_lp
**Expected excluded**: rt_alone, total_laryngectomy
**Edge justification**: S55R, S116, S119R, S31R, S120R, S30
**Predicted failure mode**: Should shift from RT alone to CRT. CR=RT alone (S120R) but PR≥50% requires concurrent chemo. May incorrectly keep RT alone.

### 🔘 H1-P2 — PR <50% — GREY ZONE (SA6)

**Type**: grey_zone
**Variables changed**: `ict_response`: complete_response → partial_response_under50; `vc_remobilization_post_ict`: true → false; `vocal_cord_mobility`: normal → fixed

```
Patient: 57-year-old male, ECOG 0. Initially presented with cT3N1 glottic SCC with fixed left vocal cord and a 2.5cm level III node.

The patient received 3 cycles of induction chemotherapy (TPF protocol). He tolerated treatment well with manageable toxicity.

Post-ICT reassessment (8 weeks after cycle 3):
- Imaging: CT and MRI show partial response with approximately 30% tumor volume reduction. Residual bulky disease at the primary site. The level III node decreased from 2.5cm to 1.8cm.
- Direct laryngoscopy: Endoscopic improvement but substantial residual tumor. Left vocal cord remains fixed. Arytenoids mobile.
- PET-CT: Persistent significant FDG uptake (SUVmax 9.1, down from 12.8).

Current function: Voice unchanged — severely impaired. No dysphagia. No airway issues.
```

**Expected recommendations**: concurrent_crt, nonsurgical_lp, total_laryngectomy
**Edge justification**: SA6, S121R
**Predicted failure mode**: GREY ZONE SA6 (67.2%): PR<50% management unresolved. Experts split between CRT and TL. Model should express uncertainty.
**Grey zone**: SA6

### 🔄 H1-P3 — Stable disease → TL preferred

**Type**: flip
**Variables changed**: `ict_response`: complete_response → stable_disease; `vc_remobilization_post_ict`: true → false; `vocal_cord_mobility`: normal → fixed

```
Patient: 57-year-old male, ECOG 0. Initially presented with cT3N1 glottic SCC with fixed left vocal cord and a 2.5cm level III node.

The patient received 3 cycles of induction chemotherapy (TPF protocol). He tolerated treatment well with manageable toxicity.

Post-ICT reassessment (8 weeks after cycle 3):
- Imaging: CT and MRI show stable disease — no significant change in tumor dimensions (<10% reduction). The level III node is unchanged at 2.5cm.
- Direct laryngoscopy: No significant endoscopic change. Left vocal cord remains fixed. Tumor bulk unchanged.
- PET-CT: Unchanged metabolic activity (SUVmax 11.9 vs 12.8 pre-ICT).

Current function: Voice unchanged — severely impaired. No dysphagia. No airway issues.
```

**Expected recommendations**: total_laryngectomy
**Expected excluded**: rt_alone
**Edge justification**: S121R
**Predicted failure mode**: Stable disease → TL is standard (S121R). CRT only if patient refuses TL. Model may incorrectly persist with non-surgical LP.

### 🔄 H1-P4 — Progression → TL clearly indicated

**Type**: flip
**Variables changed**: `ict_response`: complete_response → progression; `vc_remobilization_post_ict`: true → false; `vocal_cord_mobility`: normal → fixed

```
Patient: 57-year-old male, ECOG 0. Initially presented with cT3N1 glottic SCC with fixed left vocal cord and a 2.5cm level III node.

The patient received 3 cycles of induction chemotherapy (TPF protocol). He tolerated treatment well with manageable toxicity.

Post-ICT reassessment (8 weeks after cycle 3):
- Imaging: CT and MRI show disease progression — tumor has increased in size with new areas of cartilage involvement. The level III node has grown to 3.2cm with a new level IV node (1.5cm).
- Direct laryngoscopy: Tumor progression on endoscopy with increased bulk. Left vocal cord remains fixed, now with reduced arytenoid mobility on the left.
- PET-CT: Increased metabolic activity with new areas of uptake.

Current function: Voice worsened. Emerging dysphagia to solids.
```

**Expected recommendations**: total_laryngectomy
**Expected excluded**: rt_alone
**Edge justification**: S129
**Predicted failure mode**: Progression or no response after ICT should shift decisively toward total laryngectomy over larynx-preservation strategies (S129).
---

## H2-BASE — post_ict_response / cT4a_partial_response

**Question**: Is this patient eligible for non-surgical larynx preservation following this partial response to ICT?

### Baseline

```
Patient: 52-year-old male, ECOG 0. Initially presented with cT4aN2b glottic SCC — bulky tumor with outer cortex TC invasion and moderate anterior extralaryngeal extension. Bilateral neck disease.

Received 3 cycles of TPF induction chemotherapy.

Post-ICT reassessment:
- Imaging: >50% reduction in tumor volume. Previously significant extralaryngeal extension now appears minimal. Thyroid cartilage still shows residual abnormality at outer cortex. Neck nodes reduced by >60%.
- Direct laryngoscopy: Significant tumor shrinkage endoscopically. Left vocal cord still fixed (no remobilization). Arytenoids mobile bilaterally. Residual tumor visible but much reduced.
- Laryngeal function: voice still severely impaired, but swallowing adequate, no aspiration, no tracheostomy.
```

**Expected recommendations**: concurrent_crt, nonsurgical_lp, total_laryngectomy
**Expected excluded**: rt_alone
**Reasoning**: cT4a with PR≥50% → eligible for non-surgical LP (S55R). But cord not remobilized (S119R negative), outer cortex residual (S41R). CRT is the non-surgical option (not RT alone — needs CR for that per S120R). TL valid alternative.

### 🔄 H2-P1 — Response → stable disease

**Type**: flip
**Variables changed**: `ict_response`: partial_response_50plus → stable_disease

```
Patient: 52-year-old male, ECOG 0. Initially presented with cT4aN2b glottic SCC — bulky tumor with outer cortex TC invasion and moderate anterior extralaryngeal extension. Bilateral neck disease.

Received 3 cycles of TPF induction chemotherapy.

Post-ICT reassessment:
- Imaging: no significant change in tumor dimensions (<10% reduction). Extralaryngeal extension unchanged. Thyroid cartilage still shows residual abnormality at outer cortex. Neck nodes essentially unchanged.
- Direct laryngoscopy: No significant endoscopic change. Left vocal cord still fixed (no remobilization). Arytenoids mobile bilaterally. Residual tumor visible but much reduced.
- Laryngeal function: voice still severely impaired, but swallowing adequate, no aspiration, no tracheostomy.
```

**Expected recommendations**: total_laryngectomy
**Expected excluded**: rt_alone
**Edge justification**: S121R
**Predicted failure mode**: Stable disease at cT4a → TL clearly indicated. Non-surgical LP no longer justified (S121R: CRT only if refuses TL).

### 🔄 H2-P2 — Baseline laryngeal function → dysfunctional

**Type**: flip
**Variables changed**: `baseline_laryngeal_function`: functional → dysfunctional

```
Patient: 52-year-old male, ECOG 0. Initially presented with cT4aN2b glottic SCC — bulky tumor with outer cortex TC invasion and moderate anterior extralaryngeal extension. Bilateral neck disease.

Received 3 cycles of TPF induction chemotherapy.

Post-ICT reassessment:
- Imaging: >50% reduction in tumor volume. Previously significant extralaryngeal extension now appears minimal. Thyroid cartilage still shows residual abnormality at outer cortex. Neck nodes reduced by >60%.
- Direct laryngoscopy: Significant tumor shrinkage endoscopically. Left vocal cord still fixed (no remobilization). Arytenoids mobile bilaterally. Residual tumor visible but much reduced.
- Laryngeal function: voice still severely impaired, but emerging aspiration with liquids, tracheostomy being considered. Laryngeal function is now globally dysfunctional.
```

**Expected recommendations**: total_laryngectomy
**Edge justification**: S39R
**Predicted failure mode**: Dysfunctional larynx = absolute CI for both surgical and non-surgical LP (S39R)

### 🔄 H2-P3 — Site → hypopharyngeal

**Type**: flip
**Variables changed**: `primary_site`: glottic → hypopharyngeal

```
Patient: 52-year-old male, ECOG 0. Initially presented with cT4aN2b SCC of the piriform sinus — bulky tumor with outer cortex TC invasion and moderate anterior extralaryngeal extension. Bilateral neck disease.

Received 3 cycles of TPF induction chemotherapy.

Post-ICT reassessment:
- Imaging: >50% reduction in tumor volume. Previously significant extralaryngeal extension now appears minimal. Thyroid cartilage still shows residual abnormality at outer cortex. Neck nodes reduced by >60%.
- Direct laryngoscopy: Significant tumor shrinkage endoscopically. Left vocal cord still fixed (no remobilization). Arytenoids mobile bilaterally. Residual tumor visible but much reduced.
- Laryngeal function: voice still severely impaired, but swallowing adequate, no aspiration, no tracheostomy.
```

**Expected recommendations**: concurrent_crt, nonsurgical_lp, total_laryngectomy
**Edge justification**: S43
**Predicted failure mode**: Hypopharynx at cT4a: worse outcomes tip further toward TL (S43)

### ⊘ H2-NULL — VC remobilization (improves prognosis but doesn't change eligibility)

**Type**: null
**Variables changed**: `vc_remobilization_post_ict`: false → true; `vocal_cord_mobility`: fixed → partially_impaired

```
Patient: 52-year-old male, ECOG 0. Initially presented with cT4aN2b glottic SCC — bulky tumor with outer cortex TC invasion and moderate anterior extralaryngeal extension. Bilateral neck disease.

Received 3 cycles of TPF induction chemotherapy.

Post-ICT reassessment:
- Imaging: >50% reduction in tumor volume. Previously significant extralaryngeal extension now appears minimal. Thyroid cartilage still shows residual abnormality at outer cortex. Neck nodes reduced by >60%.
- Direct laryngoscopy: Significant tumor shrinkage endoscopically. Left vocal cord has partially remobilized (previously fixed, now partially impaired mobility). Arytenoids mobile bilaterally. Residual tumor visible but much reduced.
- Laryngeal function: voice still severely impaired, but swallowing adequate, no aspiration, no tracheostomy.
```

**Expected recommendations**: concurrent_crt, nonsurgical_lp, total_laryngectomy
**Expected excluded**: rt_alone
**Edge justification**: S119R
**Predicted failure mode**: VC remobilization improves functional LP prediction (S119R) but fundamental eligibility unchanged
---

## I1-BASE — elderly_frail / elderly_fit

**Question**: Does this patient's age affect his eligibility for larynx preservation treatments?

### Baseline

```
Patient: 76-year-old male, ECOG 0. Retired engineer. Non-smoker for 15 years (former 25 pack-years). Lives independently with wife. Walks 5km daily, plays golf twice weekly.

Comorbidities: controlled hypertension on single agent, mild hyperlipidemia on statin. No cardiac history, no diabetes, no neurological disease.

Geriatric assessment: Comprehensive Geriatric Assessment (CGA) classifies patient as FIT. G8 screening score 15/17. No frailty markers. ADL and IADL fully independent. MMSE 29/30. Timed Up-and-Go test 9 seconds.

Tumor: cT3N0 glottic SCC. Left vocal cord fixed, right mobile. Arytenoids bilaterally mobile. No cartilage involvement, no subglottic extension, no paraglottic invasion posteriorly. Adequate laryngeal exposure.

Labs: CrCl 72 mL/min (age-appropriate), NYHA I, no neuropathy, mild presbycusis (grade 1 on audiometry). Albumin 3.8, Hb 13.1.
```

**Expected recommendations**: concurrent_crt, ict_rt, nonsurgical_lp, ophl_any, ophl_type_ii, surgical_lp, tlm
**Reasoning**: Age alone NOT CI for TLM (S6R) or any LP (S80) in fit patients. CGA fit → standard treatment (S84). CrCl 72 adequate for cisplatin (>60). Grade 1 hearing = relative CI cisplatin (S69R) but not absolute.

### 🔄 I1-P1 — Frail → OPHL relative CI, adapted approach

**Type**: flip
**Variables changed**: `frailty_status`: fit → frail; `g8_score`: above_14 → below_14

```
Patient: 76-year-old male, ECOG 0. Retired engineer. Non-smoker for 15 years (former 25 pack-years). Lives independently with wife. Walks 5km daily, plays golf twice weekly.

Comorbidities: controlled hypertension on single agent, mild hyperlipidemia on statin. No cardiac history, no diabetes, no neurological disease.

Geriatric assessment: Comprehensive Geriatric Assessment (CGA) classifies patient as FRAIL. G8 screening score 10/17. Reduced grip strength, slow gait speed (TUG 18 seconds). Dependent in 2 IADLs (shopping, transport). MMSE 26/30. Weight loss 4kg over 6 months.

Tumor: cT3N0 glottic SCC. Left vocal cord fixed, right mobile. Arytenoids bilaterally mobile. No cartilage involvement, no subglottic extension, no paraglottic invasion posteriorly. Adequate laryngeal exposure.

Labs: CrCl 72 mL/min (age-appropriate), NYHA I, no neuropathy, mild presbycusis (grade 1 on audiometry). Albumin 3.8, Hb 13.1.
```

**Expected recommendations**: concurrent_crt, nonsurgical_lp, rt_alone, total_laryngectomy
**Edge justification**: S88, S84, S111R
**Predicted failure mode**: Frail → OPHL becomes relative CI (S88). Must adapt treatment per CGA (S84). May still be CRT candidate but with adapted approach.

### ⬆️ I1-P2 — Frail + cT4a + precludes OPHL/chemo → TL preferred

**Type**: escalate
**Variables changed**: `frailty_status`: fit → frail; `g8_score`: above_14 → below_14; `t_stage`: cT3 → cT4a; `thyroid_cartilage_outer_cortex`: false → true; `extralaryngeal_extension`: none → minimal_anterior; `cardiopulmonary_function`: good → impaired
**Staging impact**: cT3 → cT4a

```
Patient: 76-year-old male, ECOG 0. Retired engineer. Non-smoker for 15 years (former 25 pack-years). Lives independently with wife. Walks 5km daily, plays golf twice weekly.

Comorbidities: COPD GOLD II, controlled hypertension, mild hyperlipidemia. Cardiopulmonary function impaired.

Geriatric assessment: Comprehensive Geriatric Assessment (CGA) classifies patient as FRAIL. G8 screening score 9/17. Multiple frailty markers. COPD GOLD II limiting exercise tolerance.

Tumor: cT4aN0 glottic SCC with focal outer cortex thyroid cartilage invasion and minimal anterior extralaryngeal extension. Left vocal cord fixed, right mobile. Arytenoids bilaterally mobile. No subglottic extension, no paraglottic invasion posteriorly. Adequate laryngeal exposure.

Labs: CrCl 72 mL/min (age-appropriate), NYHA I, no neuropathy, mild presbycusis (grade 1 on audiometry). Albumin 3.8, Hb 13.1.
```

**Expected recommendations**: total_laryngectomy
**Edge justification**: S89, S88, S13
**Predicted failure mode**: Frail + advanced + comorbidities precluding OPHL/systemic → TL preferred (S89)

### 🔄 I1-P3 — Add neurodegenerative disease

**Type**: flip
**Variables changed**: `neurological_function`: good → impaired_grade1

```
Patient: 76-year-old male, ECOG 0. Retired engineer. Non-smoker for 15 years (former 25 pack-years). Lives independently with wife. Walks 5km daily, plays golf twice weekly.

Comorbidities: controlled hypertension on single agent, mild hyperlipidemia on statin. No cardiac history, no diabetes. Early Parkinson's disease — mild resting tremor, on levodopa, functionally independent but with emerging mild swallowing hesitancy.

Geriatric assessment: Comprehensive Geriatric Assessment (CGA) classifies patient as FIT. G8 screening score 15/17. No frailty markers. ADL and IADL fully independent. MMSE 29/30. Timed Up-and-Go test 9 seconds.

Tumor: cT3N0 glottic SCC. Left vocal cord fixed, right mobile. Arytenoids bilaterally mobile. No cartilage involvement, no subglottic extension, no paraglottic invasion posteriorly. Adequate laryngeal exposure.

Labs: CrCl 72 mL/min (age-appropriate), NYHA I, no neuropathy, mild presbycusis (grade 1 on audiometry). Albumin 3.8, Hb 13.1.
```

**Expected recommendations**: concurrent_crt, ict_rt, nonsurgical_lp, ophl_any, ophl_type_ii, surgical_lp
**Expected excluded**: tlm
**Edge justification**: S75R, S13
**Predicted failure mode**: Neurodegenerative disease = relative CI for surgical LP (S75R). Impaired neuro fn = CI OPHL (S13). Shifts toward non-surgical.

### ⊘ I1-NULL1 — Age 82 but STILL fit → should NOT change

**Type**: null
**Variables changed**: `age`: 70_plus → 70_plus

```
Patient: 82-year-old male, ECOG 0. Retired engineer. Non-smoker for 15 years (former 25 pack-years). Lives independently with wife. Walks 5km daily, plays golf twice weekly.

Comorbidities: controlled hypertension on single agent, mild hyperlipidemia on statin. No cardiac history, no diabetes, no neurological disease.

Geriatric assessment: Comprehensive Geriatric Assessment (CGA) classifies patient as FIT. G8 screening score 15/17. No frailty markers. ADL and IADL fully independent. MMSE 29/30. Timed Up-and-Go test 9 seconds.

Tumor: cT3N0 glottic SCC. Left vocal cord fixed, right mobile. Arytenoids bilaterally mobile. No cartilage involvement, no subglottic extension, no paraglottic invasion posteriorly. Adequate laryngeal exposure.

Labs: CrCl 72 mL/min (age-appropriate), NYHA I, no neuropathy, mild presbycusis (grade 1 on audiometry). Albumin 3.8, Hb 13.1.
```

**Expected recommendations**: concurrent_crt, ict_rt, nonsurgical_lp, ophl_any, ophl_type_ii, surgical_lp, tlm
**Edge justification**: S6R, S80
**Predicted failure mode**: Even at 82, if CGA is fit, age alone is not CI. Tests extreme age sensitivity.

### ⊘ I1-NULL2 — CrCl 55 — only affects chemo choice

**Type**: null
**Variables changed**: `renal_function`: normal → 50_60_ml_min

```
Patient: 76-year-old male, ECOG 0. Retired engineer. Non-smoker for 15 years (former 25 pack-years). Lives independently with wife. Walks 5km daily, plays golf twice weekly.

Comorbidities: controlled hypertension on single agent, mild hyperlipidemia on statin. No cardiac history, no diabetes, no neurological disease.

Geriatric assessment: Comprehensive Geriatric Assessment (CGA) classifies patient as FIT. G8 screening score 15/17. No frailty markers. ADL and IADL fully independent. MMSE 29/30. Timed Up-and-Go test 9 seconds.

Tumor: cT3N0 glottic SCC. Left vocal cord fixed, right mobile. Arytenoids bilaterally mobile. No cartilage involvement, no subglottic extension, no paraglottic invasion posteriorly. Adequate laryngeal exposure.

Labs: CrCl 55 mL/min (moderate renal impairment), NYHA I, no neuropathy, mild presbycusis (grade 1 on audiometry). Albumin 3.8, Hb 13.1.
```

**Expected recommendations**: concurrent_crt, ict_rt, nonsurgical_lp, ophl_any, ophl_type_ii, surgical_lp, tlm
**Edge justification**: S69R
**Predicted failure mode**: CrCl 55 = relative CI for cisplatin only (S69R), does NOT affect LP eligibility itself
---

## J1-BASE — pretreatment_function / airway_obstruction_isolated

**Question**: Is non-surgical larynx preservation appropriate despite the airway obstruction?

### Baseline

```
Patient: 55-year-old male, ECOG 0, no comorbidities.

Tumor: cT3N0 glottic SCC. Left vocal cord fixed, right mobile. Arytenoids bilaterally mobile.

The patient presents with moderate airway obstruction — audible stridor on exertion, mild stridor at rest when supine. He sleeps propped up on two pillows but manages his daily activities. He has not required tracheostomy and the clinical team judges that he can safely begin treatment without emergent airway intervention.

No subglottic extension, no cartilage involvement, no extralaryngeal extension. No paraglottic space invasion posteriorly.

Function: Voice severely impaired. Swallowing normal — full oral diet without difficulty. No aspiration on clinical assessment. No feeding tube. Baseline laryngeal function, apart from voice, is considered preserved.

Labs: CrCl 95, NYHA I, no neuropathy. Albumin 4.0, Hb 14.0.
```

**Expected recommendations**: concurrent_crt, ict_rt, nonsurgical_lp
**Expected excluded**: total_laryngectomy
**Reasoning**: Airway obstruction alone is explicitly NOT CI for non-surgical LP (S21). No tracheostomy (S19R clear). Swallowing normal (S19R clear). CRT (S28) and ICT (S30) both viable.

### ⬆️ J1-P1 — Tracheostomy required → relative CI

**Type**: escalate
**Variables changed**: `pretreatment_tracheostomy`: false → true

```
Patient: 55-year-old male, ECOG 0, no comorbidities.

Tumor: cT3N0 glottic SCC. Left vocal cord fixed, right mobile. Arytenoids bilaterally mobile.

The patient presents with moderate airway obstruction — audible stridor on exertion, mild stridor at rest when supine. He sleeps propped up on two pillows but manages his daily activities. He required emergency tracheostomy placement 2 weeks ago for worsening stridor at rest. The tracheostomy is in situ and functioning well.

No subglottic extension, no cartilage involvement, no extralaryngeal extension. No paraglottic space invasion posteriorly.

Function: Voice severely impaired. Swallowing normal — full oral diet without difficulty. No aspiration on clinical assessment. No feeding tube. Baseline laryngeal function, apart from voice, is considered preserved.

Labs: CrCl 95, NYHA I, no neuropathy. Albumin 4.0, Hb 14.0.
```

**Expected recommendations**: concurrent_crt, ict_rt, nonsurgical_lp, total_laryngectomy
**Edge justification**: S19R, S115
**Predicted failure mode**: Tracheostomy = relative CI (S19R-b) + poor functional prognosis (S115). Non-surgical not excluded but balance shifts.

### ⬆️ J1-P2 — Aspiration pneumonia → absolute CI non-surgical

**Type**: escalate
**Variables changed**: `swallowing_status`: normal → recurrent_pneumonia; `baseline_laryngeal_function`: functional → dysfunctional

```
Patient: 55-year-old male, ECOG 0, no comorbidities.

Tumor: cT3N0 glottic SCC. Left vocal cord fixed, right mobile. Arytenoids bilaterally mobile.

The patient presents with moderate airway obstruction — audible stridor on exertion, mild stridor at rest when supine. He sleeps propped up on two pillows but manages his daily activities. He has not required tracheostomy and the clinical team judges that he can safely begin treatment without emergent airway intervention.

No subglottic extension, no cartilage involvement, no extralaryngeal extension. No paraglottic space invasion posteriorly.

Function: Voice severely impaired. Severe dysphagia with documented aspiration. Two episodes of aspiration pneumonia in the past month requiring hospital admission. FEES demonstrates penetration and aspiration with thin liquids and purees. PEG feeding tube placed. Baseline laryngeal function is globally dysfunctional.

Labs: CrCl 95, NYHA I, no neuropathy. Albumin 4.0, Hb 14.0.
```

**Expected recommendations**: total_laryngectomy
**Edge justification**: S19R
**Predicted failure mode**: Aspiration pneumonia = absolute CI non-surgical LP (S19R-a). The blocker is aspiration, not the airway obstruction.

### 🔄 J1-P3 — Add feeding tube

**Type**: flip
**Variables changed**: `pretreatment_feeding_tube`: false → true

```
Patient: 55-year-old male, ECOG 0, no comorbidities.

Tumor: cT3N0 glottic SCC. Left vocal cord fixed, right mobile. Arytenoids bilaterally mobile.

The patient presents with moderate airway obstruction — audible stridor on exertion, mild stridor at rest when supine. He sleeps propped up on two pillows but manages his daily activities. He has not required tracheostomy and the clinical team judges that he can safely begin treatment without emergent airway intervention.

No subglottic extension, no cartilage involvement, no extralaryngeal extension. No paraglottic space invasion posteriorly.

Function: Voice severely impaired. Swallowing normal — full oral diet without difficulty. No aspiration on clinical assessment. PEG feeding tube placed 3 weeks ago for nutritional support due to severe odynophagia. Baseline laryngeal function, apart from voice and swallowing, is considered partially preserved.

Labs: CrCl 95, NYHA I, no neuropathy. Albumin 4.0, Hb 14.0.
```

**Expected recommendations**: concurrent_crt, ict_rt, nonsurgical_lp, total_laryngectomy
**Edge justification**: S19R
**Predicted failure mode**: Feeding tube = relative CI (S19R-c). Non-surgical not excluded but adds to risk profile.

### ⬆️ J1-P4 — Add significant subglottic + extensive cricoid

**Type**: escalate
**Variables changed**: `subglottic_extension`: none → significant; `cricoid_cartilage_involvement`: none → extensive

```
Patient: 55-year-old male, ECOG 0, no comorbidities.

Tumor: cT3N0 glottic SCC. Left vocal cord fixed, right mobile. Arytenoids bilaterally mobile.

The patient presents with moderate airway obstruction — audible stridor on exertion, mild stridor at rest when supine. He sleeps propped up on two pillows but manages his daily activities. He has not required tracheostomy and the clinical team judges that he can safely begin treatment without emergent airway intervention.

Significant subglottic extension (>15mm) with extensive cricoid cartilage involvement on CT. No thyroid cartilage involvement. No extralaryngeal extension. No paraglottic space invasion posteriorly.

Function: Voice severely impaired. Swallowing normal — full oral diet without difficulty. No aspiration on clinical assessment. No feeding tube. Baseline laryngeal function, apart from voice, is considered preserved.

Labs: CrCl 95, NYHA I, no neuropathy. Albumin 4.0, Hb 14.0.
```

**Expected recommendations**: concurrent_crt, nonsurgical_lp, total_laryngectomy
**Edge justification**: S20R
**Predicted failure mode**: Significant subglottic + extensive cricoid = relative CI non-surgical (S20R). Combined with airway obstruction, balance shifts significantly.

### 🔗 J1-P5 — Tracheostomy + feeding tube + aspiration → convergent CIs

**Type**: multi
**Variables changed**: `pretreatment_tracheostomy`: false → true; `pretreatment_feeding_tube`: false → true; `swallowing_status`: normal → penetration_aspiration; `baseline_laryngeal_function`: functional → dysfunctional; `ecog_ps`: 0 → 1

```
Patient: 55-year-old male, ECOG 1 (due to functional limitations from airway and swallowing compromise), no other comorbidities.

Tumor: cT3N0 glottic SCC. Left vocal cord fixed, right mobile. Arytenoids bilaterally mobile.

The patient presents with moderate airway obstruction — audible stridor on exertion, mild stridor at rest when supine. He sleeps propped up on two pillows but manages his daily activities. He required emergency tracheostomy 2 weeks ago.

No subglottic extension, no cartilage involvement, no extralaryngeal extension. No paraglottic space invasion posteriorly.

Function: Voice severely impaired. Severe dysphagia with aspiration on FEES. PEG feeding tube in situ. Baseline laryngeal function is globally dysfunctional — severe dysphonia, aspiration, tracheostomy-dependent.

Labs: CrCl 95, NYHA I, no neuropathy. Albumin 4.0, Hb 14.0.
```

**Expected recommendations**: total_laryngectomy
**Edge justification**: S19R, S39R, S115
**Predicted failure mode**: Convergent CIs: aspiration (absolute, S19R-a), tracheostomy (relative, S19R-b), feeding tube (relative, S19R-c), dysfunctional larynx (absolute for LP, S39R). Clear TL.

### 🔄 J1-P6 — DNA repair disorder → absolute CI non-surgical LP (S74R)

**Type**: flip
**Variables changed**: `dna_repair_disorder`: false → true

```
Patient: 55-year-old male, ECOG 0, no comorbidities apart from xeroderma pigmentosum (DNA repair disorder) diagnosed in childhood, with multiple prior skin cancers managed surgically.

Tumor: cT3N0 glottic SCC. Left vocal cord fixed, right mobile. Arytenoids bilaterally mobile.

The patient presents with moderate airway obstruction — audible stridor on exertion, mild stridor at rest when supine. He sleeps propped up on two pillows but manages his daily activities. He has not required tracheostomy and the clinical team judges that he can safely begin treatment without emergent airway intervention.

No subglottic extension, no cartilage involvement, no extralaryngeal extension. No paraglottic space invasion posteriorly.

Function: Voice severely impaired. Swallowing normal — full oral diet without difficulty. No aspiration on clinical assessment. No feeding tube. Baseline laryngeal function, apart from voice, is considered preserved.

Labs: CrCl 95, NYHA I, no neuropathy. Albumin 4.0, Hb 14.0.
```

**Expected recommendations**: total_laryngectomy
**Edge justification**: S74R
**Predicted failure mode**: DNA repair disorder = absolute CI for non-surgical LP (S74R) due to radiation hypersensitivity.

### 🔄 J1-P7 — Previous neck RT → relative CI non-surgical LP (S74R)

**Type**: flip
**Variables changed**: `previous_neck_rt`: false → true

```
Patient: 55-year-old male, ECOG 0, history of previous radiotherapy to the neck 12 years ago for a different head and neck primary (cT1N0 oropharyngeal SCC, treated with RT alone, disease-free since). No other comorbidities.

Tumor: cT3N0 glottic SCC. Left vocal cord fixed, right mobile. Arytenoids bilaterally mobile.

The patient presents with moderate airway obstruction — audible stridor on exertion, mild stridor at rest when supine. He sleeps propped up on two pillows but manages his daily activities. He has not required tracheostomy and the clinical team judges that he can safely begin treatment without emergent airway intervention.

No subglottic extension, no cartilage involvement, no extralaryngeal extension. No paraglottic space invasion posteriorly.

Function: Voice severely impaired. Swallowing normal — full oral diet without difficulty. No aspiration on clinical assessment. No feeding tube. Baseline laryngeal function, apart from voice, is considered preserved.

Labs: CrCl 95, NYHA I, no neuropathy. Albumin 4.0, Hb 14.0.
```

**Expected recommendations**: total_laryngectomy
**Edge justification**: S74R
**Predicted failure mode**: Previous neck RT = relative CI for re-irradiation (S74R). Non-surgical LP not excluded but significantly complicated.

### ⊘ J1-NULL — Add age 72, fit — should NOT change

**Type**: null
**Variables changed**: `age`: under_70 → 70_plus

```
Patient: 72-year-old male, ECOG 0, no comorbidities. CGA: fit. G8 15/17.

Tumor: cT3N0 glottic SCC. Left vocal cord fixed, right mobile. Arytenoids bilaterally mobile.

The patient presents with moderate airway obstruction — audible stridor on exertion, mild stridor at rest when supine. He sleeps propped up on two pillows but manages his daily activities. He has not required tracheostomy and the clinical team judges that he can safely begin treatment without emergent airway intervention.

No subglottic extension, no cartilage involvement, no extralaryngeal extension. No paraglottic space invasion posteriorly.

Function: Voice severely impaired. Swallowing normal — full oral diet without difficulty. No aspiration on clinical assessment. No feeding tube. Baseline laryngeal function, apart from voice, is considered preserved.

Labs: CrCl 95, NYHA I, no neuropathy. Albumin 4.0, Hb 14.0.
```

**Expected recommendations**: concurrent_crt, ict_rt, nonsurgical_lp
**Expected excluded**: total_laryngectomy
**Edge justification**: S21, S80
**Predicted failure mode**: Airway obstruction NOT CI (S21) + age NOT CI when fit (S80). Both null signals should hold.

---

## Coverage Summary

| Family | Baseline | Perturbations | Edges Tested |
|---|---|---|---|
| glottic_cT2 | A1-BASE | 4 | S22, S23R, S28, S4R, S5R, S6R, S8, S80, SA2 |
| glottic_cT2 | A2-BASE | 4 | S23R, S28, S4R, S5R, S6R, S7R, S8, S80 |
| glottic_cT3 | B1-BASE | 11 | S14, S16R, S17R, S18R, S27, S28, S39R, S40R, S41R, S42R, S45, S46, S49R, S5R, S6R, S7R, S80 |
| supraglottic_cT3 | C1-BASE | 5 | S10R, S112, S12, S24R, S43, S9R |
| hypopharyngeal | D1-BASE | 4 | S115, S12, S19R, S43, S80 |
| cT4a_unselected | E1-BASE | 1 | S80 |
| cT4a_selected | F1-BASE | 7 | S12, S15R, S24R, S35R, S38R, S39R, S42R, S43, S46, S47R, S80 |
| cisplatin_eligibility | G1-BASE | 19 | S52R, S67, S68R, S69R, S70, S72R, S73R, S77R |
| post_ict_response | H1-BASE | 4 | S116, S119R, S120R, S121R, S129, S30, S31R, S55R, SA6 |
| post_ict_response | H2-BASE | 4 | S119R, S121R, S39R, S43 |
| elderly_frail | I1-BASE | 5 | S111R, S13, S69R, S6R, S75R, S80, S84, S88, S89 |
| pretreatment_function | J1-BASE | 8 | S115, S19R, S20R, S21, S39R, S74R, S80 |

**Total unique edges tested**: 60
**Edges**: S10R, S111R, S112, S115, S116, S119R, S12, S120R, S121R, S129, S13, S14, S15R, S16R, S17R, S18R, S19R, S20R, S21, S22, S23R, S24R, S27, S28, S30, S31R, S35R, S38R, S39R, S40R, S41R, S42R, S43, S45, S46, S47R, S49R, S4R, S52R, S55R, S5R, S67, S68R, S69R, S6R, S70, S72R, S73R, S74R, S75R, S77R, S7R, S8, S80, S84, S88, S89, S9R, SA2, SA6