#!/usr/bin/env python3
"""Layered validation program for the response parser."""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

try:
    from .causal_templates import generate_gold_response
    from .json_utils import dump_json
    from .label_space import AGGREGATE_LABELS, derive_aggregate_labels, normalise_expected_label_lists
    from .llm_query_runner import TARGETED_QUESTIONS_BY_FAMILY
    from .response_parser import TREATMENT_ALIASES, parse_result
except ImportError:
    from causal_templates import generate_gold_response
    from json_utils import dump_json
    from label_space import AGGREGATE_LABELS, derive_aggregate_labels, normalise_expected_label_lists
    from llm_query_runner import TARGETED_QUESTIONS_BY_FAMILY
    from response_parser import TREATMENT_ALIASES, parse_result

LABELS = ("recommended", "excluded", "relative_ci", "uncertain")
MISMATCH_CAUSES = (
    "not_in_query_space",
    "aggregate_label_mismatch",
    "model_omission",
    "candidate_parser_miss",
    "model_stance_disagreement",
)

CANONICAL_TREATMENT_NAMES = {
    "tlm": "Transoral laser microsurgery (TLM)",
    "tors": "Transoral robotic surgery (TORS)",
    "ophl_type_i": "OPHL type I",
    "ophl_type_ii": "OPHL type II",
    "ophl_type_iib": "OPHL type IIB",
    "ophl_type_iii": "OPHL type III",
    "ophl_any": "Open partial horizontal laryngectomy (OPHL)",
    "total_laryngectomy": "Total laryngectomy",
    "concurrent_crt": "Concurrent chemoradiotherapy (CRT)",
    "ict_rt": "Induction chemotherapy followed by response-adapted treatment",
    "rt_alone": "Radiotherapy alone",
    "rt_accelerated": "Accelerated or hyperfractionated radiotherapy",
    "cisplatin_high_dose": "High-dose cisplatin",
    "cetuximab_concurrent": "Cetuximab concurrent with radiotherapy",
    "carboplatin_5fu": "Carboplatin + 5-FU concurrent with radiotherapy",
    "nonsurgical_lp": "Non-surgical larynx preservation",
    "surgical_lp": "Surgical larynx preservation",
}

STRUCTURED_LABEL_MAP = {
    "recommended": "APPROPRIATE",
    "excluded": "CONTRAINDICATED",
    "relative_ci": "RELATIVELY CONTRAINDICATED",
    "uncertain": "UNCERTAIN",
}

COMPILED_ALIASES = {
    treatment: [re.compile(pattern, re.I) for pattern in patterns]
    for treatment, patterns in TREATMENT_ALIASES.items()
}


def load_json(path: str | Path, default):
    path = Path(path)
    if not path.exists():
        return default
    with open(path) as f:
        return json.load(f)


def load_results(path: str | Path) -> list[dict]:
    rows = []
    with open(path) as f:
        for line in f:
            if not line.strip():
                continue
            rows.append(json.loads(line))
    return rows


def load_battery_map(path: str | Path) -> dict[str, dict]:
    battery = load_json(path, {})
    items = {}
    for row in battery.get("baselines", []):
        items[row["id"]] = row
    for row in battery.get("perturbations", []):
        items[row["id"]] = row
    return items


def ordered_battery_items(path: str | Path) -> list[dict]:
    battery = load_json(path, {})
    return list(battery.get("baselines", [])) + list(battery.get("perturbations", []))


def annotation_gold(annotation: dict | None) -> dict[str, str]:
    if not annotation:
        return {}
    parser_validation = annotation.get("parser_validation") or {}
    gold = {}
    for tx in parser_validation.get("recommended", []):
        gold[str(tx)] = "recommended"
    for tx in parser_validation.get("excluded", []):
        gold[str(tx)] = "excluded"
    for tx in parser_validation.get("relative_ci", []):
        gold[str(tx)] = "relative_ci"
    for tx in parser_validation.get("uncertain", []):
        gold[str(tx)] = "uncertain"
    return derive_aggregate_labels(gold)


def battery_gold(item: dict | None) -> dict[str, str]:
    if not item:
        return {}
    rec, exc = normalise_expected_label_lists(
        item.get("expected_recommendations", []),
        item.get("expected_excluded", []),
    )
    gold = {}
    for tx in rec:
        gold[str(tx)] = "recommended"
    for tx in exc:
        gold[str(tx)] = "excluded"
    return derive_aggregate_labels(gold)


