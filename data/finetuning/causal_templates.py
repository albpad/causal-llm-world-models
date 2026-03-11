#!/usr/bin/env python3
"""
Causal Reasoning Templates for HNC Fine-Tuning Dataset
=======================================================
Encodes the Ferrari et al. Delphi consensus as deterministic rules
for generating gold-standard clinical reasoning responses.

Each family has:
  - treatment_rules: hard blockers, soft modulators, irrelevant vars, mechanisms
  - generate_phase1(): open-ended reasoning from variable_assignments
  - generate_phase2(): structured stances with causal justification
"""

import json, copy, random
from pathlib import Path

from .paths import vignette_battery_path


# ── Treatment-level causal rules ──────────────────────────────────────────────

TREATMENT_RULES = {
    # ── TLM ──
    "tlm": {
        "full_name": "Transoral laser microsurgery (TLM)",
        "hard_blockers": {
            "laryngeal_exposure": ["insufficient"],
            "extralaryngeal_extension": ["significant", "moderate"],
            "thyroid_cartilage_outer_cortex": ["true"],
            "thyroid_cartilage_full_thickness": ["true"],
            "posterior_laryngeal_involvement": ["bilateral_arytenoid"],
            "magic_plane_crossing": ["true"],
            "neurological_function": ["impaired_grade1", "impaired_grade2"],
            "primary_site": ["hypopharyngeal"],
        },
        "soft_blockers": {
            "anterior_commissure": ["present_difficult_exposure"],
            "posterior_paraglottic_space": ["true"],
            "pre_epiglottic_space": ["massive_not_abutting_membrane", "massive_abutting_membrane"],
            "subglottic_extension": ["under_10mm_posterior", "over_10mm"],
            "tumor_volume": ["high"],
            "thyroid_cartilage_inner_cortex": ["focal"],
        },
        "irrelevant": ["age", "smoking_status", "diabetes", "renal_function",
                        "cardiac_function", "hearing_status", "frailty_status"],
        "mechanism": (
            "TLM requires adequate laryngeal exposure (Cormack-Lehane grade I-II) for transoral "
            "instrument access. Tumor extent must be compatible with endoscopic resection margins. "
            "Paraglottic space invasion, cartilage involvement, and extralaryngeal extension "
            "progressively reduce feasibility of complete transoral resection."
        ),
        "families_applicable": [
            "glottic_cT2", "glottic_cT3", "supraglottic_cT3", "hypopharyngeal",
            "elderly_frail", "cT4a_selected",
        ],
    },

    # ── TORS ──
    "tors": {
        "full_name": "Transoral robotic surgery (TORS)",
        "hard_blockers": {
            "primary_site": ["hypopharyngeal"],
            "laryngeal_exposure": ["insufficient"],
        },
        "soft_blockers": {},
        "irrelevant": ["age", "renal_function"],
        "mechanism": (
            "TORS provides similar access to TLM for supraglottic tumors with adequate exposure. "
            "Feasibility depends on robotic instrument reach and tumor accessibility."
        ),
        "families_applicable": ["supraglottic_cT3"],
    },

    # ── OPHL type I (supraglottic laryngectomy) ──
    "ophl_type_i": {
        "full_name": "Supraglottic laryngectomy (OPHL type I)",
        "hard_blockers": {
            "primary_site": ["glottic", "hypopharyngeal"],
            "baseline_laryngeal_function": ["dysfunctional"],
        },
        "soft_blockers": {},
        "irrelevant": ["age", "renal_function"],
        "mechanism": (
            "OPHL type I is indicated for supraglottic tumors without glottic extension. "
            "Requires functional larynx and adequate pulmonary reserve for postoperative swallowing."
        ),
        "families_applicable": ["supraglottic_cT3"],
    },

    # ── OPHL type II ──
    "ophl_type_ii": {
        "full_name": "Open partial horizontal laryngectomy type II (OPHL type II)",
        "hard_blockers": {
            "posterior_laryngeal_involvement": ["bilateral_arytenoid"],
            "baseline_laryngeal_function": ["dysfunctional"],
            "arytenoid_mobility": ["bilateral_fixed"],
            "primary_site": ["hypopharyngeal"],
            "subglottic_extension": ["over_10mm"],
            "cricoarytenoid_joint_invasion": ["true"],
        },
        "soft_blockers": {
            "n_stage": ["cN2", "cN3"],
            "extralaryngeal_extension": ["significant"],
        },
        "irrelevant": ["age", "renal_function", "diabetes", "hearing_status"],
        "mechanism": (
            "OPHL type II preserves at least one arytenoid unit. Bilateral arytenoid fixation, "
            "dysfunctional larynx, or extensive subglottic extension (>10mm) preclude this approach. "
            "Cricoarytenoid joint invasion eliminates the functional unit needed for reconstruction."
        ),
        "families_applicable": [
            "glottic_cT2", "glottic_cT3", "cT4a_selected", "elderly_frail",
            "pretreatment_function",
        ],
    },

    # ── OPHL type IIb ──
    "ophl_type_iib": {
        "full_name": "OPHL type IIb (cricohyoidopexy)",
        "hard_blockers": {
            "baseline_laryngeal_function": ["dysfunctional"],
        },
        "soft_blockers": {},
        "irrelevant": ["age"],
        "mechanism": (
            "OPHL type IIb extends the type II resection to include the cricoid arch. "
            "Indicated when thyroid cartilage erosion prevents standard type II reconstruction."
        ),
        "families_applicable": ["supraglottic_cT3"],
    },

    # ── OPHL type III ──
    "ophl_type_iii": {
        "full_name": "OPHL type III (tracheocricohyoidopexy)",
        "hard_blockers": {
            "baseline_laryngeal_function": ["dysfunctional"],
        },
        "soft_blockers": {},
        "irrelevant": ["age"],
        "mechanism": (
            "OPHL type III includes cricoid resection for tumors with subglottic extension >10mm "
            "or cricoarytenoid joint invasion. Requires at least one mobile arytenoid."
        ),
        "families_applicable": ["glottic_cT3"],
    },

    # ── Total laryngectomy ──
    "total_laryngectomy": {
        "full_name": "Total laryngectomy (TL)",
        "indications": {
            "t_stage": ["cT4a", "cT4b"],
            "baseline_laryngeal_function": ["dysfunctional"],
            "swallowing_status": ["recurrent_pneumonia"],
        },
        "contraindications_in_early": {
            "t_stage": ["cT2"],  # TL is overtreatment for cT2
        },
        "irrelevant": ["age", "renal_function", "hearing_status"],
        "mechanism": (
            "Total laryngectomy is indicated when organ preservation is not feasible: "
            "unresectable T4 disease, dysfunctional larynx with aspiration, or failure of "
            "non-surgical approaches. In early disease (cT2-T3), TL is overtreatment when "
            "larynx preservation options exist."
        ),
        "families_applicable": [
            "glottic_cT3", "hypopharyngeal", "cT4a_unselected", "cT4a_selected",
            "post_ict_response", "pretreatment_function",
        ],
    },

    # ── Concurrent CRT ──
    "concurrent_crt": {
        "full_name": "Concurrent chemoradiotherapy (CRT)",
        "hard_blockers": {
            "comorbidity_burden": ["severe"],
            "dna_repair_disorder": ["true"],
        },
        "indications": {
            "t_stage": ["cT3", "cT4a"],
        },
        "contraindications_in_early": {
            "t_stage": ["cT2"],  # CRT is overtreatment for cT2N0
        },
        "irrelevant": ["age"],  # fit elderly still eligible
        "mechanism": (
            "Concurrent CRT is a standard organ preservation approach for locally advanced "
            "laryngeal/hypopharyngeal cancer (T3-T4a). Not indicated for early glottic cancer "
            "(cT2N0) where RT alone provides equivalent outcomes without chemotherapy toxicity. "
            "Requires adequate organ function for cisplatin or alternative agent."
        ),
        "families_applicable": [
            "glottic_cT3", "supraglottic_cT3", "hypopharyngeal", "cT4a_selected",
            "post_ict_response", "elderly_frail", "pretreatment_function",
        ],
    },

    # ── ICT + RT ──
    "ict_rt": {
        "full_name": "Induction chemotherapy followed by response-adapted treatment (ICT+RT)",
        "hard_blockers": {
            "comorbidity_burden": ["severe"],
        },
        "irrelevant": ["age"],
        "mechanism": (
            "ICT followed by response assessment enables organ preservation in responders "
            "while identifying non-responders for early salvage laryngectomy. Indicated for "
            "locally advanced disease (T3-T4a) in patients fit for platinum-based chemotherapy."
        ),
        "families_applicable": [
            "glottic_cT3", "supraglottic_cT3", "hypopharyngeal", "cT4a_selected",
            "elderly_frail", "pretreatment_function",
        ],
    },

    # ── RT alone ──
    "rt_alone": {
        "full_name": "Radiotherapy alone (RT alone)",
        "indications": {
            "t_stage": ["cT1", "cT2"],
            "ict_response": ["complete_response"],
        },
        "hard_blockers": {
            "dna_repair_disorder": ["true"],
            "previous_neck_rt": ["true"],
        },
        "irrelevant": ["age", "renal_function", "laryngeal_exposure"],
        "mechanism": (
            "RT alone is standard for early glottic cancer (cT1-T2N0) with equivalent "
            "oncologic outcomes to surgery. Also appropriate post-ICT when complete response "
            "achieved. RT is independent of surgical exposure factors."
        ),
        "families_applicable": [
            "glottic_cT2", "post_ict_response",
        ],
    },

    # ── RT accelerated ──
    "rt_accelerated": {
        "full_name": "Accelerated or hyperfractionated radiotherapy",
        "indications": {
            "unfavorable_ct2": ["true"],
            "tumor_volume": ["high"],
        },
        "irrelevant": ["age", "laryngeal_exposure"],
        "mechanism": (
            "Accelerated fractionation may benefit unfavorable cT2 glottic cancer "
            "(bulky tumors, anterior commissure involvement, subglottic extension) "
            "by reducing overall treatment time and tumor repopulation."
        ),
        "families_applicable": ["glottic_cT2"],
    },

    # ── Cisplatin high-dose ──
    "cisplatin_high_dose": {
        "full_name": "High-dose cisplatin (100 mg/m2 q3w)",
        "hard_blockers": {
            "renal_function": ["under_50_ml_min"],
            "cardiac_function": ["nyha_III_IV"],
            "liver_function": ["child_pugh_B_C"],
            "neuropathy": ["grade_2_plus"],
            "hearing_status": ["grade_3_plus"],
            "hiv_status": ["cd4_under_200_or_aids"],
            "hepatitis": ["uncontrolled"],
            "platinum_hypersensitivity": ["true"],
            "psychiatric_disorders": ["true"],
            "bone_marrow": ["grade_2_plus"],
            "diabetes": ["uncontrolled_insulin_dependent"],
            "comorbidity_burden": ["severe"],
        },
        "soft_blockers": {
            "renal_function": ["50_60_ml_min"],
            "hearing_status": ["grade_1"],
            "social_support": ["impaired"],
            "hiv_status": ["cd4_200_350"],
        },
        "irrelevant": ["age", "diabetes_controlled"],
        "mechanism": (
            "High-dose cisplatin requires adequate renal function (CrCl >= 60 mL/min), "
            "absence of significant neuropathy (< grade 2), adequate hearing, and cardiac "
            "reserve. Each absolute contraindication independently blocks cisplatin. "
            "Relative contraindications (CrCl 50-60, grade 1 hearing loss, poor social support) "
            "do not independently block cisplatin but may prompt dose adjustment or monitoring."
        ),
        "families_applicable": ["cisplatin_eligibility"],
    },

    # ── Cetuximab ──
    "cetuximab_concurrent": {
        "full_name": "Cetuximab concurrent with RT",
        "indications_when_cisplatin_blocked": True,
        "irrelevant": ["renal_function"],
        "mechanism": (
            "Cetuximab is a biologic alternative when platinum-based chemotherapy is "
            "contraindicated. Lower nephro/ototoxicity profile but less robust evidence "
            "for larynx preservation compared to cisplatin."
        ),
        "families_applicable": ["cisplatin_eligibility"],
    },

    # ── Carboplatin/5FU ──
    "carboplatin_5fu": {
        "full_name": "Carboplatin/5-fluorouracil",
        "indications_when_cisplatin_blocked": True,
        "irrelevant": [],
        "mechanism": (
            "Carboplatin/5FU combination is an alternative concurrent regimen when high-dose "
            "cisplatin is contraindicated. Better renal safety profile than cisplatin."
        ),
        "families_applicable": ["cisplatin_eligibility"],
    },
}


