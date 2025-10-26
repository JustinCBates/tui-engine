"""Pre-commit hook: ensure files omitted from coverage are marked and simple.

This script checks the repo's .coveragerc omit list and enforces:
- Each omitted file under src/ contains the header marker COVERAGE_EXCLUDE in the first 20 lines.
- A simple AST sanity check: functions should be thin (no loops/ifs/try/with).

Exit codes: non-zero indicates a failing hook.
"""

import ast
import configparser
import sys
from pathlib import Path

ROOT = Path(__file__).parents[2].resolve()
COVRC = ROOT / ".coveragerc"


def _read_omit_list(coveragerc_path: Path):
    cfg = configparser.ConfigParser()
    cfg.read(coveragerc_path)
    if "run" not in cfg or "omit" not in cfg["run"]:
        return []
    raw = cfg["run"]["omit"]
    items = [line.strip() for line in raw.splitlines() if line.strip()]
    return items


def _is_trivial_ast(path: Path):
    """Return list of problems found in AST; empty = trivial."""
    problems = []
    try:
        src = path.read_text(encoding="utf8")
    except Exception as e:
        return [f"could not read file: {e}"]

    try:
        tree = ast.parse(src)
    except SyntaxError as e:
        return [f"syntax error: {e}"]

    # Disallow complex statements at top level beyond imports, docstring, simple assignments, function/class defs
    complex_nodes = (ast.For, ast.While, ast.If, ast.Try, ast.With)
    for node in ast.walk(tree):
        if isinstance(node, complex_nodes):
            problems.append(
                f"complex statement {node.__class__.__name__} found at line {getattr(node, 'lineno', '?')}"
            )

    # Inspect each function body for complexity
    for fn in [n for n in tree.body if isinstance(n, ast.FunctionDef)]:
        # disallow loops/ifs/try/with inside functions
        for node in ast.walk(fn):
            if isinstance(node, complex_nodes):
                problems.append(
                    f"function {fn.name} contains {node.__class__.__name__} at line {getattr(node,'lineno', '?')}"
                )

    return problems


def main():
    if not COVRC.exists():
        print(".coveragerc not found; skipping check")
        return 0

    patterns = _read_omit_list(COVRC)
    missing = []
    ast_problems = []

    for pat in patterns:
        if pat.lstrip().startswith("#"):
            continue
        # expand globs
        if any(ch in pat for ch in ["*", "?", "["]):
            matched = list(ROOT.glob(pat))
        else:
            matched = [ROOT / pat]

        for p in matched:
            if p.exists() and p.is_file():
                # only enforce for src tree
                try:
                    rel = p.relative_to(ROOT)
                except Exception:
                    rel = p
                if "src" not in str(rel):
                    continue

                txt = p.read_text(encoding="utf8")
                first20 = "\n".join(txt.splitlines()[:20])
                if "COVERAGE_EXCLUDE" not in first20:
                    missing.append(str(rel))
                else:
                    probs = _is_trivial_ast(p)
                    if probs:
                        ast_problems.append((str(rel), probs))

    if missing or ast_problems:
        print("ERROR: Coverage-excluded file policy violations:\n")
        if missing:
            print("Files missing COVERAGE_EXCLUDE header:")
            for m in missing:
                print("  -", m)
            print()
        if ast_problems:
            print("AST complexity problems in excluded files:")
            for fname, probs in ast_problems:
                print(f"  - {fname}:")
                for p in probs:
                    print("     ", p)
            print()
        print(
            "Please either add the header or move complex logic into non-excluded modules."
        )
        return 1

    print("OK: excluded files contain header and passed AST sanity checks")
    return 0


if __name__ == "__main__":
    sys.exit(main())
