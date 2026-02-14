.PHONY: install test lint format clean docker-build

install:
	pip install -e ".[dev]"

test:
	pytest --cov=fxagent --cov-report=term-missing

lint:
	ruff check src/ tests/
	mypy src/

format:
	ruff check --fix src/ tests/
	ruff format src/ tests/

clean:
	rm -rf dist/ build/ *.egg-info .pytest_cache .mypy_cache .ruff_cache
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true

docker-build:
	docker build -t fxagent .
