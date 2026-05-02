#!/usr/bin/env python3
"""Deterministic KG1 extraction and validation pipeline for the Ferrari consensus PDF."""

from __future__ import annotations

import argparse
import csv
import re
from bisect import bisect_right
from collections import Counter, defaultdict
from pathlib import Path

try:
    from pypdf import PdfReader
except ImportError:  # pragma: no cover - exercised in CLI environments
    PdfReader = None

try:
    from .json_utils import dump_json
    from .response_parser import TREATMENT_ALIASES
except ImportError:
    from json_utils import dump_json
    from response_parser import TREATMENT_ALIASES


CONSENSUS_THRESHOLD = 80.0

STATEMENT_PATTERN = re.compile(
    r"(?P<kind>Additional statement|Statement)\s+"
    r"(?P<number>\d+(?:[–-]\d+)?)\s*"
    r"\((?P<statement_id>S(?:A)?[0-9A-Z-]+)\)\s*"
    r"(?P<body>.*?)"
    r"(?P<level_of_evidence>[IVX]+(?:[–-][IVX]+)?)\s*;\s*"
    r"(?P<consensus_pct>\d{1,3}(?:[·.]\d+)?)%\s*"
    r"\((?P<voting_round>first|second|third)\)",
    re.S,
)

NUMERIC_RANGE_PATTERN = re.compile(r"^\d+(?:[–-]\d+)?$")

SECTION_HEADINGS = [
    "Granular indications for T2–T3",
    "Investigations and general aspects",
    "Transoral surgery",
    "Open partial horizontal laryngectomy",
    "Radiotherapy and chemotherapy",
    "Indications for T4a cancer",
    "Contraindications to larynx preservation",
    "Indications for salvage organ preservation surgery after radiotherapy or chemoradiotherapy failure",
    "Laryngeal function at baseline",
    "Which comorbidities are contraindications and to what extent?",
    "Which comorbidities are contraindications to larynx preservation and to what extent?",
    "Organ preservation in older patients: selection criteria",
    "Post-treatment surveillance",
    "Prognostic and predictive factors",
    "Listening to the patient’s preferences: tools and implementation",
    "Prehabilitation and rehabilitation",
    "Prehabilitation and rehabilitation protocols",
    "Cost-effectiveness of different laryngeal preservation approaches",
]

SECTION_ALIASES = {
    "Which comorbidities are contraindications to larynx preservation and to what extent?": (
        "Which comorbidities are contraindications and to what extent?"
    ),
    "Prehabilitation and rehabilitation protocols": "Prehabilitation and rehabilitation",
}

SECTION_NUMBER_RANGES = [
    (1, 4, "Investigations and general aspects"),
    (5, 12, "Transoral surgery"),
    (13, 18, "Open partial horizontal laryngectomy"),
    (19, 37, "Radiotherapy and chemotherapy"),
    (38, 55, "Indications for T4a cancer"),
    (56, 61, "Indications for salvage organ preservation surgery after radiotherapy or chemoradiotherapy failure"),
    (62, 66, "Laryngeal function at baseline"),
    (67, 78, "Which comorbidities are contraindications and to what extent?"),
    (79, 91, "Organ preservation in older patients: selection criteria"),
    (92, 110, "Post-treatment surveillance"),
    (111, 123, "Prognostic and predictive factors"),
    (124, 131, "Listening to the patient’s preferences: tools and implementation"),
    (132, 137, "Prehabilitation and rehabilitation"),
    (138, 141, "Cost-effectiveness of different laryngeal preservation approaches"),
]

SECTION_ID_OVERRIDES = {
    "SA1": "Investigations and general aspects",
    "SA2": "Investigations and general aspects",
    "SA3": "Investigations and general aspects",
    "SA4R": "Transoral surgery",
    "SA5": "Transoral surgery",
    "SA6": "Prognostic and predictive factors",
    "SA7": "Prognostic and predictive factors",
    "SA8": "Prognostic and predictive factors",
}

