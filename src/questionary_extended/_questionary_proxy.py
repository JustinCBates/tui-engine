"""A small proxy that provides a monkeypatchable `questionary` object.

This proxy supports:
- attribute overrides (tests can monkeypatch attributes on the proxy)
- delegation to the centralized runtime accessor when an attribute isn't
  overridden (so runtime mocks installed via _runtime are used)
- safe default placeholder callables that raise clear errors if used when
  not configured.

This keeps modules import-safe (no prompt_toolkit sessions at import time)
while preserving tests' ability to monkeypatch module.questionary.*
"""
from __future__ import annotations

from types import SimpleNamespace
from typing import Any, Callable, Dict
import importlib


def _default_placeholder(*a: object, **kw: object) -> object:
    raise NotImplementedError("questionary is not configured in this environment")


class QuestionaryProxy:
    """Proxy object that is safe to import and monkeypatch.

    Behavior:
    - getattr(name): return overrides[name] if set;
      else consult questionary_extended._runtime.get_questionary()
      and return getattr(real_q, name) if available; else return a
      placeholder callable.
    - setattr(name, value): store in overrides so monkeypatch.setattr works.
    """

    def __init__(self) -> None:
        # store overrides in a simple dict; avoid recursion in __getattr__
        object.__setattr__(self, "_overrides", {})

    def __getattr__(self, name: str) -> Any:
        overrides: Dict[str, Any] = object.__getattribute__(self, "_overrides")
        if name in overrides:
            return overrides[name]

        # Try the runtime accessor
        try:
            rt = importlib.import_module("questionary_extended._runtime")
            q = rt.get_questionary()
        except Exception:
            q = None

        if q is not None and hasattr(q, name):
            return getattr(q, name)

        # Return a callable placeholder for common factory names
        return _default_placeholder

    def __setattr__(self, name: str, value: Any) -> None:
        # Put everything into overrides (tests will replace functions).
        overrides: Dict[str, Any] = object.__getattribute__(self, "_overrides")
        overrides[name] = value

    def __delattr__(self, name: str) -> None:
        """Support delattr so test monkeypatch teardown can remove overrides.

        Removes the override if present; otherwise raise AttributeError to
        match normal object semantics.
        """
        overrides: Dict[str, Any] = object.__getattribute__(self, "_overrides")
        if name in overrides:
            del overrides[name]
            return
        raise AttributeError(name)

    def __dir__(self) -> list[str]:
        # Useful for introspection in tests/tools
        overrides: Dict[str, Any] = object.__getattribute__(self, "_overrides")
        names = set(overrides.keys())
        # Try to include real questionary attributes when available
        try:
            rt = importlib.import_module("questionary_extended._runtime")
            q = rt.get_questionary()
            if q is not None:
                names.update(dir(q))
        except Exception:
            pass
        return sorted(names)


# Single shared instance to import as `questionary` from modules
questionary_proxy = QuestionaryProxy()