# ── Per-family stance determination logic ─────────────────────────────────────

def _parse_vars(va):
    """Parse variable_assignments (could be string repr of dict or actual dict)."""
    if isinstance(va, str):
        return eval(va)
    return dict(va)


def _is_blocked(treatment_key, va):
    """Check if treatment is hard-blocked by any variable."""
    rules = TREATMENT_RULES.get(treatment_key, {})
    blockers = rules.get("hard_blockers", {})
    for var, blocked_vals in blockers.items():
        if va.get(var) in blocked_vals:
            return True, var, va.get(var)
    return False, None, None


def _is_soft_blocked(treatment_key, va):
    """Check if treatment is relatively contraindicated."""
    rules = TREATMENT_RULES.get(treatment_key, {})
    soft = rules.get("soft_blockers", {})
    for var, vals in soft.items():
        if va.get(var) in vals:
            return True, var, va.get(var)
    return False, None, None


def determine_stance(treatment_key, va, expected_rec, expected_exc):
    """
    Determine the gold-standard stance for a treatment given variable assignments.
    Uses a combination of rule-based logic and ground truth from the battery.
    Ground truth (expected_rec/expected_exc) takes precedence.
    """
    # Parse lists if they're strings
    if isinstance(expected_rec, str):
        expected_rec = eval(expected_rec)
    if isinstance(expected_exc, str):
        expected_exc = eval(expected_exc)

    # Check if treatment is in expected lists (ground truth priority)
    if treatment_key in expected_rec:
        return "APPROPRIATE"
    if treatment_key in expected_exc:
        return "CONTRAINDICATED"

    # For ophl_any, check if any ophl variant is recommended/excluded
    if treatment_key == "ophl_any":
        if any(t in expected_rec for t in ["ophl_type_i", "ophl_type_ii", "ophl_type_iib", "ophl_type_iii"]):
            return "APPROPRIATE"
        if any(t in expected_exc for t in ["ophl_type_i", "ophl_type_ii", "ophl_type_iib", "ophl_type_iii", "ophl_any"]):
            return "CONTRAINDICATED"

    # Check ophl variants against ophl_any in expected lists
    if treatment_key.startswith("ophl_type_"):
        if "ophl_any" in expected_rec:
            return "APPROPRIATE"
        if "ophl_any" in expected_exc:
            return "CONTRAINDICATED"

    # nonsurgical_lp maps to CRT/ICT
    if treatment_key == "nonsurgical_lp":
        if "nonsurgical_lp" in expected_rec:
            return "APPROPRIATE"
        if "nonsurgical_lp" in expected_exc:
            return "CONTRAINDICATED"

    # surgical_lp maps to TLM/OPHL
    if treatment_key == "surgical_lp":
        if "surgical_lp" in expected_rec:
            return "APPROPRIATE"
        if "surgical_lp" in expected_exc:
            return "CONTRAINDICATED"

    # Rule-based fallback
    blocked, bvar, bval = _is_blocked(treatment_key, va)
    if blocked:
        return "CONTRAINDICATED"

    soft_blocked, svar, sval = _is_soft_blocked(treatment_key, va)
    if soft_blocked:
        return "RELATIVELY CONTRAINDICATED"

    return "UNCERTAIN"


