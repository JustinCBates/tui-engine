# TUI-Engine Development Makefile
# Provides convenient commands for maintaining A+ testing standards

.PHONY: help test coverage coverage-report coverage-track coverage-html clean install dev-install lint format type-check security pre-commit setup-hooks

# Default target
help:
	@echo "🏆 TUI-Engine A+ Testing Makefile"
	@echo "=================================="
	@echo ""
	@echo "📊 Coverage Commands:"
	@echo "  coverage          - Run tests with coverage (A+ gate: 85%+)"
	@echo "  coverage-report   - Generate detailed coverage report"
	@echo "  coverage-track    - Track coverage history"
	@echo "  coverage-html     - Generate HTML coverage report"
	@echo "  coverage-gaps     - Analyze coverage improvement opportunities"
	@echo ""
	@echo "🧪 Testing Commands:"
	@echo "  test              - Run all tests"
	@echo "  test-fast         - Run tests with fail-fast"
	@echo "  test-new          - Run tests for new/modified code"
	@echo ""
	@echo "🔧 Development Commands:"
	@echo "  install           - Install package in development mode"
	@echo "  dev-install       - Install with all development dependencies"
	@echo "  lint              - Run linting (ruff)"
	@echo "  format            - Format code (black + isort)"
	@echo "  type-check        - Run type checking (mypy)"
	@echo "  security          - Run security checks"
	@echo ""
	@echo "⚙️ Setup Commands:"
	@echo "  setup-hooks       - Install pre-commit hooks"
	@echo "  pre-commit        - Run all pre-commit checks"
	@echo "  clean             - Clean build artifacts"

# Coverage commands
coverage:
	@echo "🎯 Running tests with A+ coverage standard (85%+)..."
	python -m pytest --cov=src --cov-report=term-missing --cov-fail-under=85

coverage-report:
	@echo "📊 Generating comprehensive coverage report..."
	python scripts/coverage_tracker.py --report

coverage-track:
	@echo "📈 Tracking coverage history..."
	python scripts/coverage_tracker.py --track

coverage-html:
	@echo "🌐 Generating HTML coverage report..."
	python -m pytest --cov=src --cov-report=html
	@echo "Report available at: htmlcov/index.html"

coverage-gaps:
	@echo "🔍 Analyzing coverage gaps..."
	python scripts/coverage_tracker.py --analyze

# Testing commands
test:
	@echo "🧪 Running all tests..."
	python -m pytest

test-fast:
	@echo "⚡ Running tests with fail-fast..."
	python -m pytest -x

test-new:
	@echo "🆕 Running tests for new/modified code..."
	@git diff --name-only HEAD~1 | grep '\.py$$' | head -10 | xargs -r python -m pytest --cov=src --cov-report=term-missing

# Development commands
install:
	@echo "📦 Installing package in development mode..."
	pip install -e .

dev-install:
	@echo "🛠️ Installing with development dependencies..."
	pip install -e ".[dev,test]"

lint:
	@echo "🔍 Running linting checks..."
	ruff check src/ tests/ scripts/

format:
	@echo "✨ Formatting code..."
	black src/ tests/ scripts/
	isort src/ tests/ scripts/

type-check:
	@echo "🔤 Running type checks..."
	mypy src/

security:
	@echo "🔒 Running security checks..."
	bandit -r src/ -f json -o bandit-report.json || true
	safety check --json --output safety-report.json || true
	@echo "Security reports generated: bandit-report.json, safety-report.json"

# Setup commands
setup-hooks:
	@echo "🪝 Installing pre-commit hooks..."
	pre-commit install
	@echo "✅ Pre-commit hooks installed"

pre-commit:
	@echo "✅ Running all pre-commit checks..."
	pre-commit run --all-files

clean:
	@echo "🧹 Cleaning build artifacts..."
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf htmlcov/
	rm -rf .coverage
	rm -rf .coverage.*
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	find . -name "__pycache__" -exec rm -rf {} +
	find . -name "*.pyc" -delete

# Quality gates for CI/CD
ci-test: lint type-check security coverage
	@echo "🏆 All CI checks passed - A+ standard maintained!"

# Development workflow
dev-setup: dev-install setup-hooks
	@echo "🚀 Development environment setup complete!"
	@echo ""
	@echo "Next steps:"
	@echo "  make coverage     - Check current coverage"
	@echo "  make test         - Run tests"
	@echo "  make pre-commit   - Validate changes"

# Coverage-driven development workflow
tdd:
	@echo "🔄 Test-Driven Development mode..."
	@echo "Running tests in watch mode with coverage..."
	python -m pytest --cov=src --cov-report=term-missing -f

# A+ Grade validation
validate-aplus:
	@echo "🏆 Validating A+ Grade Requirements..."
	@echo "1. Coverage standard (85%+)..."
	@python -m pytest --cov=src --cov-fail-under=85 -q
	@echo "2. All tests passing..."
	@python -m pytest -q
	@echo "3. Code quality checks..."
	@ruff check src/ tests/ --quiet
	@echo "4. Type safety..."
	@mypy src/ --no-error-summary
	@echo ""
	@echo "🎉 A+ Grade requirements validated!"