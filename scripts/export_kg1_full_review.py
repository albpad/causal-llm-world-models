#!/usr/bin/env python3
"""Export the actual analysis KG1 into review-friendly markdown and CSV artifacts."""

from __future__ import annotations

import csv
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from causal_llm_eval.causal_templates import FAMILY_TREATMENTS, TREATMENT_RULES  # noqa: E402


def load_battery(path: Path) -> dict:
    with path.open() as f:
        return json.load(f)


def fmt_list(values: list[str]) -> str:
    return ", ".join(values) if values else ""


def fmt_mapping(mapping: dict[str, list[str]]) -> str:
    if not mapping:
        return ""
    parts = []
    for key in sorted(mapping):
        parts.append(f"{key}={ '|'.join(str(v) for v in mapping[key]) }")
    return "; ".join(parts)


def fmt_vars(changes: list[dict]) -> str:
    if not changes:
        return ""
    return "; ".join(
        f"{row['variable']}: {row['from']} -> {row['to']}"
        for row in changes
    )


def treatment_rule_rows() -> list[dict]:
    rows = []
    for treatment in sorted(TREATMENT_RULES):
        rule = TREATMENT_RULES[treatment]
        rows.append(
            {
                "treatment": treatment,
                "full_name": rule.get("full_name", ""),
                "families_applicable": fmt_list(rule.get("families_applicable", [])),
                "hard_blockers": fmt_mapping(rule.get("hard_blockers", {})),
                "soft_blockers": fmt_mapping(rule.get("soft_blockers", {})),
                "indications": fmt_mapping(rule.get("indications", {})),
                "contraindications_in_early": fmt_mapping(rule.get("contraindications_in_early", {})),
                "indications_when_cisplatin_blocked": str(rule.get("indications_when_cisplatin_blocked", False)),
                "irrelevant": fmt_list(rule.get("irrelevant", [])),
                "mechanism": rule.get("mechanism", ""),
            }
        )
    return rows


def family_rows() -> list[dict]:
    rows = []
    for family in sorted(FAMILY_TREATMENTS):
        rows.append(
            {
                "family": family,
                "treatments_evaluated": fmt_list(FAMILY_TREATMENTS[family]),
            }
        )
    return rows


def baseline_rows(battery: dict) -> list[dict]:
    rows = []
    for row in battery["baselines"]:
        rows.append(
            {
                "id": row["id"],
                "family": row["family"],
                "subtype": row["subtype"],
                "expected_recommendations": fmt_list(row.get("expected_recommendations", [])),
                "expected_excluded": fmt_list(row.get("expected_excluded", [])),
                "question": row.get("question", ""),
                "clinical_text": row.get("clinical_text", "").strip(),
                "expected_reasoning": row.get("expected_reasoning", ""),
            }
        )
    return rows


def perturbation_rows(battery: dict) -> list[dict]:
    rows = []
    for row in battery["perturbations"]:
        rows.append(
            {
                "id": row["id"],
                "baseline_id": row["baseline_id"],
                "family": row["family"],
                "type": row["type"],
                "label": row["label"],
                "variables_changed": fmt_vars(row.get("variables_changed", [])),
                "staging_impact": row.get("staging_impact", ""),
                "expected_recommendations": fmt_list(row.get("expected_recommendations", [])),
                "expected_excluded": fmt_list(row.get("expected_excluded", [])),
                "edge_justification": fmt_list(row.get("edge_justification", [])),
                "grey_zone_statement": row.get("grey_zone_statement", "") or "",
                "predicted_failure_mode": row.get("predicted_failure_mode", ""),
                "notes": row.get("notes", "") or "",
                "clinical_text": row.get("clinical_text", "").strip(),
            }
        )
    return rows


