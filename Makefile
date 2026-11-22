PYTHON ?= python

.PHONY: install data test run docker

install:
	$(PYTHON) -m pip install -e ".[dev]"

data:
	$(PYTHON) scripts/generate_synthetic_data.py

test:
	$(PYTHON) -m compileall -q vitalink tests scripts
	pytest

run:
	uvicorn vitalink.api:app --reload

docker:
	docker compose up --build
