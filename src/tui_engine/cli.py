"""Minimal CLI entrypoint for the tui_engine package.

This module provides a tiny set of functions so packaging/CI tools and
coverage helpers can import and exercise the CLI without pulling heavy
interactive dependencies.
"""
from __future__ import annotations

import sys


def demo():
    """Run a lightweight demo (no interactive prompts)."""
    print("TUI Engine demo: headless run")


def form_builder():
    print("TUI Engine form builder (no-op)")


def themes():
    print("TUI Engine themes list (no-op)")


def wizard_demo(times: int = 1):
    print(f"TUI Engine wizard demo x{times}")


def quick(ptype: str):
    print(f"Quick demo for {ptype}")


def main():
    """Simple main entry used by packaging scripts.

    This intentionally does not require third-party interactive libs.
    """
    print("TUI Engine CLI - no interactive runtime available in CI")


if __name__ == "__main__":
    main()
