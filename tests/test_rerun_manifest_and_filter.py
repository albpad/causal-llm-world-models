import json
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


def write_jsonl(path: Path, rows: list[dict]) -> None:
    with open(path, "w") as f:
        for row in rows:
            f.write(json.dumps(row) + "\n")


def test_build_rerun_manifest_can_force_include_complete_rows(tmp_path):
    battery = tmp_path / "battery.json"
    battery.write_text(
        json.dumps(
            {
                "baselines": [{
                    "id": "A1",
                    "family": "demo",
                    "type": "baseline",
                    "clinical_text": "baseline",
                    "question": "q",
                    "expected_recommendations": [],
                    "expected_excluded": [],
                }],
                "perturbations": [{
                    "id": "A1-P2",
                    "family": "demo",
                    "type": "perturbation",
                    "baseline_id": "A1",
                    "clinical_text": "perturbation",
                    "question": "q",
                    "expected_recommendations": [],
                    "expected_excluded": [],
                }],
            }
        )
    )
    results = tmp_path / "run.jsonl"
    rows = [
        {
            "hash": "h1",
            "item_id": "A1-P2",
            "model_name": "demo-model",
            "run_idx": 0,
            "error": None,
            "phase1_response": "phase 1",
            "phase2_response": "phase 2",
        },
        {
            "hash": "h2",
            "item_id": "A1",
            "model_name": "demo-model",
            "run_idx": 0,
            "error": None,
            "phase1_response": "phase 1",
            "phase2_response": "",
        },
    ]
    write_jsonl(results, rows)

    out = tmp_path / "manifest.json"
    subprocess.run(
        [
            sys.executable,
            str(REPO_ROOT / "scripts" / "build_rerun_manifest.py"),
            "--results",
            str(results),
            "--battery",
            str(battery),
            "--model",
            "demo-model",
            "--items",
            "A1-P2",
            "--include-complete",
            "--out",
            str(out),
        ],
        check=True,
        cwd=REPO_ROOT,
    )

    manifest = json.loads(out.read_text())
    assert manifest["n_incomplete"] == 1
    assert manifest["items"] == ["A1-P2"]
    assert manifest["include_complete"] is True
    assert [row["item_id"] for row in manifest["rows"]] == ["A1-P2"]


def test_filter_results_jsonl_preserves_input_order_and_applies_filters(tmp_path):
    left = tmp_path / "left.jsonl"
    right = tmp_path / "right.jsonl"
    write_jsonl(
        left,
        [
            {"hash": "a", "item_id": "A1", "model_name": "m1", "run_idx": 0},
            {"hash": "b", "item_id": "A2", "model_name": "m2", "run_idx": 1},
        ],
    )
    write_jsonl(
        right,
        [
            {"hash": "c", "item_id": "A1", "model_name": "m1", "run_idx": 2},
            {"hash": "d", "item_id": "A3", "model_name": "m1", "run_idx": 0},
        ],
    )

    out = tmp_path / "subset.jsonl"
    subprocess.run(
        [
            sys.executable,
            str(REPO_ROOT / "scripts" / "filter_results_jsonl.py"),
            "--results",
            str(left),
            str(right),
            "--model",
            "m1",
            "--max-run-idx",
            "1",
            "--items",
            "A1,A3",
            "--out",
            str(out),
        ],
        check=True,
        cwd=REPO_ROOT,
    )

    rows = [json.loads(line) for line in out.read_text().splitlines() if line.strip()]
    assert [row["hash"] for row in rows] == ["a", "d"]
