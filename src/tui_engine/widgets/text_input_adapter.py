"""Text input wrapper implementing ValueWidgetProtocol.

This adapter wraps either a real prompt-toolkit TextArea-like object or a
very small fake object used in tests. It provides the minimal contract
expected by the PTKAdapter: focus(), _tui_sync(), get_value(), set_value().
"""
from __future__ import annotations

from typing import Any

from .protocols import ValueWidgetProtocol

try:
    from prompt_toolkit.widgets import TextArea  # type: ignore
    _PTK_AVAILABLE = True
except Exception:
    TextArea = None  # type: ignore
    _PTK_AVAILABLE = False


class TextInputAdapter(ValueWidgetProtocol):
    # runtime contract attributes required by TuiWidgetProtocol
    _tui_path: str | None = None
    _tui_focusable: bool = True
    """Wrapper for text inputs.

    Args:
        widget: The real widget to wrap (e.g., prompt_toolkit.widgets.TextArea)
                or a simple object with a `text` attribute. If None, a
                simple in-memory fallback is used.
    """

    def __init__(self, widget: Any | None = None) -> None:
        # If a widget is None, create a minimal fallback object with `.text`.
        if widget is None:
            class _Fallback:
                def __init__(self, text: str = "") -> None:
                    self.text = text
                    # Provide a buffer attribute to satisfy attribute checks
                    # and provide a `.text` property used by some adapters.
                    class _Buf:
                        text: str

                        def __init__(self, text: str = "") -> None:
                            self.text = text

                    self.buffer = _Buf(text)
                    # Provide a .value attribute to satisfy callers and type checkers
                    self.value = text

                def focus(self) -> None:
                    # No-op, but present for tests
                    return None

                def __repr__(self) -> str:
                    return f"<_Fallback text={self.text!r}>"

            self._widget = _Fallback("")
        else:
            self._widget = widget

        # last synced value (useful in tests and for adapter-driven sync)
        self._last_synced: str = ""

    def focus(self) -> None:
        w = self._widget
        if w is None:
            return
        if hasattr(w, "focus") and callable(w.focus):
            try:
                w.focus()
            except Exception:
                return

    def _tui_sync(self) -> None:
        # Pull the current widget value into _last_synced.
        self._last_synced = self.get_value() or ""

    def get_value(self) -> str:
        w = self._widget
        if w is None:
            return ""
        # Common prompt-toolkit TextArea exposes .text
        if hasattr(w, "text"):
            val = w.text
            return "" if val is None else str(val)
        # Some widget-like objects use .buffer.text
        if hasattr(w, "buffer") and hasattr(w.buffer, "text"):
            val = w.buffer.text
            return "" if val is None else str(val)
        try:
            return str(w)
        except Exception:
            return ""

    def set_value(self, value: str) -> None:
        w = self._widget
        if w is None:
            return
        if hasattr(w, "text"):
            try:
                w.text = value
                return
            except Exception:
                pass
        if hasattr(w, "buffer") and hasattr(w.buffer, "text"):
            try:
                w.buffer.text = value
                return
            except Exception:
                pass
        try:
            w.value = value
        except Exception:
            return

    def __repr__(self) -> str:  # pragma: no cover - trivial
        return f"<TextInputAdapter widget={self._widget!r}>"

    @property
    def ptk_widget(self) -> Any:
        """Return the underlying prompt-toolkit widget (if any).

        PTKAdapter expects a `.ptk_widget` or a raw widget so it can mount
        and focus the real UI control. Exposing this keeps adapters thin.
        """
        return self._widget
