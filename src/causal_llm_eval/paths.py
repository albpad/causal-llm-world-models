"""Path helpers for package-local data and repository-relative assets."""
from __future__ import annotations
from pathlib import Path

PACKAGE_ROOT = Path(__file__).resolve().parent
SRC_ROOT = PACKAGE_ROOT.parent
REPO_ROOT = SRC_ROOT.parent
DATA_DIR = REPO_ROOT / "data"
VIGNETTES_DIR = DATA_DIR / "vignettes"
FINETUNING_DIR = DATA_DIR / "finetuning"
RESULTS_DIR = REPO_ROOT / "results"
ANALYSIS_DIR = RESULTS_DIR / "analysis"

def vignette_battery_path() -> Path:
    return VIGNETTES_DIR / "vignette_battery.json"

def resolve_repo_path(*parts: str) -> Path:
    return REPO_ROOT.joinpath(*parts)
