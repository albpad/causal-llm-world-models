# Repository cleanup notes

This repository was reorganized from an exploratory project folder. Main changes:

1. Created a package-style `src/` layout for reusable code.
2. Moved execution helpers to `scripts/` and notebooks to `notebooks/`.
3. Moved source vignette assets to `data/vignettes/`.
4. Grouped raw outputs, parsed analyses, and world-model metrics under `results/`.
5. Collected manuscript and supporting reports under `manuscript/` and `docs/`.
6. Added `.gitignore`, `requirements.txt`, `pyproject.toml`, and `Makefile`.

The cleanup preserves the original file contents wherever possible and only adjusts imports where needed for the new layout.
