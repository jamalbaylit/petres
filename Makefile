.PHONY: docs

test:
	uv run --group test pytest

docs:
	cd docs && make html