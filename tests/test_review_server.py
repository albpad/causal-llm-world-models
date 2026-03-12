from pathlib import Path

from causal_llm_eval.review_server import ReviewRepository, normalise_status


def test_normalise_status_defaults_to_unreviewed():
    assert normalise_status("accepted") == "accepted"
    assert normalise_status("invalid") == "unreviewed"


def test_review_repository_discovers_datasets_and_builds_bundle(tmp_path):
    analysis_root = tmp_path / "analysis"
    raw_root = tmp_path / "raw"
    annotations_dir = tmp_path / "annotations"
    dataset_dir = analysis_root / "demo-model"
    raw_dataset_dir = raw_root / "demo-model"
    dataset_dir.mkdir(parents=True)
    raw_dataset_dir.mkdir(parents=True)

    battery_path = tmp_path / "battery.json"
    battery_path.write_text(
        """
        {
          "baselines": [{"id": "B1", "family": "demo", "clinical_text": "text", "question": "q", "expected_recommendations": ["tlm"], "expected_excluded": []}],
          "perturbations": [{"id": "P1", "baseline_id": "B1", "family": "demo", "clinical_text": "pert", "question": "q2", "expected_recommendations": [], "expected_excluded": ["tlm"], "edge_justification": ["S1"], "type": "flip"}]
        }
        """.strip()
    )
    (dataset_dir / "parsed.json").write_text(
        '[{"item_id":"B1","model_name":"demo-model","run_idx":0,"stances":[{"treatment":"tlm","stance":"recommended","confidence":0.9,"evidence":"ok","phase":"phase2"}],"conditionality":false,"uncertainty":false}]'
    )
    (dataset_dir / "edge_tests.json").write_text(
        '[{"pert_id":"P1","base_id":"B1","model":"demo-model","treatment":"tlm","edges":["S1"],"significant":true,"jsd":0.2,"base_rec_rate":1.0,"pert_rec_rate":0.0}]'
    )
    (dataset_dir / "metrics.json").write_text('{"demo-model":{"rec_accuracy":0.8,"exc_accuracy":0.9,"rec_precision":1.0,"cond_rate":0.4,"null_spec":0.7}}')
    (dataset_dir / "kg2.json").write_text('{"demo-model":{"S1":{"detected":true,"detection_rate":1.0}}}')
    (dataset_dir / "kg2_enhanced.json").write_text(
        '{"demo-model":{"S1":{"edge_id":"S1","model":"demo-model","detected":true,"soft_detected":true,"detection_rate":1.0,"n_probes":1,"direction_correct":true,"direction_rate":1.0,"mean_jsd":0.2,"median_jsd":0.2,"jsd_ci_lower":0.1,"jsd_ci_upper":0.3,"conditionality_tested":false,"conditionality_correct":null,"active_in_contexts":[],"expected_contexts":[],"omnibus_significant":true,"omnibus_p":0.01}}}'
    )
    (dataset_dir / "graph_comparison.json").write_text('{"demo-model":{"f1":0.9}}')
    (dataset_dir / "divergences.json").write_text('[]')
    (dataset_dir / "spurious_edges.json").write_text('{}')
    (raw_dataset_dir / "run_20260311_1000.jsonl").write_text(
        '{"item_id":"B1","model_name":"demo-model","run_idx":0,"phase1_response":"raw1","phase2_response":"raw2","item_type":"baseline"}\n'
    )
    world_model_path = tmp_path / "world_model.json"
    world_model_path.write_text('{"demo-model":{"wms":0.6,"coverage_score":0.5,"fidelity_score":0.7,"stability_score":0.4,"rigidity_penalty":0.1}}')

    repo = ReviewRepository(
        analysis_root=analysis_root,
        raw_root=raw_root,
        battery_path=battery_path,
        world_model_path=world_model_path,
        annotations_dir=annotations_dir,
    )
    datasets = repo.list_datasets()
    assert datasets[0]["name"] == "demo-model"
    bundle = repo.load_bundle("demo-model")
    assert bundle["dataset"]["n_cases"] == 2
    assert bundle["cases"][0]["item_id"] == "B1"
    assert bundle["edges"][0]["edge_id"] == "S1"
    assert bundle["world_model_metrics"]["demo-model"]["wms"] == 0.6
