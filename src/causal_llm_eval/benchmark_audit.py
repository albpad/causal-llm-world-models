#!/usr/bin/env python3
"""Benchmark audit and KG1 traceability artifact generation."""

from __future__ import annotations

import argparse
import csv
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

try:
    from .json_utils import dump_json
    from .label_space import normalise_expected_label_lists
    from .llm_query_runner import TARGETED_QUESTIONS_BY_FAMILY
    from .response_parser import TREATMENT_ALIASES
    from .vignette_generator import check_staging_consistency
except ImportError:
    from json_utils import dump_json
    from label_space import normalise_expected_label_lists
    from llm_query_runner import TARGETED_QUESTIONS_BY_FAMILY
    from response_parser import TREATMENT_ALIASES
    from vignette_generator import check_staging_consistency


COMPILED_ALIASES = {
    treatment: [re.compile(pattern, re.I) for pattern in patterns]
    for treatment, patterns in TREATMENT_ALIASES.items()
}


def load_battery(path: str | Path) -> dict:
    with open(path) as f:
        return json.load(f)


def all_items(battery: dict) -> list[dict]:
    return list(battery.get("baselines", [])) + list(battery.get("perturbations", []))


def query_space_for_family(family: str) -> set[str]:
    questions = "\n".join(TARGETED_QUESTIONS_BY_FAMILY.get(family, []))
    return {
        treatment
        for treatment, patterns in COMPILED_ALIASES.items()
        if any(pattern.search(questions) for pattern in patterns)
    }


def compute_article_edge_count(graph_path: str | Path | None) -> int | None:
    if not graph_path:
        return None
    graph_path = Path(graph_path)
    if not graph_path.exists():
        return None
    with open(graph_path) as f:
        graph = json.load(f)
    if not graph:
        return None
    first = next(iter(graph.values()))
    tp = first.get("true_positives")
    fn = first.get("false_negatives")
    if tp is None or fn is None:
        return None
    return tp + fn


def build_traceability_rows(battery: dict) -> list[dict]:
    rows = []
    baseline_map = {item["id"]: item for item in battery.get("baselines", [])}
    for item in battery.get("perturbations", []):
        rec, exc = normalise_expected_label_lists(
            item.get("expected_recommendations", []),
            item.get("expected_excluded", []),
        )
        for edge_id in item.get("edge_justification", []):
            rows.append(
                {
                    "edge_id": edge_id,
                    "item_id": item["id"],
                    "baseline_id": item.get("baseline_id", ""),
                    "family": item.get("family", ""),
                    "type": item.get("type", ""),
                    "label": item.get("label", ""),
                    "expected_recommendations": ", ".join(rec),
                    "expected_excluded": ", ".join(exc),
                    "baseline_label": baseline_map.get(item.get("baseline_id", ""), {}).get("subtype", ""),
                }
            )
    return sorted(rows, key=lambda row: (row["edge_id"], row["family"], row["item_id"]))


def compute_integrity_summary(battery: dict, graph_path: str | Path | None = None) -> dict:
    baselines = battery.get("baselines", [])
    perturbations = battery.get("perturbations", [])
    baseline_map = {item["id"]: item for item in baselines}
    items = all_items(battery)
    perturb_type_counts = Counter(item.get("type", "baseline") for item in perturbations)

    unique_statement_ids = sorted({edge for item in perturbations for edge in item.get("edge_justification", [])})

    missing_traceability = [
        item["id"]
        for item in perturbations
        if item.get("type") != "null" and not item.get("edge_justification")
    ]

    null_drift = []
    staging_warnings = {}
    family_query_space = {}
    query_space_gaps = {}

    for item in perturbations:
        if item.get("type") == "null":
            baseline = baseline_map[item["baseline_id"]]
            base_rec, base_exc = normalise_expected_label_lists(
                baseline.get("expected_recommendations", []),
                baseline.get("expected_excluded", []),
            )
            item_rec, item_exc = normalise_expected_label_lists(
                item.get("expected_recommendations", []),
                item.get("expected_excluded", []),
            )
            if sorted(base_rec) != sorted(item_rec) or sorted(base_exc) != sorted(item_exc):
                null_drift.append(
                    {
                        "item_id": item["id"],
                        "baseline_id": item["baseline_id"],
                        "baseline_rec": base_rec,
                        "baseline_exc": base_exc,
                        "item_rec": item_rec,
                        "item_exc": item_exc,
                    }
                )

        warnings = check_staging_consistency(item.get("variable_assignments", {}))
        if warnings:
            staging_warnings[item["id"]] = warnings

    for family in sorted({item.get("family", "") for item in items}):
        family_items = [item for item in items if item.get("family") == family]
        expected = set()
        for item in family_items:
            rec, exc = normalise_expected_label_lists(
                item.get("expected_recommendations", []),
                item.get("expected_excluded", []),
            )
            expected |= set(rec) | set(exc)
        query_space = query_space_for_family(family)
        family_query_space[family] = sorted(query_space)
        query_space_gaps[family] = {
            "expected_labels": sorted(expected),
            "query_space": sorted(query_space),
            "missing_from_query_space": sorted(expected - query_space),
            "concrete_missing_from_query_space": sorted(
                label
                for label in expected - query_space
                if label not in {"nonsurgical_lp", "surgical_lp", "ophl_any"}
            ),
        }

    return {
        "counts": {
            "baselines": len(baselines),
            "perturbations": len(perturbations),
            "items_total": len(items),
            "statement_linked_rules": len(unique_statement_ids),
            "evaluation_edges_in_article_metrics": compute_article_edge_count(graph_path),
            "perturbation_type_counts": dict(perturb_type_counts),
        },
        "unique_statement_ids": unique_statement_ids,
        "missing_traceability": missing_traceability,
        "null_drift": null_drift,
        "staging_warnings": staging_warnings,
        "family_query_space": family_query_space,
        "query_space_gaps": query_space_gaps,
    }


