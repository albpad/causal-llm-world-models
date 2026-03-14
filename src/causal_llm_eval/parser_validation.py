#!/usr/bin/env python3
"""Evaluation and validation program for the response parser."""

from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path

from .response_parser import parse_result

LABELS = ("recommended", "excluded", "relative_ci", "uncertain")


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
    return gold


def battery_gold(item: dict | None) -> dict[str, str]:
    if not item:
        return {}
    gold = {}
    for tx in item.get("expected_recommendations", []):
        gold[str(tx)] = "recommended"
    for tx in item.get("expected_excluded", []):
        gold[str(tx)] = "excluded"
    return gold


def choose_gold(item: dict | None, annotation: dict | None) -> tuple[dict[str, str], str]:
    annotated = annotation_gold(annotation)
    if annotated:
        return annotated, "clinician_annotation"
    return battery_gold(item), "battery_expectation"


def stance_map(parsed_row: dict | None) -> dict[str, str]:
    if not parsed_row:
        return {}
    return {stance["treatment"]: stance["stance"] for stance in parsed_row.get("stances", [])}


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
        for treatment, label in stance_map(row).items():
            votes[treatment][label] += 1
    consensus = {}
    for treatment, counts in votes.items():
        consensus[treatment] = counts.most_common(1)[0][0]
    return consensus


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
        }
        parsed_rows.append(row_payload)
        grouped[(item_id, model_name)].append(row_payload)

        for mismatch in evaluation["per_treatment"]:
            if mismatch["matched"]:
                continue
            if len(row_examples) < max_examples:
                example = {
                    **mismatch,
                    "phase1_preview": (row.get("phase1_response") or "")[:220],
                    "phase2_preview": (row.get("phase2_response") or "")[:220],
                }
                row_examples.append(example)

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
        }

    summary = {
        "results_file": str(results_path),
        "battery_file": str(battery_path),
        "annotations_file": str(annotations_path) if annotations_path else None,
        "model_filter": model_filter,
        "row_level": {
            "n_rows": len(parsed_rows),
            "exact_match_rate": completeness["row_exact_matches"] / len(parsed_rows) if parsed_rows else None,
            "label_metrics": summarise_label_counts(row_label_counts),
        },
        "consensus_level": {
            "n_cases": len(consensus_rows),
            "exact_match_rate": completeness["consensus_exact_matches"] / len(consensus_rows) if consensus_rows else None,
            "label_metrics": summarise_label_counts(consensus_label_counts),
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

    with open(outdir / "parser_validation_summary.json", "w") as f:
        json.dump(summary, f, indent=2)
    with open(outdir / "parser_validation_examples.json", "w") as f:
        json.dump(summary["examples"], f, indent=2)

    lines = []
    lines.append("# Parser Validation Report\n")
    lines.append("## Overview")
    lines.append(f"- Results file: `{summary['results_file']}`")
    lines.append(f"- Battery file: `{summary['battery_file']}`")
    lines.append(f"- Annotations file: `{summary['annotations_file'] or 'none'}`")
    if summary["model_filter"]:
        lines.append(f"- Model filter: `{summary['model_filter']}`")
    lines.append("")
    lines.append("## Row-Level Performance")
    lines.append(f"- Rows evaluated: `{summary['row_level']['n_rows']}`")
    erm = summary["row_level"]["exact_match_rate"]
    lines.append(f"- Exact match rate: `{erm:.1%}`" if erm is not None else "- Exact match rate: `n/a`")
    for label, metrics in summary["row_level"]["label_metrics"].items():
        p = metrics["precision"]
        r = metrics["recall"]
        f1 = metrics["f1"]
        lines.append(
            f"- `{label}`: precision `{p:.1%}` recall `{r:.1%}` f1 `{f1:.1%}`"
            if None not in (p, r, f1)
            else f"- `{label}`: insufficient support"
        )
    lines.append("")
    lines.append("## Consensus-Level Performance")
    lines.append(f"- Case/model groups: `{summary['consensus_level']['n_cases']}`")
    cem = summary["consensus_level"]["exact_match_rate"]
    lines.append(f"- Exact match rate: `{cem:.1%}`" if cem is not None else "- Exact match rate: `n/a`")
    for label, metrics in summary["consensus_level"]["label_metrics"].items():
        p = metrics["precision"]
        r = metrics["recall"]
        f1 = metrics["f1"]
        lines.append(
            f"- `{label}`: precision `{p:.1%}` recall `{r:.1%}` f1 `{f1:.1%}`"
            if None not in (p, r, f1)
            else f"- `{label}`: insufficient support"
        )
    lines.append("")
    lines.append("## Completeness")
    for key, value in summary["completeness"].items():
        lines.append(f"- `{key}`: `{value}`")
    lines.append("")
    lines.append("## Gold Sources")
    for source, count in sorted(summary["gold_sources"].items()):
        lines.append(f"- `{source}`: `{count}` rows")
    lines.append("")
    lines.append("## Frequent Treatment Errors")
    for treatment, stats in sorted(summary["by_treatment"].items(), key=lambda item: (item[1]["accuracy"] or 0, item[0]))[:10]:
        acc = stats["accuracy"]
        top_error = ", ".join(f"{label} x{count}" for label, count in stats["top_errors"]) or "none"
        lines.append(f"- `{treatment}`: accuracy `{acc:.1%}`; top errors `{top_error}`")
    lines.append("")
    lines.append("## Example Mismatches")
    for example in summary["examples"][:15]:
        lines.append(
            f"- `{example['item_id']}` / `{example['model_name']}` / `{example['treatment']}`: "
            f"gold `{example['gold']}` vs predicted `{example['predicted']}`"
        )

    with open(outdir / "parser_validation_report.md", "w") as f:
        f.write("\n".join(lines) + "\n")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Validate parser outputs against battery expectations or clinician adjudication.")
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
