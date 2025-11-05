"""Widget Protocol definitions for tui_engine wrappers.

This file defines the minimal Protocol surface used by the PTK adapters.
Wrappers should implement these protocols; adapters rely on `_tui_sync`
and `focus` to coordinate widget <> element state.
"""
from __future__ import annotations

from typing import Any, Protocol, Sequence, runtime_checkable


@runtime_checkable
class TuiWidgetProtocol(Protocol):
    """Minimal runtime contract for TUI widget wrappers.

    Implementations should attach `_tui_path` and `_tui_focusable` attributes
    and provide a `_tui_sync()` method that pushes widget state back to the
    domain or returns a value that the adapter will apply.
    """

    _tui_path: str | None
    _tui_focusable: bool

    def focus(self) -> None: ...

    def _tui_sync(self) -> Any | None: ...


@runtime_checkable
class ValueWidgetProtocol(TuiWidgetProtocol, Protocol):
    """Widgets that carry a single value (e.g. text inputs).

    Methods:
        get_value() -> Any
        set_value(val)
    """

    def get_value(self) -> Any: ...

    def set_value(self, value: Any) -> None: ...


@runtime_checkable
class ChoiceWidgetProtocol(TuiWidgetProtocol, Protocol):
    """Widgets that expose options and selection(s).

    Expected properties:
        options: Sequence[Tuple[value, label]]
    """

    options: Sequence[tuple[Any, str]]

    def get_selected(self) -> Any: ...

    def set_selected(self, sel: Any) -> None: ...


@runtime_checkable
class ActionWidgetProtocol(TuiWidgetProtocol, Protocol):
    """Widgets that represent actions (buttons).

    Should expose a `click()` or equivalent to trigger the handler.
    """

    def click(self) -> None: ...