def generate_causal_reasoning(treatment_key, stance, va, expected_rec, expected_exc):
    """Generate a causal reasoning string for a given treatment stance."""
    rules = TREATMENT_RULES.get(treatment_key, {})
    mechanism = rules.get("mechanism", "")
    full_name = rules.get("full_name", treatment_key)

    # Build the reasoning based on stance
    if stance == "CONTRAINDICATED":
        blocked, bvar, bval = _is_blocked(treatment_key, va)
        if blocked:
            return (
                f"{full_name} is CONTRAINDICATED because {bvar} is '{bval}', "
                f"which is an absolute blocker. {mechanism}"
            )
        # If ground truth says excluded but rules don't detect it
        return (
            f"{full_name} is CONTRAINDICATED for this clinical scenario. "
            f"The combination of clinical features makes this treatment inappropriate. "
            f"{mechanism}"
        )

    elif stance == "RELATIVELY CONTRAINDICATED":
        soft, svar, sval = _is_soft_blocked(treatment_key, va)
        if soft:
            return (
                f"{full_name} is RELATIVELY CONTRAINDICATED because {svar} is '{sval}', "
                f"which is a relative (not absolute) risk factor. {mechanism} "
                f"This does not absolutely prevent use but requires careful consideration."
            )
        return f"{full_name} is relatively contraindicated. {mechanism}"

    elif stance == "APPROPRIATE":
        # List checked blockers that are clear
        blockers = rules.get("hard_blockers", {})
        clear_checks = []
        for var, blocked_vals in blockers.items():
            current_val = va.get(var, "unknown")
            if current_val not in blocked_vals and current_val != "unknown":
                clear_checks.append(f"{var}='{current_val}' (not blocked)")

        checks_str = "; ".join(clear_checks[:4]) if clear_checks else "no blocking contraindications identified"
        return (
            f"{full_name} is APPROPRIATE. Key checks: {checks_str}. "
            f"{mechanism}"
        )

    else:  # UNCERTAIN
        return (
            f"{full_name}: The clinical picture is ambiguous for this treatment. "
            f"{mechanism} "
            f"A multidisciplinary discussion weighing patient preferences and institutional "
            f"expertise is recommended."
        )


