.PHONY: install run test lint

install:
	pip install -e '.[dev]'

run:
	uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

test:
	pytest -q

lint:
	ruff check .
