#!/usr/bin/env python3
"""
KG₁ Vignette Generator — Full Test Battery
============================================
Generates clinical vignettes + perturbations for LLM causal reasoning evaluation.
Reads KG₁ from kg1_data.json, applies perturbation logic with consistency checks,
outputs Markdown (human review) and JSON (LLM API).

Usage:
    python vignette_generator.py [--kg1 kg1_data.json] [--outdir outputs]
"""

import json, copy, hashlib, argparse, os
from dataclasses import dataclass, field, asdict
from typing import Optional
from pathlib import Path

try:
    from .label_space import normalise_expected_label_lists
except ImportError:
    from label_space import normalise_expected_label_lists

# ═══════════════════════════════════════════════════════════════════
# DATA STRUCTURES
# ═══════════════════════════════════════════════════════════════════

@dataclass
class VariableChange:
    variable: str
    from_value: str
    to_value: str

@dataclass
class TextReplacement:
    old_text: str
    new_text: str

@dataclass
class Perturbation:
    id: str
    pert_type: str                            # flip, escalate, null, grey_zone, multi
    label: str
    variables_changed: list                   # list of VariableChange
    staging_impact: Optional[str]
    text_replacements: list                   # list of TextReplacement
    expected_recommendations: list
    expected_excluded: list
    edge_justification: list
    predicted_failure_mode: str
    notes: str = ""
    grey_zone_statement: Optional[str] = None
    family_override: Optional[str] = None

@dataclass
class BaselineTemplate:
    id: str
    family: str
    subtype: str
    variable_assignments: dict
    clinical_text: str
    question: str
    expected_recommendations: list
    expected_excluded: list
    expected_reasoning: str
    perturbations: list = field(default_factory=list)  # list of Perturbation

def vc(var, fr, to):
    """Shorthand for VariableChange."""
    return VariableChange(var, str(fr), str(to))

def tr(old, new):
    """Shorthand for TextReplacement."""
    return TextReplacement(old, new)

# ═══════════════════════════════════════════════════════════════════
# STAGING PROPAGATION RULES
# ═══════════════════════════════════════════════════════════════════

T4A_TRIGGERS = {
    "thyroid_cartilage_outer_cortex": "true",
    "thyroid_cartilage_full_thickness": "true",
    "extralaryngeal_extension": "significant",
}

T3_TRIGGERS = {
    "vocal_cord_mobility": "fixed",
}

def check_staging_consistency(variables: dict) -> list:
    """Return warnings if variable state is inconsistent with T stage."""
    warnings = []
    t = variables.get("t_stage", "")
    for var, trigger_val in T4A_TRIGGERS.items():
        if str(variables.get(var, "")) == trigger_val and t != "cT4a":
            warnings.append(f"STAGING ERROR: {var}={trigger_val} requires t_stage=cT4a, got {t}")
    for var, trigger_val in T3_TRIGGERS.items():
        if str(variables.get(var, "")) == trigger_val and t in ("cT1", "cT2"):
            warnings.append(f"STAGING ERROR: {var}={trigger_val} requires t_stage≥cT3, got {t}")
    # Bilateral arytenoid + functional larynx is implausible
    if variables.get("posterior_laryngeal_involvement") == "bilateral_arytenoid":
        if variables.get("baseline_laryngeal_function") == "functional":
            warnings.append("COHERENCE WARNING: bilateral arytenoid involvement with functional larynx is unusual")
    # ECOG 0 with tracheostomy + feeding tube
    if variables.get("ecog_ps") == "0":
        if variables.get("pretreatment_tracheostomy") == "true" and variables.get("pretreatment_feeding_tube") == "true":
            warnings.append("COHERENCE WARNING: ECOG 0 with tracheostomy + feeding tube is implausible")
    return warnings


# ═══════════════════════════════════════════════════════════════════
# TEMPLATE DEFINITIONS
# ═══════════════════════════════════════════════════════════════════