# ── Family-specific treatment lists (which treatments to evaluate per family) ─

FAMILY_TREATMENTS = {
    "glottic_cT2": ["tlm", "rt_alone", "rt_accelerated", "concurrent_crt",
                     "ophl_type_ii", "total_laryngectomy"],
    "glottic_cT3": ["tlm", "ophl_type_ii", "ophl_type_iii", "concurrent_crt",
                     "ict_rt", "total_laryngectomy"],
    "supraglottic_cT3": ["tlm", "tors", "ophl_type_i", "ophl_type_iib",
                          "concurrent_crt", "ict_rt", "total_laryngectomy"],
    "hypopharyngeal": ["tlm", "ophl_type_ii", "concurrent_crt", "ict_rt",
                        "total_laryngectomy"],
    "cT4a_unselected": ["total_laryngectomy", "ophl_any", "concurrent_crt", "tlm"],
    "cT4a_selected": ["total_laryngectomy", "ophl_any", "ophl_type_ii",
                       "concurrent_crt", "ict_rt", "tlm"],
    "cisplatin_eligibility": ["cisplatin_high_dose", "cetuximab_concurrent",
                               "carboplatin_5fu"],
    "post_ict_response": ["rt_alone", "concurrent_crt", "total_laryngectomy"],
    "elderly_frail": ["tlm", "ophl_type_ii", "concurrent_crt", "ict_rt",
                       "rt_alone", "total_laryngectomy"],
    "pretreatment_function": ["concurrent_crt", "ict_rt", "total_laryngectomy",
                               "nonsurgical_lp"],
}