def write_markdown(summary: dict, traceability_rows: list[dict], outdir: Path) -> None:
    lines = []
    counts = summary["counts"]
    lines.append("# Vignette Integrity Report\n")
    lines.append("## Benchmark Summary")
    lines.append(f"- Baselines: `{counts['baselines']}`")
    lines.append(f"- Perturbations: `{counts['perturbations']}`")
    lines.append(f"- Total items: `{counts['items_total']}`")
    lines.append(f"- Statement-linked rules: `{counts['statement_linked_rules']}`")
    if counts["evaluation_edges_in_article_metrics"] is not None:
        lines.append(f"- Evaluation edges in article metrics: `{counts['evaluation_edges_in_article_metrics']}`")
    lines.append("")
    lines.append("## Integrity Checks")
    lines.append(f"- Non-null perturbations missing traceability: `{len(summary['missing_traceability'])}`")
    lines.append(f"- Null controls drifting from baseline expectations: `{len(summary['null_drift'])}`")
    lines.append(f"- Items with staging warnings: `{len(summary['staging_warnings'])}`")
    lines.append("")

    lines.append("## Query-Space Audit by Family")
    for family, gap in summary["query_space_gaps"].items():
        concrete_missing = ", ".join(gap["concrete_missing_from_query_space"]) or "none"
        lines.append(f"- `{family}`: concrete labels missing from targeted query space: `{concrete_missing}`")
    lines.append("")

    lines.append("## Traceability Matrix Preview")
    lines.append("| Edge ID | Family | Item ID | Type | Baseline |")
    lines.append("|---|---|---|---|---|")
    for row in traceability_rows[:25]:
        lines.append(
            f"| `{row['edge_id']}` | `{row['family']}` | `{row['item_id']}` | `{row['type']}` | `{row['baseline_id']}` |"
        )
    lines.append("")

    lines.append("## Null Drift Details")
    if not summary["null_drift"]:
        lines.append("- None")
    else:
        for row in summary["null_drift"]:
            lines.append(f"- `{row['item_id']}` vs `{row['baseline_id']}`")
    lines.append("")

    lines.append("## Staging Warnings")
    if not summary["staging_warnings"]:
        lines.append("- None")
    else:
        for item_id, warnings in sorted(summary["staging_warnings"].items()):
            lines.append(f"- `{item_id}`: {'; '.join(warnings)}")

    with open(outdir / "vignette_integrity_report.md", "w") as f:
        f.write("\n".join(lines) + "\n")


