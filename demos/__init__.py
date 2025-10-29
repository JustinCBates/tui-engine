"""Demos package for the tui-engine repository.

This file makes the `demos` directory an importable package so modules can be
imported as `demos.xxx` and scripts can be run with `python -m demos.main_menu`.

Recommended usage:
  # from the repo root
  python -m demos.main_menu

The `demos/main_menu.py` script also contains a small convenience helper that
adds the project root to `sys.path` when running the script directly from the
`demos/` directory; that helper is intentionally left in place to preserve
the casual `python ./main_menu.py` workflow.
"""

__all__ = [
    "main_menu",
    "demo_form",
    "demo_container",
  # backward compatibility wrappers
  "container_demo",
]
