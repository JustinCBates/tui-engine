#!/usr/bin/env python3
"""Simple checker to detect bash-only constructs in changed files.

Intended to be used as a local pre-commit hook. It scans files passed as
arguments and fails if it finds obvious bash-only idioms such as heredocs
(`<<`), `||`, or `&&` which are likely to break PowerShell users.
"""
import sys
import re
from pathlib import Path

PATTERNS = [
    (re.compile(r"<<\s*['\"]?\w+['\"]?"), "heredoc '<<' found"),
    (re.compile(r"\|\|"), "bash '||' found"),
    (re.compile(r"&&"), "bash '&&' found"),
]


def scan_file(path: Path):
    text = path.read_text(encoding="utf8", errors="ignore")
    findings = []
    for pat, msg in PATTERNS:
        if pat.search(text):
            findings.append(msg)
    return findings


def main(argv):
    if not argv:
        print("Usage: check_no_bash.py <file> [files...]")
        return 0

    bad = False
    for p in argv:
        path = Path(p)
        if not path.exists():
            continue
        findings = scan_file(path)
        if findings:
            bad = True
            print(f"{path}: ")
            for f in findings:
                print(f"  - {f}")

    if bad:
        print("\nDetected bash-only constructs. Please rewrite examples to be PowerShell-safe or exclude binary/third-party files.")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
