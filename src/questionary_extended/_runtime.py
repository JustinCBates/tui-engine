"""Runtime helpers for resolving the `questionary` dependency.

This module centralizes how the package locates the `questionary` object so
production code and tests share a single contract. Tests should set the
runtime mock via `set_questionary_for_tests` (or by inserting into
`sys.modules['questionary']`) and production code should call `get_questionary()`
to obtain the implementation.
"""

from __future__ import annotations

import importlib
import sys
from typing import Any, Optional

# Cached runtime object (may be a real module or a test-provided SimpleNamespace)
_QUESTIONARY: Optional[Any] = None


def set_questionary_for_tests(obj: Any) -> None:
    """Set the package-level questionary object for tests.

    Tests should call this (or insert into sys.modules) to ensure all code in
    the package sees the same mock. This function is idempotent and reversible
    via :func:`clear_questionary_for_tests`.
    """
    global _QUESTIONARY
    _QUESTIONARY = obj


def clear_questionary_for_tests() -> None:
    """Clear any previously-set questionary object (restores lazy import)."""
    global _QUESTIONARY
    _QUESTIONARY = None


def get_questionary() -> Optional[Any]:
    """Return the resolved `questionary` object or ``None`` if unavailable.

    Resolution order:
    1. If tests have set an explicit runtime object via
       ``set_questionary_for_tests``, return it.
    2. If ``sys.modules['questionary']`` exists (tests often insert a fake
       module there), return it and cache it.
    3. Attempt ``importlib.import_module('questionary')`` and cache/return it.
    4. If import fails, return ``None`` (callers decide whether to raise).
    """
    global _QUESTIONARY
    if _QUESTIONARY is not None:
        return _QUESTIONARY

    q = sys.modules.get("questionary")
    if q is not None:
        _QUESTIONARY = q
        return q

    try:
        q = importlib.import_module("questionary")
        _QUESTIONARY = q
        return q
    except Exception:
        return None
