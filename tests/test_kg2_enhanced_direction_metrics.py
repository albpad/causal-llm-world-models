from causal_llm_eval.kg2_enhanced import KG2Edge, compute_graph_comparison


def test_graph_comparison_uses_soft_direction_accuracy_as_primary_metric():
    kg2 = {
        "demo-model": {
            "E1": KG2Edge(
                edge_id="E1",
                model="demo-model",
                detected=False,
                soft_detected=True,
                direction_correct=True,
                direction_rate=0.8,
            ),
            "E2": KG2Edge(
                edge_id="E2",
                model="demo-model",
                detected=True,
                soft_detected=True,
                direction_correct=False,
                direction_rate=0.0,
            ),
            "E3": KG2Edge(
                edge_id="E3",
                model="demo-model",
                detected=False,
                soft_detected=False,
                direction_correct=None,
                direction_rate=0.0,
            ),
        }
    }

    comp = compute_graph_comparison(kg2)["demo-model"]
    assert comp.direction_accuracy == 0.5
    assert comp.hard_direction_accuracy == 0.0
    assert round(comp.mean_direction_rate, 3) == 0.4


def test_graph_comparison_exposes_soft_precision_and_fdr():
    kg2 = {
        "demo-model": {
            "E1": KG2Edge(edge_id="E1", model="demo-model", detected=True, soft_detected=True, direction_correct=True),
            "E2": KG2Edge(edge_id="E2", model="demo-model", detected=False, soft_detected=True, direction_correct=False),
        }
    }
    spurious = {
        "phantom_edges": [
            {"model": "demo-model", "pert_id": "P1", "treatment": "foo"},
            {"model": "demo-model", "pert_id": "P2", "treatment": "bar"},
        ],
        "null_jsd_by_model": {"demo-model": [0.1, 0.2]},
    }

    comp = compute_graph_comparison(kg2, spurious_data=spurious)["demo-model"]
    assert comp.soft_true_positives == 2
    assert comp.soft_false_positives == 2
    assert comp.soft_precision == 0.5
    assert comp.soft_fdr == 0.5
    assert comp.hard_precision == comp.precision
