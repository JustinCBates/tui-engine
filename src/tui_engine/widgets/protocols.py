from typing import Protocol, Any, Optional, Sequence, Tuple


class TuiWidgetProtocol(Protocol):
    """Minimal runtime contract for TUI widget wrappers.

    Implementations should attach `_tui_path` and `_tui_focusable` attributes
    and provide a `_tui_sync()` method that pushes widget state back to the
    domain or returns a value that the adapter will apply.
    """

    _tui_path: Optional[str]
    _tui_focusable: bool

    def focus(self) -> None: ...

    def _tui_sync(self) -> Optional[Any]: ...


class ValueWidgetProtocol(TuiWidgetProtocol, Protocol):
    """Widgets that carry a single value (e.g. text inputs).

    Methods:
        get_value() -> Any
        set_value(val)
    """

    def get_value(self) -> Any: ...

    def set_value(self, value: Any) -> None: ...


class ChoiceWidgetProtocol(TuiWidgetProtocol, Protocol):
    """Widgets that expose options and selection(s).

    Expected properties:
        options: Sequence[Tuple[value, label]]
    """

    options: Sequence[Tuple[Any, str]]

    def get_selected(self) -> Any: ...

    def set_selected(self, sel: Any) -> None: ...


class ActionWidgetProtocol(TuiWidgetProtocol, Protocol):
    """Widgets that represent actions (buttons).

    Should expose a `click()` or equivalent to trigger the handler.
    """

    def click(self) -> None: ...