DIRECT_SCOPE_PATTERNS = {
    "larynx_preservation_any": [
        r"larynx[-\s]?preservation strateg(?:y|ies)",
        r"laryngeal preservation approach(?:es)?",
        r"larynx[-\s]?preservation treatment(?:s)?",
        r"organ preservation treatment(?:s)?",
        r"\blaryngeal preservation\b",
        r"\borgan preservation\b",
        r"\borgan conservation\b",
    ],
    "nonsurgical_lp": [
        r"non[-\s]?surgical organ preservation",
        r"non[-\s]?surgical larynx[-\s]?preservation",
        r"non[-\s]?surgical treatments?",
        r"non[-\s]?surgical organ conservation protocols?",
        r"chemoradiation[-\s]?based approach(?:es)?",
        r"induction chemotherapy[-\s]?based",
    ],
    "surgical_lp": [
        r"surgical larynx[-\s]?preservation",
        r"conservative surgery",
        r"conservative laryngeal surgery",
        r"partial laryngectomy",
    ],
}

RULE_TYPE_PATTERNS = {
    "response_adapted": [
        r"response to induction chemotherapy",
        r"complete response after induction chemotherapy",
        r"partial response after induction chemotherapy",
        r"stable disease after induction chemotherapy",
        r"no response to induction chemotherapy",
        r"after induction chemotherapy",
        r"in case of response",
    ],
    "relative_contraindication": [
        r"relative contraindication",
        r"relative contraindications",
        r"might be a contraindication",
        r"particularly regarding",
    ],
    "absolute_contraindication": [
        r"absolute contraindication",
        r"\bare contraindications\b",
        r"\bis contraindicated\b",
        r"\bcontraindicated in\b",
        r"\bshould not be treated\b",
        r"\bnot suitable candidates?\b",
        r"\bpreclude\b",
        r"\bpreventing\b",
        r"\bpoor(er)? survival compared with total laryngectomy\b",
    ],
    "exception": [
        r"\bnot a contraindication\b",
        r"\bnot a sufficient criterion to contraindicate\b",
        r"\balone is not a contraindication\b",
    ],
    "fallback_option": [
        r"\bwho refuse total laryngectomy\b",
        r"\bwho decline total laryngectomy\b",
        r"\bcan be considered as concurrent treatment\b",
        r"\bcould be offered\b",
    ],
    "recommendation": [
        r"\btreatment of choice\b",
        r"\bshould be preferred\b",
        r"\bis indicated\b",
        r"\badequate treatment option\b",
        r"\bvaluable option\b",
        r"\bmight be considered\b",
        r"\bcan be considered\b",
        r"\bshould be offered\b",
        r"\bshould be performed over\b",
        r"\bshould entail\b",
        r"\bpreferred\b",
    ],
    "selection_factor": [
        r"\ballows? for the appropriate selection\b",
        r"\bprognostic significance\b",
        r"\bassociated with poor functional outcomes\b",
        r"\bassociated with poorer functional and survival outcomes\b",
        r"\bassociated with progression[-\s]?free survival\b",
        r"\blower rates of organ preservation\b",
        r"\bpredict(or|ive)\b",
        r"\bfavourable prognostic factor\b",
        r"\bnot suitable candidates\b",
        r"\bmore aggressive management\b",
        r"\bcarefully weighed against the risks\b",
        r"\bhigher risk of treatment complications\b",
        r"\boutcomes that are more similar to cT3\b",
    ],
}

TARGET_ORDER = [
    "total_laryngectomy",
    "tlm",
    "tors",
    "ophl_type_iib",
    "ophl_type_iii",
    "ophl_type_ii",
    "ophl_type_i",
    "ophl_any",
    "concurrent_crt",
    "ict_rt",
    "rt_accelerated",
    "rt_alone",
    "cisplatin_high_dose",
    "cetuximab_concurrent",
    "carboplatin_5fu",
    "nonsurgical_lp",
    "surgical_lp",
]

EXTRACTION_TREATMENT_ALIASES = {
    "carboplatin_5fu": [r"carboplatin[-\s]?based treatment"],
}


def _fuzzy_heading_pattern(heading: str) -> re.Pattern[str]:
    tokens = heading.split()
    return re.compile(
        r"(?<!\w)" + r"\s*".join(re.escape(token) for token in tokens) + r"(?=\s|Statement|Additional|$)",
        re.I,
    )


COMPILED_HEADING_PATTERNS = {
    heading: _fuzzy_heading_pattern(heading)
    for heading in SECTION_HEADINGS
}

