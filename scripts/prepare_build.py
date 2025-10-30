#!/usr/bin/env python3
"""
Prepare a clean build branch from `develop` by removing development-only files
and updating configuration for a production-ready branch.

This is a lightweight, idempotent helper intended for manual use. It is not
used by the test-suite and exists to simplify release workflows.
"""

import shutil
import subprocess
import sys
from pathlib import Path


def run_command(cmd: str, check: bool = True, capture_output: bool = False) -> subprocess.CompletedProcess:
    """Run a shell command and return CompletedProcess."""
    print(f"Running: {cmd}")
    return subprocess.run(
        cmd, shell=True, check=check, capture_output=capture_output, text=True
    )


def get_git_branch() -> str:
    """Return current git branch name or empty string on error."""
    try:
        result = run_command("git branch --show-current", capture_output=True)
        return result.stdout.strip()
    except Exception:
        return ""


def update_pyproject_for_build() -> None:
    """Trim development dependency groups from pyproject.toml in-place.

    This is a best-effort operation: if the file is missing or contains
    unexpected structure, it will be left unchanged.
    """
    pyproject_path = Path("pyproject.toml")
    if not pyproject_path.exists():
        print("pyproject.toml not found, skipping update")
        return

    content = pyproject_path.read_text()
    lines = content.splitlines()
    new_lines = []
    skip_section = False

    for line in lines:
        stripped = line.strip()
        if stripped.startswith("[project.optional-dependencies]"):
            skip_section = True
            new_lines.append(line)
            continue
        if skip_section and stripped.startswith("["):
            skip_section = False
            new_lines.append(line)
            continue
        if skip_section and any(
            k in line for k in ("dev =", "test =", "quality =", "security =")
        ):
            # skip these groups
            continue
        new_lines.append(line)

    pyproject_path.write_text("\n".join(new_lines))
    print("Updated pyproject.toml for production (best-effort)")


def prepare_build_branch() -> None:
    """Create/update a `build` branch from `develop` and remove dev files.

    This function performs non-destructive, reversible operations where
    possible. Use with caution in CI.
    """
    print(" Preparing build branch")

    current = get_git_branch()
    if current != "develop":
        print(f"Switching to develop (current: {current})")
        run_command("git checkout develop")
        run_command("git pull origin develop")

    # Ensure a fresh build branch
    run_command("git branch -D build", check=False)
    run_command("git push origin --delete build", check=False)
    run_command("git checkout -b build")

    # Minimal set of development files to remove in build branch
    build_excludes = [
        "tests/",
        "benchmarks/",
        "scripts/",
        "htmlcov/",
        ".pytest_cache/",
        ".mypy_cache/",
        ".ruff_cache/",
        ".coverage",
    ]

    for pattern in build_excludes:
        p = Path(pattern)
        if p.exists():
            try:
                if p.is_dir():
                    shutil.rmtree(p)
                    print(f"Removed directory: {p}")
                else:
                    p.unlink()
                    print(f"Removed file: {p}")
            except Exception as e:
                print(f"Warning: could not remove {p}: {e}")

    # Update configuration
    update_pyproject_for_build()

    run_command("git add -A")
    run_command('git commit -m "Prepare production build branch"', check=False)
    run_command("git push -u origin build", check=False)

    print(" Build branch prepared (best-effort)")
    run_command("git checkout develop", check=False)


def main() -> None:
    if len(sys.argv) > 1 and sys.argv[1] in ("-h", "--help"):
        print(__doc__)
        return
    prepare_build_branch()


if __name__ == "__main__":
    main()