def choose_gold(item: dict | None, annotation: dict | None) -> tuple[dict[str, str], str]:
    annotated = annotation_gold(annotation)
    if annotated:
        return annotated, "clinician_annotation"
    return battery_gold(item), "battery_expectation"


def stance_map(parsed_row: dict | None) -> dict[str, str]:
    if not parsed_row:
        return {}
    return derive_aggregate_labels(
        {stance["treatment"]: stance["stance"] for stance in parsed_row.get("stances", [])}
    )


def evaluate_predictions(
    predicted: dict[str, str],
    gold: dict[str, str],
    item_id: str,
    model_name: str,
    run_idx: int | str,
) -> dict:
    compare_set = sorted(set(predicted) | set(gold))
    per_treatment = []
    label_counts = {label: {"tp": 0, "fp": 0, "fn": 0} for label in LABELS}
    matches = 0

    for treatment in compare_set:
        pred_label = predicted.get(treatment, "absent")
        gold_label = gold.get(treatment, "absent")
        matched = pred_label == gold_label
        matches += int(matched)
        per_treatment.append(
            {
                "item_id": item_id,
                "model_name": model_name,
                "run_idx": run_idx,
                "treatment": treatment,
                "predicted": pred_label,
                "gold": gold_label,
                "matched": matched,
            }
        )
        for label in LABELS:
            if pred_label == label and gold_label == label:
                label_counts[label]["tp"] += 1
            elif pred_label == label and gold_label != label:
                label_counts[label]["fp"] += 1
            elif pred_label != label and gold_label == label:
                label_counts[label]["fn"] += 1

    exact_match = bool(compare_set) and matches == len(compare_set)
    return {
        "per_treatment": per_treatment,
        "label_counts": label_counts,
        "exact_match": exact_match,
        "n_compared": len(compare_set),
    }


def evaluate_gold_targets_only(
    predicted: dict[str, str],
    gold: dict[str, str],
    item_id: str,
    model_name: str,
    run_idx: int | str,
) -> dict:
    compare_set = sorted(gold)
    per_treatment = []
    label_counts = {label: {"tp": 0, "fp": 0, "fn": 0} for label in LABELS}
    matches = 0

    for treatment in compare_set:
        pred_label = predicted.get(treatment, "absent")
        gold_label = gold[treatment]
        matched = pred_label == gold_label
        matches += int(matched)
        per_treatment.append(
            {
                "item_id": item_id,
                "model_name": model_name,
                "run_idx": run_idx,
                "treatment": treatment,
                "predicted": pred_label,
                "gold": gold_label,
                "matched": matched,
            }
        )
        for label in LABELS:
            if pred_label == label and gold_label == label:
                label_counts[label]["tp"] += 1
            elif pred_label != label and gold_label == label:
                label_counts[label]["fn"] += 1
            elif pred_label == label and gold_label != label:
                label_counts[label]["fp"] += 1

    return {
        "per_treatment": per_treatment,
        "label_counts": label_counts,
        "exact_match": bool(compare_set) and matches == len(compare_set),
        "n_compared": len(compare_set),
    }


def merge_label_counts(target: dict, update: dict) -> None:
    for label in LABELS:
        for key in ("tp", "fp", "fn"):
            target[label][key] += update[label][key]


def summarise_label_counts(label_counts: dict) -> dict:
    out = {}
    for label, counts in label_counts.items():
        tp = counts["tp"]
        fp = counts["fp"]
        fn = counts["fn"]
        precision = tp / (tp + fp) if tp + fp else None
        recall = tp / (tp + fn) if tp + fn else None
        f1 = (
            2 * precision * recall / (precision + recall)
            if precision is not None and recall is not None and precision + recall
            else None
        )
        out[label] = {
            **counts,
            "precision": precision,
            "recall": recall,
            "f1": f1,
        }
    return out


def build_consensus(rows: list[dict]) -> dict[str, str]:
    votes = defaultdict(Counter)
    for row in rows:
        for treatment, label in row["predicted"].items():
            votes[treatment][label] += 1
    return {treatment: counts.most_common(1)[0][0] for treatment, counts in votes.items()}