COMPILED_TREATMENT_PATTERNS = {
    treatment: [
        re.compile(pattern, re.I)
        for pattern in [*TREATMENT_ALIASES.get(treatment, []), *EXTRACTION_TREATMENT_ALIASES.get(treatment, [])]
    ]
    for treatment in set(TREATMENT_ALIASES) | set(EXTRACTION_TREATMENT_ALIASES)
}

COMPILED_SCOPE_PATTERNS = {
    scope: [re.compile(pattern, re.I) for pattern in patterns]
    for scope, patterns in DIRECT_SCOPE_PATTERNS.items()
}

COMPILED_RULE_PATTERNS = {
    label: [re.compile(pattern, re.I) for pattern in patterns]
    for label, patterns in RULE_TYPE_PATTERNS.items()
}


def clean_pdf_page_text(text: str) -> str:
    text = text.replace("\u00ad", "")
    text = text.replace("\xa0", " ")
    text = text.replace("­", "")
    text = re.sub(r"(?m)^www\.thelancet\.com/oncology.*$", "", text)
    text = re.sub(r"(?m)^e\d+\s+www\.thelancet\.com/oncology.*$", "", text)
    text = re.sub(r"(?m)^Policy Review.*$", "", text)
    text = re.sub(r"Statement Level of evidence;\s*\n\s*rate of consensus \(round\)\*", "", text)
    text = text.replace("(Continued from previous page)", "")
    text = re.sub(r"([A-Za-z0-9])-\s*\n\s*([A-Za-z0-9])", r"\1\2", text)
    text = re.sub(r"([A-Za-z])\s*\n\s*([A-Za-z])", r"\1 \2", text)
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def load_pdf_text(pdf_path: str | Path) -> tuple[str, list[int]]:
    if PdfReader is None:  # pragma: no cover - exercised in CLI environments
        raise RuntimeError("pypdf is required for PDF extraction. Install it with `pip install pypdf`.")

    reader = PdfReader(str(pdf_path))
    cleaned_pages = [clean_pdf_page_text(page.extract_text() or "") for page in reader.pages]

    offsets: list[int] = []
    text_chunks: list[str] = []
    cursor = 0
    for page_text in cleaned_pages:
        offsets.append(cursor)
        text_chunks.append(page_text)
        cursor += len(page_text) + 2

    return "\n\n".join(text_chunks), offsets


def page_for_offset(offset: int, page_offsets: list[int]) -> int:
    page_index = bisect_right(page_offsets, offset) - 1
    return page_index + 1


def extract_section_positions(text: str) -> list[tuple[int, str]]:
    positions: list[tuple[int, str]] = []
    for heading, pattern in COMPILED_HEADING_PATTERNS.items():
        for match in pattern.finditer(text):
            canonical = SECTION_ALIASES.get(heading, heading)
            positions.append((match.start(), canonical))
    positions.sort(key=lambda item: item[0])
    return positions


def nearest_section(statement_start: int, section_positions: list[tuple[int, str]]) -> str:
    prior = [section for pos, section in section_positions if pos <= statement_start]
    return prior[-1] if prior else ""


def section_from_number(statement_id: str, number_start: int | None) -> str:
    if statement_id in SECTION_ID_OVERRIDES:
        return SECTION_ID_OVERRIDES[statement_id]
    if number_start is None:
        return ""
    for start, end, section in SECTION_NUMBER_RANGES:
        if start <= number_start <= end:
            return section
    return ""


def parse_statement_number(number_text: str) -> tuple[int | None, int | None]:
    cleaned = number_text.replace("–", "-")
    if not NUMERIC_RANGE_PATTERN.match(cleaned):
        return None, None
    if "-" not in cleaned:
        value = int(cleaned)
        return value, value
    start, end = cleaned.split("-", 1)
    return int(start), int(end)