def build_all_templates() -> list:
    """Build and return all 12 baseline templates with perturbations."""
    templates = []

    # ─────────────────────────────────────────────────────────────
    # A1 — Glottic cT2 Favorable, TLM-Eligible
    # ─────────────────────────────────────────────────────────────
    a1 = BaselineTemplate(
        id="A1-BASE", family="glottic_cT2", subtype="favorable_TLM_eligible",
        variable_assignments={
            "t_stage":"cT2","n_stage":"cN0","primary_site":"glottic",
            "tumor_volume":"low","unfavorable_ct2":"false",
            "thyroid_cartilage_inner_cortex":"none","thyroid_cartilage_outer_cortex":"false",
            "thyroid_cartilage_erosion":"false","posterior_paraglottic_space":"false",
            "pre_epiglottic_space":"none","anterior_commissure":"none",
            "subglottic_extension":"none","extralaryngeal_extension":"none",
            "posterior_laryngeal_involvement":"none","magic_plane_crossing":"false",
            "vocal_cord_mobility":"partially_impaired","arytenoid_mobility":"bilateral_mobile",
            "baseline_laryngeal_function":"functional","swallowing_status":"normal",
            "pretreatment_tracheostomy":"false","pretreatment_feeding_tube":"false",
            "airway_obstruction":"false","laryngeal_exposure":"adequate",
            "age":"under_70","ecog_ps":"0","frailty_status":"fit",
            "cardiopulmonary_function":"good","neurological_function":"good",
            "renal_function":"normal","cardiac_function":"normal","neuropathy":"none",
        },
        clinical_text="""Patient: 54-year-old male, retired teacher, ECOG 0. Non-smoker for 8 years (former 20 pack-year history). Moderate alcohol intake. No significant comorbidities.

Tumor: cT2N0 glottic squamous cell carcinoma of the left true vocal cord. The lesion involves the middle and anterior third of the left vocal cord with impaired mobility but no fixation.

Imaging: CT and MRI show no cartilage involvement, no paraglottic space invasion, no subglottic extension, and no pre-epiglottic space involvement. No suspicious lymph nodes.

Function: Mild dysphonia (VHI-10: 18). No dysphagia. No airway compromise. Adequate laryngeal exposure confirmed on clinic suspension laryngoscopy simulation.

Labs: Normal blood panel, CrCl 102 mL/min.""",
        question="What are the appropriate treatment options for this patient?",
        expected_recommendations=["tlm","rt_alone","ophl_type_ii"],
        expected_excluded=["concurrent_crt","total_laryngectomy"],
        expected_reasoning="Favorable cT2N0: TLM viable (adequate exposure, no blocking features). RT alone adequate per S22. No indication for chemo at cT2N0.",
    )
    a1.perturbations = [
        Perturbation("A1-P1","flip","Laryngeal exposure insufficient",
            [vc("laryngeal_exposure","adequate","insufficient")], None,
            [tr("Adequate laryngeal exposure confirmed on clinic suspension laryngoscopy simulation.",
                "Laryngeal exposure assessed as insufficient on preoperative suspension laryngoscopy simulation — limited visualisation of the posterior glottis due to anatomy.")],
            ["rt_alone","ophl_type_ii"], ["tlm"],
            ["S5R","S22"], "Correctly blocks TLM while preserving other options"),
        Perturbation("A1-P2","escalate","Vocal cord fixed → upstages to cT3 (STAGING PROPAGATION)",
            [vc("vocal_cord_mobility","partially_impaired","fixed"),
             vc("t_stage","cT2","cT3")],
            "cT2 → cT3 (vocal cord fixation defines T3 by AJCC)",
            [tr("with impaired mobility but no fixation.",
                "with complete fixation of the left vocal cord."),
             tr("Tumor: cT2N0 glottic squamous cell carcinoma",
                "Tumor: cT3N0 glottic squamous cell carcinoma"),
             tr("Mild dysphonia (VHI-10: 18).","Severe dysphonia (VHI-10: 32).")],
            ["tlm","ophl_type_ii","concurrent_crt","ict_rt"],["total_laryngectomy"],
            ["S23R","S4R","S28"],
            "Must recognize that fixed cord upstages to cT3 and open the full cT3 decision landscape including CRT and ICT, not just escalate RT",
            family_override="glottic_cT3"),
        Perturbation("A1-P3","flip","Add unfavorable cT2 features without fixation (SA2)",
            [vc("unfavorable_ct2","false","true"),
             vc("tumor_volume","low","high"),
             vc("anterior_commissure","none","present_good_exposure"),
             vc("subglottic_extension","none","under_10mm_anterior")], None,
            [tr("The lesion involves the middle and anterior third of the left vocal cord with impaired mobility but no fixation.",
                "The lesion is bulky, involving the entire left vocal cord with extension to the anterior commissure and minor anterior subglottic extension (approximately 7mm). Cord mobility is impaired but not fixed."),
             tr("no subglottic extension, and no pre-epiglottic space involvement.",
                "minor anterior subglottic extension, and no pre-epiglottic space involvement."),
             tr("Mild dysphonia (VHI-10: 18).","Moderate dysphonia (VHI-10: 24).")],
            ["tlm","rt_alone","rt_accelerated","ophl_type_ii"],["total_laryngectomy"],
            ["SA2","S23R","S8"],
            "Should recognise unfavorable cT2 features (bulky, AC, subglottic, impaired mobility) warrant consideration of accelerated RT (S23R) even though still staged cT2"),
        Perturbation("A1-NULL","null","Age 74, fit — should NOT change options",
            [vc("age","under_70","70_plus")], None,
            [tr("Patient: 54-year-old male, retired teacher, ECOG 0.",
                "Patient: 74-year-old male, retired teacher, ECOG 0. Comprehensive Geriatric Assessment: fit. G8 score 15/17.")],
            ["tlm","rt_alone","ophl_type_ii"], [],
            ["S6R","S80"], "Over-sensitivity to age in fit patient"),
    ]
    templates.append(a1)

    # ─────────────────────────────────────────────────────────────
    # A2 — Glottic cT2 Unfavorable, Reduced Cord Mobility
    # ─────────────────────────────────────────────────────────────
    a2 = BaselineTemplate(
        id="A2-BASE", family="glottic_cT2", subtype="unfavorable_reduced_mobility",
        variable_assignments={
            "t_stage":"cT2","n_stage":"cN0","primary_site":"glottic",
            "tumor_volume":"high","unfavorable_ct2":"true",
            "thyroid_cartilage_inner_cortex":"none","thyroid_cartilage_erosion":"false",
            "posterior_paraglottic_space":"false","pre_epiglottic_space":"none",
            "anterior_commissure":"present_good_exposure",
            "subglottic_extension":"under_10mm_anterior",
            "vocal_cord_mobility":"partially_impaired",
            "arytenoid_mobility":"bilateral_mobile","laryngeal_exposure":"adequate",
            "baseline_laryngeal_function":"functional","swallowing_status":"normal",
            "pretreatment_tracheostomy":"false","airway_obstruction":"false",
            "age":"under_70","ecog_ps":"0","renal_function":"normal",
        },
        clinical_text="""Patient: 61-year-old male, ECOG 0. Active smoker (35 pack-years). No significant comorbidities apart from mild COPD (GOLD I).

Tumor: cT2N0 glottic SCC. The lesion is bulky, involving the entire left vocal cord with extension to the anterior commissure. Left vocal cord mobility is reduced. The right cord is normal. Arytenoids bilaterally mobile.

Imaging: MRI shows anterior commissure involvement with adequate visualisation on office endoscopy. There is minor anterior subglottic extension (approximately 7mm). No paraglottic space invasion. No cartilage involvement. No suspicious lymph nodes.

Function: Moderate dysphonia. No dysphagia, no airway compromise. Laryngeal exposure assessed as adequate.

Labs: CrCl 89 mL/min, albumin 4.0, Hb 13.8.""",
        question="What are the appropriate treatment options for this patient?",
        expected_recommendations=["tlm","rt_alone","rt_accelerated","ophl_type_ii"],
        expected_excluded=["total_laryngectomy"],
        expected_reasoning="Unfavorable cT2 (SA2): bulky, AC involvement, reduced cord, anterior subglottic. TLM technically feasible (exposure adequate, AC with good exposure per S8). Accelerated RT warranted given reduced cord (S23R).",
    )
    a2.perturbations = [
        Perturbation("A2-P1","flip","AC difficult exposure → TLM relative CI",
            [vc("anterior_commissure","present_good_exposure","present_difficult_exposure")], None,
            [tr("anterior commissure involvement with adequate visualisation on office endoscopy.",
                "anterior commissure involvement with difficult visualisation — office endoscopy shows limited access to the anterior commissure region.")],
            ["rt_alone","rt_accelerated","ophl_type_ii"], ["tlm"],
            ["S7R","S8"],
            "Should block TLM due to AC with difficult exposure (S7R absolute CI)"),
        Perturbation("A2-P2","flip","Laryngeal exposure insufficient",
            [vc("laryngeal_exposure","adequate","insufficient")], None,
            [tr("Laryngeal exposure assessed as adequate.",
                "Laryngeal exposure assessed as insufficient on preoperative evaluation — Cormack-Lehane grade III.")],
            ["rt_alone","rt_accelerated","ophl_type_ii"], ["tlm"],
            ["S5R"], "Absolute CI TLM (S5R, 100%)"),
        Perturbation("A2-P3","escalate","Vocal cord fixed → upstages to cT3",
            [vc("vocal_cord_mobility","partially_impaired","fixed"),
             vc("t_stage","cT2","cT3")],
            "cT2 → cT3 (vocal cord fixation defines T3 by AJCC)",
            [tr("Left vocal cord mobility is reduced.","Left vocal cord is fixed."),
             tr("cT2N0 glottic SCC.","cT3N0 glottic SCC.")],
            ["concurrent_crt","ophl_type_ii","ict_rt","tlm"], [],
            ["S23R","S4R","S28"],
            "Fixed cord = T3 by definition. Must upstage and offer full cT3 options including CRT/ICT.",
            family_override="glottic_cT3"),
        Perturbation("A2-NULL","null","Age 73, fit",
            [vc("age","under_70","70_plus")], None,
            [tr("Patient: 61-year-old male, ECOG 0.",
                "Patient: 73-year-old male, ECOG 0. Comprehensive Geriatric Assessment: fit. G8 15/17.")],
            ["tlm","rt_alone","rt_accelerated","ophl_type_ii"], [],
            ["S6R","S80"], "Age alone should not change any recommendation"),
    ]
    templates.append(a2)

    # ─────────────────────────────────────────────────────────────
    # B1 — Glottic cT3 TLM-Eligible (CENTREPIECE — most perturbations)
    # ─────────────────────────────────────────────────────────────
    b1 = BaselineTemplate(
        id="B1-BASE", family="glottic_cT3", subtype="TLM_eligible_clean",
        variable_assignments={
            "t_stage":"cT3","n_stage":"cN0","primary_site":"glottic",
            "tumor_volume":"low",
            "thyroid_cartilage_inner_cortex":"none","thyroid_cartilage_outer_cortex":"false",
            "thyroid_cartilage_erosion":"false","cricoid_cartilage_involvement":"none",
            "posterior_paraglottic_space":"false","pre_epiglottic_space":"none",
            "anterior_commissure":"none","subglottic_extension":"none",
            "extralaryngeal_extension":"none","posterior_laryngeal_involvement":"none",
            "magic_plane_crossing":"false","cricoarytenoid_joint_invasion":"false",
            "vocal_cord_mobility":"fixed","arytenoid_mobility":"bilateral_mobile",
            "baseline_laryngeal_function":"functional","swallowing_status":"normal",
            "pretreatment_tracheostomy":"false","pretreatment_feeding_tube":"false",
            "airway_obstruction":"false","laryngeal_exposure":"adequate",
            "age":"under_70","ecog_ps":"0","frailty_status":"fit",
            "cardiopulmonary_function":"good","neurological_function":"good",
            "renal_function":"normal","cardiac_function":"normal","neuropathy":"none",
        },
        clinical_text="""Patient: 58-year-old male, ECOG 0. Former smoker (quit 3 years ago, 25 pack-years). Social drinker. No significant comorbidities.

Tumor: cT3N0 glottic SCC. Left vocal cord fixed, right cord fully mobile. Arytenoids bilaterally mobile. The lesion involves the left vocal cord with extension into the anterior paraglottic space on the left side only.

Imaging: MRI shows paraglottic space invasion confined to the anterior compartment on the left. No posterior paraglottic involvement. No thyroid cartilage involvement (inner or outer cortex intact). No cricoid involvement. No pre-epiglottic space invasion. No subglottic extension. No suspicious lymph nodes.

Function: Moderate-to-severe dysphonia. No dysphagia, no aspiration. No airway obstruction. No tracheostomy. Laryngeal exposure assessed as adequate on preoperative evaluation (Cormack-Lehane grade I).

Labs: CrCl 98 mL/min, NYHA I, no neuropathy, normal hearing. Albumin 4.2, Hb 14.5.""",
        question="What larynx-preservation treatment options are appropriate for this patient?",
        expected_recommendations=["tlm","ophl_type_ii","concurrent_crt","ict_rt"],
        expected_excluded=["total_laryngectomy"],
        expected_reasoning="Clean cT3N0: TLM viable (adequate exposure, no S7R blockers). OPHL-II viable (no S15R/S16R/S17R blockers). CRT highest LP rate (S28). ICT viable (S30, LoE I).",
    )
    b1.perturbations = [
        # --- TC INNER CORTEX: treatment-conditional pattern ---
        Perturbation("B1-P1","flip","Focal TC inner cortex (TREATMENT-CONDITIONAL)",
            [vc("thyroid_cartilage_inner_cortex","none","focal")], None,
            [tr("No thyroid cartilage involvement (inner or outer cortex intact).",
                "MRI shows focal inner cortex involvement of the thyroid cartilage on the left, without outer cortex or full-thickness invasion. Outer cortex intact.")],
            ["ophl_type_ii","concurrent_crt","ict_rt"], ["tlm"],
            ["S7R","S14","S27","S28"],
            "Over-generalisation: 'cartilage = no surgery' without distinguishing TLM from OPHL",
            notes="KEY TEST: TC inner cortex is absolute CI for TLM (S7R) but NOT CI for OPHL-II (S14) and NOT CI for CRT (S27)"),
        Perturbation("B1-P2","escalate","Outer cortex → cT4a (STAGING PROPAGATION)",
            [vc("thyroid_cartilage_outer_cortex","false","true"),
             vc("extralaryngeal_extension","none","minimal_anterior"),
             vc("t_stage","cT3","cT4a")],
            "cT3 → cT4a (outer cortex invasion by AJCC definition)",
            [tr("Tumor: cT3N0 glottic SCC.","Tumor: cT4aN0 glottic SCC."),
             tr("No thyroid cartilage involvement (inner or outer cortex intact). No cricoid involvement. No pre-epiglottic space invasion. No subglottic extension.",
                "CT shows focal outer cortex invasion of the thyroid cartilage anteriorly with minimal anterior extralaryngeal soft tissue extension confined to the strap muscles. No deep muscle invasion, no magic plane crossing. No cricoid involvement. No pre-epiglottic space invasion. No subglottic extension.")],
            ["ophl_any","total_laryngectomy","concurrent_crt"], ["tlm"],
            ["S45","S46","S40R","S41R","S49R"],
            "Binary: 'cT4a = TL always' (misses selected LP exception per S46, S40R second clause)"),
        # --- Individual S7R sub-edges ---
        Perturbation("B1-P3","flip","Posterior paraglottic space → TLM blocked",
            [vc("posterior_paraglottic_space","false","true")], None,
            [tr("No posterior paraglottic involvement.",
                "Posterior paraglottic space involvement on the left, extending to the posterior compartment.")],
            ["ophl_type_ii","concurrent_crt","ict_rt"], ["tlm"],
            ["S7R"], "Should block TLM specifically, not all surgery"),
        Perturbation("B1-P4","flip","Massive PES abutting membrane → TLM blocked",
            [vc("pre_epiglottic_space","none","massive_abutting_membrane")], None,
            [tr("No pre-epiglottic space invasion.",
                "Massive pre-epiglottic space invasion with tumor abutting the thyrohyoid membrane.")],
            ["ophl_type_ii","concurrent_crt","ict_rt"], ["tlm"],
            ["S7R"], "TLM absolute CI; OPHL/CRT remain viable"),
        Perturbation("B1-P5","flip","Posterior subglottic <10mm → TLM blocked",
            [vc("subglottic_extension","none","under_10mm_posterior")], None,
            [tr("No subglottic extension.",
                "Subglottic extension of approximately 8mm posteriorly.")],
            ["ophl_type_ii","concurrent_crt","ict_rt"], ["tlm"],
            ["S7R"], "Subtle: posterior <10mm blocks TLM but anterior <10mm does not"),
        Perturbation("B1-P6","flip","Laryngeal exposure insufficient",
            [vc("laryngeal_exposure","adequate","insufficient")], None,
            [tr("Laryngeal exposure assessed as adequate on preoperative evaluation (Cormack-Lehane grade I).",
                "Laryngeal exposure assessed as insufficient on preoperative evaluation (Cormack-Lehane grade III) — limited visualisation due to anatomy.")],
            ["ophl_type_ii","concurrent_crt","ict_rt"], ["tlm"],
            ["S5R"], "Absolute CI TLM (S5R, 100%)"),
        Perturbation("B1-P7","flip","AC difficult exposure → TLM blocked",
            [vc("anterior_commissure","none","present_difficult_exposure")], None,
            [tr("The lesion involves the left vocal cord with extension into the anterior paraglottic space on the left side only.",
                "The lesion involves the left vocal cord with extension to the anterior commissure and into the anterior paraglottic space on the left side. Anterior commissure exposure is assessed as difficult on preoperative evaluation.")],
            ["ophl_type_ii","concurrent_crt","ict_rt"], ["tlm"],
            ["S7R"], "AC with difficult exposure = absolute CI TLM"),
        # --- Additional edge coverage ---
        Perturbation("B1-P8","flip","Bilateral arytenoid → CI ALL conservative surgery (S16R)",
            [vc("posterior_laryngeal_involvement","none","bilateral_arytenoid"),
             vc("arytenoid_mobility","bilateral_mobile","bilateral_fixed"),
             vc("baseline_laryngeal_function","functional","dysfunctional")], None,
            [tr("Arytenoids bilaterally mobile. The lesion involves the left vocal cord",
                "Both arytenoids fixed with bilateral posterior involvement. The lesion involves the left vocal cord"),
             tr("No posterior paraglottic involvement.",
                "Bilateral posterior involvement with both arytenoids fixed."),
             tr("Moderate-to-severe dysphonia. No dysphagia, no aspiration.",
                "Severe dysphonia with emerging aspiration risk due to bilateral arytenoid fixation.")],
            ["total_laryngectomy","concurrent_crt"], ["tlm","ophl_any","surgical_lp"],
            ["S16R","S39R","S42R"],
            "Bilateral arytenoid = CI ALL conservative surgery (S16R, 98%). Must block OPHL too, not just TLM."),
        Perturbation("B1-P9","flip","Subglottic >10mm + CAJ invasion → CI OPHL-II (S17R)",
            [vc("subglottic_extension","none","over_10mm"),
             vc("cricoarytenoid_joint_invasion","false","true")], None,
            [tr("No subglottic extension.",
                "Subglottic extension >10mm with cricoarytenoid joint invasion on the left."),
             tr("No cricoid involvement.",
                "Cricoid involvement with CAJ invasion.")],
            ["concurrent_crt","ict_rt","ophl_type_iii"], ["tlm","ophl_type_ii"],
            ["S17R","S18R"],
            ">10mm subglottic + CAJ = absolute CI OPHL-II (S17R). But >10mm anterior subglottic may allow OPHL-III in expert centers (S18R)."),
        # --- NOT-CONTRAINDICATION null tests ---
        Perturbation("B1-NULL1","null","Age 73, fit — should NOT change",
            [vc("age","under_70","70_plus"),vc("frailty_status","fit","fit")], None,
            [tr("Patient: 58-year-old male, ECOG 0.",
                "Patient: 73-year-old male, ECOG 0. Comprehensive Geriatric Assessment: fit. G8 score 15/17.")],
            ["tlm","ophl_type_ii","concurrent_crt","ict_rt"], [],
            ["S6R","S80"], "Over-sensitivity to age in fit elderly"),
        Perturbation("B1-NULL2","null","Focal TC inner cortex — CRT should NOT be blocked",
            [vc("thyroid_cartilage_inner_cortex","none","focal")], None,
            [tr("No thyroid cartilage involvement (inner or outer cortex intact).",
                "MRI shows focal inner cortex involvement of the thyroid cartilage on the left, without outer cortex or full-thickness invasion.")],
            ["concurrent_crt"], [],
            ["S27"],
            "Tests S27 specifically: TC inner cortex is NOT CI for CRT. Ask targeted: 'Is CRT contraindicated by the cartilage finding?'",
            notes="TARGETED QUESTION VARIANT: 'Given the focal inner cortex thyroid cartilage involvement, is concurrent chemoradiotherapy contraindicated?'"),
    ]
    templates.append(b1)

    # ─────────────────────────────────────────────────────────────
    # C1 — Supraglottic cT3, Limited PES (SITE-CONDITIONAL)
    # ─────────────────────────────────────────────────────────────
    c1 = BaselineTemplate(
        id="C1-BASE", family="supraglottic_cT3", subtype="limited_PES",
        variable_assignments={
            "t_stage":"cT3","n_stage":"cN1","primary_site":"supraglottic",
            "tumor_volume":"low",
            "thyroid_cartilage_inner_cortex":"none","thyroid_cartilage_erosion":"false",
            "pre_epiglottic_space":"limited","posterior_paraglottic_space":"false",
            "subglottic_extension":"none","extralaryngeal_extension":"none",
            "posterior_laryngeal_involvement":"none","magic_plane_crossing":"false",
            "vocal_cord_mobility":"partially_impaired","arytenoid_mobility":"bilateral_mobile",
            "baseline_laryngeal_function":"functional","swallowing_status":"normal",
            "pretreatment_tracheostomy":"false","airway_obstruction":"false",
            "laryngeal_exposure":"adequate",
            "age":"under_70","ecog_ps":"0",
            "cardiopulmonary_function":"good","neurological_function":"good",
            "renal_function":"normal",
        },
        clinical_text="""Patient: 56-year-old male, ECOG 0. Former smoker (quit 6 years, 30 pack-years). No significant comorbidities.

Tumor: cT3N1 supraglottic SCC arising from the epiglottis. There is a single ipsilateral level II lymph node (2.2cm, no extranodal extension on imaging).

Imaging: MRI shows limited pre-epiglottic space invasion — the tumor extends into the anterior portion of the PES without reaching the thyroid cartilage. No thyroid cartilage erosion or involvement. No paraglottic space invasion posteriorly. Vocal cord mobility mildly reduced on the left but not fixed. Arytenoids bilaterally mobile. No subglottic extension.

Function: Mild dysphagia to solids (no aspiration on FEES). Voice mildly altered. No airway obstruction. No tracheostomy. Laryngeal exposure adequate.

Labs: CrCl 94, NYHA I, normal hearing. Albumin 3.9, Hb 13.6.""",
        question="What larynx-preservation treatment options are appropriate for this patient?",
        expected_recommendations=["tlm","tors","ophl_type_i","concurrent_crt","ict_rt"],
        expected_excluded=["total_laryngectomy"],
        expected_reasoning="Supraglottic cT3 with limited PES: TLM/TORS viable per S10R. OPHL-I viable. CRT + ICT viable. N1 does not contraindicate surgical LP (S24R only for N2+).",
    )
    c1.perturbations = [
        Perturbation("C1-P1","escalate","PES pronounced → OPHL type I preferred",
            [vc("pre_epiglottic_space","limited","massive_not_abutting_membrane")], None,
            [tr("limited pre-epiglottic space invasion — the tumor extends into the anterior portion of the PES without reaching the thyroid cartilage.",
                "pronounced pre-epiglottic space invasion — the tumor fills most of the PES but does not abut the thyrohyoid membrane or thyroid cartilage.")],
            ["ophl_type_i","concurrent_crt","ict_rt"], ["tlm"],
            ["S10R"],
            "Pronounced PES shifts from TLM/TORS toward OPHL-I (S10R-b)"),
        Perturbation("C1-P2","escalate","PES + TC erosion → OPHL-IIB (SITE-CONDITIONAL)",
            [vc("pre_epiglottic_space","limited","massive_not_abutting_membrane"),
             vc("thyroid_cartilage_erosion","false","true")], None,
            [tr("limited pre-epiglottic space invasion — the tumor extends into the anterior portion of the PES without reaching the thyroid cartilage. No thyroid cartilage erosion or involvement.",
                "pronounced pre-epiglottic space invasion with thyroid cartilage erosion on CT. No full-thickness infiltration, no outer cortex invasion.")],
            ["ophl_type_iib","concurrent_crt","ict_rt"], ["tlm"],
            ["S10R"],
            "CRITICAL SITE-CONDITIONAL: TC erosion = INDICATION for OPHL-IIB in supraglottic (S10R) but would be CI for TLM in glottic (S9R)",
            notes="This is the site-conditional pattern: same finding (TC erosion) has opposite meaning at different sites"),
        Perturbation("C1-P3","flip","Change site to glottic + keep TC erosion (SITE CROSSOVER)",
            [vc("primary_site","supraglottic","glottic"),
             vc("pre_epiglottic_space","limited","none"),
             vc("thyroid_cartilage_erosion","false","true")], None,
            [tr("Tumor: cT3N1 supraglottic SCC arising from the epiglottis.",
                "Tumor: cT3N1 glottic SCC."),
             tr("limited pre-epiglottic space invasion — the tumor extends into the anterior portion of the PES without reaching the thyroid cartilage. No thyroid cartilage erosion or involvement.",
                "no pre-epiglottic space involvement. Thyroid cartilage erosion on CT, without full-thickness infiltration or outer cortex invasion.")],
            ["ophl_type_ii","concurrent_crt","ict_rt"], ["tlm"],
            ["S9R","S10R"],
            "TC erosion now = CI for TLM (S9R) in glottic. NOT an indication for OPHL-IIB (that's supraglottic-specific). Tests site-conditionality.",
            family_override="glottic_cT3"),
        Perturbation("C1-P4","flip","N2 → relative CI partial laryngectomy",
            [vc("n_stage","cN1","cN2")], None,
            [tr("a single ipsilateral level II lymph node (2.2cm, no extranodal extension on imaging).",
                "bilateral lymphadenopathy — 3.0cm left level II, 2.5cm left level III, 1.8cm right level II. No extranodal extension on imaging.")],
            ["concurrent_crt","ict_rt"], ["tlm"],
            ["S24R"],
            "N2+ = relative CI for partial laryngectomy (S24R), preference shifts to CRT"),
        Perturbation("C1-P5","flip","Site → hypopharyngeal (SITE-CONDITIONAL)",
            [vc("primary_site","supraglottic","hypopharyngeal"),
             vc("pre_epiglottic_space","limited","none")], None,
            [tr("Tumor: cT3N1 supraglottic SCC arising from the epiglottis.",
                "Tumor: cT3N1 SCC of the left piriform sinus."),
             tr("MRI shows limited pre-epiglottic space invasion — the tumor extends into the anterior portion of the PES without reaching the thyroid cartilage.",
                "MRI shows tumor confined to the piriform sinus with extension to the medial wall.")],
            ["concurrent_crt","ict_rt","total_laryngectomy"], ["tlm"],
            ["S12","S43","S112"],
            "Hypopharyngeal: TLM not first-line (S12), worse outcomes with non-surgical (S43)"),
    ]
    templates.append(c1)

    # ─────────────────────────────────────────────────────────────
    # D1 — Hypopharyngeal cT3 Advanced
    # ─────────────────────────────────────────────────────────────
    d1 = BaselineTemplate(
        id="D1-BASE", family="hypopharyngeal", subtype="cT3_advanced",
        variable_assignments={
            "t_stage":"cT3","n_stage":"cN2","primary_site":"hypopharyngeal",
            "tumor_volume":"high",
            "thyroid_cartilage_inner_cortex":"none","thyroid_cartilage_outer_cortex":"false",
            "subglottic_extension":"none","extralaryngeal_extension":"none",
            "posterior_laryngeal_involvement":"unilateral_arytenoid",
            "vocal_cord_mobility":"fixed","arytenoid_mobility":"unilateral_fixed",
            "baseline_laryngeal_function":"functional",
            "swallowing_status":"impaired_no_aspiration",
            "pretreatment_tracheostomy":"false","pretreatment_feeding_tube":"false",
            "airway_obstruction":"false","laryngeal_exposure":"adequate",
            "age":"under_70","ecog_ps":"1",
            "renal_function":"normal","cardiac_function":"normal","neuropathy":"none",
            "comorbidity_burden":"none_mild",
        },
        clinical_text="""Patient: 63-year-old male, ECOG 1. Current smoker (40 pack-years), heavy alcohol use (>14 units/week). Mild malnutrition (albumin 3.3, BMI 19.2, unintentional weight loss 5kg over 3 months).

Tumor: cT3N2b SCC of the left piriform sinus extending to the postcricoid area. Left vocal cord fixed, left arytenoid fixed. Right cord and arytenoid mobile. No cartilage invasion on imaging.

Imaging: CT and MRI show bulky primary with bilateral level II-IV lymphadenopathy (largest 3.5cm left level III, 2.0cm right level II), no extranodal extension. No subglottic extension. No extralaryngeal extension. No carotid artery encasement.

Function: Moderate dysphagia to solids, managing liquids and soft diet. No aspiration on FEES. Voice severely impaired. No airway obstruction, no tracheostomy, no feeding tube.

Labs: CrCl 82, NYHA I, no neuropathy, normal hearing, Hb 12.1.""",
        question="What are the treatment options for this patient, and what is the preferred strategy?",
        expected_recommendations=["concurrent_crt","ict_rt","total_laryngectomy"],
        expected_excluded=["tlm"],
        expected_reasoning="Hypopharyngeal advanced: TLM not first-line (S12). OPHL limited by unilateral arytenoid + N2 (S24R). ICT → response assessment especially relevant (S30). Hypopharyngeal origin = worse LP outcomes (S43).",
    )
    d1.perturbations = [
        Perturbation("D1-P1","flip","Site → glottic (SITE CROSSOVER)",
            [vc("primary_site","hypopharyngeal","glottic")], None,
            [tr("cT3N2b SCC of the left piriform sinus extending to the postcricoid area.",
                "cT3N2b glottic SCC with transglottic extension.")],
            ["concurrent_crt","ict_rt","ophl_type_ii","total_laryngectomy"], [],
            ["S12","S43"],
            "Removing site-specific penalties: TLM now discussable, non-surgical outcomes not penalised by site"),
        Perturbation("D1-P2","escalate","Add aspiration pneumonia → absolute CI non-surgical",
            [vc("swallowing_status","impaired_no_aspiration","recurrent_pneumonia")], None,
            [tr("Moderate dysphagia to solids, managing liquids and soft diet. No aspiration on FEES.",
                "Severe dysphagia with documented aspiration. Two episodes of aspiration pneumonia in the past 6 weeks requiring hospitalisation. FEES shows penetration and aspiration with thin liquids.")],
            ["total_laryngectomy"], ["nonsurgical_lp"],
            ["S19R"],
            "Recurrent aspiration pneumonia = absolute CI for non-surgical LP (S19R-a)"),
        Perturbation("D1-P3","escalate","Add tracheostomy",
            [vc("pretreatment_tracheostomy","false","true"),
             vc("airway_obstruction","false","true")], None,
            [tr("No airway obstruction, no tracheostomy, no feeding tube.",
                "Severe airway obstruction requiring tracheostomy placement 2 weeks ago. No feeding tube.")],
            ["concurrent_crt","ict_rt","total_laryngectomy"], [],
            ["S19R","S115"],
            "Tracheostomy = relative CI non-surgical (S19R-b) + poor functional prognosis (S115). Non-surgical not excluded but balance shifts."),
        Perturbation("D1-NULL","null","Age 73, fit",
            [vc("age","under_70","70_plus")], None,
            [tr("Patient: 63-year-old male, ECOG 1.",
                "Patient: 73-year-old male, ECOG 1. Comprehensive Geriatric Assessment: fit. G8 14/17.")],
            ["concurrent_crt","ict_rt","total_laryngectomy"], [],
            ["S80"], "Age alone should not change recommendation"),
    ]
    templates.append(d1)

    # ─────────────────────────────────────────────────────────────
    # E1 — cT4a Unselected (Clear TL)
    # ─────────────────────────────────────────────────────────────
    e1 = BaselineTemplate(
        id="E1-BASE", family="cT4a_unselected", subtype="significant_extralaryngeal",
        variable_assignments={
            "t_stage":"cT4a","n_stage":"cN1","primary_site":"glottic",
            "tumor_volume":"high",
            "thyroid_cartilage_outer_cortex":"true","thyroid_cartilage_full_thickness":"true",
            "extralaryngeal_extension":"significant","subglottic_extension":"significant",
            "cricoid_cartilage_involvement":"extensive","magic_plane_crossing":"true",
            "posterior_laryngeal_involvement":"unilateral_arytenoid",
            "vocal_cord_mobility":"fixed","arytenoid_mobility":"unilateral_fixed",
            "baseline_laryngeal_function":"dysfunctional",
            "swallowing_status":"impaired_no_aspiration",
            "pretreatment_tracheostomy":"true","airway_obstruction":"true",
            "laryngeal_exposure":"insufficient",
            "age":"under_70","ecog_ps":"1","frailty_status":"fit",
            "renal_function":"normal","cardiac_function":"normal",
        },
        clinical_text="""Patient: 59-year-old male, ECOG 1. Active smoker (45 pack-years). Moderate alcohol intake. Otherwise healthy.

Tumor: cT4aN1 glottic SCC. Bulky transglottic tumor with left vocal cord fixation and left arytenoid fixation. Right cord mobile.

Imaging: CT shows full-thickness thyroid cartilage infiltration with significant extralaryngeal soft tissue extension invading the strap muscles bilaterally. Extensive subglottic extension (>15mm) with cricoid cartilage invasion. The tumor crosses the magic plane. Single ipsilateral level III lymph node (2.5cm).

Function: Severe dysphonia — largely non-communicative by voice. Emergency tracheostomy placed 1 week ago for critical airway obstruction. Moderate dysphagia to solids but tolerating liquids. Laryngeal function is considered globally dysfunctional.

Direct laryngoscopy: Laryngeal exposure is insufficient due to tumor bulk and anatomy.

Labs: CrCl 91, NYHA I, no neuropathy. Albumin 3.4, Hb 12.8.""",
        question="What is the recommended treatment for this patient?",
        expected_recommendations=["total_laryngectomy"],
        expected_excluded=["tlm","ophl_any","nonsurgical_lp"],
        expected_reasoning="Unambiguous TL: significant extralaryngeal (S38R), extensive subglottic (S38R), TLM CI (S45/S5R), magic plane (S15R), dysfunctional larynx (S39R), tracheostomy (S19R-b/S115).",
    )
    e1.perturbations = [
        Perturbation("E1-NULL","null","Add age 75, fit — TL still indicated",
            [vc("age","under_70","70_plus")], None,
            [tr("Patient: 59-year-old male, ECOG 1.",
                "Patient: 75-year-old male, ECOG 1. CGA: fit. G8 14/17.")],
            ["total_laryngectomy"], ["tlm","ophl_any","nonsurgical_lp"],
            ["S80"], "Age should not change clear TL indication"),
    ]
    templates.append(e1)

    # ─────────────────────────────────────────────────────────────
    # F1 — cT4a Selected (LP Possibly Viable)
    # ─────────────────────────────────────────────────────────────
    f1 = BaselineTemplate(
        id="F1-BASE", family="cT4a_selected", subtype="minimal_anterior_favorable",
        variable_assignments={
            "t_stage":"cT4a","n_stage":"cN0","primary_site":"glottic",
            "tumor_volume":"low",
            "thyroid_cartilage_outer_cortex":"true","thyroid_cartilage_full_thickness":"false",
            "extralaryngeal_extension":"minimal_anterior",
            "subglottic_extension":"none","cricoid_cartilage_involvement":"none",
            "magic_plane_crossing":"false",
            "posterior_laryngeal_involvement":"none",
            "vocal_cord_mobility":"fixed","arytenoid_mobility":"bilateral_mobile",
            "baseline_laryngeal_function":"functional","swallowing_status":"normal",
            "pretreatment_tracheostomy":"false","pretreatment_feeding_tube":"false",
            "airway_obstruction":"false","laryngeal_exposure":"adequate",
            "age":"under_70","ecog_ps":"0","frailty_status":"fit",
            "cardiopulmonary_function":"good","neurological_function":"good",
            "renal_function":"normal",
        },
        clinical_text="""Patient: 55-year-old male, ECOG 0. Former smoker (quit 5 years, 20 pack-years). No comorbidities. Highly motivated for voice preservation.

Tumor: cT4aN0 glottic SCC. Left vocal cord fixed, right mobile. Arytenoids bilaterally mobile.

Imaging: CT shows focal outer cortex thyroid cartilage invasion anteriorly with minimal soft tissue extension confined to the immediate anterior strap muscle plane. No deep muscle invasion. No involvement beyond the anterior compartment. No magic plane crossing. No subglottic extension. No cricoid involvement. No suspicious lymph nodes.

Function: Moderate dysphonia but communicative. No dysphagia, no aspiration. No airway obstruction. No tracheostomy. Baseline laryngeal function considered preserved/functional. Adequate laryngeal exposure.

Labs: CrCl 104, NYHA I, no neuropathy. Albumin 4.3, Hb 14.8.""",
        question="Is larynx preservation a viable option for this cT4a patient?",
        expected_recommendations=["ophl_any","concurrent_crt","total_laryngectomy"],
        expected_excluded=["tlm"],
        expected_reasoning="Favorable cT4a: meets S46 criteria (N0, minimal anterior extralaryngeal, fit). OPHL viable. Non-surgical LP has very few but real indications (S49R). TL preferred for unselected but LP achieves equal outcomes in selected patients (S40R). TLM absolute CI (S45).",
    )
    f1.perturbations = [
        Perturbation("F1-P1","escalate","Extralaryngeal → significant: LP collapses",
            [vc("extralaryngeal_extension","minimal_anterior","significant")], None,
            [tr("minimal soft tissue extension confined to the immediate anterior strap muscle plane. No deep muscle invasion. No involvement beyond the anterior compartment.",
                "significant extralaryngeal soft tissue extension invading the strap muscles bilaterally with deep muscle involvement.")],
            ["total_laryngectomy"], ["tlm","ophl_any"],
            ["S38R","S39R"],
            "Significant extralaryngeal = TL indication (S38R), CI for LP (S39R)"),
        Perturbation("F1-P2","flip","Magic plane crossing → OPHL-I/II blocked",
            [vc("magic_plane_crossing","false","true")], None,
            [tr("No magic plane crossing.",
                "The tumor crosses the magic plane.")],
            ["total_laryngectomy","concurrent_crt"], ["tlm","ophl_type_i","ophl_type_ii"],
            ["S15R"],
            "Magic plane = CI for OPHL-I and OPHL-II (S15R). Only OPHL-III or TL remain surgical options."),
        Perturbation("F1-P3","flip","Baseline laryngeal function → dysfunctional",
            [vc("baseline_laryngeal_function","functional","dysfunctional")], None,
            [tr("Baseline laryngeal function considered preserved/functional.",
                "Baseline laryngeal function is considered globally dysfunctional — severe dysphonia, swallowing difficulties emerging."),
             tr("Moderate dysphonia but communicative. No dysphagia, no aspiration.",
                "Severe dysphonia, largely non-communicative. Emerging dysphagia to solids.")],
            ["total_laryngectomy"], ["surgical_lp","nonsurgical_lp"],
            ["S39R","S42R"],
            "Dysfunctional baseline = absolute CI for BOTH surgical and non-surgical LP (S39R). Forces TL."),
        Perturbation("F1-P4","flip","N stage → cN2",
            [vc("n_stage","cN0","cN2")], None,
            [tr("No suspicious lymph nodes.",
                "Bilateral lymphadenopathy — 2.8cm left level III, 2.0cm right level II. No extranodal extension.")],
            ["concurrent_crt","total_laryngectomy"], ["ophl_any"],
            ["S24R","S46"],
            "N2 = relative CI for partial laryngectomy (S24R). S46 requires N0-1 for OPHL in cT4a."),
        Perturbation("F1-P5","flip","Site → hypopharyngeal",
            [vc("primary_site","glottic","hypopharyngeal")], None,
            [tr("cT4aN0 glottic SCC.","cT4aN0 SCC of the piriform sinus.")],
            ["total_laryngectomy","concurrent_crt"], ["tlm"],
            ["S12","S43"],
            "Hypopharynx at cT4a: worse outcomes non-surgical (S43), TLM not first-line (S12)"),
        Perturbation("F1-GREY1","grey_zone","Post-OPHL: adjuvant RT for pT4aN0 neg margins no PNI/LVI?",
            [], None,
            [tr("Labs: CrCl 104, NYHA I, no neuropathy. Albumin 4.3, Hb 14.8.",
                "Labs: CrCl 104, NYHA I, no neuropathy. Albumin 4.3, Hb 14.8.\n\n[FOLLOW-UP SCENARIO]: The patient underwent OPHL. Final pathology: pT4aN0, all margins negative (>5mm), no perineural invasion, no lymphovascular invasion. Should adjuvant radiotherapy be administered?")],
            [], [],
            ["S47R","S35R"],
            "GREY ZONE S47R (61.4%): experts split on omitting adjuvant RT with favorable pathology. Model should express uncertainty.",
            grey_zone_statement="S47R"),
        Perturbation("F1-NULL","null","Age 74, fit",
            [vc("age","under_70","70_plus")], None,
            [tr("Patient: 55-year-old male, ECOG 0.",
                "Patient: 74-year-old male, ECOG 0. CGA: fit. G8 15/17.")],
            ["ophl_any","concurrent_crt","total_laryngectomy"], [],
            ["S80"], "Age alone should not change LP eligibility in fit patient"),
    ]
    templates.append(f1)

    # ─────────────────────────────────────────────────────────────
    # G1 — Cisplatin Eligibility
    # ─────────────────────────────────────────────────────────────
    g1 = BaselineTemplate(
        id="G1-BASE", family="cisplatin_eligibility", subtype="fully_eligible",
        variable_assignments={
            "t_stage":"cT3","n_stage":"cN1","primary_site":"glottic",
            "ecog_ps":"0","ecog_ps_source":"null",
            "renal_function":"normal","cardiac_function":"normal",
            "liver_function":"normal","neuropathy":"none",
            "hearing_status":"grade_0","bone_marrow":"normal",
            "hiv_status":"negative","hepatitis":"negative",
            "platinum_hypersensitivity":"false","psychiatric_disorders":"false",
            "diabetes":"none","pregnancy_lactation":"false",
            "social_support":"adequate","cisplatin_relative_ci_count":"0",
            "comorbidity_burden":"none_mild",
        },
        clinical_text="""Patient: 60-year-old male, ECOG 0.

Tumor: cT3N1 glottic SCC. The multidisciplinary team has decided that concurrent chemoradiotherapy is the treatment strategy. The clinical question is the choice of concurrent systemic agent.

Renal: CrCl 95 mL/min, normal electrolytes.
Cardiac: NYHA class I, LVEF 65%, normal ECG, no cardiac history.
Hepatic: normal LFTs, no chronic liver disease (Child-Pugh A equivalent).
Neurological: no peripheral neuropathy, no hearing deficit on pure-tone audiometry.
Haematological: Hb 14.2, WBC 7.8, platelets 245, normal differential.
Infectious: HIV negative, HBV surface antigen negative, HCV antibody negative.
Other: no known platinum allergy, no psychiatric history, no diabetes, not pregnant. Good social and family support.
Nutritional status adequate (albumin 4.1, BMI 24).""",
        question="Is high-dose cisplatin (100 mg/m² q3w, up to 300 mg/m² cumulative) appropriate as the concurrent systemic agent?",
        expected_recommendations=["cisplatin_high_dose"],
        expected_excluded=["cetuximab_concurrent","carboplatin_5fu"],
        expected_reasoning="No absolute or relative CIs. High-dose cisplatin preferred (S52R, LoE I-II).",
    )
    # Build cisplatin perturbation series
    cis_abs = [
        ("G1-ABS01","renal_function","normal","under_50_ml_min","Renal: CrCl 95 mL/min, normal electrolytes.","Renal: CrCl 38 mL/min (stage 3b CKD), elevated creatinine 2.1 mg/dL.","S68R","CrCl <50 absolute CI"),
        ("G1-ABS02","cardiac_function","normal","nyha_III_IV","Cardiac: NYHA class I, LVEF 65%, normal ECG, no cardiac history.","Cardiac: NYHA class III congestive heart failure, LVEF 40%, on furosemide and carvedilol. History of myocardial infarction 2019.","S68R","NYHA III-IV / LVEF ≤50 absolute CI"),
        ("G1-ABS03","liver_function","normal","child_pugh_B_C","Hepatic: normal LFTs, no chronic liver disease (Child-Pugh A equivalent).","Hepatic: Child-Pugh B alcoholic cirrhosis (score 8). Albumin 2.8, bilirubin 2.5, mild ascites.","S68R","Child-Pugh B/C absolute CI"),
        ("G1-ABS04","neuropathy","none","grade_2_plus","Neurological: no peripheral neuropathy, no hearing deficit on pure-tone audiometry.","Neurological: grade 2 sensorimotor peripheral neuropathy — numbness and tingling in hands and feet affecting fine motor tasks. Normal hearing.","S68R","Grade ≥2 neuropathy absolute CI"),
        ("G1-ABS05","hiv_status","negative","cd4_under_200_or_aids","Infectious: HIV negative, HBV surface antigen negative, HCV antibody negative.","Infectious: HIV positive, CD4 count 180 cells/µL with recent Pneumocystis pneumonia (AIDS-defining). On HAART with poor virological control. HBV/HCV negative.","S68R","CD4 <200/AIDS absolute CI"),
        ("G1-ABS06","hepatitis","negative","uncontrolled","Infectious: HIV negative, HBV surface antigen negative, HCV antibody negative.","Infectious: HIV negative. Chronic hepatitis B with high viral load (HBV DNA >20,000 IU/mL), not currently on antiviral therapy. HBeAg positive. HCV negative.","S68R","Uncontrolled HBV absolute CI"),
        ("G1-ABS07","platinum_hypersensitivity","false","true","Other: no known platinum allergy, no psychiatric history, no diabetes, not pregnant.","Other: documented grade 3 anaphylactic reaction to cisplatin during prior treatment (urticaria, bronchospasm, hypotension requiring adrenaline). No psychiatric history, no diabetes, not pregnant.","S68R","Platinum hypersensitivity absolute CI"),
        ("G1-ABS08","psychiatric_disorders","false","true","Other: no known platinum allergy, no psychiatric history, no diabetes, not pregnant.","Other: no platinum allergy. Severe treatment-resistant schizophrenia with limited capacity for informed consent and poor treatment compliance — under psychiatric care with supervised medication. No diabetes, not pregnant.","S68R","Severe psychiatric disorder absolute CI"),
        ("G1-ABS09","diabetes","none","uncontrolled_insulin_dependent","Other: no known platinum allergy, no psychiatric history, no diabetes, not pregnant.","Other: no platinum allergy, no psychiatric history. Uncontrolled type 1 diabetes — HbA1c 12.3%, recurrent diabetic ketoacidosis (3 hospitalisations this year), insulin-dependent with poor glycaemic control despite endocrine follow-up. Not pregnant.","S68R","Uncontrolled insulin-dependent DM absolute CI"),
        ("G1-ABS10","bone_marrow","normal","grade_2_plus","Haematological: Hb 14.2, WBC 7.8, platelets 245, normal differential.","Haematological: Hb 8.9, WBC 2.1 (ANC 0.8), platelets 62 — grade 3 pancytopenia. Under investigation for myelodysplastic syndrome.","S68R","Grade >2 bone marrow absolute CI"),
    ]
    for pid, var, fr, to, old_txt, new_txt, edge, label in cis_abs:
        g1.perturbations.append(Perturbation(
            pid, "flip", label,
            [vc(var, fr, to)], None,
            [tr(old_txt, new_txt)],
            ["cetuximab_concurrent","carboplatin_5fu"], ["cisplatin_high_dose"],
            [edge, "S52R", "S72R"],
            f"Should identify {var} as absolute CI and recommend alternative agent"))

    # Relative CIs
    cis_rel = [
        ("G1-REL01","renal_function","normal","50_60_ml_min","Renal: CrCl 95 mL/min, normal electrolytes.","Renal: CrCl 55 mL/min (mild-moderate renal impairment), creatinine 1.4 mg/dL.","S69R","CrCl 50-60 = RELATIVE CI only, not absolute"),
        ("G1-REL02","hearing_status","grade_0","grade_1","Neurological: no peripheral neuropathy, no hearing deficit on pure-tone audiometry.","Neurological: no peripheral neuropathy. Grade 1 bilateral sensorineural hearing loss on audiometry — mild high-frequency deficit, functionally adequate.","S69R","Grade 1 hearing = RELATIVE CI only"),
        ("G1-REL03","social_support","adequate","impaired","Good social and family support.","Limited social support — lives alone, nearest family 200km away. No reliable transport to treatment centre.","S69R","Impaired social support = RELATIVE CI only"),
        ("G1-REL04","hiv_status","negative","cd4_200_350","Infectious: HIV negative, HBV surface antigen negative, HCV antibody negative.","Infectious: HIV positive, CD4 count 280 cells/µL, on HAART with suppressed viral load. No AIDS-defining illnesses. HBV/HCV negative.","S69R","CD4 200-350 = RELATIVE CI only, not absolute"),
    ]
    for pid, var, fr, to, old_txt, new_txt, edge, label in cis_rel:
        g1.perturbations.append(Perturbation(
            pid, "flip", label,
            [vc(var, fr, to)], None,
            [tr(old_txt, new_txt)],
            ["cisplatin_high_dose"], [],
            [edge],
            f"Should identify as RELATIVE CI — cisplatin still possible with monitoring. Must NOT declare absolute CI."))

    # ECOG source-conditional
    g1.perturbations.append(Perturbation(
        "G1-ECOG-TUM","flip","ECOG 2 tumor-driven → cisplatin STILL OK (SOURCE-CONDITIONAL)",
        [vc("ecog_ps","0","2_tumor_related"),vc("ecog_ps_source","null","tumor_driven")], None,
        [tr("Patient: 60-year-old male, ECOG 0.",
            "Patient: 60-year-old male, ECOG 2. His reduced functional status is entirely attributable to the bulky laryngeal tumor causing severe dysphagia and weight loss. Prior to symptom onset 4 months ago, he was fully active (ECOG 0). No pre-existing functional limitations.")],
        ["cisplatin_high_dose"], [],
        ["S77R","S52R"],
        "Blanket 'ECOG 2 = unfit for cisplatin' without evaluating cause. Must distinguish tumor-driven (OK) from comorbidity-driven (CI)."))
    g1.perturbations.append(Perturbation(
        "G1-ECOG-COM","flip","ECOG 2 comorbidity-driven → cisplatin ABSOLUTE CI (SOURCE-CONDITIONAL)",
        [vc("ecog_ps","0","2_comorbidity_related"),vc("ecog_ps_source","null","comorbidity_driven"),
         vc("cardiopulmonary_function","good","impaired")], None,
        [tr("Patient: 60-year-old male, ECOG 0.",
            "Patient: 60-year-old male, ECOG 2. He has longstanding COPD (GOLD III) and peripheral vascular disease limiting his mobility. He requires assistance with some daily activities. His functional limitations predate the cancer diagnosis by several years. The tumor itself causes only mild symptoms."),
         tr("Cardiac: NYHA class I, LVEF 65%, normal ECG, no cardiac history.",
            "Cardiac: NYHA class II, LVEF 55%. COPD GOLD III, FEV1 35% predicted.")],
        ["cetuximab_concurrent","carboplatin_5fu"], ["cisplatin_high_dose"],
        ["S68R","S77R","S52R","S72R"],
        "Same ECOG 2 as G1-ECOG-TUM but opposite recommendation — tests whether model distinguishes etiology"))

    # Grey zone: 2 relative CIs
    g1.perturbations.append(Perturbation(
        "G1-GREY-S70","grey_zone","2 relative CIs — grey zone (ACCUMULATION-NON-PATTERN)",
        [vc("renal_function","normal","50_60_ml_min"),
         vc("hearing_status","grade_0","grade_1"),
         vc("cisplatin_relative_ci_count","0","2_plus")], None,
        [tr("Renal: CrCl 95 mL/min, normal electrolytes.",
            "Renal: CrCl 55 mL/min (mild-moderate impairment), creatinine 1.4 mg/dL."),
         tr("Neurological: no peripheral neuropathy, no hearing deficit on pure-tone audiometry.",
            "Neurological: no peripheral neuropathy. Grade 1 bilateral sensorineural hearing loss on audiometry.")],
        ["cisplatin_high_dose"], [],  # cisplatin still possible — grey zone
        ["S70","S69R"],
        "Model incorrectly aggregates 2 relative CIs into absolute CI. S70 (75%) failed consensus — experts split on this. Appropriate response is uncertainty.",
        grey_zone_statement="S70"))

    # Comorbidity burden → CI non-surgical LP (S67)
    g1.perturbations.append(Perturbation(
        "G1-ABS11", "flip", "Severe comorbidity burden → unfit for chemo (S67)",
        [vc("comorbidity_burden","none_mild","severe")], None,
        [tr("Nutritional status adequate (albumin 4.1, BMI 24).",
            "Severe comorbidity burden (ACE-27 score 3): COPD GOLD III, chronic kidney disease stage 3, compensated heart failure. Nutritional status marginal (albumin 3.2, BMI 20).")],
        ["rt_accelerated"], ["cisplatin_high_dose","cetuximab_concurrent","carboplatin_5fu","concurrent_crt","ict_rt","nonsurgical_lp"],
        ["S67","S73R"],
        "Severe comorbidity burden = unfit for any chemo-based LP (S67). If TL is declined, accelerated or hyperfractionated RT alone is the fallback (S73R).",
        notes="TARGETED QUESTION VARIANT: 'If this patient declines total laryngectomy and is unfit for any systemic therapy, what larynx-preservation option, if any, remains appropriate?'"))

    # Null: controlled diabetes
    g1.perturbations.append(Perturbation(
        "G1-NULL","null","Controlled T2DM — NOT a CI",
        [vc("diabetes","none","controlled")], None,
        [tr("Other: no known platinum allergy, no psychiatric history, no diabetes, not pregnant.",
            "Other: no known platinum allergy, no psychiatric history. Well-controlled type 2 diabetes on metformin (HbA1c 6.8%, no end-organ damage, no neuropathy). Not pregnant.")],
        ["cisplatin_high_dose"], [],
        [], "Over-generalises 'diabetes = problem for chemo'"))
    templates.append(g1)

    # ─────────────────────────────────────────────────────────────
    # H1 — Post-ICT Complete Response (GRADED-RESPONSE-CONDITIONAL)
    # ─────────────────────────────────────────────────────────────
    h1 = BaselineTemplate(
        id="H1-BASE", family="post_ict_response", subtype="complete_response",
        variable_assignments={
            "t_stage":"cT3","n_stage":"cN1","primary_site":"glottic",
            "ict_response":"complete_response",
            "vc_remobilization_post_ict":"true",
            "vocal_cord_mobility":"normal",
            "baseline_laryngeal_function":"functional",
            "swallowing_status":"normal",
            "ecog_ps":"0","renal_function":"normal",
        },
        clinical_text="""Patient: 57-year-old male, ECOG 0. Initially presented with cT3N1 glottic SCC with fixed left vocal cord and a 2.5cm level III node.

The patient received 3 cycles of induction chemotherapy (TPF protocol). He tolerated treatment well with manageable toxicity.

Post-ICT reassessment (8 weeks after cycle 3):
- Imaging: CT and MRI show complete radiological response at the primary site. The level III node has resolved completely. No residual tumor visible on imaging.
- Direct laryngoscopy: Complete endoscopic response. The previously fixed left vocal cord has regained normal mobility. Both arytenoids mobile. Mucosa appears normal.
- PET-CT: No FDG-avid disease at the primary site or neck.

Current function: Voice significantly improved. No dysphagia. No airway issues.""",
        question="What is the appropriate definitive treatment following this complete response to induction chemotherapy?",
        expected_recommendations=["rt_alone"],
        expected_excluded=["concurrent_crt","total_laryngectomy"],
        expected_reasoning="CR + VC remobilization after ICT → RT alone (S31R, S120R). NOT CRT. VC remobilization predicts functional LP (S119R). ICT CR is favorable factor (S116).",
    )
    h1.perturbations = [
        Perturbation("H1-P1","flip","PR ≥50% — shifts from RT alone to CRT",
            [vc("ict_response","complete_response","partial_response_50plus"),
             vc("vc_remobilization_post_ict","true","false"),
             vc("vocal_cord_mobility","normal","partially_impaired")], None,
            [tr("complete radiological response at the primary site. The level III node has resolved completely. No residual tumor visible on imaging.",
                "partial response with >50% tumor volume reduction at the primary site. The level III node has decreased from 2.5cm to 1.0cm. Residual tumor visible but significantly reduced."),
             tr("Complete endoscopic response. The previously fixed left vocal cord has regained normal mobility. Both arytenoids mobile. Mucosa appears normal.",
                "Significant endoscopic tumor reduction but residual disease visible. The left vocal cord remains partially impaired (improved from fixed but not fully mobile). Arytenoids mobile."),
             tr("PET-CT: No FDG-avid disease at the primary site or neck.",
                "PET-CT: Reduced but persistent FDG uptake at the primary site (SUVmax 4.2, down from 12.8). Neck nodes show minimal residual uptake."),
             tr("Voice significantly improved. No dysphagia. No airway issues.",
                "Voice improved but still moderately impaired. No dysphagia. No airway issues.")],
            ["concurrent_crt"], ["rt_alone","total_laryngectomy"],
            ["S55R","S116","S119R","S31R","S120R","S30"],
            "Should shift from RT alone to CRT. CR=RT alone (S120R) but PR≥50% requires concurrent chemo. May incorrectly keep RT alone."),
        Perturbation("H1-P2","grey_zone","PR <50% — GREY ZONE (SA6)",
            [vc("ict_response","complete_response","partial_response_under50"),
             vc("vc_remobilization_post_ict","true","false"),
             vc("vocal_cord_mobility","normal","fixed")], None,
            [tr("complete radiological response at the primary site. The level III node has resolved completely. No residual tumor visible on imaging.",
                "partial response with approximately 30% tumor volume reduction. Residual bulky disease at the primary site. The level III node decreased from 2.5cm to 1.8cm."),
             tr("Complete endoscopic response. The previously fixed left vocal cord has regained normal mobility. Both arytenoids mobile. Mucosa appears normal.",
                "Endoscopic improvement but substantial residual tumor. Left vocal cord remains fixed. Arytenoids mobile."),
             tr("PET-CT: No FDG-avid disease at the primary site or neck.",
                "PET-CT: Persistent significant FDG uptake (SUVmax 9.1, down from 12.8)."),
             tr("Voice significantly improved. No dysphagia. No airway issues.",
                "Voice unchanged — severely impaired. No dysphagia. No airway issues.")],
            ["total_laryngectomy","concurrent_crt"], [],
            ["SA6","S121R"],
            "GREY ZONE SA6 (67.2%): PR<50% management unresolved. Experts split between CRT and TL. Model should express uncertainty.",
            grey_zone_statement="SA6"),
        Perturbation("H1-P3","flip","Stable disease → TL preferred",
            [vc("ict_response","complete_response","stable_disease"),
             vc("vc_remobilization_post_ict","true","false"),
             vc("vocal_cord_mobility","normal","fixed")], None,
            [tr("complete radiological response at the primary site. The level III node has resolved completely. No residual tumor visible on imaging.",
                "stable disease — no significant change in tumor dimensions (<10% reduction). The level III node is unchanged at 2.5cm."),
             tr("Complete endoscopic response. The previously fixed left vocal cord has regained normal mobility. Both arytenoids mobile. Mucosa appears normal.",
                "No significant endoscopic change. Left vocal cord remains fixed. Tumor bulk unchanged."),
             tr("PET-CT: No FDG-avid disease at the primary site or neck.",
                "PET-CT: Unchanged metabolic activity (SUVmax 11.9 vs 12.8 pre-ICT)."),
             tr("Voice significantly improved. No dysphagia. No airway issues.",
                "Voice unchanged — severely impaired. No dysphagia. No airway issues.")],
            ["total_laryngectomy"], ["rt_alone"],
            ["S121R"],
            "Stable disease → TL is standard (S121R). CRT only if patient refuses TL. Model may incorrectly persist with non-surgical LP."),
        Perturbation("H1-P4","flip","Progression → TL clearly indicated",
            [vc("ict_response","complete_response","progression"),
             vc("vc_remobilization_post_ict","true","false"),
             vc("vocal_cord_mobility","normal","fixed")], None,
            [tr("complete radiological response at the primary site. The level III node has resolved completely. No residual tumor visible on imaging.",
                "disease progression — tumor has increased in size with new areas of cartilage involvement. The level III node has grown to 3.2cm with a new level IV node (1.5cm)."),
             tr("Complete endoscopic response. The previously fixed left vocal cord has regained normal mobility. Both arytenoids mobile. Mucosa appears normal.",
                "Tumor progression on endoscopy with increased bulk. Left vocal cord remains fixed, now with reduced arytenoid mobility on the left."),
             tr("PET-CT: No FDG-avid disease at the primary site or neck.",
                "PET-CT: Increased metabolic activity with new areas of uptake."),
             tr("Voice significantly improved. No dysphagia. No airway issues.",
                "Voice worsened. Emerging dysphagia to solids.")],
            ["total_laryngectomy"], ["rt_alone","nonsurgical_lp"],
            ["S129"],
            "Progression or no response after ICT should shift decisively toward total laryngectomy over larynx-preservation strategies (S129)."),
    ]
    templates.append(h1)

    # ─────────────────────────────────────────────────────────────
    # H2 — Post-ICT cT4a Partial Response
    # ─────────────────────────────────────────────────────────────
    h2 = BaselineTemplate(
        id="H2-BASE", family="post_ict_response", subtype="cT4a_partial_response",
        variable_assignments={
            "t_stage":"cT4a","n_stage":"cN2","primary_site":"glottic",
            "tumor_volume":"high",
            "thyroid_cartilage_outer_cortex":"true",
            "extralaryngeal_extension":"minimal_anterior",
            "ict_response":"partial_response_50plus",
            "vc_remobilization_post_ict":"false",
            "vocal_cord_mobility":"fixed",
            "baseline_laryngeal_function":"functional",
            "swallowing_status":"normal",
            "pretreatment_tracheostomy":"false",
            "ecog_ps":"0","renal_function":"normal",
        },
        clinical_text="""Patient: 52-year-old male, ECOG 0. Initially presented with cT4aN2b glottic SCC — bulky tumor with outer cortex TC invasion and moderate anterior extralaryngeal extension. Bilateral neck disease.

Received 3 cycles of TPF induction chemotherapy.

Post-ICT reassessment:
- Imaging: >50% reduction in tumor volume. Previously significant extralaryngeal extension now appears minimal. Thyroid cartilage still shows residual abnormality at outer cortex. Neck nodes reduced by >60%.
- Direct laryngoscopy: Significant tumor shrinkage endoscopically. Left vocal cord still fixed (no remobilization). Arytenoids mobile bilaterally. Residual tumor visible but much reduced.
- Laryngeal function: voice still severely impaired, but swallowing adequate, no aspiration, no tracheostomy.""",
        question="Is this patient eligible for non-surgical larynx preservation following this partial response to ICT?",
        expected_recommendations=["concurrent_crt","total_laryngectomy"],
        expected_excluded=["rt_alone"],
        expected_reasoning="cT4a with PR≥50% → eligible for non-surgical LP (S55R). But cord not remobilized (S119R negative), outer cortex residual (S41R). CRT is the non-surgical option (not RT alone — needs CR for that per S120R). TL valid alternative.",
    )
    h2.perturbations = [
        Perturbation("H2-P1","flip","Response → stable disease",
            [vc("ict_response","partial_response_50plus","stable_disease")], None,
            [tr(">50% reduction in tumor volume. Previously significant extralaryngeal extension now appears minimal.",
                "no significant change in tumor dimensions (<10% reduction). Extralaryngeal extension unchanged."),
             tr("Significant tumor shrinkage endoscopically.","No significant endoscopic change."),
             tr("Neck nodes reduced by >60%.","Neck nodes essentially unchanged.")],
            ["total_laryngectomy"], ["rt_alone","nonsurgical_lp"],
            ["S121R"],
            "Stable disease at cT4a → TL clearly indicated. Non-surgical LP no longer justified (S121R: CRT only if refuses TL)."),
        Perturbation("H2-P2","flip","Baseline laryngeal function → dysfunctional",
            [vc("baseline_laryngeal_function","functional","dysfunctional")], None,
            [tr("swallowing adequate, no aspiration, no tracheostomy.",
                "emerging aspiration with liquids, tracheostomy being considered. Laryngeal function is now globally dysfunctional.")],
            ["total_laryngectomy"], ["surgical_lp","nonsurgical_lp"],
            ["S39R"],
            "Dysfunctional larynx = absolute CI for both surgical and non-surgical LP (S39R)"),
        Perturbation("H2-P3","flip","Site → hypopharyngeal",
            [vc("primary_site","glottic","hypopharyngeal")], None,
            [tr("cT4aN2b glottic SCC","cT4aN2b SCC of the piriform sinus")],
            ["total_laryngectomy","concurrent_crt"], [],
            ["S43"],
            "Hypopharynx at cT4a: worse outcomes tip further toward TL (S43)"),
        Perturbation("H2-NULL","null","VC remobilization (improves prognosis but doesn't change eligibility)",
            [vc("vc_remobilization_post_ict","false","true"),
             vc("vocal_cord_mobility","fixed","partially_impaired")], None,
            [tr("Left vocal cord still fixed (no remobilization).",
                "Left vocal cord has partially remobilized (previously fixed, now partially impaired mobility).")],
            ["concurrent_crt","total_laryngectomy"], [],
            ["S119R"],
            "VC remobilization improves functional LP prediction (S119R) but fundamental eligibility unchanged"),
    ]
    templates.append(h2)

    # ─────────────────────────────────────────────────────────────
    # I1 — Elderly Fit (FRAILTY-CONDITIONAL)
    # ─────────────────────────────────────────────────────────────
    i1 = BaselineTemplate(
        id="I1-BASE", family="elderly_frail", subtype="elderly_fit",
        variable_assignments={
            "t_stage":"cT3","n_stage":"cN0","primary_site":"glottic",
            "vocal_cord_mobility":"fixed","arytenoid_mobility":"bilateral_mobile",
            "baseline_laryngeal_function":"functional","laryngeal_exposure":"adequate",
            "thyroid_cartilage_inner_cortex":"none","subglottic_extension":"none",
            "pretreatment_tracheostomy":"false",
            "age":"70_plus","ecog_ps":"0","frailty_status":"fit",
            "g8_score":"above_14",
            "cardiopulmonary_function":"good","neurological_function":"good",
            "nutritional_status":"adequate","comorbidity_burden":"none_mild",
            "renal_function":"normal","cardiac_function":"normal","neuropathy":"none",
            "hearing_status":"grade_1",
        },
        clinical_text="""Patient: 76-year-old male, ECOG 0. Retired engineer. Non-smoker for 15 years (former 25 pack-years). Lives independently with wife. Walks 5km daily, plays golf twice weekly.

Comorbidities: controlled hypertension on single agent, mild hyperlipidemia on statin. No cardiac history, no diabetes, no neurological disease.

Geriatric assessment: Comprehensive Geriatric Assessment (CGA) classifies patient as FIT. G8 screening score 15/17. No frailty markers. ADL and IADL fully independent. MMSE 29/30. Timed Up-and-Go test 9 seconds.

Tumor: cT3N0 glottic SCC. Left vocal cord fixed, right mobile. Arytenoids bilaterally mobile. No cartilage involvement, no subglottic extension, no paraglottic invasion posteriorly. Adequate laryngeal exposure.

Labs: CrCl 72 mL/min (age-appropriate), NYHA I, no neuropathy, mild presbycusis (grade 1 on audiometry). Albumin 3.8, Hb 13.1.""",
        question="Does this patient's age affect his eligibility for larynx preservation treatments?",
        expected_recommendations=["tlm","ophl_type_ii","concurrent_crt","ict_rt"],
        expected_excluded=[],
        expected_reasoning="Age alone NOT CI for TLM (S6R) or any LP (S80) in fit patients. CGA fit → standard treatment (S84). CrCl 72 adequate for cisplatin (>60). Grade 1 hearing = relative CI cisplatin (S69R) but not absolute.",
    )
    i1.perturbations = [
        Perturbation("I1-P1","flip","Frail → OPHL relative CI, adapted approach",
            [vc("frailty_status","fit","frail"),vc("g8_score","above_14","below_14")], None,
            [tr("Comprehensive Geriatric Assessment (CGA) classifies patient as FIT. G8 screening score 15/17. No frailty markers. ADL and IADL fully independent. MMSE 29/30. Timed Up-and-Go test 9 seconds.",
                "Comprehensive Geriatric Assessment (CGA) classifies patient as FRAIL. G8 screening score 10/17. Reduced grip strength, slow gait speed (TUG 18 seconds). Dependent in 2 IADLs (shopping, transport). MMSE 26/30. Weight loss 4kg over 6 months.")],
            ["concurrent_crt","rt_alone","total_laryngectomy"], [],
            ["S88","S84","S111R"],
            "Frail → OPHL becomes relative CI (S88). Must adapt treatment per CGA (S84). May still be CRT candidate but with adapted approach."),
        Perturbation("I1-P2","escalate","Frail + cT4a + precludes OPHL/chemo → TL preferred",
            [vc("frailty_status","fit","frail"),vc("g8_score","above_14","below_14"),
             vc("t_stage","cT3","cT4a"),vc("thyroid_cartilage_outer_cortex","false","true"),
             vc("extralaryngeal_extension","none","minimal_anterior"),
             vc("cardiopulmonary_function","good","impaired")],
            "cT3 → cT4a",
            [tr("Tumor: cT3N0 glottic SCC.",
                "Tumor: cT4aN0 glottic SCC with focal outer cortex thyroid cartilage invasion and minimal anterior extralaryngeal extension."),
             tr("No cartilage involvement, no subglottic extension, no paraglottic invasion posteriorly.",
                "No subglottic extension, no paraglottic invasion posteriorly."),
             tr("Comprehensive Geriatric Assessment (CGA) classifies patient as FIT. G8 screening score 15/17. No frailty markers. ADL and IADL fully independent. MMSE 29/30. Timed Up-and-Go test 9 seconds.",
                "Comprehensive Geriatric Assessment (CGA) classifies patient as FRAIL. G8 screening score 9/17. Multiple frailty markers. COPD GOLD II limiting exercise tolerance."),
             tr("Comorbidities: controlled hypertension on single agent, mild hyperlipidemia on statin. No cardiac history, no diabetes, no neurological disease.",
                "Comorbidities: COPD GOLD II, controlled hypertension, mild hyperlipidemia. Cardiopulmonary function impaired.")],
            ["total_laryngectomy"], [],
            ["S89","S88","S13"],
            "Frail + advanced + comorbidities precluding OPHL/systemic → TL preferred (S89)"),
        Perturbation("I1-P3","flip","Add neurodegenerative disease",
            [vc("neurological_function","good","impaired_grade1")], None,
            [tr("No cardiac history, no diabetes, no neurological disease.",
                "No cardiac history, no diabetes. Early Parkinson's disease — mild resting tremor, on levodopa, functionally independent but with emerging mild swallowing hesitancy.")],
            ["concurrent_crt","ict_rt","ophl_type_ii"], ["tlm"],
            ["S75R","S13"],
            "Neurodegenerative disease = relative CI for surgical LP (S75R). Impaired neuro fn = CI OPHL (S13). Shifts toward non-surgical."),
        Perturbation("I1-NULL1","null","Age 82 but STILL fit → should NOT change",
            [vc("age","70_plus","70_plus")], None,
            [tr("Patient: 76-year-old male, ECOG 0.",
                "Patient: 82-year-old male, ECOG 0.")],
            ["tlm","ophl_type_ii","concurrent_crt","ict_rt"], [],
            ["S6R","S80"],
            "Even at 82, if CGA is fit, age alone is not CI. Tests extreme age sensitivity."),
        Perturbation("I1-NULL2","null","CrCl 55 — only affects chemo choice",
            [vc("renal_function","normal","50_60_ml_min")], None,
            [tr("CrCl 72 mL/min (age-appropriate)",
                "CrCl 55 mL/min (moderate renal impairment)")],
            ["tlm","ophl_type_ii","concurrent_crt","ict_rt"], [],
            ["S69R"],
            "CrCl 55 = relative CI for cisplatin only (S69R), does NOT affect LP eligibility itself"),
    ]
    templates.append(i1)

    # ─────────────────────────────────────────────────────────────
    # J1 — Airway Obstruction (ISOLATION-CONDITIONAL)
    # ─────────────────────────────────────────────────────────────
    j1 = BaselineTemplate(
        id="J1-BASE", family="pretreatment_function", subtype="airway_obstruction_isolated",
        variable_assignments={
            "t_stage":"cT3","n_stage":"cN0","primary_site":"glottic",
            "vocal_cord_mobility":"fixed","arytenoid_mobility":"bilateral_mobile",
            "baseline_laryngeal_function":"functional","swallowing_status":"normal",
            "airway_obstruction":"true",
            "pretreatment_tracheostomy":"false","pretreatment_feeding_tube":"false",
            "subglottic_extension":"none","cricoid_cartilage_involvement":"none",
            "thyroid_cartilage_inner_cortex":"none","extralaryngeal_extension":"none",
            "age":"under_70","ecog_ps":"0","renal_function":"normal",
            "dna_repair_disorder":"false","previous_neck_rt":"false",
        },
        clinical_text="""Patient: 55-year-old male, ECOG 0, no comorbidities.

Tumor: cT3N0 glottic SCC. Left vocal cord fixed, right mobile. Arytenoids bilaterally mobile.

The patient presents with moderate airway obstruction — audible stridor on exertion, mild stridor at rest when supine. He sleeps propped up on two pillows but manages his daily activities. He has not required tracheostomy and the clinical team judges that he can safely begin treatment without emergent airway intervention.

No subglottic extension, no cartilage involvement, no extralaryngeal extension. No paraglottic space invasion posteriorly.

Function: Voice severely impaired. Swallowing normal — full oral diet without difficulty. No aspiration on clinical assessment. No feeding tube. Baseline laryngeal function, apart from voice, is considered preserved.

Labs: CrCl 95, NYHA I, no neuropathy. Albumin 4.0, Hb 14.0.""",
        question="Is non-surgical larynx preservation appropriate despite the airway obstruction?",
        expected_recommendations=["concurrent_crt","ict_rt","nonsurgical_lp"],
        expected_excluded=["total_laryngectomy"],
        expected_reasoning="Airway obstruction alone is explicitly NOT CI for non-surgical LP (S21). No tracheostomy (S19R clear). Swallowing normal (S19R clear). CRT (S28) and ICT (S30) both viable.",
    )
    j1.perturbations = [
        Perturbation("J1-P1","escalate","Tracheostomy required → relative CI",
            [vc("pretreatment_tracheostomy","false","true")], None,
            [tr("He has not required tracheostomy and the clinical team judges that he can safely begin treatment without emergent airway intervention.",
                "He required emergency tracheostomy placement 2 weeks ago for worsening stridor at rest. The tracheostomy is in situ and functioning well.")],
            ["concurrent_crt","ict_rt","total_laryngectomy"], [],
            ["S19R","S115"],
            "Tracheostomy = relative CI (S19R-b) + poor functional prognosis (S115). Non-surgical not excluded but balance shifts."),
        Perturbation("J1-P2","escalate","Aspiration pneumonia → absolute CI non-surgical",
            [vc("swallowing_status","normal","recurrent_pneumonia"),
             vc("baseline_laryngeal_function","functional","dysfunctional")], None,
            [tr("Swallowing normal — full oral diet without difficulty. No aspiration on clinical assessment. No feeding tube. Baseline laryngeal function, apart from voice, is considered preserved.",
                "Severe dysphagia with documented aspiration. Two episodes of aspiration pneumonia in the past month requiring hospital admission. FEES demonstrates penetration and aspiration with thin liquids and purees. PEG feeding tube placed. Baseline laryngeal function is globally dysfunctional.")],
            ["total_laryngectomy"], ["nonsurgical_lp"],
            ["S19R"],
            "Aspiration pneumonia = absolute CI non-surgical LP (S19R-a). The blocker is aspiration, not the airway obstruction."),
        Perturbation("J1-P3","flip","Add feeding tube",
            [vc("pretreatment_feeding_tube","false","true")], None,
            [tr("No feeding tube. Baseline laryngeal function, apart from voice, is considered preserved.",
                "PEG feeding tube placed 3 weeks ago for nutritional support due to severe odynophagia. Baseline laryngeal function, apart from voice and swallowing, is considered partially preserved.")],
            ["concurrent_crt","ict_rt","total_laryngectomy"], [],
            ["S19R"],
            "Feeding tube = relative CI (S19R-c). Non-surgical not excluded but adds to risk profile."),
        Perturbation("J1-P4","escalate","Add significant subglottic + extensive cricoid",
            [vc("subglottic_extension","none","significant"),
             vc("cricoid_cartilage_involvement","none","extensive")], None,
            [tr("No subglottic extension, no cartilage involvement, no extralaryngeal extension.",
                "Significant subglottic extension (>15mm) with extensive cricoid cartilage involvement on CT. No thyroid cartilage involvement. No extralaryngeal extension.")],
            ["total_laryngectomy","concurrent_crt"], [],
            ["S20R"],
            "Significant subglottic + extensive cricoid = relative CI non-surgical (S20R). Combined with airway obstruction, balance shifts significantly."),
        Perturbation("J1-P5","multi","Tracheostomy + feeding tube + aspiration → convergent CIs",
            [vc("pretreatment_tracheostomy","false","true"),
             vc("pretreatment_feeding_tube","false","true"),
             vc("swallowing_status","normal","penetration_aspiration"),
             vc("baseline_laryngeal_function","functional","dysfunctional"),
             vc("ecog_ps","0","1")], None,
            [tr("He has not required tracheostomy and the clinical team judges that he can safely begin treatment without emergent airway intervention.",
                "He required emergency tracheostomy 2 weeks ago."),
             tr("Patient: 55-year-old male, ECOG 0, no comorbidities.",
                "Patient: 55-year-old male, ECOG 1 (due to functional limitations from airway and swallowing compromise), no other comorbidities."),
             tr("Swallowing normal — full oral diet without difficulty. No aspiration on clinical assessment. No feeding tube. Baseline laryngeal function, apart from voice, is considered preserved.",
                "Severe dysphagia with aspiration on FEES. PEG feeding tube in situ. Baseline laryngeal function is globally dysfunctional — severe dysphonia, aspiration, tracheostomy-dependent.")],
            ["total_laryngectomy"], ["nonsurgical_lp","surgical_lp"],
            ["S19R","S39R","S115"],
            "Convergent CIs: aspiration (absolute, S19R-a), tracheostomy (relative, S19R-b), feeding tube (relative, S19R-c), dysfunctional larynx (absolute for LP, S39R). Clear TL."),
        Perturbation("J1-P6","flip","DNA repair disorder → absolute CI non-surgical LP (S74R)",
            [vc("dna_repair_disorder","false","true")], None,
            [tr("no comorbidities.",
                "no comorbidities apart from xeroderma pigmentosum (DNA repair disorder) diagnosed in childhood, with multiple prior skin cancers managed surgically.")],
            ["total_laryngectomy","surgical_lp"], ["nonsurgical_lp"],
            ["S74R"],
            "DNA repair disorder = absolute CI for non-surgical LP (S74R) due to radiation hypersensitivity."),
        Perturbation("J1-P7","flip","Previous neck RT → relative CI non-surgical LP (S74R)",
            [vc("previous_neck_rt","false","true")], None,
            [tr("no comorbidities.",
                "history of previous radiotherapy to the neck 12 years ago for a different head and neck primary (cT1N0 oropharyngeal SCC, treated with RT alone, disease-free since). No other comorbidities.")],
            ["total_laryngectomy","surgical_lp"], [],
            ["S74R"],
            "Previous neck RT = relative CI for re-irradiation (S74R). Non-surgical LP not excluded but significantly complicated."),
        Perturbation("J1-NULL","null","Add age 72, fit — should NOT change",
            [vc("age","under_70","70_plus")], None,
            [tr("Patient: 55-year-old male, ECOG 0, no comorbidities.",
                "Patient: 72-year-old male, ECOG 0, no comorbidities. CGA: fit. G8 15/17.")],
            ["concurrent_crt","ict_rt","nonsurgical_lp"], [],
            ["S21","S80"],
            "Airway obstruction NOT CI (S21) + age NOT CI when fit (S80). Both null signals should hold."),
    ]
    templates.append(j1)

    return templates


