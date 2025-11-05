"""Domain-level factories for creating Element instances.

These are backend-agnostic; adapters map the created Element instances to
concrete UI widgets (for example prompt-toolkit adapters in
`tui_engine.widgets`).
"""
from typing import Any, Callable, Optional

from ..container import Container
from ..element import Element


def text(name: str, value: str = "", *, offset: Optional[int] = None, **metadata: Any) -> Element:
    # Accept offset and arbitrary metadata to support adapter layout hints.
    e = Element(name, variant="text", value=value)
    if offset is not None:
        try:
            e.metadata['offset'] = int(offset)
        except Exception:
            pass
    # Merge any extra metadata provided by callers
    try:
        for k, v in metadata.items():
            e.metadata.setdefault(k, v)
    except Exception:
        pass
    return e


def input(name: str, value: str = "", on_enter: Optional[Callable[..., Any]] = None, *, enter_moves_focus: Optional[bool] = None) -> Element:
    e = Element(name, variant="input", value=value, focusable=True)
    if on_enter is not None:
        try:
            e.on_enter = on_enter
        except Exception:
            e.metadata['on_enter'] = on_enter
    if enter_moves_focus is not None:
        try:
            e.metadata['enter_moves_focus'] = bool(enter_moves_focus)
        except Exception:
            pass
    return e


def button(label: str, on_click: Optional[Callable[..., Any]] = None) -> Element:
    e = Element(label, variant="button", focusable=True)
    if on_click is not None:
        try:
            e.on_click = on_click
        except Exception:
            e.metadata['on_click'] = on_click
    return e

__all__ = ["text", "input", "button"]