def extract_statement_rows(text: str, page_offsets: list[int]) -> list[dict]:
    sections = extract_section_positions(text)
    rows: list[dict] = []
    for match in STATEMENT_PATTERN.finditer(text):
        number_start, number_end = parse_statement_number(match.group("number"))
        consensus_pct = float(match.group("consensus_pct").replace("·", "."))
        statement_text = re.sub(r"\s+", " ", match.group("body")).strip()
        statement_id = match.group("statement_id")
        section = section_from_number(statement_id, number_start) or nearest_section(match.start(), sections)
        rows.append(
            {
                "statement_id": statement_id,
                "kind": match.group("kind").lower().replace(" ", "_"),
                "number_text": match.group("number"),
                "number_start": number_start,
                "number_end": number_end,
                "section": section,
                "statement_text": statement_text,
                "level_of_evidence": match.group("level_of_evidence"),
                "consensus_pct": consensus_pct,
                "voting_round": match.group("voting_round"),
                "meets_80pct_table_threshold": consensus_pct >= CONSENSUS_THRESHOLD,
                "page_hint": page_for_offset(match.start(), page_offsets),
            }
        )
    return rows


def mentioned_treatments(text: str) -> list[str]:
    found = []
    fallback_refusal = bool(re.search(r"\b(refuse|decline)\s+total laryngectomy\b", text, re.I))
    for treatment in TARGET_ORDER:
        patterns = COMPILED_TREATMENT_PATTERNS.get(treatment, [])
        if any(pattern.search(text) for pattern in patterns):
            if treatment == "total_laryngectomy" and fallback_refusal:
                continue
            found.append(treatment)
    return found


def infer_decision_scopes(text: str, targets: list[str]) -> list[str]:
    scopes = []
    for scope, patterns in COMPILED_SCOPE_PATTERNS.items():
        if any(pattern.search(text) for pattern in patterns):
            scopes.append(scope)

    if any(target in {"tlm", "tors", "ophl_any", "ophl_type_i", "ophl_type_iib", "ophl_type_ii", "ophl_type_iii"} for target in targets):
        scopes.append("surgical_lp")
    if any(target in {"concurrent_crt", "ict_rt", "rt_alone", "rt_accelerated", "cetuximab_concurrent", "carboplatin_5fu"} for target in targets):
        scopes.append("nonsurgical_lp")
    if scopes:
        scopes.append("larynx_preservation_any")

    deduped = []
    for scope in scopes:
        if scope not in deduped:
            deduped.append(scope)
    return deduped


def classify_statement(statement: dict, targets: list[str], scopes: list[str]) -> str:
    text = statement["statement_text"]
    for label in ("response_adapted", "relative_contraindication", "absolute_contraindication", "exception", "fallback_option", "recommendation"):
        if any(pattern.search(text) for pattern in COMPILED_RULE_PATTERNS[label]):
            return label

    if any(pattern.search(text) for pattern in COMPILED_RULE_PATTERNS["selection_factor"]):
        return "selection_factor"

    if targets or scopes:
        if "surveillance" not in statement.get("section", "").lower():
            return "contextual_selection"

    return "non_decisional"


def graph_candidate_from_class(rule_class: str) -> bool:
    return rule_class in {
        "response_adapted",
        "relative_contraindication",
        "absolute_contraindication",
        "exception",
        "fallback_option",
        "recommendation",
        "selection_factor",
        "contextual_selection",
    }


def rule_direction(rule_class: str) -> str:
    if rule_class in {"absolute_contraindication", "relative_contraindication"}:
        return "negative"
    if rule_class in {"exception", "fallback_option", "recommendation", "response_adapted"}:
        return "positive"
    if rule_class in {"selection_factor", "contextual_selection"}:
        return "qualified"
    return "informational"


def split_series(text: str) -> list[str]:
    items = []
    current = []
    depth = 0
    for char in text:
        if char == "(":
            depth += 1
        elif char == ")" and depth > 0:
            depth -= 1
        if char in ",;" and depth == 0:
            item = "".join(current).strip(" .")
            if item:
                items.append(item)
            current = []
            continue
        current.append(char)
    tail = "".join(current).strip(" .")
    if tail:
        items.append(tail)
    return items


def atomic_conditions(statement_text: str) -> list[str]:
    enumerated = re.split(r"\(\d+\)\s*", statement_text)
    enumerated = [chunk.strip(" .;") for chunk in enumerated if chunk.strip(" .;")]
    if len(enumerated) > 1:
        return enumerated

    if ":" in statement_text:
        _, tail = statement_text.split(":", 1)
        items = split_series(tail)
        if len(items) > 1:
            return items

    return [statement_text.strip()]