# ═══════════════════════════════════════════════════════════════════
# GENERATOR ENGINE
# ═══════════════════════════════════════════════════════════════════

def apply_perturbation(baseline: BaselineTemplate, pert: Perturbation) -> dict:
    """Apply a perturbation to a baseline, returning the perturbed vignette dict."""
    # Apply variable changes
    new_vars = dict(baseline.variable_assignments)
    for vchange in pert.variables_changed:
        if isinstance(vchange, VariableChange):
            new_vars[vchange.variable] = vchange.to_value
        else:
            new_vars[vchange["variable"]] = vchange["to_value"]

    # Apply text replacements
    new_text = baseline.clinical_text
    for repl in pert.text_replacements:
        if isinstance(repl, TextReplacement):
            old, new = repl.old_text, repl.new_text
        else:
            old, new = repl["old_text"], repl["new_text"]
        if old not in new_text:
            print(f"  WARNING [{pert.id}]: text replacement target not found: '{old[:60]}...'")
        new_text = new_text.replace(old, new)

    # Check consistency
    warnings = check_staging_consistency(new_vars)

    # Use targeted question if specified in notes
    question = baseline.question
    if "TARGETED QUESTION VARIANT:" in (pert.notes or ""):
        targeted = pert.notes.split("TARGETED QUESTION VARIANT:")[1].strip().strip("'\"")
        question = targeted

    return {
        "id": pert.id,
        "baseline_id": baseline.id,
        "family": pert.family_override or baseline.family,
        "type": pert.pert_type,
        "label": pert.label,
        "variables_changed": [
            {"variable": v.variable, "from": v.from_value, "to": v.to_value}
            if isinstance(v, VariableChange) else v
            for v in pert.variables_changed
        ],
        "staging_impact": pert.staging_impact,
        "variable_assignments": new_vars,
        "clinical_text": new_text,
        "question": question,
        "expected_recommendations": pert.expected_recommendations,
        "expected_excluded": pert.expected_excluded,
        "edge_justification": pert.edge_justification,
        "predicted_failure_mode": pert.predicted_failure_mode,
        "grey_zone_statement": pert.grey_zone_statement,
        "notes": pert.notes,
        "consistency_warnings": warnings,
    }


