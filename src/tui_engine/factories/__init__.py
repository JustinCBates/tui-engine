"""Domain-level factories for creating Element instances.

These are backend-agnostic; adapters map the created Element instances to
concrete UI widgets (for example prompt-toolkit adapters in
`tui_engine.widgets`).
"""
from typing import Optional, Callable, Any

from ..container import ContainerElement
from ..element import Element


def text(name: str, value: str = "") -> Element:
    return Element(name, variant="text", value=value)


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