def compile_candidate_rules(statements: list[dict]) -> tuple[list[dict], list[dict]]:
    enriched_statements = []
    candidate_rules: list[dict] = []

    for statement in statements:
        targets = mentioned_treatments(statement["statement_text"])
        scopes = infer_decision_scopes(statement["statement_text"], targets)
        statement_class = classify_statement(statement, targets, scopes)
        graph_candidate = graph_candidate_from_class(statement_class)
        conditions = atomic_conditions(statement["statement_text"])

        enriched = dict(statement)
        enriched["mentioned_treatments"] = targets
        enriched["decision_scopes"] = scopes
        enriched["statement_class"] = statement_class
        enriched["graph_candidate"] = graph_candidate
        enriched["atomic_condition_count"] = len(conditions)
        enriched_statements.append(enriched)

        if not graph_candidate:
            continue

        target_list = targets or [""]
        scope_list = scopes or [""]
        row_id = 1
        for target in target_list:
            for scope in scope_list:
                for condition in conditions:
                    candidate_rules.append(
                        {
                            "rule_id": f"{statement['statement_id']}#{row_id}",
                            "statement_id": statement["statement_id"],
                            "section": statement["section"],
                            "page_hint": statement["page_hint"],
                            "rule_class": statement_class,
                            "direction": rule_direction(statement_class),
                            "target_treatment": target,
                            "decision_scope": scope,
                            "condition_text": condition,
                            "level_of_evidence": statement["level_of_evidence"],
                            "consensus_pct": statement["consensus_pct"],
                            "voting_round": statement["voting_round"],
                            "meets_80pct_table_threshold": statement["meets_80pct_table_threshold"],
                        }
                    )
                    row_id += 1

    return enriched_statements, candidate_rules


def load_traceability(traceability_path: str | Path) -> list[dict]:
    with open(traceability_path, newline="") as f:
        return list(csv.DictReader(f))


def build_alignment_rows(
    statements: list[dict],
    candidate_rules: list[dict],
    traceability_rows: list[dict],
) -> list[dict]:
    statement_map = {row["statement_id"]: row for row in statements}
    rules_by_statement: dict[str, list[dict]] = defaultdict(list)
    for row in candidate_rules:
        rules_by_statement[row["statement_id"]].append(row)

    traceability_by_statement: dict[str, list[dict]] = defaultdict(list)
    for row in traceability_rows:
        traceability_by_statement[row["edge_id"]].append(row)

    rows = []
    for statement_id in sorted(traceability_by_statement):
        statement = statement_map.get(statement_id)
        rules = rules_by_statement.get(statement_id, [])
        trace_rows = traceability_by_statement[statement_id]
        families = sorted({row["family"] for row in trace_rows})
        item_ids = sorted({row["item_id"] for row in trace_rows})
        rows.append(
            {
                "statement_id": statement_id,
                "extracted_from_pdf": bool(statement),
                "section": statement["section"] if statement else "",
                "page_hint": statement["page_hint"] if statement else "",
                "consensus_pct": statement["consensus_pct"] if statement else "",
                "voting_round": statement["voting_round"] if statement else "",
                "meets_80pct_table_threshold": statement["meets_80pct_table_threshold"] if statement else "",
                "statement_class": statement["statement_class"] if statement else "",
                "graph_candidate": statement["graph_candidate"] if statement else False,
                "mentioned_treatments": ", ".join(statement["mentioned_treatments"]) if statement else "",
                "decision_scopes": ", ".join(statement["decision_scopes"]) if statement else "",
                "candidate_rule_count": len(rules),
                "families": ", ".join(families),
                "benchmark_item_count": len(item_ids),
                "benchmark_items": ", ".join(item_ids),
            }
        )
    return rows


