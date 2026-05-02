from causal_llm_eval.domain_evaluation import (
    build_edge_risk_map,
    compute_risk_weighted_fidelity,
    ordered_models,
    treatment_risk_weight,
)
from causal_llm_eval.kg2_enhanced import KG2Edge


def test_treatment_risk_weight_prioritises_total_laryngectomy():
    assert treatment_risk_weight("total_laryngectomy") == 3
    assert treatment_risk_weight("tlm") == 2
    assert treatment_risk_weight("carboplatin_5fu") == 1


def test_build_edge_risk_map_uses_highest_weighted_treatment():
    rows = [
        {
            "edge_id": "S1",
            "expected_recommendations": "tlm, total_laryngectomy",
            "expected_excluded": "",
        },
        {
            "edge_id": "S2",
            "expected_recommendations": "carboplatin_5fu",
            "expected_excluded": "",
        },
    ]
    risk = build_edge_risk_map(rows)
    assert risk["S1"]["weight"] == 3
    assert risk["S2"]["weight"] == 1


def test_compute_risk_weighted_fidelity_uses_tl_weighting():
    kg2 = {
        "demo-model": {
            "S1": KG2Edge(edge_id="S1", model="demo-model", detected=False, soft_detected=True, direction_correct=False),
            "S2": KG2Edge(edge_id="S2", model="demo-model", detected=False, soft_detected=True, direction_correct=True),
        }
    }
    sid_details = {
        "demo-model": {
            "details": [
                {"treatment": "total_laryngectomy", "wrong": True},
                {"treatment": "tlm", "wrong": False},
            ]
        }
    }
    risk_map = {
        "S1": {"weight": 3, "treatments": ["total_laryngectomy"]},
        "S2": {"weight": 2, "treatments": ["tlm"]},
    }

    summary = compute_risk_weighted_fidelity(kg2, sid_details, risk_map)["demo-model"]
    assert summary["weighted_wrong_direction_rate"] == 3 / 5
    assert summary["weighted_sid_rate"] == 3 / 5
    assert summary["tier3_wrong_direction_edges"] == 1
    assert summary["tier3_sid_errors"] == 1


def test_ordered_models_handles_subsets_and_gemma():
    models = ordered_models({"gemma-4-31b-it", "kimi-k2.5"})
    assert models == ["kimi-k2.5", "gemma-4-31b-it"]
