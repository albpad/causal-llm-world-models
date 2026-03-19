import json

from causal_llm_eval.benchmark_audit import build_traceability_rows, compute_integrity_summary


def test_benchmark_audit_detects_null_drift_and_traceability():
    battery = {
        "baselines": [
            {
                "id": "B1",
                "family": "glottic_cT2",
                "expected_recommendations": ["tlm"],
                "expected_excluded": ["total_laryngectomy"],
                "variable_assignments": {"t_stage": "cT2"},
            }
        ],
        "perturbations": [
            {
                "id": "P1",
                "baseline_id": "B1",
                "family": "glottic_cT2",
                "type": "flip",
                "label": "test",
                "expected_recommendations": ["tlm"],
                "expected_excluded": [],
                "edge_justification": ["S1"],
                "variable_assignments": {"t_stage": "cT2"},
            },
            {
                "id": "N1",
                "baseline_id": "B1",
                "family": "glottic_cT2",
                "type": "null",
                "label": "null",
                "expected_recommendations": [],
                "expected_excluded": [],
                "edge_justification": ["S2"],
                "variable_assignments": {"t_stage": "cT2"},
            },
        ],
    }

    summary = compute_integrity_summary(battery)
    rows = build_traceability_rows(battery)

    assert summary["counts"]["baselines"] == 1
    assert summary["counts"]["perturbations"] == 2
    assert summary["counts"]["items_total"] == 3
    assert summary["counts"]["statement_linked_rules"] == 2
    assert len(summary["null_drift"]) == 1
    assert summary["missing_traceability"] == []
    assert rows[0]["edge_id"] == "S1"