def edge_rows(battery: dict) -> list[dict]:
    rows = []
    for row in battery["perturbations"]:
        edges = row.get("edge_justification", [])
        if not edges:
            rows.append(
                {
                    "edge_id": "",
                    "item_id": row["id"],
                    "baseline_id": row["baseline_id"],
                    "family": row["family"],
                    "type": row["type"],
                    "label": row["label"],
                    "variables_changed": fmt_vars(row.get("variables_changed", [])),
                    "expected_recommendations": fmt_list(row.get("expected_recommendations", [])),
                    "expected_excluded": fmt_list(row.get("expected_excluded", [])),
                    "grey_zone_statement": row.get("grey_zone_statement", "") or "",
                }
            )
            continue

        for edge_id in edges:
            rows.append(
                {
                    "edge_id": edge_id,
                    "item_id": row["id"],
                    "baseline_id": row["baseline_id"],
                    "family": row["family"],
                    "type": row["type"],
                    "label": row["label"],
                    "variables_changed": fmt_vars(row.get("variables_changed", [])),
                    "expected_recommendations": fmt_list(row.get("expected_recommendations", [])),
                    "expected_excluded": fmt_list(row.get("expected_excluded", [])),
                    "grey_zone_statement": row.get("grey_zone_statement", "") or "",
                }
            )
    return rows