def _normalise_null_controls(battery: dict) -> None:
    """Null items should preserve baseline expectations exactly."""
    baseline_map = {row["id"]: row for row in battery["baselines"]}
    for pert in battery["perturbations"]:
        if pert.get("type") != "null":
            continue
        baseline = baseline_map.get(pert["baseline_id"])
        if not baseline:
            continue
        pert["expected_recommendations"] = list(baseline.get("expected_recommendations", []))
        pert["expected_excluded"] = list(baseline.get("expected_excluded", []))


def _normalise_expected_labels(battery: dict) -> None:
    for row in battery["baselines"] + battery["perturbations"]:
        rec, exc = normalise_expected_label_lists(
            row.get("expected_recommendations", []),
            row.get("expected_excluded", []),
        )
        row["expected_recommendations"] = rec
        row["expected_excluded"] = exc


def generate_battery(templates: list) -> dict:
    """Generate the complete test battery from templates."""
    battery = {
        "meta": {
            "source": "Ferrari et al., Lancet Oncol 2025; 26: e264-81",
            "title": "KG₁ Clinical Vignette Battery for LLM Causal Reasoning Evaluation",
            "description": "Semi-synthetic clinical vignettes with perturbations testing LLM treatment recommendations against expert consensus ground truth.",
            "total_baselines": 0,
            "total_perturbations": 0,
            "total_items": 0,
        },
        "baselines": [],
        "perturbations": [],
    }

    for tmpl in templates:
        baseline_dict = {
            "id": tmpl.id,
            "family": tmpl.family,
            "subtype": tmpl.subtype,
            "variable_assignments": tmpl.variable_assignments,
            "clinical_text": tmpl.clinical_text,
            "question": tmpl.question,
            "expected_recommendations": tmpl.expected_recommendations,
            "expected_excluded": tmpl.expected_excluded,
            "expected_reasoning": tmpl.expected_reasoning,
            "num_perturbations": len(tmpl.perturbations),
        }
        warnings = check_staging_consistency(tmpl.variable_assignments)
        if warnings:
            baseline_dict["consistency_warnings"] = warnings
        battery["baselines"].append(baseline_dict)

        for pert in tmpl.perturbations:
            pdict = apply_perturbation(tmpl, pert)
            battery["perturbations"].append(pdict)

    _normalise_null_controls(battery)
    _normalise_expected_labels(battery)

    battery["meta"]["total_baselines"] = len(battery["baselines"])
    battery["meta"]["total_perturbations"] = len(battery["perturbations"])
    battery["meta"]["total_items"] = battery["meta"]["total_baselines"] + battery["meta"]["total_perturbations"]

    # Compute coverage stats
    all_edges = set()
    for p in battery["perturbations"]:
        all_edges.update(p.get("edge_justification", []))
    battery["meta"]["edges_tested"] = sorted(all_edges)
    battery["meta"]["unique_edges_tested"] = len(all_edges)

    type_counts = {}
    for p in battery["perturbations"]:
        t = p["type"]
        type_counts[t] = type_counts.get(t, 0) + 1
    battery["meta"]["perturbation_types"] = type_counts

    return battery


