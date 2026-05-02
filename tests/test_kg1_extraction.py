from causal_llm_eval.kg1_extraction import (
    build_alignment_rows,
    build_validation_summary,
    compile_candidate_rules,
    extract_statement_rows,
)


def test_extract_statement_rows_handles_heading_fused_to_statement():
    text = (
        "Prognostic and predictive factorsStatement 111 (S111R) "
        "Performance status, comorbidities, and tumour-node-metastasis stage "
        "have prognostic significance for overall survival in laryngeal and "
        "hypopharyngeal cancer treated with larynx-preservation strategies."
        "IV; 98.5% (first)"
    )

    rows = extract_statement_rows(text, [0])

    assert len(rows) == 1
    assert rows[0]["statement_id"] == "S111R"
    assert rows[0]["section"] == "Prognostic and predictive factors"
    assert rows[0]["meets_80pct_table_threshold"] is True


def test_compile_candidate_rules_marks_contextual_selection_factors():
    statements = [
        {
            "statement_id": "S84",
            "kind": "statement",
            "number_text": "84",
            "number_start": 84,
            "number_end": 84,
            "section": "Organ preservation in older patients: selection criteria",
            "statement_text": (
                "Vulnerable and frail patients are at higher risk of treatment "
                "complications and face a higher risk of non-cancer-related death, "
                "due to comorbidities and treatment-induced toxic effects. Therefore, "
                "organ preservation strategies in this group of patients should be "
                "carefully weighed against the risks."
            ),
            "level_of_evidence": "IV",
            "consensus_pct": 89.0,
            "voting_round": "first",
            "meets_80pct_table_threshold": True,
            "page_hint": 1,
        }
    ]

    enriched, candidate_rules = compile_candidate_rules(statements)

    assert enriched[0]["statement_class"] == "selection_factor"
    assert enriched[0]["graph_candidate"] is True
    assert candidate_rules
    assert candidate_rules[0]["decision_scope"] == "larynx_preservation_any"


def test_compile_candidate_rules_extracts_multiple_fallback_targets():
    statements = [
        {
            "statement_id": "S72R",
            "kind": "statement",
            "number_text": "72",
            "number_start": 72,
            "number_end": 72,
            "section": "Which comorbidities are contraindications and to what extent?",
            "statement_text": (
                "Carboplatin-based treatment or cetuximab can be considered as concurrent "
                "treatment in patients unfit for any schedule of cisplatin-based chemotherapy "
                "who refuse total laryngectomy."
            ),
            "level_of_evidence": "II",
            "consensus_pct": 90.4,
            "voting_round": "second",
            "meets_80pct_table_threshold": True,
            "page_hint": 1,
        }
    ]

    _, candidate_rules = compile_candidate_rules(statements)
    targets = {row["target_treatment"] for row in candidate_rules}

    assert "cetuximab_concurrent" in targets
    assert "carboplatin_5fu" in targets


def test_validation_summary_flags_low_consensus_benchmark_anchor():
    statements = [
        {
            "statement_id": "SA6",
            "kind": "additional_statement",
            "number_text": "6",
            "number_start": 6,
            "number_end": 6,
            "section": "Prognostic and predictive factors",
            "statement_text": (
                "In patients with laryngeal cancer who have a partial response after "
                "induction chemotherapy, subsequent curative treatment should entail "
                "radiotherapy alone."
            ),
            "level_of_evidence": "II",
            "consensus_pct": 67.2,
            "voting_round": "second",
            "meets_80pct_table_threshold": False,
            "page_hint": 1,
            "mentioned_treatments": ["rt_alone", "ict_rt"],
            "decision_scopes": ["nonsurgical_lp", "larynx_preservation_any"],
            "statement_class": "response_adapted",
            "graph_candidate": True,
            "atomic_condition_count": 1,
        }
    ]
    candidate_rules = [
        {
            "rule_id": "SA6#1",
            "statement_id": "SA6",
            "section": "Prognostic and predictive factors",
            "page_hint": 1,
            "rule_class": "response_adapted",
            "direction": "positive",
            "target_treatment": "rt_alone",
            "decision_scope": "nonsurgical_lp",
            "condition_text": "partial response after induction chemotherapy",
            "level_of_evidence": "II",
            "consensus_pct": 67.2,
            "voting_round": "second",
            "meets_80pct_table_threshold": False,
        }
    ]
    traceability_rows = [
        {
            "edge_id": "SA6",
            "family": "post_ict_response",
            "item_id": "H2-P1",
            "baseline_id": "H2-BASE",
            "type": "flip",
            "label": "Partial response",
            "expected_recommendations": "rt_alone",
            "expected_excluded": "",
            "baseline_label": "stable_disease",
        }
    ]

    alignment_rows = build_alignment_rows(statements, candidate_rules, traceability_rows)
    summary = build_validation_summary(statements, candidate_rules, alignment_rows, traceability_rows, "doc 3.pdf")

    assert summary["coverage"]["benchmark_below_80pct_table_threshold"] == ["SA6"]
    assert summary["coverage"]["benchmark_without_candidate_rules"] == []
