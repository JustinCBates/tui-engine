"""RadioListAdapter: wrapper for single-select radio list widgets.

This adapter implements ChoiceWidgetProtocol and wraps either a real
prompt-toolkit RadioList (when available) or a lightweight fake object used
in tests. It exposes `ptk_widget` to access the real widget for layout
insertion while providing `get_selected`, `set_selected`, `focus` and
`_tui_sync` for the adapter surface.
"""
from __future__ import annotations

from typing import Any, Iterable, Sequence

from .protocols import ChoiceWidgetProtocol


class RadioListAdapter(ChoiceWidgetProtocol):
    # runtime contract attributes (may be set by factory on underlying widget)
    _tui_path: str | None = None
    _tui_focusable: bool = True
    # expose options attribute to satisfy ChoiceWidgetProtocol
    options: Sequence[tuple[Any, str]] = ()

    def __init__(self, widget: Any | None = None, element: Any | None = None):
        self._widget = widget
        self.element = element

    def focus(self) -> None:
        w = self._widget
        if w is None:
            return
        if hasattr(w, "focus") and callable(w.focus):
            try:
                w.focus()
            except Exception:
                pass

    def _tui_sync(self) -> Any | None:
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
                return w.current_value
            # some variants expose `selected` or `value`
            if hasattr(w, "selected"):
                return w.selected
            if hasattr(w, "value"):
                return w.value
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
        from typing import Any

        val: Any = None
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
                w.current_value = val
                return
            if hasattr(w, "selected"):
                w.selected = val
                return
            if hasattr(w, "value"):
                w.value = val
                return
        except Exception:
            pass

    @property
    def ptk_widget(self) -> Any:
        return self._widget

    def __repr__(self) -> str:  # pragma: no cover - trivial
        return f"<RadioListAdapter widget={self._widget!r}>"