# ═══════════════════════════════════════════════════════════════════
# MARKDOWN OUTPUT
# ═══════════════════════════════════════════════════════════════════

def battery_to_markdown(battery: dict) -> str:
    """Render the test battery as a human-readable Markdown document."""
    lines = []
    m = battery["meta"]
    lines.append(f"# {m['title']}")
    lines.append(f"\n> Source: {m['source']}")
    lines.append(f"> Generated test battery: **{m['total_baselines']}** baselines, **{m['total_perturbations']}** perturbations, **{m['total_items']}** total items")
    lines.append(f"> Unique KG₁ edges tested: **{m['unique_edges_tested']}**")
    lines.append(f"> Perturbation types: {m['perturbation_types']}")
    lines.append("")

    # Group perturbations by baseline
    pert_by_base = {}
    for p in battery["perturbations"]:
        bid = p["baseline_id"]
        pert_by_base.setdefault(bid, []).append(p)

    for base in battery["baselines"]:
        bid = base["id"]
        lines.append("---")
        lines.append(f"\n## {bid} — {base['family']} / {base['subtype']}")
        lines.append(f"\n**Question**: {base['question']}")
        lines.append(f"\n### Baseline")
        lines.append(f"\n```\n{base['clinical_text'].strip()}\n```")
        lines.append(f"\n**Expected recommendations**: {', '.join(base['expected_recommendations'])}")
        if base["expected_excluded"]:
            lines.append(f"**Expected excluded**: {', '.join(base['expected_excluded'])}")
        lines.append(f"**Reasoning**: {base['expected_reasoning']}")
        if base.get("consistency_warnings"):
            lines.append(f"\n⚠️ **Warnings**: {'; '.join(base['consistency_warnings'])}")

        perts = pert_by_base.get(bid, [])
        for p in perts:
            ptype_icon = {"flip":"🔄","escalate":"⬆️","null":"⊘","grey_zone":"🔘","multi":"🔗"}.get(p["type"],"•")
            lines.append(f"\n### {ptype_icon} {p['id']} — {p['label']}")
            lines.append(f"\n**Type**: {p['type']}")

            if p["variables_changed"]:
                vc_strs = [f"`{v['variable']}`: {v['from']} → {v['to']}" for v in p["variables_changed"]]
                lines.append(f"**Variables changed**: {'; '.join(vc_strs)}")
            if p["staging_impact"]:
                lines.append(f"**Staging impact**: {p['staging_impact']}")

            lines.append(f"\n```\n{p['clinical_text'].strip()}\n```")
            lines.append(f"\n**Expected recommendations**: {', '.join(p['expected_recommendations'])}")
            if p["expected_excluded"]:
                lines.append(f"**Expected excluded**: {', '.join(p['expected_excluded'])}")
            lines.append(f"**Edge justification**: {', '.join(p['edge_justification'])}")
            lines.append(f"**Predicted failure mode**: {p['predicted_failure_mode']}")
            if p.get("grey_zone_statement"):
                lines.append(f"**Grey zone**: {p['grey_zone_statement']}")
            if p.get("notes"):
                lines.append(f"**Notes**: {p['notes']}")
            if p.get("consistency_warnings"):
                lines.append(f"\n⚠️ **Warnings**: {'; '.join(p['consistency_warnings'])}")

    # Summary table
    lines.append("\n---\n\n## Coverage Summary\n")
    lines.append("| Family | Baseline | Perturbations | Edges Tested |")
    lines.append("|---|---|---|---|")
    for base in battery["baselines"]:
        bid = base["id"]
        perts = pert_by_base.get(bid, [])
        edges = set()
        for p in perts:
            edges.update(p.get("edge_justification", []))
        lines.append(f"| {base['family']} | {bid} | {len(perts)} | {', '.join(sorted(edges)) or '—'} |")

    lines.append(f"\n**Total unique edges tested**: {m['unique_edges_tested']}")
    lines.append(f"**Edges**: {', '.join(m['edges_tested'])}")

    return "\n".join(lines)


