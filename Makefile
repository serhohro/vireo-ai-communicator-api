.PHONY: help install test conformance bench vectors serve clean

help:
	@echo "Vireo v3.1 - targets: install, test, conformance, bench, vectors, serve, clean"

install:
	pip install -r requirements.txt

test:
	pytest tests/ -v

conformance:
	pytest tests/conformance/ -v

bench:
	python -m benches.wire_perf.bench_wire --profile=all
	python -m benches.wire_perf.bench_crypto

vectors:
	python scripts/generate_test_vectors.py

serve:
	python -m api.server

clean:
	rm -f nonces.db nonces.db-shm nonces.db-wal did_registry.json keys.json
	rm -rf .pytest_cache .mypy_cache .ruff_cache htmlcov .coverage
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
