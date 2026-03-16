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
    assert summary["row_level"]["n_rows"] == 1
    assert summary["gold_sources"]["battery_expectation"] == 1
    assert summary["row_level"]["exact_match_rate"] == 1.0
    assert summary["row_level"]["label_metrics"]["recommended"]["tp"] == 2
    assert summary["row_level"]["label_metrics"]["excluded"]["tp"] == 1


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
    assert summary["row_level"]["exact_match_rate"] == 0.0
    assert summary["row_level"]["label_metrics"]["recommended"]["fp"] == 2
    assert summary["row_level"]["label_metrics"]["excluded"]["fn"] == 1


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