def treatment_is_mentioned(text: str, treatment: str) -> bool:
    return any(pattern.search(text) for pattern in COMPILED_ALIASES.get(treatment, []))


def query_space_for_family(family: str) -> set[str]:
    questions = "\n".join(TARGETED_QUESTIONS_BY_FAMILY.get(family, []))
    return {
        treatment
        for treatment, patterns in COMPILED_ALIASES.items()
        if any(pattern.search(questions) for pattern in patterns)
    }


def classify_real_output_mismatch(row: dict, treatment: str, predicted: str, family: str) -> str:
    if treatment in AGGREGATE_LABELS:
        return "aggregate_label_mismatch"
    text = f"{row.get('phase1_response', '')}\n{row.get('phase2_response', '')}"
    in_query_space = treatment in query_space_for_family(family)
    mentioned = treatment_is_mentioned(text, treatment)
    if not in_query_space and not mentioned:
        return "not_in_query_space"
    if predicted == "absent":
        return "candidate_parser_miss" if mentioned else "model_omission"
    return "model_stance_disagreement"


def summarise_eval_records(records: list[dict], label_counts: dict) -> dict:
    exact_matches = sum(1 for record in records if record["exact_match"])
    return {
        "n_rows": len(records),
        "exact_match_rate": exact_matches / len(records) if records else None,
        "label_metrics": summarise_label_counts(label_counts),
    }


def validate_gold_templates(items: list[dict], max_examples: int = 10) -> dict:
    records = []
    label_counts = {label: {"tp": 0, "fp": 0, "fn": 0} for label in LABELS}
    examples = []
    for item in items:
        row = {
            "item_id": item["id"],
            "model_name": "gold-template",
            "run_idx": 0,
            "error": None,
            "phase1_response": generate_gold_response(item, family=item.get("family")),
            "phase2_response": "",
        }
        parsed = parse_result(row)
        predicted = stance_map(parsed)
        gold = battery_gold(item)
        evaluation = evaluate_gold_targets_only(predicted, gold, item["id"], "gold-template", 0)
        merge_label_counts(label_counts, evaluation["label_counts"])
        records.append({"item_id": item["id"], "predicted": predicted, "gold": gold, "exact_match": evaluation["exact_match"]})
        for mismatch in evaluation["per_treatment"]:
            if mismatch["matched"] or len(examples) >= max_examples:
                continue
            examples.append(mismatch)
    return {
        "summary": summarise_eval_records(records, label_counts),
        "examples": examples,
    }


def validate_structured_snippets(max_examples: int = 10) -> dict:
    records = []
    label_counts = {label: {"tp": 0, "fp": 0, "fn": 0} for label in LABELS}
    examples = []
    for treatment, display_name in CANONICAL_TREATMENT_NAMES.items():
        for label, structured in STRUCTURED_LABEL_MAP.items():
            row = {
                "item_id": f"structured-{treatment}-{label}",
                "model_name": "structured-snippet",
                "run_idx": 0,
                "error": None,
                "phase1_response": "",
                "phase2_response": f"**{display_name}**: {structured}\nReasoning: Validation snippet.",
            }
            parsed = parse_result(row)
            predicted = stance_map(parsed)
            gold = derive_aggregate_labels({treatment: label})
            evaluation = evaluate_gold_targets_only(predicted, gold, row["item_id"], row["model_name"], 0)
            merge_label_counts(label_counts, evaluation["label_counts"])
            records.append({"item_id": row["item_id"], "predicted": predicted, "gold": gold, "exact_match": evaluation["exact_match"]})
            for mismatch in evaluation["per_treatment"]:
                if mismatch["matched"] or len(examples) >= max_examples:
                    continue
                examples.append(mismatch)
    return {
        "summary": summarise_eval_records(records, label_counts),
        "examples": examples,
    }


