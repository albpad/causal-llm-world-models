import json

from causal_llm_eval.parser_validation import validate_parser
from causal_llm_eval.response_parser import parse_result


def test_parser_validator_uses_battery_expectations(tmp_path):
    battery = tmp_path / "battery.json"
    battery.write_text(
        json.dumps(
            {
                "baselines": [
                    {
                        "id": "B1",
                        "family": "demo",
                        "clinical_text": "x",
                        "question": "q",
                        "expected_recommendations": ["tlm"],
                        "expected_excluded": ["total_laryngectomy"],
                    }
                ],
                "perturbations": [],
            }
        )
    )
    results = tmp_path / "run.jsonl"
    row = {
        "item_id": "B1",
        "model_name": "demo-model",
        "run_idx": 0,
        "error": None,
        "phase1_response": "Transoral laser microsurgery (TLM) would be appropriate.",
        "phase2_response": "**Transoral laser microsurgery (TLM)**: APPROPRIATE\nReasoning: limited disease.\n**Total laryngectomy**: CONTRAINDICATED\nReasoning: not needed.",
    }
    results.write_text(json.dumps(row) + "\n")

    summary = validate_parser(results, battery)
    assert summary["battery_alignment"]["n_rows"] == 1
    assert summary["gold_sources"]["battery_expectation"] == 1
    assert summary["battery_alignment"]["exact_match_rate"] == 1.0
    assert summary["battery_alignment"]["label_metrics"]["recommended"]["tp"] == 2
    assert summary["battery_alignment"]["label_metrics"]["excluded"]["tp"] == 1
    assert summary["structured_snippet_validation"]["summary"]["exact_match_rate"] >= 0.85


def test_parser_validator_prefers_clinician_annotations(tmp_path):
    battery = tmp_path / "battery.json"
    battery.write_text(
        json.dumps(
            {
                "baselines": [
                    {
                        "id": "B1",
                        "family": "demo",
                        "clinical_text": "x",
                        "question": "q",
                        "expected_recommendations": ["tlm"],
                        "expected_excluded": [],
                    }
                ],
                "perturbations": [],
            }
        )
    )
    annotations = tmp_path / "annotations.json"
    annotations.write_text(
        json.dumps(
            {
                "cases": {
                    "B1": {
                        "parser_validation": {
                            "verdict": "incorrect",
                            "recommended": [],
                            "excluded": ["tlm"],
                            "uncertain": [],
                        }
                    }
                }
            }
        )
    )
    results = tmp_path / "run.jsonl"
    row = {
        "item_id": "B1",
        "model_name": "demo-model",
        "run_idx": 0,
        "error": None,
        "phase1_response": "Transoral laser microsurgery (TLM) would be appropriate.",
        "phase2_response": "**Transoral laser microsurgery (TLM)**: APPROPRIATE\nReasoning: limited disease.",
    }
    results.write_text(json.dumps(row) + "\n")

    summary = validate_parser(results, battery, annotations)
    assert summary["gold_sources"]["clinician_annotation"] == 1
    assert summary["battery_alignment"]["exact_match_rate"] == 0.0
    assert summary["battery_alignment"]["label_metrics"]["recommended"]["fp"] == 2
    assert summary["battery_alignment"]["label_metrics"]["excluded"]["fn"] == 1


def test_parser_derives_aggregate_labels_from_concrete_treatments():
    row = {
        "item_id": "B1",
        "model_name": "demo-model",
        "run_idx": 0,
        "error": None,
        "phase1_response": "",
        "phase2_response": (
            "**OPHL type II**: APPROPRIATE\n"
            "Reasoning: feasible.\n"
            "**Concurrent chemoradiotherapy**: CONTRAINDICATED\n"
            "Reasoning: poor function."
        ),
    }
    parsed = parse_result(row)
    stances = {entry["treatment"]: entry["stance"] for entry in parsed["stances"]}
    assert stances["ophl_type_ii"] == "recommended"
    assert stances["ophl_any"] == "recommended"
    assert stances["surgical_lp"] == "recommended"
    assert "nonsurgical_lp" not in stances


def test_parser_validator_consensus_alignment_uses_predicted_maps(tmp_path):
    battery = tmp_path / "battery.json"
    battery.write_text(
        json.dumps(
            {
                "baselines": [
                    {
                        "id": "B1",
                        "family": "pretreatment_function",
                        "clinical_text": "x",
                        "question": "q",
                        "expected_recommendations": ["concurrent_crt"],
                        "expected_excluded": ["total_laryngectomy"],
                    }
                ],
                "perturbations": [],
            }
        )
    )
    results = tmp_path / "run.jsonl"
    rows = [
        {
            "item_id": "B1",
            "model_name": "demo-model",
            "run_idx": 0,
            "error": None,
            "phase1_response": "",
            "phase2_response": (
                    "**Concurrent chemoradiotherapy (CRT)**: APPROPRIATE\n"
                    "Reasoning: suitable.\n"
                    "**Total laryngectomy**: CONTRAINDICATED\n"
                "Reasoning: not needed."
            ),
        },
        {
            "item_id": "B1",
            "model_name": "demo-model",
            "run_idx": 1,
            "error": None,
            "phase1_response": "",
            "phase2_response": (
                    "**Concurrent chemoradiotherapy (CRT)**: APPROPRIATE\n"
                    "Reasoning: suitable.\n"
                    "**Total laryngectomy**: CONTRAINDICATED\n"
                "Reasoning: not needed."
            ),
        },
    ]
    results.write_text("\n".join(json.dumps(row) for row in rows) + "\n")

    summary = validate_parser(results, battery)
    assert summary["consensus_alignment"]["n_rows"] == 1
    assert summary["consensus_alignment"]["exact_match_rate"] == 1.0
