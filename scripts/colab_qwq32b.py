#!/usr/bin/env python3
"""Preset wrapper for the QwQ-32B research pipeline."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from causal_llm_eval.research_app import main


if __name__ == "__main__":
    raise SystemExit(main(["--preset", "qwq32b", *sys.argv[1:]]))