def validate_parser(
    results_path: str | Path,
    battery_path: str | Path,
    annotations_path: str | Path | None = None,
    model_filter: str | None = None,
    max_examples: int = 25,
) -> dict:
    battery_items = load_battery_map(battery_path)
    annotations = load_json(annotations_path, {"cases": {}}) if annotations_path else {"cases": {}}
    rows = load_results(results_path)
    if model_filter:
        rows = [row for row in rows if row.get("model_name") == model_filter]

    parsed_rows = []
    row_label_counts = {label: {"tp": 0, "fp": 0, "fn": 0} for label in LABELS}
    consensus_label_counts = {label: {"tp": 0, "fp": 0, "fn": 0} for label in LABELS}
    row_examples = []
    grouped = defaultdict(list)
    source_counts = Counter()
    completeness = Counter()
    mismatch_cause_counts = Counter()
    mismatch_cause_by_treatment = defaultdict(Counter)
    mismatch_cause_examples = defaultdict(list)

    for row in rows:
        parsed = parse_result(row)
        item_id = row["item_id"]
        model_name = row.get("model_name", "")
        run_idx = row.get("run_idx", "")
        item = battery_items.get(item_id)
        annotation = annotations.get("cases", {}).get(item_id, {})
        gold, source = choose_gold(item, annotation)
        source_counts[source] += 1

        completeness["rows"] += 1
        if row.get("error"):
            completeness["error_rows"] += 1
        if not (row.get("phase1_response") or "").strip():
            completeness["blank_phase1"] += 1
        if not (row.get("phase2_response") or "").strip():
            completeness["blank_phase2"] += 1

        predicted = stance_map(parsed)
        if not parsed:
            completeness["unparsed_rows"] += 1
        else:
            completeness["parsed_rows"] += 1
            if not predicted:
                completeness["zero_stance_rows"] += 1

        evaluation = evaluate_predictions(predicted, gold, item_id, model_name, run_idx)
        merge_label_counts(row_label_counts, evaluation["label_counts"])
        if evaluation["exact_match"]:
            completeness["row_exact_matches"] += 1

        row_payload = {
            "item_id": item_id,
            "model_name": model_name,
            "run_idx": run_idx,
            "gold_source": source,
            "gold": gold,
            "predicted": predicted,
            "exact_match": evaluation["exact_match"],
            "n_compared": evaluation["n_compared"],
            "family": item.get("family", "") if item else "",
        }
        parsed_rows.append(row_payload)
        grouped[(item_id, model_name)].append(row_payload)

        for mismatch in evaluation["per_treatment"]:
            if mismatch["matched"]:
                continue
            cause = classify_real_output_mismatch(
                row=row,
                treatment=mismatch["treatment"],
                predicted=mismatch["predicted"],
                family=row_payload["family"],
            )
            mismatch_cause_counts[cause] += 1
            mismatch_cause_by_treatment[mismatch["treatment"]][cause] += 1
            if len(mismatch_cause_examples[cause]) < max_examples:
                mismatch_cause_examples[cause].append(
                    {
                        **mismatch,
                        "item_id": item_id,
                        "model_name": model_name,
                        "run_idx": run_idx,
                        "phase1_preview": (row.get("phase1_response") or "")[:220],
                        "phase2_preview": (row.get("phase2_response") or "")[:220],
                    }
                )
            if len(row_examples) < max_examples:
                row_examples.append(
                    {
                        **mismatch,
                        "mismatch_cause": cause,
                        "phase1_preview": (row.get("phase1_response") or "")[:220],
                        "phase2_preview": (row.get("phase2_response") or "")[:220],
                    }
                )

    consensus_rows = []
    for (item_id, model_name), group in grouped.items():
        annotation = annotations.get("cases", {}).get(item_id, {})
        gold, source = choose_gold(battery_items.get(item_id), annotation)
        consensus_pred = build_consensus(group)
        evaluation = evaluate_predictions(consensus_pred, gold, item_id, model_name, "consensus")
        merge_label_counts(consensus_label_counts, evaluation["label_counts"])
        consensus_rows.append(
            {
                "item_id": item_id,
                "model_name": model_name,
                "gold_source": source,
                "gold": gold,
                "predicted": consensus_pred,
                "exact_match": evaluation["exact_match"],
                "n_compared": evaluation["n_compared"],
                "n_runs": len(group),
            }
        )
        if evaluation["exact_match"]:
            completeness["consensus_exact_matches"] += 1

    by_treatment = defaultdict(lambda: {"n": 0, "correct": 0, "errors": Counter()})
    for row in parsed_rows:
        compare_set = set(row["gold"]) | set(row["predicted"])
        for treatment in compare_set:
            gold_label = row["gold"].get(treatment, "absent")
            pred_label = row["predicted"].get(treatment, "absent")
            by_treatment[treatment]["n"] += 1
            if gold_label == pred_label:
                by_treatment[treatment]["correct"] += 1
            else:
                by_treatment[treatment]["errors"][f"{gold_label}->{pred_label}"] += 1

    by_treatment_summary = {}
    for treatment, stats in sorted(by_treatment.items()):
        by_treatment_summary[treatment] = {
            "n": stats["n"],
            "accuracy": stats["correct"] / stats["n"] if stats["n"] else None,
            "top_errors": stats["errors"].most_common(5),
            "mismatch_causes": dict(mismatch_cause_by_treatment.get(treatment, {})),
        }

    battery_items_ordered = ordered_battery_items(battery_path)
    gold_template_validation = validate_gold_templates(battery_items_ordered, max_examples=max_examples)
    structured_snippet_validation = validate_structured_snippets(max_examples=max_examples)

    summary = {
        "results_file": str(results_path),
        "battery_file": str(battery_path),
        "annotations_file": str(annotations_path) if annotations_path else None,
        "model_filter": model_filter,
        "battery_alignment": summarise_eval_records(parsed_rows, row_label_counts),
        "consensus_alignment": summarise_eval_records(consensus_rows, consensus_label_counts),
        "gold_template_validation": gold_template_validation,
        "structured_snippet_validation": structured_snippet_validation,
        "real_output_audit": {
            "mismatch_cause_counts": dict(mismatch_cause_counts),
            "mismatch_cause_examples": dict(mismatch_cause_examples),
        },
        "completeness": {
            "rows": completeness["rows"],
            "parsed_rows": completeness["parsed_rows"],
            "unparsed_rows": completeness["unparsed_rows"],
            "blank_phase1": completeness["blank_phase1"],
            "blank_phase2": completeness["blank_phase2"],
            "zero_stance_rows": completeness["zero_stance_rows"],
            "error_rows": completeness["error_rows"],
        },
        "gold_sources": dict(source_counts),
        "examples": row_examples,
        "by_treatment": by_treatment_summary,
        "consensus_rows": consensus_rows,
    }
    return summary


