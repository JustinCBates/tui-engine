"""Small compatibility shims for prompt-toolkit widgets.

These provide minimal fallback implementations when certain PTK widgets are missing.
They are intentionally tiny and only implement the API surface the adapters/factory use.
"""
from typing import Any, Iterable, List, Tuple


def maybe_checkboxlist(values: Iterable[Tuple[str, str]]) -> Any:
    """Return a real prompt-toolkit CheckboxList if available, otherwise a small fallback.

    The `values` argument is the same shape used by prompt-toolkit: an iterable of (value, label).
    The fallback implements `.values` and `.current_values` to be read/set by adapters.
    """
    try:
        from prompt_toolkit.widgets import CheckboxList

        return CheckboxList(list(values))
    except Exception:
        # Minimal fallback: keep values list and a selected set
        class _FallbackCheckboxList:
            __ptk_repr__ = "fallback.CheckboxList"

            def __init__(self, vals: Iterable[Tuple[str, str]]):
                self.values: List[Tuple[str, str]] = list(vals)
                self.selected: set[str] = set()

            def get_selected_values(self) -> List[str]:
                return [v for v, _ in self.values if v in self.selected]

            def set_selected_values(self, items: Iterable[str]) -> None:
                self.selected = set(items)

            # small helper adapters expect a textual repr for debugging
            def __repr__(self) -> str:
                return f"<FallbackCheckboxList values={len(self.values)} selected={len(self.selected)}>"

        return _FallbackCheckboxList(values)


def maybe_radiolist(values: Iterable[Tuple[str, str]]) -> Any:
    """Return a real prompt-toolkit RadioList if available, otherwise a small fallback.

    The fallback implements `.values` and `.current_value`.
    """
    try:
        from prompt_toolkit.widgets import RadioList

        return RadioList(list(values))
    except Exception:
        class _FallbackRadioList:
            __ptk_repr__ = "fallback.RadioList"

            def __init__(self, vals: Iterable[Tuple[str, str]]):
                self.values: List[Tuple[str, str]] = list(vals)
                self.current_value = None

            def get_selected(self) -> Any:
                return self.current_value

            def set_selected(self, value: Any) -> None:
                self.current_value = value

            def __repr__(self) -> str:
                return f"<FallbackRadioList values={len(self.values)} current={self.current_value}>"

        return _FallbackRadioList(values)
