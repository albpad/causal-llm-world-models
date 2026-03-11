.PHONY: install dev test package clean

install:
	pip install -e .

dev:
	pip install -e .[dev]

test:
	pytest

package:
	python -m build

clean:
	find . -type d -name "__pycache__" -prune -exec rm -rf {} +
	find . -type f \( -name "*.pyc" -o -name ".DS_Store" \) -delete
