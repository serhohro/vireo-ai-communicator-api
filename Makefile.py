# VIREO v3.0.0 — Makefile
# Open Wire Protocol · WASM · Rust · Formal Verification
# ============================================================

.PHONY: help install test lint format clean build publish docs \
        test-unit test-conformance test-interop test-performance \
        build-wasm build-rust docker docker-build docker-run \
        security audit bench coverage

# Variables
PYTHON = python3
PIP = pip
PWD = $(shell pwd)

help:
	@echo "🌿 Vireo v3.0.0 — Available commands:"
	@echo ""
	@echo "📦 Installation:"
	@echo "  make install        Install Python dependencies"
	@echo "  make install-all    Install all dependencies (Python + Rust + WASM)"
	@echo ""
	@echo "🧪 Testing:"
	@echo "  make test           Run all tests"
	@echo "  make test-unit      Run unit tests"
	@echo "  make test-conformance Run conformance tests"
	@echo "  make test-interop   Run interoperability tests"
	@echo "  make test-performance Run performance tests"
	@echo ""
	@echo "🔧 Development:"
	@echo "  make lint           Run linters"
	@echo "  make format         Format code"
	@echo "  make clean          Clean artifacts"
	@echo "  make coverage       Generate coverage report"
	@echo ""
	@echo "⚡ Build:"
	@echo "  make build          Build Python package"
	@echo "  make build-wasm     Build WASM runtime"
	@echo "  make build-rust     Build Rust SDK"
	@echo "  make build-all      Build everything"
	@echo ""
	@echo "🐳 Docker:"
	@echo "  make docker         Build Docker image"
	@echo "  make docker-run     Run Docker container"
	@echo ""
	@echo "📚 Documentation:"
	@echo "  make docs           Build documentation"
	@echo "  make docs-serve     Serve documentation"
	@echo ""
	@echo "🔐 Security:"
	@echo "  make security       Run security checks"
	@echo "  make audit          Audit dependencies"
	@echo ""
	@echo "📊 Benchmarks:"
	@echo "  make bench          Run benchmarks"
	@echo ""

# ============================================================
# INSTALLATION
# ============================================================

install:
	$(PIP) install -e .[dev,test,docs]

install-all: install
	@echo "📦 Installing Rust SDK..."
	cd sdk/rust && cargo build --release
	@echo "📦 Installing TypeScript SDK..."
	cd sdk/typescript && npm install && npm run build
	@echo "📦 Building WASM..."
	$(MAKE) build-wasm

install-eu:
	$(PIP) install -e .[eu-llm]

# ============================================================
# TESTING
# ============================================================

test:
	pytest tests/ -v --cov=core --cov=protocol --cov=language --cov=runtime --cov-report=html --cov-report=term

test-unit:
	pytest tests/unit/ -v

test-conformance:
	pytest tests/conformance/ -v

test-interop:
	pytest tests/interop/ -v

test-performance:
	pytest tests/performance/ -v -m benchmark

test-wasm:
	pytest tests/wasm/ -v

test-rust:
	cd sdk/rust && cargo test

test-all: test test-rust test-wasm

coverage:
	pytest tests/ --cov=core --cov=protocol --cov=language --cov=runtime --cov-report=html
	@echo "📊 Coverage report: htmlcov/index.html"

# ============================================================
# DEVELOPMENT
# ============================================================

lint:
	ruff check core/ protocol/ language/ runtime/ api/ tests/
	mypy core/ protocol/ language/ runtime/ api/
	flake8 core/ protocol/ language/ runtime/ api/ tests/

format:
	black core/ protocol/ language/ runtime/ api/ tests/
	ruff check --fix core/ protocol/ language/ runtime/ api/ tests/

clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	rm -rf .ruff_cache/
	rm -rf htmlcov/
	rm -rf .coverage
	rm -rf .tox/
	rm -rf .benchmarks/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.so" -delete
	find . -type f -name "*.o" -delete

# ============================================================
# BUILD
# ============================================================

build: clean
	$(PYTHON) -m build

build-wasm:
	@echo "⚡ Building WASM..."
	cd sdk/rust && wasm-pack build --target web --out-dir ../../web/wasm
	@echo "✅ WASM built: web/wasm/"

build-rust:
	@echo "🦀 Building Rust SDK..."
	cd sdk/rust && cargo build --release
	@echo "✅ Rust SDK built: sdk/rust/target/release/"

build-all: build build-wasm build-rust

# ============================================================
# DOCKER
# ============================================================

docker:
	docker build -t vireo:v3 -f docker/Dockerfile.python .

docker-run:
	docker run -p 5000:5000 -v $(PWD)/keys:/app/keys vireo:v3

docker-compose:
	docker-compose -f docker/docker-compose.yml up

docker-compose-down:
	docker-compose -f docker/docker-compose.yml down

# ============================================================
# DOCUMENTATION
# ============================================================

docs:
	mkdocs build

docs-serve:
	mkdocs serve

# ============================================================
# SECURITY
# ============================================================

security:
	@echo "🔐 Running security checks..."
	bandit -r core/ protocol/ language/ runtime/ api/
	safety check
	pip-audit

audit:
	@echo "📊 Auditing dependencies..."
	pip-audit -r requirements.txt
	cargo audit --manifest-path sdk/rust/Cargo.toml
	npm audit --prefix sdk/typescript

# ============================================================
# BENCHMARKS
# ============================================================

bench:
	@echo "📊 Running benchmarks..."
	pytest tests/performance/ -v --benchmark-only --benchmark-json=benchmarks.json
	@echo "✅ Benchmarks saved to benchmarks.json"

bench-wire:
	@echo "📊 Wire Format benchmarks..."
	pytest tests/performance/test_wire_format.py -v --benchmark-only

bench-rust:
	@echo "📊 Rust benchmarks..."
	cd sdk/rust && cargo bench

# ============================================================
# PUBLISH
# ============================================================

publish: build
	twine upload dist/*

publish-test: build
	twine upload --repository testpypi dist/*

# ============================================================
# DEVELOPMENT SERVER
# ============================================================

dev:
	$(PYTHON) api/server.py --debug

prod:
	$(PYTHON) api/server.py --production

# ============================================================
# GENERATE TEST VECTORS
# ============================================================

vectors:
	$(PYTHON) scripts/generate_test_vectors.py

# ============================================================
# MIGRATION
# ============================================================

migrate:
	$(PYTHON) scripts/migrate_v2_to_v3.py

# ============================================================
# DEFAULT
# ============================================================

default: help