def build_validation_summary(
    statements: list[dict],
    candidate_rules: list[dict],
    alignment_rows: list[dict],
    traceability_rows: list[dict],
    pdf_path: str | Path,
) -> dict:
    extracted_ids = {row["statement_id"] for row in statements}
    traceability_ids = {row["edge_id"] for row in traceability_rows}
    benchmark_found = sorted(traceability_ids & extracted_ids)
    benchmark_missing = sorted(traceability_ids - extracted_ids)

    benchmark_with_candidate_rules = sorted(
        row["statement_id"] for row in alignment_rows if row["candidate_rule_count"] > 0
    )
    benchmark_without_candidate_rules = sorted(
        row["statement_id"] for row in alignment_rows if row["candidate_rule_count"] == 0
    )
    benchmark_below_threshold = sorted(
        row["statement_id"]
        for row in alignment_rows
        if row["consensus_pct"] != "" and float(row["consensus_pct"]) < CONSENSUS_THRESHOLD
    )

    rule_class_counts = Counter(row["rule_class"] for row in candidate_rules)
    benchmark_class_counts = Counter(
        row["statement_class"] for row in alignment_rows if row["statement_class"]
    )

    return {
        "source_pdf": str(pdf_path),
        "counts": {
            "statement_rows_extracted": len(statements),
            "unique_statement_ids_extracted": len(extracted_ids),
            "statement_rows_meeting_80pct_table_threshold": sum(
                1 for row in statements if row["meets_80pct_table_threshold"]
            ),
            "statement_rows_below_80pct_table_threshold": sum(
                1 for row in statements if not row["meets_80pct_table_threshold"]
            ),
            "candidate_rules_total": len(candidate_rules),
            "candidate_rules_with_explicit_target": sum(1 for row in candidate_rules if row["target_treatment"]),
            "candidate_rules_with_decision_scope": sum(1 for row in candidate_rules if row["decision_scope"]),
            "benchmark_statement_ids": len(traceability_ids),
            "benchmark_statement_ids_found_in_pdf": len(benchmark_found),
            "benchmark_statement_ids_with_candidate_rules": len(benchmark_with_candidate_rules),
        },
        "coverage": {
            "benchmark_missing_from_pdf": benchmark_missing,
            "benchmark_without_candidate_rules": benchmark_without_candidate_rules,
            "benchmark_below_80pct_table_threshold": benchmark_below_threshold,
        },
        "class_counts": {
            "candidate_rule_classes": dict(rule_class_counts),
            "benchmark_statement_classes": dict(benchmark_class_counts),
        },
        "notes": [
            "The PDF table is treated as a source table, not as the sole source of final approval status.",
            "The article reports 137 approved statements, but the visible PDF table includes rows below the 80% threshold and does not encode the appendix-level revision history required to reconstruct final conference approvals deterministically.",
            "Validation therefore checks source-table extraction coverage and benchmark alignment, not conference-level adjudication.",
        ],
    }