def generate_gold_response(item, family=None):
    """
    Generate a complete gold-standard response (Phase 1 + Phase 2 combined)
    for a vignette battery item.

    Parameters:
        item: dict with clinical_text, question, expected_recommendations,
              expected_excluded, family, variable_assignments
        family: override family (optional)

    Returns:
        str: Complete gold-standard assistant response
    """
    fam = family or item.get("family", "")
    va = _parse_vars(item.get("variable_assignments", {}))
    expected_rec = item.get("expected_recommendations", [])
    expected_exc = item.get("expected_excluded", [])
    if isinstance(expected_rec, str):
        expected_rec = eval(expected_rec)
    if isinstance(expected_exc, str):
        expected_exc = eval(expected_exc)

    treatments = FAMILY_TREATMENTS.get(fam, [])

    # ── Phase 1: Open-ended reasoning ──
    lines = []
    lines.append("## Clinical Assessment\n")

    # Key staging info
    t = va.get("t_stage", "")
    n = va.get("n_stage", "")
    site = va.get("primary_site", "")
    if t or n or site:
        lines.append(f"This is a {t}{n} {site} squamous cell carcinoma case.\n")

    # Key variables
    key_vars = [
        ("vocal_cord_mobility", "Vocal cord mobility"),
        ("laryngeal_exposure", "Laryngeal exposure"),
        ("baseline_laryngeal_function", "Baseline laryngeal function"),
        ("thyroid_cartilage_outer_cortex", "Thyroid cartilage outer cortex invasion"),
        ("thyroid_cartilage_inner_cortex", "Thyroid cartilage inner cortex"),
        ("extralaryngeal_extension", "Extralaryngeal extension"),
        ("subglottic_extension", "Subglottic extension"),
        ("arytenoid_mobility", "Arytenoid mobility"),
        ("frailty_status", "Frailty status"),
        ("renal_function", "Renal function"),
        ("ict_response", "ICT response"),
        ("swallowing_status", "Swallowing status"),
        ("ecog_ps", "ECOG performance status"),
    ]
    noted = []
    for var, label in key_vars:
        v = va.get(var)
        if v and v not in ("none", "false", "normal", "unknown", "null", "negative"):
            noted.append(f"- {label}: {v}")
    if noted:
        lines.append("Key clinical findings:\n" + "\n".join(noted) + "\n")

    # ── Phase 1: Treatment-by-treatment reasoning ──
    lines.append("## Treatment Option Analysis\n")

    for tx in treatments:
        stance = determine_stance(tx, va, expected_rec, expected_exc)
        reasoning = generate_causal_reasoning(tx, stance, va, expected_rec, expected_exc)
        full_name = TREATMENT_RULES.get(tx, {}).get("full_name", tx)

        lines.append(f"**{full_name}**: {stance}")
        lines.append(f"Reasoning: {reasoning}\n")

        # Sensitivity analysis: what would change this?
        rules = TREATMENT_RULES.get(tx, {})
        if stance == "APPROPRIATE" and rules.get("hard_blockers"):
            # Pick one blocker to illustrate sensitivity
            blockers = list(rules["hard_blockers"].items())
            if blockers:
                bvar, bvals = blockers[0]
                lines.append(
                    f"Sensitivity: If {bvar} were '{bvals[0]}', this would change to "
                    f"CONTRAINDICATED.\n"
                )
        elif stance == "CONTRAINDICATED":
            blocked, bvar, bval = _is_blocked(tx, va)
            if blocked:
                lines.append(
                    f"Sensitivity: If {bvar} were restored to a non-blocking value, "
                    f"this treatment could become viable.\n"
                )

    # ── Summary ──
    rec_names = [TREATMENT_RULES.get(t, {}).get("full_name", t) for t in treatments
                 if determine_stance(t, va, expected_rec, expected_exc) == "APPROPRIATE"]
    exc_names = [TREATMENT_RULES.get(t, {}).get("full_name", t) for t in treatments
                 if determine_stance(t, va, expected_rec, expected_exc) == "CONTRAINDICATED"]

    lines.append("## Summary\n")
    if rec_names:
        lines.append(f"Recommended options: {', '.join(rec_names)}.")
    if exc_names:
        lines.append(f"Contraindicated: {', '.join(exc_names)}.")
    lines.append(
        "These recommendations are based on the specific clinical variables described "
        "and align with current multidisciplinary expert consensus for head and neck "
        "cancer management."
    )

    return "\n".join(lines)


