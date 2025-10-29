"""CheckboxListAdapter: wrapper for multi-select checkbox-list widgets.

Implements ChoiceWidgetProtocol. Works with prompt-toolkit CheckboxList when
available or a simple fake object for tests. Exposes `.ptk_widget`, focus,
`_tui_sync`, `get_selected`, and `set_selected`.
"""
from __future__ import annotations

from typing import Any, Iterable, List, Optional

from .protocols import ChoiceWidgetProtocol


class CheckboxListAdapter(ChoiceWidgetProtocol):
    # runtime contract attributes
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

    def _tui_sync(self) -> Optional[List[Any]]:
        """Return a list of selected values from the underlying widget."""
        w = self._widget
        if w is None:
            return None
        try:
            # common names: checked_values, current_values, selected
            if hasattr(w, "checked_values"):
                return list(getattr(w, "checked_values"))
            if hasattr(w, "current_values"):
                return list(getattr(w, "current_values"))
            if hasattr(w, "selected"):
                v = getattr(w, "selected")
                try:
                    return list(v)
                except Exception:
                    return [v]
        except Exception:
            pass
        return None

    def get_selected(self) -> Iterable[Any]:
        v = self._tui_sync()
        return [] if v is None else list(v)

    def set_selected(self, selected: Iterable[Any]) -> None:
        # Normalize to list
        vals = []
        try:
            for s in selected:
                vals.append(s)
        except Exception:
            # treat selected as single value
            vals = [selected]

        w = self._widget
        if w is None:
            return
        try:
            if hasattr(w, "checked_values"):
                try:
                    setattr(w, "checked_values", vals)
                    return
                except Exception:
                    pass
            if hasattr(w, "current_values"):
                try:
                    setattr(w, "current_values", vals)
                    return
                except Exception:
                    pass
            if hasattr(w, "selected"):
                try:
                    setattr(w, "selected", set(vals))
                    return
                except Exception:
                    pass
        except Exception:
            pass

    @property
    def ptk_widget(self) -> Any:
        return self._widget

    def __repr__(self) -> str:  # pragma: no cover - trivial
        return f"<CheckboxListAdapter widget={self._widget!r}>"