def write_csv(path: str | Path, rows: list[dict], fieldnames: list[str]) -> None:
    with open(path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def format_statement_rows_for_csv(rows: list[dict]) -> list[dict]:
    formatted = []
    for row in rows:
        item = dict(row)
        item["mentioned_treatments"] = ", ".join(row.get("mentioned_treatments", []))
        item["decision_scopes"] = ", ".join(row.get("decision_scopes", []))
        formatted.append(item)
    return formatted


def write_validation_markdown(summary: dict, alignment_rows: list[dict], outdir: str | Path) -> None:
    outdir = Path(outdir)
    lines = []
    counts = summary["counts"]

    lines.append("# KG1 Extraction Validation\n")
    lines.append(f"- Source PDF: `{summary['source_pdf']}`")
    lines.append(f"- Statement rows extracted: `{counts['statement_rows_extracted']}`")
    lines.append(f"- Rows meeting 80% table threshold: `{counts['statement_rows_meeting_80pct_table_threshold']}`")
    lines.append(f"- Rows below 80% table threshold: `{counts['statement_rows_below_80pct_table_threshold']}`")
    lines.append(f"- Candidate rules generated: `{counts['candidate_rules_total']}`")
    lines.append(f"- Benchmark statement IDs: `{counts['benchmark_statement_ids']}`")
    lines.append(f"- Benchmark IDs found in PDF extraction: `{counts['benchmark_statement_ids_found_in_pdf']}`")
    lines.append(f"- Benchmark IDs with candidate rules: `{counts['benchmark_statement_ids_with_candidate_rules']}`")
    lines.append("")

    lines.append("## Coverage")
    missing = ", ".join(summary["coverage"]["benchmark_missing_from_pdf"]) or "none"
    without_rules = ", ".join(summary["coverage"]["benchmark_without_candidate_rules"]) or "none"
    below_threshold = ", ".join(summary["coverage"]["benchmark_below_80pct_table_threshold"]) or "none"
    lines.append(f"- Benchmark IDs missing from PDF extraction: `{missing}`")
    lines.append(f"- Benchmark IDs without candidate rules: `{without_rules}`")
    lines.append(f"- Benchmark IDs below the 80% table threshold: `{below_threshold}`")
    lines.append("")

    lines.append("## Notes")
    for note in summary["notes"]:
        lines.append(f"- {note}")
    lines.append("")

    lines.append("## Benchmark Alignment Preview")
    lines.append("| Statement ID | Section | Class | Candidate Rules | Families | 80% Table Threshold |")
    lines.append("|---|---|---|---|---|---|")
    for row in alignment_rows[:25]:
        meets = row["meets_80pct_table_threshold"]
        meets_str = str(meets) if meets != "" else ""
        lines.append(
            f"| `{row['statement_id']}` | `{row['section']}` | `{row['statement_class']}` | `{row['candidate_rule_count']}` | `{row['families']}` | `{meets_str}` |"
        )

    with open(outdir / "validation_report.md", "w") as f:
        f.write("\n".join(lines) + "\n")


def run_pipeline(
    pdf_path: str | Path,
    outdir: str | Path,
    traceability_path: str | Path,
) -> dict:
    outdir = Path(outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    text, page_offsets = load_pdf_text(pdf_path)
    statements = extract_statement_rows(text, page_offsets)
    enriched_statements, candidate_rules = compile_candidate_rules(statements)
    traceability_rows = load_traceability(traceability_path)
    alignment_rows = build_alignment_rows(enriched_statements, candidate_rules, traceability_rows)
    summary = build_validation_summary(enriched_statements, candidate_rules, alignment_rows, traceability_rows, pdf_path)

    dump_json(outdir / "statement_rows.json", enriched_statements)
    dump_json(outdir / "candidate_rules.json", candidate_rules)
    dump_json(outdir / "validation_summary.json", summary)

    write_csv(
        outdir / "statement_rows.csv",
        format_statement_rows_for_csv(enriched_statements),
        [
            "statement_id",
            "kind",
            "number_text",
            "number_start",
            "number_end",
            "section",
            "page_hint",
            "level_of_evidence",
            "consensus_pct",
            "voting_round",
            "meets_80pct_table_threshold",
            "statement_class",
            "graph_candidate",
            "atomic_condition_count",
            "mentioned_treatments",
            "decision_scopes",
            "statement_text",
        ],
    )
    write_csv(
        outdir / "candidate_rules.csv",
        candidate_rules,
        [
            "rule_id",
            "statement_id",
            "section",
            "page_hint",
            "rule_class",
            "direction",
            "target_treatment",
            "decision_scope",
            "condition_text",
            "level_of_evidence",
            "consensus_pct",
            "voting_round",
            "meets_80pct_table_threshold",
        ],
    )
    write_csv(
        outdir / "benchmark_alignment.csv",
        alignment_rows,
        [
            "statement_id",
            "extracted_from_pdf",
            "section",
            "page_hint",
            "consensus_pct",
            "voting_round",
            "meets_80pct_table_threshold",
            "statement_class",
            "graph_candidate",
            "mentioned_treatments",
            "decision_scopes",
            "candidate_rule_count",
            "families",
            "benchmark_item_count",
            "benchmark_items",
        ],
    )
    write_validation_markdown(summary, alignment_rows, outdir)
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description="Extract and validate KG1 candidate rules from the Ferrari PDF.")
    parser.add_argument("--pdf", required=True, help="Path to the Ferrari consensus PDF.")
    parser.add_argument(
        "--traceability",
        default="docs/review/final_benchmark_lock/kg1_traceability_matrix.csv",
        help="Path to the locked KG1 traceability matrix.",
    )
    parser.add_argument(
        "--outdir",
        default="results/kg1_extraction/ferrari_pdf",
        help="Directory for extraction artifacts.",
    )
    args = parser.parse_args()

    summary = run_pipeline(args.pdf, args.outdir, args.traceability)
    counts = summary["counts"]
    print(
        "KG1 extraction complete: "
        f"{counts['statement_rows_extracted']} statement rows, "
        f"{counts['candidate_rules_total']} candidate rules, "
        f"{counts['benchmark_statement_ids_found_in_pdf']}/{counts['benchmark_statement_ids']} "
        "benchmark statement IDs recovered from the PDF."
    )


if __name__ == "__main__":
    main()
