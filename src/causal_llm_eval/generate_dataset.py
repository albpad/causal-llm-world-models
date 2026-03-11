#!/usr/bin/env python3
"""
Fine-Tuning Dataset Generator for Kimi K2.5 HNC Clinical Reasoning
===================================================================
Generates ~500 focused training examples targeting specific gaps:
  A. Missed edge correction (165)
  B. Phantom edge countermeasures (50)
  C. Null perturbation robustness (80)
  D. Exclusion bias correction (100)
  E. Direction error correction (80)
  F. Contrastive pairs (25)

Usage:
    python generate_dataset.py
    python generate_dataset.py --output synthetic_training_data.jsonl
"""

import json, random, copy
from pathlib import Path

from .causal_templates import (
    generate_gold_response, generate_null_response,
    generate_contrastive_response, determine_stance,
    FAMILY_TREATMENTS, TREATMENT_RULES, _parse_vars
)

from .llm_query_runner import (
    SYSTEM_PROMPT, OPEN_ENDED_TEMPLATE, TARGETED_TEMPLATE,
    TARGETED_QUESTIONS_BY_FAMILY, build_targeted_questions
)

from .paths import vignette_battery_path, ANALYSIS_DIR

BATTERY_PATH = vignette_battery_path()
KIMI_ANALYSIS = ANALYSIS_DIR / "kimi-k2.5"


def load_battery():
    with open(BATTERY_PATH) as f:
        bat = json.load(f)
    baselines = {b["id"]: b for b in bat["baselines"]}
    perturbations = {p["id"]: p for p in bat["perturbations"]}
    return baselines, perturbations, bat


def load_kimi_analysis():
    """Load Kimi's gap analysis data."""
    data = {}
    for fname in ["kg2_enhanced.json", "spurious_edges.json", "edge_tests.json",
                   "divergences.json", "metrics.json"]:
        p = KIMI_ANALYSIS / fname
        if p.exists():
            with open(p) as f:
                data[fname.replace(".json", "")] = json.load(f)
    return data


def format_example(clinical_text, question, gold_response, family, metadata=None):
    """Format a single training example in Together.ai JSONL format."""
    user_content = OPEN_ENDED_TEMPLATE.format(
        clinical_text=clinical_text.strip(),
        question=question.strip()
    )
    # Append Phase 2 questions to the user message for combined training
    phase2_qs = build_targeted_questions(family)
    user_content += "\n\nAdditionally, for each treatment option, provide a structured assessment using EXACTLY one of: APPROPRIATE / CONTRAINDICATED / RELATIVELY CONTRAINDICATED / UNCERTAIN.\n\n" + phase2_qs

    return {
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_content},
            {"role": "assistant", "content": gold_response},
        ],
        "metadata": metadata or {},
    }


# ── Variant generation helpers ────────────────────────────────────────────────

# Clinically neutral variations for augmentation
AGE_VARIANTS = [
    ("48-year-old", "male"), ("52-year-old", "male"), ("56-year-old", "female"),
    ("61-year-old", "male"), ("63-year-old", "female"), ("67-year-old", "male"),
    ("58-year-old", "male"), ("54-year-old", "female"), ("65-year-old", "male"),
]

COMORBIDITY_NEUTRAL = [
    "No significant comorbidities.",
    "Well-controlled hypertension on ACE inhibitor.",
    "Mild hypothyroidism on levothyroxine, otherwise healthy.",
    "History of appendectomy at age 30, no other medical history.",
    "Mild osteoarthritis, no other comorbidities.",
]

SMOKING_NEUTRAL = [
    "Former smoker (quit 5 years ago, 20 pack-year history).",
    "Non-smoker for 10 years (former 15 pack-year history).",
    "Former smoker (quit 8 years ago, 25 pack-years).",
    "Never smoker.",
    "Social smoker, minimal history (3 pack-years).",
]