def write_csv(path: Path, rows: list[dict], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def write_markdown(
    path: Path,
    battery: dict,
    treatment_rows: list[dict],
    family_rows_: list[dict],
    baseline_rows_: list[dict],
    perturbation_rows_: list[dict],
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)

    pert_by_base = defaultdict(list)
    for row in perturbation_rows_:
        pert_by_base[row["baseline_id"]].append(row)

    family_counts = Counter(row["family"] for row in baseline_rows_)
    pert_family_counts = Counter(row["family"] for row in perturbation_rows_)

    lines = []
    lines.append("# Full KG1 Review")
    lines.append("")
    lines.append("This artifact shows the actual benchmark used in analysis:")
    lines.append("- the locked battery in `data/vignettes/vignette_battery.json`")
    lines.append("- the family treatment question space in `src/causal_llm_eval/causal_templates.py`")
    lines.append("- the treatment-level fallback rule layer in `src/causal_llm_eval/causal_templates.py`")
    lines.append("")
    lines.append("## Summary")
    lines.append(f"- Baselines: `{battery['meta']['total_baselines']}`")
    lines.append(f"- Perturbations: `{battery['meta']['total_perturbations']}`")
    lines.append(f"- Total items: `{battery['meta']['total_items']}`")
    lines.append(f"- Unique statement-linked rules: `{battery['meta']['unique_edges_tested']}`")
    lines.append(f"- Perturbation types: `{battery['meta']['perturbation_types']}`")
    lines.append("")
    lines.append("## Families")
    lines.append("| Family | Baselines | Perturbations | Treatments Evaluated |")
    lines.append("|---|---|---|---|")
    for row in family_rows_:
        family = row["family"]
        lines.append(
            f"| `{family}` | `{family_counts.get(family, 0)}` | `{pert_family_counts.get(family, 0)}` | `{row['treatments_evaluated']}` |"
        )
    lines.append("")
    lines.append("## Treatment Rule Layer")
    for row in treatment_rows:
        lines.append(f"### `{row['treatment']}`")
        lines.append(f"- Full name: {row['full_name']}")
        lines.append(f"- Families applicable: `{row['families_applicable'] or 'none'}`")
        lines.append(f"- Hard blockers: `{row['hard_blockers'] or 'none'}`")
        lines.append(f"- Soft blockers: `{row['soft_blockers'] or 'none'}`")
        lines.append(f"- Indications: `{row['indications'] or 'none'}`")
        lines.append(f"- Early contraindications: `{row['contraindications_in_early'] or 'none'}`")
        lines.append(
            f"- Alternative-on-cisplatin-block: `{row['indications_when_cisplatin_blocked']}`"
        )
        lines.append(f"- Irrelevant variables: `{row['irrelevant'] or 'none'}`")
        lines.append(f"- Mechanism: {row['mechanism']}")
        lines.append("")

    lines.append("## Locked Baselines and Perturbations")
    for base in baseline_rows_:
        lines.append(f"### `{base['id']}` — `{base['family']}` / `{base['subtype']}`")
        lines.append(f"- Expected recommendations: `{base['expected_recommendations']}`")
        lines.append(f"- Expected excluded: `{base['expected_excluded'] or 'none'}`")
        lines.append(f"- Question: {base['question']}")
        lines.append("")
        lines.append("```text")
        lines.append(base["clinical_text"])
        lines.append("```")
        lines.append("")
        lines.append(f"- Expected reasoning: {base['expected_reasoning']}")
        lines.append("")
        lines.append("| Perturbation | Type | Variables Changed | Expected Recommendations | Expected Excluded | Edge Justification | Grey Zone |")
        lines.append("|---|---|---|---|---|---|---|")
        for pert in pert_by_base.get(base["id"], []):
            lines.append(
                f"| `{pert['id']}` | `{pert['type']}` | `{pert['variables_changed'] or 'none'}` | `{pert['expected_recommendations'] or 'none'}` | `{pert['expected_excluded'] or 'none'}` | `{pert['edge_justification'] or 'none'}` | `{pert['grey_zone_statement'] or 'none'}` |"
            )
        lines.append("")
        for pert in pert_by_base.get(base["id"], []):
            lines.append(f"#### `{pert['id']}` — {pert['label']}")
            lines.append(f"- Predicted failure mode: {pert['predicted_failure_mode']}")
            if pert["notes"]:
                lines.append(f"- Notes: {pert['notes']}")
            lines.append("```text")
            lines.append(pert["clinical_text"])
            lines.append("```")
            lines.append("")

    with path.open("w") as f:
        f.write("\n".join(lines) + "\n")


def main() -> None:
    battery_path = ROOT / "data" / "vignettes" / "vignette_battery.json"
    outdir = ROOT / "docs" / "review" / "kg1_full_review"

    battery = load_battery(battery_path)
    treatment_rows_ = treatment_rule_rows()
    family_rows_ = family_rows()
    baseline_rows_ = baseline_rows(battery)
    perturbation_rows_ = perturbation_rows(battery)
    edge_rows_ = edge_rows(battery)

    write_csv(
        outdir / "treatment_rules.csv",
        treatment_rows_,
        [
            "treatment",
            "full_name",
            "families_applicable",
            "hard_blockers",
            "soft_blockers",
            "indications",
            "contraindications_in_early",
            "indications_when_cisplatin_blocked",
            "irrelevant",
            "mechanism",
        ],
    )
    write_csv(
        outdir / "family_treatments.csv",
        family_rows_,
        ["family", "treatments_evaluated"],
    )
    write_csv(
        outdir / "baselines.csv",
        baseline_rows_,
        [
            "id",
            "family",
            "subtype",
            "expected_recommendations",
            "expected_excluded",
            "question",
            "clinical_text",
            "expected_reasoning",
        ],
    )
    write_csv(
        outdir / "perturbations.csv",
        perturbation_rows_,
        [
            "id",
            "baseline_id",
            "family",
            "type",
            "label",
            "variables_changed",
            "staging_impact",
            "expected_recommendations",
            "expected_excluded",
            "edge_justification",
            "grey_zone_statement",
            "predicted_failure_mode",
            "notes",
            "clinical_text",
        ],
    )
    write_csv(
        outdir / "edge_registry.csv",
        edge_rows_,
        [
            "edge_id",
            "item_id",
            "baseline_id",
            "family",
            "type",
            "label",
            "variables_changed",
            "expected_recommendations",
            "expected_excluded",
            "grey_zone_statement",
        ],
    )
    write_markdown(
        outdir / "kg1_full_review.md",
        battery,
        treatment_rows_,
        family_rows_,
        baseline_rows_,
        perturbation_rows_,
    )

    print(f"Wrote KG1 full review to {outdir}")


if __name__ == "__main__":
    main()
