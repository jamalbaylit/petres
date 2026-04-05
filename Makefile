.PHONY: docs test test-min-deps discover-min-deps apply-min-deps

test:
	uv run --group test pytest

test-min-deps:
	uv pip install --resolution lowest-direct --upgrade . --group test
	uv run --no-sync --group test pytest -ra

discover-min-deps:
	uv run python scripts/discover_min_deps.py

apply-min-deps:
	uv run python scripts/discover_min_deps.py --apply

docs:
	cd docs && make html