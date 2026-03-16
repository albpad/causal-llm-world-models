from causal_llm_eval.vignette_generator import build_all_templates, generate_battery


def _lookup(battery):
    items = {}
    for row in battery["baselines"]:
        items[row["id"]] = row
    for row in battery["perturbations"]:
        items[row["id"]] = row
    return items


def test_null_controls_inherit_baseline_expectations():
    battery = generate_battery(build_all_templates())
    items = _lookup(battery)
    for item_id in ("A1-NULL", "B1-NULL2", "G1-NULL", "J1-NULL"):
        item = items[item_id]
        base = items[item["baseline_id"]]
        assert item["expected_recommendations"] == base["expected_recommendations"]
        assert item["expected_excluded"] == base["expected_excluded"]


def test_key_kg1_repairs_are_present():
    battery = generate_battery(build_all_templates())
    items = _lookup(battery)
    assert items["H1-P4"]["edge_justification"] == ["S129"]
    assert items["G1-ABS11"]["expected_recommendations"] == ["nonsurgical_lp", "rt_accelerated"]
    assert items["A1-P2"]["family"] == "glottic_cT3"
    assert items["A2-P3"]["family"] == "glottic_cT3"
    assert items["C1-P3"]["family"] == "glottic_cT3"