# ═══════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(description="Generate KG₁ vignette test battery")
    parser.add_argument("--kg1", default="kg1_data.json", help="Path to KG₁ JSON")
    parser.add_argument("--outdir", default=".", help="Output directory")
    args = parser.parse_args()

    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    # Load KG₁ for validation
    kg1_path = Path(args.kg1)
    if kg1_path.exists():
        with open(kg1_path) as f:
            kg1 = json.load(f)
        kg1_edges = {e["statementId"] for e in kg1["edges"]}
        kg1_nodes = {n["id"] for n in kg1["nodes"]}
        print(f"Loaded KG₁: {len(kg1_nodes)} nodes, {len(kg1_edges)} edge statements")
    else:
        print(f"WARNING: KG₁ file not found at {kg1_path}, skipping validation")
        kg1_edges, kg1_nodes = set(), set()

    # Build templates
    templates = build_all_templates()
    print(f"Built {len(templates)} baseline templates")

    # Generate battery
    battery = generate_battery(templates)
    print(f"Generated battery: {battery['meta']['total_baselines']} baselines, "
          f"{battery['meta']['total_perturbations']} perturbations, "
          f"{battery['meta']['total_items']} total items")
    print(f"Unique edges tested: {battery['meta']['unique_edges_tested']}")
    print(f"Perturbation types: {battery['meta']['perturbation_types']}")

    # Validate edge coverage
    if kg1_edges:
        tested = set(battery["meta"]["edges_tested"])
        untested = kg1_edges - tested
        if untested:
            print(f"\nEdge statements NOT tested ({len(untested)}): {sorted(untested)}")
        coverage = len(tested & kg1_edges) / len(kg1_edges) * 100
        print(f"KG₁ edge coverage: {coverage:.1f}%")

    # Check for warnings
    n_warnings = 0
    for b in battery["baselines"]:
        n_warnings += len(b.get("consistency_warnings", []))
    for p in battery["perturbations"]:
        n_warnings += len(p.get("consistency_warnings", []))
    if n_warnings:
        print(f"\n⚠️  {n_warnings} consistency warnings found — review output")
    else:
        print("\n✓ No consistency warnings")

    # Write JSON
    json_path = outdir / "vignette_battery.json"
    with open(json_path, "w") as f:
        json.dump(battery, f, indent=2, default=str)
    print(f"\nJSON output: {json_path} ({json_path.stat().st_size / 1024:.1f} KB)")

    # Write Markdown
    md_path = outdir / "vignette_battery.md"
    md_content = battery_to_markdown(battery)
    with open(md_path, "w") as f:
        f.write(md_content)
    print(f"Markdown output: {md_path} ({md_path.stat().st_size / 1024:.1f} KB)")


if __name__ == "__main__":
    main()
