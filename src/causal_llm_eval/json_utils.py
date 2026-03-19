"""Helpers for writing strict JSON artifacts."""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any


def json_safe(value: Any) -> Any:
    if isinstance(value, float):
        return value if math.isfinite(value) else None
    if isinstance(value, dict):
        return {key: json_safe(item) for key, item in value.items()}
    if isinstance(value, list):
        return [json_safe(item) for item in value]
    if isinstance(value, tuple):
        return [json_safe(item) for item in value]
    return value


def dump_json(path: str | Path, value: Any, *, indent: int = 2, default: Any | None = None) -> None:
    with open(path, "w") as f:
        json.dump(json_safe(value), f, indent=indent, default=default, allow_nan=False)
