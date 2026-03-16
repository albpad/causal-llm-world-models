"""Canonical and aggregate treatment label helpers."""

from __future__ import annotations

from copy import deepcopy

AGGREGATE_MEMBERS = {
    "ophl_any": ["ophl_type_i", "ophl_type_iib", "ophl_type_ii", "ophl_type_iii"],
    "surgical_lp": ["tlm", "tors", "ophl_any", "ophl_type_i", "ophl_type_iib", "ophl_type_ii", "ophl_type_iii"],
    "nonsurgical_lp": [
        "concurrent_crt",
        "ict_rt",
        "rt_alone",
        "rt_accelerated",
        "cetuximab_concurrent",
        "carboplatin_5fu",
    ],
}

AGGREGATE_LABELS = set(AGGREGATE_MEMBERS)


def derive_aggregate_labels(labels: dict[str, str]) -> dict[str, str]:
    """Add aggregate treatment labels derived from concrete treatment labels."""
    expanded = dict(labels)
    for aggregate, members in AGGREGATE_MEMBERS.items():
        member_labels = [expanded[m] for m in members if m in expanded]
        if not member_labels:
            continue
        if any(label == "recommended" for label in member_labels):
            expanded[aggregate] = "recommended"
        elif any(label == "relative_ci" for label in member_labels):
            expanded[aggregate] = "relative_ci"
        elif any(label == "uncertain" for label in member_labels):
            expanded[aggregate] = "uncertain"
    return expanded


def derive_aggregate_stance_records(records: dict[str, dict]) -> dict[str, dict]:
    """Add aggregate stance records derived from concrete stance records."""
    expanded = deepcopy(records)
    label_map = {tx: row["stance"] for tx, row in records.items()}
    derived = derive_aggregate_labels(label_map)
    for aggregate, label in derived.items():
        members = [records[m] for m in AGGREGATE_MEMBERS.get(aggregate, []) if m in records]
        if members:
            expanded[aggregate] = {
                "treatment": aggregate,
                "stance": label,
                "confidence": max(member["confidence"] for member in members),
                "evidence": f"Derived from {', '.join(member['treatment'] for member in members)}",
                "phase": "derived",
            }
        elif aggregate not in expanded:
            continue
    return expanded


def normalise_expected_label_lists(recommended: list[str], excluded: list[str]) -> tuple[list[str], list[str]]:
    """Normalise gold labels so aggregate labels are derived from concrete labels only."""
    concrete = {}

    for label in recommended:
        if label not in AGGREGATE_LABELS:
            concrete[label] = "recommended"

    for label in excluded:
        if label not in AGGREGATE_LABELS:
            concrete[label] = "excluded"

    normalised = derive_aggregate_labels(concrete)

    rec = sorted([label for label, stance in normalised.items() if stance == "recommended"])
    exc = sorted([label for label, stance in normalised.items() if stance == "excluded"])
    return rec, exc
