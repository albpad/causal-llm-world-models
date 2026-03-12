from causal_llm_eval.research_app import PRESETS, estimate_run_cost, serialize_enhanced_kg2


def test_presets_cover_notebook_variants():
    assert {"single-model", "full-study", "kimi-k25", "kimi-k25-thinking", "qwq32b"} <= set(PRESETS)


def test_estimate_run_cost_positive():
    assert estimate_run_cost(["llama-3.1-8b"], n_items=88, n_runs=30) > 0


def test_serialize_enhanced_kg2_removes_raw_jsd_values():
    from causal_llm_eval.kg2_enhanced import KG2Edge

    edge = KG2Edge(edge_id="S1", model="demo", detected=True, jsd_values=[0.1, 0.2])
    serial = serialize_enhanced_kg2({"demo": {"S1": edge}})
    assert "jsd_values" not in serial["demo"]["S1"]
    assert serial["demo"]["S1"]["detected"] is True
