#!/usr/bin/env python3
"""Launch the clinician review app."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from causal_llm_eval.review_server import main


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
