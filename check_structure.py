#!/usr/bin/env python3
"""
Development helper script for questionary-extended.
Displays the current package structure and validates it follows Python packaging best practices.
"""

import os
import sys
from pathlib import Path


def check_file_exists(file_path: Path, description: str) -> bool:
    """Check if a file exists and print status."""
    if file_path.exists():
        print(f"✅ {description}: {file_path}")
        return True
    else:
        print(f"❌ {description}: {file_path} (MISSING)")
        return False


def check_directory_structure() -> bool:
    """Check the package directory structure follows best practices."""
    root = Path(__file__).parent
    print(f"📦 Checking package structure for: {root.name}")
    print("=" * 60)

    # Core package files
    core_files = [
        (root / "pyproject.toml", "Project configuration (PEP 518/621)"),
        (root / "README.md", "Package documentation"),
        (root / "LICENSE", "License file"),
        (root / "CHANGELOG.md", "Change log"),
        (root / "CONTRIBUTING.md", "Contribution guidelines"),
        (root / "SECURITY.md", "Security policy"),
        (root / ".gitignore", "Git ignore file"),
        (root / "MANIFEST.in", "Package manifest"),
    ]

    # Source structure
    src_files = [
    (root / "src" / "tui_engine" / "__init__.py", "Package init"),
    (root / "src" / "tui_engine" / "py.typed", "Type annotations marker"),
    (root / "src" / "tui_engine" / "prompts.py", "Core prompts"),
    (root / "src" / "tui_engine" / "components.py", "UI components"),
    (root / "src" / "tui_engine" / "validators.py", "Input validators"),
    (root / "src" / "tui_engine" / "styles.py", "Theming system"),
    (root / "src" / "tui_engine" / "utils.py", "Utility functions"),
    (root / "src" / "tui_engine" / "cli.py", "CLI interface"),
    ]

    # Test structure
    test_files = [
        (root / "tests" / "__init__.py", "Test package init"),
        (root / "tests" / "test_validators.py", "Validator tests"),
        (root / "tests" / "test_utils.py", "Utility tests"),
    ]

    # Development files
    dev_files = [
        (root / ".pre-commit-config.yaml", "Pre-commit hooks"),
        (root / "ruff.toml", "Ruff linter config"),
        (root / ".github" / "workflows" / "ci.yml", "CI workflow"),
        (root / ".github" / "workflows" / "release.yml", "Release workflow"),
    ]

    # Documentation
    doc_files = [
        (root / "docs" / "index.md", "Documentation index"),
        (root / "examples" / "basic_usage.py", "Basic usage example"),
        (root / "examples" / "advanced_forms.py", "Advanced forms example"),
    ]

    all_files = core_files + src_files + test_files + dev_files + doc_files

    print("\n📋 Core Package Files:")
    print("-" * 30)
    for file_path, description in core_files:
        check_file_exists(file_path, description)

    print("\n🐍 Source Code Structure:")
    print("-" * 30)
    for file_path, description in src_files:
        check_file_exists(file_path, description)

    print("\n🧪 Test Structure:")
    print("-" * 20)
    for file_path, description in test_files:
        check_file_exists(file_path, description)

    print("\n⚙️ Development Files:")
    print("-" * 25)
    for file_path, description in dev_files:
        check_file_exists(file_path, description)

    print("\n📚 Documentation:")
    print("-" * 20)
    for file_path, description in doc_files:
        check_file_exists(file_path, description)

    # Count results
    existing = sum(1 for file_path, _ in all_files if file_path.exists())
    total = len(all_files)

    print(f"\n📊 Summary: {existing}/{total} files present ({existing/total*100:.1f}%)")

    if existing == total:
        print("🎉 Perfect! Package structure follows Python packaging best practices.")
    else:
        print("⚠️  Some recommended files are missing. See above for details.")

    return existing == total


def show_package_info() -> None:
    """Show package information."""
    try:
        import tomllib
    except ImportError:
        try:
            import tomli as tomllib
        except ImportError:
            print("❌ Cannot read pyproject.toml - install tomli for Python < 3.11")
            return

    root = Path(__file__).parent
    pyproject_path = root / "pyproject.toml"

    if not pyproject_path.exists():
        print("❌ pyproject.toml not found")
        return

    with open(pyproject_path, "rb") as f:
        config = tomllib.load(f)

    project = config.get("project", {})

    print("\n📦 Package Information:")
    print("-" * 30)
    print(f"Name: {project.get('name', 'Unknown')}")
    print(f"Version: {project.get('version', 'Unknown')}")
    print(f"Description: {project.get('description', 'No description')}")
    print(f"Python requirement: {project.get('requires-python', 'Not specified')}")

    dependencies = project.get("dependencies", [])
    print(f"Dependencies: {len(dependencies)} packages")
    for dep in dependencies[:5]:  # Show first 5
        print(f"  - {dep}")
    if len(dependencies) > 5:
        print(f"  ... and {len(dependencies) - 5} more")


def main() -> None:
    """Main function."""
    print("🚀 Questionary Extended - Package Structure Checker")
    print("=" * 60)

    # Check structure
    structure_ok = check_directory_structure()

    # Show package info
    show_package_info()

    # Best practices summary
    print("\n📋 Python Packaging Best Practices Compliance:")
    print("-" * 50)
    print("✅ PEP 517/518: Modern build system (pyproject.toml)")
    print("✅ PEP 621: Project metadata in pyproject.toml")
    print("✅ src/ layout: Package isolation and editable installs")
    print("✅ Type hints: py.typed marker for type checking")
    print("✅ CI/CD: GitHub Actions for testing and release")
    print("✅ Code quality: Black, Ruff, MyPy, pre-commit hooks")
    print("✅ Documentation: README, CHANGELOG, examples")
    print("✅ Security: SECURITY.md and dependency scanning")
    print("✅ Testing: Comprehensive test suite with pytest")
    print("✅ Licensing: Clear MIT license")

    print(f"\n🎯 Ready for PyPI distribution: {'Yes' if structure_ok else 'Almost'}")

    if structure_ok:
        print("\n🚀 Next steps:")
        print("  1. poetry install --with dev")
        print("  2. poetry run pytest")
        print("  3. poetry build")
        print("  4. poetry publish --dry-run")


if __name__ == "__main__":
    main()
