#!/usr/bin/env python3
"""Build a statement-centric expert validation sheet for the normalized KG1 ontology."""

from __future__ import annotations

import csv
import json
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load_json(path: Path):
    with path.open() as f:
        return json.load(f)


def load_csv(path: Path) -> list[dict]:
    with path.open() as f:
        return list(csv.DictReader(f))


def fmt_list(values: list[str]) -> str:
    return ", ".join(values) if values else ""


def parse_label_list(text: str) -> list[str]:
    if not text:
        return []
    return [part.strip() for part in text.split(",") if part.strip()]


def build_rows() -> list[dict]:
    statement_rows = load_json(ROOT / "results" / "kg1_extraction" / "ferrari_pdf" / "statement_rows.json")
    benchmark_summary = load_json(ROOT / "docs" / "review" / "final_benchmark_lock" / "benchmark_audit_summary.json")
    edge_rows = load_csv(ROOT / "docs" / "review" / "kg1_full_review" / "edge_registry.csv")

    statement_map = {row["statement_id"]: row for row in statement_rows}
    benchmark_ids = benchmark_summary["unique_statement_ids"]

    grouped: dict[str, list[dict]] = defaultdict(list)
    for row in edge_rows:
        if row["edge_id"]:
            grouped[row["edge_id"]].append(row)

    output = []
    for statement_id in benchmark_ids:
        statement = statement_map[statement_id]
        rows = grouped.get(statement_id, [])

        families = sorted({row["family"] for row in rows if row["family"]})
        item_ids = sorted({row["item_id"] for row in rows if row["item_id"]})
        item_labels = sorted({row["label"] for row in rows if row["label"]})
        variables = []
        value_transitions = []
        for row in rows:
            vc = row["variables_changed"]
            if not vc:
                continue
            for chunk in vc.split(";"):
                chunk = chunk.strip()
                if not chunk:
                    continue
                value_transitions.append(chunk)
                var = chunk.split(":", 1)[0].strip()
                variables.append(var)

        recommended = sorted(
            {
                label
                for row in rows
                for label in parse_label_list(row["expected_recommendations"])
            }
        )
        excluded = sorted(
            {
                label
                for row in rows
                for label in parse_label_list(row["expected_excluded"])
            }
        )

        grey_zone = any(row["grey_zone_statement"] for row in rows)

        output.append(
            {
                "expert_review_status": "",
                "expert_validated_variable_mapping": "",
                "expert_validated_treatment_effect": "",
                "expert_comments": "",
                "statement_id": statement_id,
                "section": statement.get("section", ""),
                "source_statement_text": statement.get("statement_text", ""),
                "consensus_pct": statement.get("consensus_pct", ""),
                "voting_round": statement.get("voting_round", ""),
                "statement_class": statement.get("statement_class", ""),
                "benchmark_families": fmt_list(families),
                "benchmark_item_ids": fmt_list(item_ids),
                "benchmark_item_labels": fmt_list(item_labels),
                "normalized_variables": fmt_list(sorted(set(variables))),
                "normalized_value_transitions": fmt_list(sorted(set(value_transitions))),
                "recommended_treatments_observed": fmt_list(recommended),
                "excluded_treatments_observed": fmt_list(excluded),
                "grey_zone_probe": str(grey_zone),
            }
        )
    return output


def write_csv(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "expert_review_status",
        "expert_validated_variable_mapping",
        "expert_validated_treatment_effect",
        "expert_comments",
        "statement_id",
        "section",
        "source_statement_text",
        "consensus_pct",
        "voting_round",
        "statement_class",
        "benchmark_families",
        "benchmark_item_ids",
        "benchmark_item_labels",
        "normalized_variables",
        "normalized_value_transitions",
        "recommended_treatments_observed",
        "excluded_treatments_observed",
        "grey_zone_probe",
    ]
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def write_markdown(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = []
    lines.append("# KG1 Ontology Validation Sheet")
    lines.append("")
    lines.append("Purpose: rapid expert review of how each benchmark statement was normalized into variables, value transitions, and treatment consequences.")
    lines.append("")
    lines.append("How to use:")
    lines.append("- Work primarily from the CSV if you want to edit directly.")
    lines.append("- Mark `expert_review_status` as `approved`, `revise`, or `unclear`.")
    lines.append("- Use `expert_validated_variable_mapping` to confirm whether the chosen normalized variable(s) are clinically appropriate.")
    lines.append("- Use `expert_validated_treatment_effect` to confirm whether the observed treatment consequence is faithful to the source statement.")
    lines.append("")
    lines.append("Key files:")
    lines.append(f"- CSV: `{path.with_suffix('.csv')}`")
    lines.append("- Source benchmark: `data/vignettes/vignette_battery.json`")
    lines.append("- Source statement extraction: `results/kg1_extraction/ferrari_pdf/statement_rows.json`")
    lines.append("")
    lines.append("## Preview")
    lines.append("| Statement | Class | Variables | Recommended | Excluded | Grey zone |")
    lines.append("|---|---|---|---|---|---|")
    for row in rows[:20]:
        lines.append(
            f"| `{row['statement_id']}` | `{row['statement_class']}` | `{row['normalized_variables'] or 'none'}` | `{row['recommended_treatments_observed'] or 'none'}` | `{row['excluded_treatments_observed'] or 'none'}` | `{row['grey_zone_probe']}` |"
        )
    with path.open("w") as f:
        f.write("\n".join(lines) + "\n")


def main() -> None:
    outdir = ROOT / "docs" / "review" / "ontology_validation_sheet"
    rows = build_rows()
    csv_path = outdir / "kg1_ontology_validation_sheet.csv"
    md_path = outdir / "kg1_ontology_validation_sheet.md"
    write_csv(csv_path, rows)
    write_markdown(md_path, rows)
    print(f"Wrote ontology validation sheet to {outdir}")


if __name__ == "__main__":
    main()