def make_variant(clinical_text, variant_idx):
    """Create a variant of clinical text by substituting neutral demographics."""
    text = str(clinical_text)
    # These substitutions change only non-causal features
    if variant_idx < len(AGE_VARIANTS):
        age, gender = AGE_VARIANTS[variant_idx]
        # Replace the age/gender at start of clinical text
        import re
        text = re.sub(
            r'\d+-year-old (male|female)',
            f'{age} {gender}',
            text, count=1
        )
    if variant_idx < len(COMORBIDITY_NEUTRAL):
        # Add or replace comorbidity line (only if neutral)
        pass  # Keep original comorbidities to not change clinical meaning
    return text


# ── Dataset generation functions ──────────────────────────────────────────────

def generate_missed_edge_examples(baselines, perturbations, analysis):
    """
    A. Missed edge correction: For each of the 33 undetected edges,
    generate 5 training examples showing the correct stance shift.
    """
    examples = []
    kg2 = analysis.get("kg2_enhanced", {}).get("kimi-k2.5", {})

    # Find missed edges (not soft-detected)
    missed_edges = {eid: data for eid, data in kg2.items()
                    if not data.get("soft_detected", False)}

    # Map edges to perturbations that test them
    edge_to_perts = {}
    for pid, p in perturbations.items():
        edges = p.get("edge_justification", [])
        if isinstance(edges, str):
            edges = eval(edges)
        for e in edges:
            if e in missed_edges:
                if e not in edge_to_perts:
                    edge_to_perts[e] = []
                edge_to_perts[e].append(p)

    count = 0
    for edge_id, perts in edge_to_perts.items():
        for variant_idx in range(min(5, max(1, 5 // len(perts)))):
            for p in perts[:3]:  # Max 3 perturbations per edge
                clinical_text = make_variant(p["clinical_text"], variant_idx)
                gold = generate_gold_response(p)

                examples.append(format_example(
                    clinical_text=clinical_text,
                    question=p["question"],
                    gold_response=gold,
                    family=p["family"],
                    metadata={
                        "category": "missed_edge",
                        "edge_id": edge_id,
                        "pert_id": p["id"],
                        "variant": variant_idx,
                        "edge_jsd": missed_edges[edge_id].get("mean_jsd", 0),
                    }
                ))
                count += 1
                if count >= 165:
                    return examples

    # If we haven't reached 165, add more variants from high-priority missed edges
    priority_edges = sorted(missed_edges.keys(),
                            key=lambda e: missed_edges[e].get("mean_jsd", 0),
                            reverse=True)
    for edge_id in priority_edges:
        if count >= 165:
            break
        if edge_id in edge_to_perts:
            for p in edge_to_perts[edge_id]:
                for vi in range(5, 9):
                    clinical_text = make_variant(p["clinical_text"], vi % len(AGE_VARIANTS))
                    gold = generate_gold_response(p)
                    examples.append(format_example(
                        clinical_text=clinical_text,
                        question=p["question"],
                        gold_response=gold,
                        family=p["family"],
                        metadata={
                            "category": "missed_edge_priority",
                            "edge_id": edge_id,
                            "pert_id": p["id"],
                            "variant": vi,
                        }
                    ))
                    count += 1
                    if count >= 165:
                        break
                if count >= 165:
                    break

    return examples


def generate_phantom_countermeasures(baselines, perturbations, analysis):
    """
    B. Phantom edge countermeasures: For each of 10 phantom edges,
    generate 5 examples where the phantom treatment should NOT shift.
    """
    examples = []
    spur = analysis.get("spurious_edges", {})
    phantom_edges = spur.get("phantom_edges", [])

    for phantom in phantom_edges:
        pid = phantom.get("pert_id", "")
        treatment = phantom.get("treatment", "")

        p = perturbations.get(pid)
        if not p:
            continue

        base_id = p.get("baseline_id", "")
        base = baselines.get(base_id)
        if not base:
            continue

        for variant_idx in range(5):
            # Use the perturbation text but emphasize stability of phantom treatment
            clinical_text = make_variant(p["clinical_text"], variant_idx)

            # Generate response that explicitly keeps phantom treatment stable
            gold = generate_gold_response(p)
            # Add explicit phantom countermeasure note
            vc = p.get("variables_changed", [])
            if isinstance(vc, str):
                vc = eval(vc)
            change_desc = "; ".join(
                f"{c['variable']}: '{c['from']}' -> '{c['to']}'" for c in vc
            ) if vc else "clinical modification"

            gold += (
                f"\n\nIMPORTANT: The change ({change_desc}) affects the treatments "
                f"listed above but does NOT affect {treatment}. "
                f"The variable changed does not causally influence {treatment} eligibility."
            )

            examples.append(format_example(
                clinical_text=clinical_text,
                question=p["question"],
                gold_response=gold,
                family=p["family"],
                metadata={
                    "category": "phantom_countermeasure",
                    "pert_id": pid,
                    "phantom_treatment": treatment,
                    "phantom_jsd": phantom.get("jsd", 0),
                    "variant": variant_idx,
                }
            ))

    return examples[:50]


def generate_null_examples(baselines, perturbations, bat):
    """
    C. Null perturbation robustness: Generate examples emphasizing
    stability on null perturbations.
    """
    examples = []
    null_perts = [p for p in bat["perturbations"] if p.get("type") == "null"]

    for p in null_perts:
        base_id = p.get("baseline_id", "")
        base = baselines.get(base_id)
        if not base:
            continue

        vc = p.get("variables_changed", [])
        if isinstance(vc, str):
            vc = eval(vc)
        change_desc = "; ".join(
            f"{c['variable']}: '{c['from']}' -> '{c['to']}'" for c in vc
        ) if vc else "minor modification"

        for variant_idx in range(7):  # ~7 variants per null = ~84 total
            clinical_text = make_variant(p["clinical_text"], variant_idx % len(AGE_VARIANTS))
            gold = generate_null_response(p, base, vc, change_desc)

            examples.append(format_example(
                clinical_text=clinical_text,
                question=p["question"],
                gold_response=gold,
                family=p["family"],
                metadata={
                    "category": "null_robustness",
                    "pert_id": p["id"],
                    "base_id": base_id,
                    "change_desc": change_desc,
                    "variant": variant_idx,
                }
            ))

    return examples[:80]


def generate_exclusion_bias_correction(baselines, perturbations, analysis):
    """
    D. Exclusion bias correction: Generate positive recommendation examples
    to counteract Kimi's tendency to over-exclude.
    """
    examples = []

    # Find items where expected_recommendations has multiple treatments
    # (these are cases where the model should say YES to several options)
    all_items = list(baselines.values()) + list(perturbations.values())

    # Prioritize items with many recommended treatments
    rich_rec_items = []
    for item in all_items:
        rec = item.get("expected_recommendations", [])
        if isinstance(rec, str):
            rec = eval(rec)
        if len(rec) >= 2:
            rich_rec_items.append((item, len(rec)))

    rich_rec_items.sort(key=lambda x: x[1], reverse=True)

    count = 0
    for item, n_rec in rich_rec_items:
        for variant_idx in range(5):
            clinical_text = make_variant(item["clinical_text"], variant_idx % len(AGE_VARIANTS))
            gold = generate_gold_response(item)

            examples.append(format_example(
                clinical_text=clinical_text,
                question=item["question"],
                gold_response=gold,
                family=item["family"],
                metadata={
                    "category": "exclusion_bias_correction",
                    "item_id": item["id"],
                    "n_recommended": n_rec,
                    "variant": variant_idx,
                }
            ))
            count += 1
            if count >= 100:
                return examples

    return examples


def generate_direction_corrections(baselines, perturbations, analysis):
    """
    E. Direction error correction: For each of the ~16 wrong-direction edges,
    generate examples with explicit directional reasoning.
    """
    examples = []
    kg2 = analysis.get("kg2_enhanced", {}).get("kimi-k2.5", {})

    # Find edges with direction_correct=False or direction_rate < 0.5
    wrong_dir_edges = {eid: data for eid, data in kg2.items()
                       if data.get("direction_rate", 1.0) < 0.5}

    # Map to perturbations
    edge_to_perts = {}
    for pid, p in perturbations.items():
        edges = p.get("edge_justification", [])
        if isinstance(edges, str):
            edges = eval(edges)
        for e in edges:
            if e in wrong_dir_edges:
                if e not in edge_to_perts:
                    edge_to_perts[e] = []
                edge_to_perts[e].append(p)

    count = 0
    for edge_id, perts in edge_to_perts.items():
        for p in perts[:2]:
            base_id = p.get("baseline_id", "")
            base = baselines.get(base_id)
            if not base:
                continue

            vc = p.get("variables_changed", [])
            if isinstance(vc, str):
                vc = eval(vc)

            for variant_idx in range(5):
                clinical_text = make_variant(p["clinical_text"], variant_idx % len(AGE_VARIANTS))
                gold = generate_gold_response(p)

                # Add explicit directionality teaching
                if vc:
                    change_desc = f"{vc[0]['variable']}: '{vc[0]['from']}' -> '{vc[0]['to']}'"
                    gold += (
                        f"\n\n**Directional note**: When {change_desc}, "
                        f"the expected direction of change for affected treatments is as follows: "
                    )
                    rec_base = base.get("expected_recommendations", [])
                    rec_pert = p.get("expected_recommendations", [])
                    exc_pert = p.get("expected_excluded", [])
                    if isinstance(rec_base, str): rec_base = eval(rec_base)
                    if isinstance(rec_pert, str): rec_pert = eval(rec_pert)
                    if isinstance(exc_pert, str): exc_pert = eval(exc_pert)

                    # Treatments that went from rec -> exc
                    lost = [t for t in rec_base if t in exc_pert]
                    gained = [t for t in rec_pert if t not in rec_base]
                    if lost:
                        gold += f"Treatments becoming CONTRAINDICATED: {', '.join(lost)}. "
                    if gained:
                        gold += f"Treatments becoming newly APPROPRIATE: {', '.join(gained)}. "

                examples.append(format_example(
                    clinical_text=clinical_text,
                    question=p["question"],
                    gold_response=gold,
                    family=p["family"],
                    metadata={
                        "category": "direction_correction",
                        "edge_id": edge_id,
                        "pert_id": p["id"],
                        "direction_rate": wrong_dir_edges[edge_id].get("direction_rate", 0),
                        "variant": variant_idx,
                    }
                ))
                count += 1
                if count >= 80:
                    return examples

    return examples


def generate_contrastive_pairs(baselines, perturbations):
    """
    F. Contrastive pairs: Compare base vs perturbation cases side-by-side.
    """
    examples = []

    # Select diverse perturbations across families
    families_seen = set()
    selected = []
    for pid, p in perturbations.items():
        if p.get("type") in ("flip", "escalate"):
            fam = p["family"]
            if fam not in families_seen or len(selected) < 25:
                selected.append(p)
                families_seen.add(fam)
        if len(selected) >= 25:
            break

    for p in selected:
        base_id = p.get("baseline_id", "")
        base = baselines.get(base_id)
        if not base:
            continue

        vc = p.get("variables_changed", [])
        if isinstance(vc, str):
            vc = eval(vc)

        # Build contrastive prompt
        contrastive_prompt = (
            f"Compare the following two cases. The ONLY difference is noted below.\n\n"
            f"**CASE A (Baseline)**:\n{base['clinical_text'].strip()}\n\n"
            f"**CASE B (Modified)**:\n{p['clinical_text'].strip()}\n\n"
            f"**Variable changed**: {'; '.join(f\"{c['variable']}: '{c['from']}' -> '{c['to']}'\" for c in vc)}\n\n"
            f"For each treatment option, explain whether the variable change should alter "
            f"the recommendation and WHY (causal mechanism)."
        )

        gold = generate_contrastive_response(base, p, vc)

        examples.append({
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": contrastive_prompt},
                {"role": "assistant", "content": gold},
            ],
            "metadata": {
                "category": "contrastive_pair",
                "base_id": base_id,
                "pert_id": p["id"],
                "family": p["family"],
                "type": p.get("type"),
            }
        })

    return examples[:25]


# ── Main generation pipeline ──────────────────────────────────────────────────

def generate_full_dataset(output_path=None):
    """Generate the complete ~500 example fine-tuning dataset."""
    baselines, perturbations, bat = load_battery()
    analysis = load_kimi_analysis()

    print("Generating fine-tuning dataset...")
    print(f"  Battery: {len(baselines)} baselines, {len(perturbations)} perturbations")

    # Generate each category
    print("\n[A] Missed edge correction...")
    missed = generate_missed_edge_examples(baselines, perturbations, analysis)
    print(f"    Generated {len(missed)} examples")

    print("[B] Phantom edge countermeasures...")
    phantom = generate_phantom_countermeasures(baselines, perturbations, analysis)
    print(f"    Generated {len(phantom)} examples")

    print("[C] Null perturbation robustness...")
    nulls = generate_null_examples(baselines, perturbations, bat)
    print(f"    Generated {len(nulls)} examples")

    print("[D] Exclusion bias correction...")
    bias = generate_exclusion_bias_correction(baselines, perturbations, analysis)
    print(f"    Generated {len(bias)} examples")

    print("[E] Direction error correction...")
    direction = generate_direction_corrections(baselines, perturbations, analysis)
    print(f"    Generated {len(direction)} examples")

    print("[F] Contrastive pairs...")
    contrastive = generate_contrastive_pairs(baselines, perturbations)
    print(f"    Generated {len(contrastive)} examples")

    # Combine all
    all_examples = missed + phantom + nulls + bias + direction + contrastive
    random.shuffle(all_examples)

    print(f"\n{'='*50}")
    print(f"TOTAL: {len(all_examples)} training examples")
    print(f"{'='*50}")

    # Category breakdown
    cats = {}
    for ex in all_examples:
        cat = ex.get("metadata", {}).get("category", "unknown")
        cats[cat] = cats.get(cat, 0) + 1
    for cat, n in sorted(cats.items()):
        print(f"  {cat}: {n}")

    # Token estimate
    total_chars = sum(
        sum(len(m["content"]) for m in ex["messages"])
        for ex in all_examples
    )
    est_tokens = total_chars / 4  # rough estimate
    print(f"\nEstimated total tokens: ~{est_tokens:,.0f}")
    print(f"Estimated cost (3 epochs, $0.50/M tokens): ~${est_tokens * 3 / 1_000_000 * 0.50:.2f}")

    # Save
    if output_path is None:
        output_path = Path(__file__).parent / "synthetic_training_data.jsonl"
    else:
        output_path = Path(output_path)

    with open(output_path, "w") as f:
        for ex in all_examples:
            # Strip metadata for Together.ai format (keep only messages)
            together_ex = {"messages": ex["messages"]}
            f.write(json.dumps(together_ex) + "\n")

    # Also save with metadata for analysis
    meta_path = output_path.with_suffix(".meta.jsonl")
    with open(meta_path, "w") as f:
        for ex in all_examples:
            f.write(json.dumps(ex) + "\n")

    print(f"\nSaved: {output_path}")
    print(f"Saved (with metadata): {meta_path}")

    return all_examples


if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--output", default=None)
    args = p.parse_args()
    generate_full_dataset(args.output)