def write_report(summary: dict, output_dir: str | Path) -> None:
    outdir = Path(output_dir)
    outdir.mkdir(parents=True, exist_ok=True)

    dump_json(outdir / "parser_validation_summary.json", summary)
    dump_json(outdir / "parser_validation_examples.json", summary["examples"])

    lines = []
    lines.append("# Parser Validation Report\n")
    lines.append("## Overview")
    lines.append(f"- Results file: `{summary['results_file']}`")
    lines.append(f"- Battery file: `{summary['battery_file']}`")
    lines.append(f"- Annotations file: `{summary['annotations_file'] or 'none'}`")
    if summary["model_filter"]:
        lines.append(f"- Model filter: `{summary['model_filter']}`")
    lines.append("")

    lines.append("## 1. Battery Alignment on Real Model Outputs")
    lines.append("This section is **not** pure parser accuracy. It measures alignment between parsed model outputs and battery expectations, so disagreement can come from query-space gaps, model omissions, or true parser misses.")
    bal = summary["battery_alignment"]
    lines.append(f"- Rows evaluated: `{bal['n_rows']}`")
    erm = bal["exact_match_rate"]
    lines.append(f"- Exact match rate: `{erm:.1%}`" if erm is not None else "- Exact match rate: `n/a`")
    for label, metrics in bal["label_metrics"].items():
        p = metrics["precision"]
        r = metrics["recall"]
        f1 = metrics["f1"]
        lines.append(
            f"- `{label}`: precision `{p:.1%}` recall `{r:.1%}` f1 `{f1:.1%}`"
            if None not in (p, r, f1)
            else f"- `{label}`: insufficient support"
        )
    lines.append("")

    lines.append("## 2. Consensus Alignment Across Runs")
    cal = summary["consensus_alignment"]
    lines.append(f"- Case/model groups: `{cal['n_rows']}`")
    cem = cal["exact_match_rate"]
    lines.append(f"- Exact match rate: `{cem:.1%}`" if cem is not None else "- Exact match rate: `n/a`")
    for label, metrics in cal["label_metrics"].items():
        p = metrics["precision"]
        r = metrics["recall"]
        f1 = metrics["f1"]
        lines.append(
            f"- `{label}`: precision `{p:.1%}` recall `{r:.1%}` f1 `{f1:.1%}`"
            if None not in (p, r, f1)
            else f"- `{label}`: insufficient support"
        )
    lines.append("")

    lines.append("## 3. Deterministic Gold-Template Validation")
    gtv = summary["gold_template_validation"]["summary"]
    lines.append(f"- Cases evaluated: `{gtv['n_rows']}`")
    gem = gtv["exact_match_rate"]
    lines.append(f"- Exact match rate: `{gem:.1%}`" if gem is not None else "- Exact match rate: `n/a`")
    for label, metrics in gtv["label_metrics"].items():
        p = metrics["precision"]
        r = metrics["recall"]
        f1 = metrics["f1"]
        lines.append(
            f"- `{label}`: precision `{p:.1%}` recall `{r:.1%}` f1 `{f1:.1%}`"
            if None not in (p, r, f1)
            else f"- `{label}`: insufficient support"
        )
    lines.append("")

    lines.append("## 4. Structured Label Validation")
    ssv = summary["structured_snippet_validation"]["summary"]
    lines.append(f"- Snippets evaluated: `{ssv['n_rows']}`")
    sem = ssv["exact_match_rate"]
    lines.append(f"- Exact match rate: `{sem:.1%}`" if sem is not None else "- Exact match rate: `n/a`")
    for label, metrics in ssv["label_metrics"].items():
        p = metrics["precision"]
        r = metrics["recall"]
        f1 = metrics["f1"]
        lines.append(
            f"- `{label}`: precision `{p:.1%}` recall `{r:.1%}` f1 `{f1:.1%}`"
            if None not in (p, r, f1)
            else f"- `{label}`: insufficient support"
        )
    lines.append("")

    lines.append("## 5. Real-Output Mismatch Audit")
    lines.append("These counts separate benchmark/query issues from model behavior and candidate parser misses.")
    for cause in MISMATCH_CAUSES:
        lines.append(f"- `{cause}`: `{summary['real_output_audit']['mismatch_cause_counts'].get(cause, 0)}`")
    lines.append("")

    lines.append("## 6. Completeness")
    for key, value in summary["completeness"].items():
        lines.append(f"- `{key}`: `{value}`")
    lines.append("")

    lines.append("## 7. Gold Sources")
    for source, count in sorted(summary["gold_sources"].items()):
        lines.append(f"- `{source}`: `{count}` rows")
    lines.append("")

    lines.append("## 8. Frequent Treatment-Level Error Clusters")
    for treatment, stats in sorted(summary["by_treatment"].items(), key=lambda item: (item[1]["accuracy"] or 0, item[0]))[:10]:
        acc = stats["accuracy"]
        top_error = ", ".join(f"{label} x{count}" for label, count in stats["top_errors"]) or "none"
        cause_mix = ", ".join(f"{label} x{count}" for label, count in sorted(stats["mismatch_causes"].items())) or "none"
        lines.append(f"- `{treatment}`: accuracy `{acc:.1%}`; top errors `{top_error}`; cause mix `{cause_mix}`")
    lines.append("")

    lines.append("## 9. Example Real-Output Mismatches")
    for example in summary["examples"][:15]:
        lines.append(
            f"- `{example['item_id']}` / `{example['model_name']}` / `{example['treatment']}`: "
            f"gold `{example['gold']}` vs predicted `{example['predicted']}` "
            f"(`{example['mismatch_cause']}`)"
        )

    with open(outdir / "parser_validation_report.md", "w") as f:
        f.write("\n".join(lines) + "\n")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Validate parser outputs against battery expectations or clinician adjudication."
    )
    parser.add_argument("--results", required=True, help="Raw run_*.jsonl file to validate.")
    parser.add_argument("--battery", default="data/vignettes/vignette_battery.json")
    parser.add_argument("--annotations", help="Optional review annotation file from results/review_annotations.")
    parser.add_argument("--outdir", required=True)
    parser.add_argument("--model", help="Optional model filter.")
    parser.add_argument("--max-examples", type=int, default=25)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    summary = validate_parser(
        results_path=args.results,
        battery_path=args.battery,
        annotations_path=args.annotations,
        model_filter=args.model,
        max_examples=args.max_examples,
    )
    write_report(summary, args.outdir)
    print(f"Wrote parser validation artifacts to {args.outdir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
