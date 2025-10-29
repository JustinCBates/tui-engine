"""RadioListAdapter: wrapper for single-select radio list widgets.

This adapter implements ChoiceWidgetProtocol and wraps either a real
prompt-toolkit RadioList (when available) or a lightweight fake object used
in tests. It exposes `ptk_widget` to access the real widget for layout
insertion while providing `get_selected`, `set_selected`, `focus` and
`_tui_sync` for the adapter surface.
"""
from __future__ import annotations

from typing import Any, Iterable, List, Optional

from .protocols import ChoiceWidgetProtocol


class RadioListAdapter(ChoiceWidgetProtocol):
    # runtime contract attributes (may be set by factory on underlying widget)
    _tui_path: Optional[str] = None
    _tui_focusable: bool = True

    def __init__(self, widget: Optional[Any] = None, element: Optional[Any] = None):
        self._widget = widget
        self.element = element

    def focus(self) -> None:
        w = self._widget
        if w is None:
            return
        if hasattr(w, "focus") and callable(getattr(w, "focus")):
            try:
                w.focus()
            except Exception:
                pass

    def _tui_sync(self) -> Optional[Any]:
        """Read the selected value from the wrapped widget and return it.

        For RadioList single-select semantics, return the raw selected value.
        The PTKAdapter will write it back to the domain element.
        """
        w = self._widget
        if w is None:
            return None
        try:
            # common attribute name for RadioList
            if hasattr(w, "current_value"):
                return getattr(w, "current_value")
            # some variants expose `selected` or `value`
            if hasattr(w, "selected"):
                return getattr(w, "selected")
            if hasattr(w, "value"):
                return getattr(w, "value")
        except Exception:
            pass
        return None

    def get_selected(self) -> Iterable[Any]:
        sel = self._tui_sync()
        if sel is None:
            return []
        return [sel]

    def set_selected(self, selected: Iterable[Any]) -> None:
        # Accept either an iterable or a single value; use the first element
        val = None
        try:
            # if it's a string or single value, treat it as scalar
            if isinstance(selected, (str, bytes)):
                val = selected
            else:
                # try to iterate
                for s in selected:
                    val = s
                    break
        except Exception:
            val = selected

        w = self._widget
        if w is None:
            return
        try:
            if hasattr(w, "current_value"):
                setattr(w, "current_value", val)
                return
            if hasattr(w, "selected"):
                setattr(w, "selected", val)
                return
            if hasattr(w, "value"):
                setattr(w, "value", val)
                return
        except Exception:
            pass

    @property
    def ptk_widget(self) -> Any:
        return self._widget

    def __repr__(self) -> str:  # pragma: no cover - trivial
        return f"<RadioListAdapter widget={self._widget!r}>"
