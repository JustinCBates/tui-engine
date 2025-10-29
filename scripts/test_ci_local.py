#!/usr/bin/env python3
"""
Local CI/CD Testing Script

This script simulates the GitHub Actions workflows locally for testing purposes.
Use this to verify your changes before pushing to GitHub.

Usage:
    python scripts/test_ci_local.py [workflow]

    workflows: test, lint, security, build, all (default)
"""

import argparse
import os
import subprocess
import sys
from pathlib import Path


def run_command(cmd, description="", continue_on_error=False):
    """Run a command and handle errors."""
    print(f"\n🔄 {description}")
    print(f"Running: {cmd}")
    print("-" * 50)

    result = subprocess.run(cmd, shell=True, cwd=Path(__file__).parent.parent)

    if result.returncode != 0:
        print(f"❌ Failed: {description}")
        if not continue_on_error:
            sys.exit(1)
        else:
            print("⚠️  Continuing despite failure...")
    else:
        print(f"✅ Success: {description}")

    return result.returncode == 0


def test_workflow():
    """Run the test workflow locally."""
    print("\n🧪 === TEST WORKFLOW ===")

    # Install dependencies (prefer requirements-dev.txt for simple installs)
    req_file = Path(__file__).parent.parent / "requirements-dev.txt"
    if req_file.exists():
        run_command(
            f"pip install -r {req_file}",
            "Installing development dependencies from requirements-dev.txt",
        )
    else:
        run_command(
            'pip install -e ".[dev]"',
            "Installing development dependencies via project metadata",
        )

    # Run tests
    run_command(
        f'"{sys.executable}" -m pytest --cov=src/tui_engine --cov-report=xml --cov-report=term-missing --cov-report=html',
        "Running tests with coverage",
    )


def lint_workflow():
    """Run the lint workflow locally."""
    print("\n🔍 === LINT WORKFLOW ===")

    # Install lint dependencies
    run_command("pip install ruff black mypy", "Installing lint dependencies")

    # Run linting
    run_command(
        "ruff check src/ tests/", "Running ruff linting", continue_on_error=True
    )

    # Run type checking
    run_command("mypy src/", "Running mypy type checking", continue_on_error=True)

    # Run formatting check
    run_command(
        "black --check src/ tests/", "Checking code formatting", continue_on_error=True
    )


def security_workflow():
    """Run the security workflow locally."""
    print("\n🛡️  === SECURITY WORKFLOW ===")

    # Install security tools
    run_command("pip install bandit safety pip-audit", "Installing security tools")

    # Run security checks
    run_command(
        "bandit -r src/ -f json -o bandit-report.json",
        "Running bandit security audit",
        continue_on_error=True,
    )

    run_command(
        "safety check --json --output safety-report.json",
        "Running safety dependency check",
        continue_on_error=True,
    )

    run_command(
        "pip-audit --format=json --output=pip-audit-report.json",
        "Running pip-audit vulnerability scan",
        continue_on_error=True,
    )


def build_workflow():
    """Run the build workflow locally."""
    print("\n🏗️  === BUILD WORKFLOW ===")

    # Install build tools
    run_command("pip install build twine", "Installing build tools")

    # Clean previous builds
    run_command(
        "rm -rf dist/ build/ *.egg-info/",
        "Cleaning previous builds",
        continue_on_error=True,
    )

    # Build package
    run_command("python -m build", "Building package")

    # Check package
    run_command("twine check dist/*", "Checking package with twine")


def performance_workflow():
    """Run performance tests locally."""
    print("\n⚡ === PERFORMANCE WORKFLOW ===")

    # Install performance tools
    run_command(
        "pip install pytest-benchmark memory-profiler", "Installing performance tools"
    )

    # Run benchmarks
    run_command(
        "pytest benchmarks/ --benchmark-json=benchmark-results.json",
        "Running performance benchmarks",
        continue_on_error=True,
    )

    # Test import speed
    import_test = """
import time
start = time.perf_counter()
import tui_engine
end = time.perf_counter()
print(f"Import time: {(end - start) * 1000:.2f}ms")
"""

    with open("temp_import_test.py", "w") as f:
        f.write(import_test)

    run_command(
        "python temp_import_test.py", "Testing import speed", continue_on_error=True
    )

    # Cleanup
    run_command(
        "rm -f temp_import_test.py",
        "Cleaning up temporary files",
        continue_on_error=True,
    )


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Local CI/CD Testing")
    parser.add_argument(
        "workflow",
        nargs="?",
        default="all",
        choices=["test", "lint", "security", "build", "performance", "all"],
        help="Workflow to run (default: all)",
    )

    args = parser.parse_args()

    print("🚀 Local CI/CD Testing Script")
    print("=" * 50)
    print(f"Running workflow: {args.workflow}")

    workflows = {
        "test": test_workflow,
        "lint": lint_workflow,
        "security": security_workflow,
        "build": build_workflow,
        "performance": performance_workflow,
    }

    if args.workflow == "all":
        success_count = 0
        total_count = len(workflows)

        for name, workflow_func in workflows.items():
            try:
                workflow_func()
                success_count += 1
            except SystemExit:
                print(f"❌ Workflow '{name}' failed")

        print("\n📊 === FINAL RESULTS ===")
        print(f"✅ {success_count}/{total_count} workflows passed")

        if success_count == total_count:
            print("🎉 All workflows passed! Ready for GitHub Actions.")
        else:
            print("⚠️  Some workflows failed. Please fix issues before pushing.")
            sys.exit(1)

    else:
        workflows[args.workflow]()
        print(f"\n✅ Workflow '{args.workflow}' completed successfully!")


if __name__ == "__main__":
    main()