# ── Null perturbation response template ───────────────────────────────────────

def generate_null_response(item, baseline_item, variable_changed, change_desc):
    """
    Generate a gold response for a null perturbation emphasizing stability.
    """
    fam = item.get("family", "")
    va = _parse_vars(item.get("variable_assignments", {}))
    expected_rec = item.get("expected_recommendations", [])
    expected_exc = item.get("expected_excluded", [])
    if isinstance(expected_rec, str):
        expected_rec = eval(expected_rec)
    if isinstance(expected_exc, str):
        expected_exc = eval(expected_exc)

    treatments = FAMILY_TREATMENTS.get(fam, [])

    lines = []
    lines.append("## Clinical Assessment\n")
    lines.append(
        f"Note: This case includes a modification ({change_desc}). "
        f"However, this change is therapeutically neutral per expert consensus "
        f"and should NOT alter treatment recommendations.\n"
    )

    # Generate same stances as baseline
    lines.append("## Treatment Option Analysis\n")
    for tx in treatments:
        stance = determine_stance(tx, va, expected_rec, expected_exc)
        full_name = TREATMENT_RULES.get(tx, {}).get("full_name", tx)
        reasoning = generate_causal_reasoning(tx, stance, va, expected_rec, expected_exc)

        lines.append(f"**{full_name}**: {stance}")
        lines.append(f"Reasoning: {reasoning}")
        lines.append(
            f"Note: The {change_desc} does NOT affect this treatment's eligibility. "
            f"The variables that drive this decision ({', '.join(list(TREATMENT_RULES.get(tx, {}).get('hard_blockers', {}).keys())[:3])}) "
            f"remain unchanged.\n"
        )

    lines.append("## Summary\n")
    lines.append(
        f"Despite the {change_desc}, all treatment recommendations remain unchanged. "
        f"The modified variable does not causally influence treatment eligibility in this context."
    )

    return "\n".join(lines)


