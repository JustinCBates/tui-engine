"""Button wrapper adapter implementing ActionWidgetProtocol.

Provides a small, testable surface around prompt_toolkit Button or any
button-like object. Exposes `click()`, `focus()`, and `_tui_sync()` so the
PTK adapter can coordinate actions and state.
"""
from __future__ import annotations

from typing import Any

from tui_engine.widgets.protocols import ActionWidgetProtocol


class ButtonAdapter(ActionWidgetProtocol):
    """Wrap a button-like widget and expose a stable testable API.

    Args:
        widget: real prompt-toolkit Button (or a fake with similar surface)
        element: optional domain element this widget is bound to
    """

    _tui_path: str | None
    _tui_focusable: bool

    def __init__(self, widget: Any, element: Any | None = None) -> None:
        self._widget = widget
        self._element = element

        # Mirror runtime contract attributes on the adapter
        self._tui_path = getattr(widget, "_tui_path", None)
        self._tui_focusable = bool(getattr(widget, "_tui_focusable", True))

    @property
    def ptk_widget(self) -> Any:
        """Return the underlying raw widget for insertion into layouts."""
        return self._widget

    def focus(self) -> None:
        try:
            if hasattr(self._widget, "focus") and callable(self._widget.focus):
                try:
                    self._widget.focus()
                    return
                except Exception:
                    pass
            # Some widgets support a 'window' or 'container' focus API
            if hasattr(self._widget, "container") and hasattr(self._widget.container, "focus"):
                try:
                    self._widget.container.focus()
                except Exception:
                    pass
        except Exception:
            pass

    def _tui_sync(self) -> Any | None:
        """Buttons typically do not carry value; ensure element state is preserved.

        This is a no-op for most buttons but kept for symmetry with other
        adapters. Return None or any diagnostic payload.
        """
        return None

    def click(self) -> None:
        """Trigger the button action. Try the raw widget handler first, then
        fall back to calling the domain element's `on_click` if present."""
        # Try raw widget handler
        try:
            # prompt-toolkit Button exposes a `handler` attribute
            handler = getattr(self._widget, "handler", None)
            if callable(handler):
                try:
                    handler()
                except Exception:
                    # swallow widget handler exceptions and continue to element
                    pass

        except Exception:
            pass

        # Then call the element's on_click if present
        try:
            if self._element is not None:
                h = getattr(self._element, "on_click", None)
                if callable(h):
                    try:
                        h()
                    except Exception:
                        pass
        except Exception:
            pass
