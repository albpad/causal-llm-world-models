import json
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


def test_build_study_manifest_creates_expected_rows(tmp_path):
    battery = tmp_path / "battery.json"
    battery.write_text(
        json.dumps(
            {
                "baselines": [
                    {
                        "id": "A1",
                        "family": "demo",
                        "type": "baseline",
                        "clinical_text": "x",
                        "question": "q",
                        "expected_recommendations": [],
                        "expected_excluded": [],
                    }
                ],
                "perturbations": [
                    {
                        "id": "A1-P1",
                        "family": "demo",
                        "type": "perturbation",
                        "baseline_id": "A1",
                        "clinical_text": "y",
                        "question": "q",
                        "expected_recommendations": [],
                        "expected_excluded": [],
                    }
                ],
            }
        )
    )
    out = tmp_path / "manifest.json"
    subprocess.run(
        [
            sys.executable,
            str(REPO_ROOT / "scripts" / "build_study_manifest.py"),
            "--battery",
            str(battery),
            "--models",
            "m1,m2",
            "--runs",
            "2",
            "--out",
            str(out),
        ],
        cwd=REPO_ROOT,
        check=True,
    )

    manifest = json.loads(out.read_text())
    assert manifest["model_names"] == ["m1", "m2"]
    assert manifest["runs"] == 2
    assert manifest["n_rows"] == 8
    assert manifest["rows"][0]["item_id"] == "A1"
    assert manifest["rows"][-1]["run_idx"] == 1