# ── Contrastive pair response template ────────────────────────────────────────

def generate_contrastive_response(base_item, pert_item, variables_changed):
    """
    Generate a gold response comparing base and perturbation cases,
    explaining which treatments change and why.
    """
    fam = base_item.get("family", "")
    va_base = _parse_vars(base_item.get("variable_assignments", {}))
    va_pert = _parse_vars(pert_item.get("variable_assignments", {}))
    rec_base = base_item.get("expected_recommendations", [])
    exc_base = base_item.get("expected_excluded", [])
    rec_pert = pert_item.get("expected_recommendations", [])
    exc_pert = pert_item.get("expected_excluded", [])

    for lst_name in ["rec_base", "exc_base", "rec_pert", "exc_pert"]:
        lst = eval(lst_name)
        if isinstance(lst, str):
            exec(f"{lst_name} = eval(lst)")

    if isinstance(rec_base, str): rec_base = eval(rec_base)
    if isinstance(exc_base, str): exc_base = eval(exc_base)
    if isinstance(rec_pert, str): rec_pert = eval(rec_pert)
    if isinstance(exc_pert, str): exc_pert = eval(exc_pert)

    treatments = FAMILY_TREATMENTS.get(fam, [])
    vc = variables_changed if isinstance(variables_changed, list) else eval(str(variables_changed))

    lines = []
    lines.append("## Contrastive Analysis\n")

    change_desc = "; ".join(
        f"{c['variable']}: '{c['from']}' -> '{c['to']}'" for c in vc
    )
    lines.append(f"The key difference between Case A and Case B is: {change_desc}\n")

    lines.append("## Treatment-by-Treatment Comparison\n")
    for tx in treatments:
        stance_base = determine_stance(tx, va_base, rec_base, exc_base)
        stance_pert = determine_stance(tx, va_pert, rec_pert, exc_pert)
        full_name = TREATMENT_RULES.get(tx, {}).get("full_name", tx)

        if stance_base != stance_pert:
            lines.append(
                f"**{full_name}**: CHANGES from {stance_base} (Case A) to {stance_pert} (Case B)"
            )
            lines.append(
                f"Causal mechanism: The change in {vc[0]['variable']} from '{vc[0]['from']}' "
                f"to '{vc[0]['to']}' directly affects {tx} eligibility because "
                f"{TREATMENT_RULES.get(tx, {}).get('mechanism', 'of clinical impact on treatment feasibility.')}.\n"
            )
        else:
            lines.append(
                f"**{full_name}**: NO CHANGE (remains {stance_base} in both cases)"
            )
            lines.append(
                f"The variable change ({vc[0]['variable']}) does not causally affect "
                f"{tx} eligibility.\n"
            )

    return "\n".join(lines)


if __name__ == "__main__":
    # Quick test: generate a gold response for A1-BASE
    with open(vignette_battery_path()) as f:
        battery = json.load(f)

    b = battery["baselines"][0]  # A1-BASE
    print(f"=== {b['id']} ({b['family']}) ===\n")
    resp = generate_gold_response(b)
    print(resp[:2000])
    print(f"\n... ({len(resp)} total chars)")