def write_html(summary: dict, outdir: Path) -> None:
    counts = summary["counts"]
    family_cards = []
    for family, gap in summary["query_space_gaps"].items():
        missing = gap["concrete_missing_from_query_space"]
        missing_html = "".join(f"<li>{label}</li>" for label in missing) or "<li>None</li>"
        family_cards.append(
            f"""
            <section class="card">
              <h3>{family}</h3>
              <p><strong>Query space:</strong> {", ".join(gap["query_space"]) or "None"}</p>
              <p><strong>Expected labels:</strong> {", ".join(gap["expected_labels"]) or "None"}</p>
              <div class="pill {'warn' if missing else 'ok'}">{'Concrete gaps present' if missing else 'No concrete query-space gaps'}</div>
              <ul>{missing_html}</ul>
            </section>
            """
        )

    html = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>KG1 Benchmark Review</title>
  <style>
    :root {{
      --bg: #f5f1e8;
      --ink: #202020;
      --muted: #6a6258;
      --panel: #fffdf8;
      --line: #d9cfc0;
      --ok: #2d6a4f;
      --warn: #b35c1e;
      --accent: #173f5f;
    }}
    body {{ font-family: Georgia, 'Times New Roman', serif; background: linear-gradient(180deg, #efe7d7 0%, var(--bg) 100%); color: var(--ink); margin: 0; }}
    .wrap {{ max-width: 1180px; margin: 0 auto; padding: 40px 24px 64px; }}
    h1, h2, h3 {{ margin: 0 0 12px; }}
    p, li {{ line-height: 1.5; }}
    .hero {{ background: var(--panel); border: 1px solid var(--line); border-radius: 24px; padding: 28px; box-shadow: 0 12px 32px rgba(32,32,32,0.06); }}
    .stats {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 12px; margin-top: 20px; }}
    .stat {{ background: #faf6ef; border: 1px solid var(--line); border-radius: 18px; padding: 16px; }}
    .label {{ color: var(--muted); font-size: 12px; text-transform: uppercase; letter-spacing: 0.08em; }}
    .value {{ font-size: 32px; font-weight: 700; margin-top: 6px; }}
    .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 16px; margin-top: 24px; }}
    .card {{ background: var(--panel); border: 1px solid var(--line); border-radius: 20px; padding: 20px; }}
    .pill {{ display: inline-block; padding: 6px 10px; border-radius: 999px; font-size: 12px; margin: 10px 0; }}
    .pill.ok {{ background: rgba(45,106,79,0.1); color: var(--ok); }}
    .pill.warn {{ background: rgba(179,92,30,0.12); color: var(--warn); }}
    .small {{ color: var(--muted); }}
  </style>
</head>
<body>
  <div class="wrap">
    <section class="hero">
      <h1>Final KG1 / Vignette Benchmark Review</h1>
      <p class="small">Clinician-facing audit of the final benchmark used for the six-model study.</p>
      <div class="stats">
        <div class="stat"><div class="label">Baselines</div><div class="value">{counts['baselines']}</div></div>
        <div class="stat"><div class="label">Perturbations</div><div class="value">{counts['perturbations']}</div></div>
        <div class="stat"><div class="label">Total Items</div><div class="value">{counts['items_total']}</div></div>
        <div class="stat"><div class="label">Statement-Linked Rules</div><div class="value">{counts['statement_linked_rules']}</div></div>
        <div class="stat"><div class="label">Article Evaluation Edges</div><div class="value">{counts['evaluation_edges_in_article_metrics'] or 'n/a'}</div></div>
      </div>
    </section>
    <section class="grid">
      <section class="card">
        <h2>Integrity Summary</h2>
        <p><strong>Missing traceability:</strong> {len(summary['missing_traceability'])}</p>
        <p><strong>Null drift:</strong> {len(summary['null_drift'])}</p>
        <p><strong>Staging warnings:</strong> {len(summary['staging_warnings'])}</p>
      </section>
      <section class="card">
        <h2>Perturbation Types</h2>
        <ul>
          {''.join(f"<li>{kind}: {count}</li>" for kind, count in sorted(counts['perturbation_type_counts'].items()))}
        </ul>
      </section>
    </section>
    <h2 style="margin-top: 28px;">Family Query-Space Audit</h2>
    <div class="grid">
      {''.join(family_cards)}
    </div>
  </div>
</body>
</html>
"""
    with open(outdir / "kg1_final_benchmark_review.html", "w") as f:
        f.write(html)


def write_traceability_csv(rows: list[dict], outdir: Path) -> None:
    fieldnames = [
        "edge_id",
        "family",
        "item_id",
        "baseline_id",
        "type",
        "label",
        "expected_recommendations",
        "expected_excluded",
        "baseline_label",
    ]
    with open(outdir / "kg1_traceability_matrix.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def write_artifacts(summary: dict, traceability_rows: list[dict], outdir: str | Path) -> None:
    outdir = Path(outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    dump_json(outdir / "benchmark_audit_summary.json", summary)
    write_traceability_csv(traceability_rows, outdir)
    write_markdown(summary, traceability_rows, outdir)
    write_html(summary, outdir)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Audit the vignette battery and KG1 traceability.")
    parser.add_argument("--battery", default="data/vignettes/vignette_battery.json")
    parser.add_argument("--graph-comparison", default="results/analysis/article-metrics-6models-gemma4/graph_comparison.json")
    parser.add_argument("--outdir", required=True)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    battery = load_battery(args.battery)
    summary = compute_integrity_summary(battery, args.graph_comparison)
    traceability_rows = build_traceability_rows(battery)
    write_artifacts(summary, traceability_rows, args.outdir)
    print(f"Wrote benchmark audit artifacts to {args.outdir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
