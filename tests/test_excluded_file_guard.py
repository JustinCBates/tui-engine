import configparser
from pathlib import Path
from typing import List


def _read_omit_list(coveragerc_path: Path) -> List[str]:
    cfg = configparser.ConfigParser()
    cfg.read(coveragerc_path)
    if "run" not in cfg or "omit" not in cfg["run"]:
        return []
    raw = cfg["run"]["omit"]
    # split on newlines and strip
    items = [line.strip() for line in raw.splitlines() if line.strip()]
    return items


def test_omitted_files_have_exclude_header():
    root = Path(__file__).parents[1].resolve()
    covrc = root / ".coveragerc"
    assert covrc.exists(), ".coveragerc not found in repo root"

    patterns = _read_omit_list(covrc)
    missing_headers: List[str] = []
    expanded_files: List[Path] = []

    for pat in patterns:
        # skip comment lines in the config
        if pat.lstrip().startswith("#"):
            continue
        # expand globs relative to repo root
        if any(ch in pat for ch in ["*", "?", "["]):
            matched = list(root.glob(pat))
        else:
            matched = [root / pat]

        for p in matched:
            if p.exists() and p.is_file():
                expanded_files.append(p)

    # For each expanded file that is in the src tree, ensure it contains marker
    import ast

    def _is_trivial(path: Path):
        """Return list of AST problems (empty = trivial)."""
        problems = []
        try:
            src = path.read_text(encoding="utf8")
        except Exception as e:
            return [f"could not read file: {e}"]

        try:
            tree = ast.parse(src)
        except SyntaxError as e:
            return [f"syntax error: {e}"]

        complex_nodes = (ast.For, ast.While, ast.If, ast.Try, ast.With)
        for node in ast.walk(tree):
            if isinstance(node, complex_nodes):
                problems.append(
                    f"complex node {node.__class__.__name__} at line {getattr(node,'lineno', '?')}"
                )

        # Functions containing complex nodes are flagged
        for fn in [n for n in tree.body if isinstance(n, ast.FunctionDef)]:
            for node in ast.walk(fn):
                if isinstance(node, complex_nodes):
                    problems.append(
                        f"function {fn.name} contains {node.__class__.__name__} at line {getattr(node,'lineno','?')}"
                    )

        return problems

    for f in sorted(set(expanded_files)):
        try:
            rel = f.relative_to(root)
        except Exception:
            rel = f
        if "src" not in str(rel):
            continue
        content = f.read_text(encoding="utf8")
        first_lines = "\n".join(content.splitlines()[:20])
        if "COVERAGE_EXCLUDE" not in first_lines:
            missing_headers.append(str(rel))
        else:
            # If the file explicitly allows complexity, skip AST checks
            if "COVERAGE_EXCLUDE_ALLOW_COMPLEX" in first_lines:
                continue
            # run AST triviality check and report any problems
            probs = _is_trivial(f)
            if probs:
                missing_headers.append(
                    str(rel)
                    + " (AST issues: "
                    + ", ".join(probs[:3])
                    + ("..." if len(probs) > 3 else "")
                    + ")"
                )

    if missing_headers:
        msg = (
            "The following files are listed in .coveragerc omit but do not contain the header 'COVERAGE_EXCLUDE' in their first 20 lines:\n"
            + "\n".join(missing_headers)
            + "\n\nPlease add a header comment like:\n# COVERAGE_EXCLUDE: thin wrapper — do not add original logic here\n"
        )
        raise AssertionError(msg)
