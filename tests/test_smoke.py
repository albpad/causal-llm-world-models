from pathlib import Path

from causal_llm_eval.llm_query_runner import MODEL_REGISTRY, build_targeted_questions, load_battery
from causal_llm_eval.response_parser import extract_stances, detect_conditionality, detect_uncertainty


def test_registry_not_empty():
    assert len(MODEL_REGISTRY) >= 2
    assert all("model_id" in cfg for cfg in MODEL_REGISTRY.values())
    assert MODEL_REGISTRY["gemma-4-31b-it"]["model_id"] == "google/gemma-4-31B-it"


def test_battery_loads():
    battery = Path("data/vignettes/vignette_battery.json")
    items = load_battery(battery)
    assert len(items) == 88
    assert all("clinical_text" in item for item in items)


def test_targeted_questions():
    text = build_targeted_questions("glottic_cT3")
    assert "TLM" in text and "OPHL" in text


def test_stance_extraction_negation():
    text = "TLM is appropriate. CRT is appropriate. Total laryngectomy is not indicated."
    stances = {s["treatment"]: s["stance"] for s in extract_stances(text, "phase1")}
    assert stances.get("tlm") == "recommended"
    assert stances.get("concurrent_crt") == "recommended"
    assert stances.get("total_laryngectomy") == "excluded"


def test_conditionality_and_uncertainty():
    assert detect_conditionality("TLM is contraindicated but OPHL is appropriate in this context")
    assert detect_uncertainty("This is a grey zone case with no clear consensus")
