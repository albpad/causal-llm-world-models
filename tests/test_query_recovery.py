import json
from pathlib import Path

from causal_llm_eval.llm_query_runner import is_complete_result, load_completed


def test_is_complete_result_rejects_blank_success():
    row = {"error": None, "phase1_response": "answer", "phase2_response": ""}
    assert is_complete_result(row) is False
    assert is_complete_result(row, require_phase2=False) is True


def test_load_completed_uses_strict_completeness(tmp_path):
    path = tmp_path / "run.jsonl"
    rows = [
        {"hash": "good", "error": None, "phase1_response": "a", "phase2_response": "b"},
        {"hash": "blank", "error": None, "phase1_response": "a", "phase2_response": ""},
        {"hash": "err", "error": "HTTPError", "phase1_response": "", "phase2_response": ""},
    ]
    with open(path, "w") as f:
        for row in rows:
            f.write(json.dumps(row) + "\n")

    assert load_completed(path) == {"good"}
    assert load_completed(path, require_phase2=False) == {"good", "blank"}
