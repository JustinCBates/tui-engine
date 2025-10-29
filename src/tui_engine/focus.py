"""Focus registry and basic traversal utilities.

This is a small, testable FocusRegistry that keeps an ordered list of focusable
element identifiers (we use element.path as the stable id). It supports:
- register(element): add focusable element
- unregister(element): remove
- focus_next() / focus_prev(): move focus with wrap
- set_focused(element_or_path): programmatic focus
- get_focused(): returns the currently focused id or None
- modal_trap(context_id): context manager to temporarily limit traversal

The registry is intentionally lightweight and synchronous; the PTK adapter
will integrate with prompt-toolkit key bindings and Application.invalidate().
"""
from __future__ import annotations

from contextlib import contextmanager
from typing import List, Optional


class FocusRegistry:
    def __init__(self):
        # ordered list of focusable ids (strings: element.path)
        self._order: List[str] = []
        self._focused: Optional[str] = None
        # If set, traversal is limited to entries in this set
        self._trap_set: Optional[set] = None

    def register(self, element) -> None:
        pid = getattr(element, "path", None)
        if pid is None:
            return
        if pid in self._order:
            return
        self._order.append(pid)
        if self._focused is None:
            self._focused = pid

    def unregister(self, element) -> None:
        pid = getattr(element, "path", None)
        if pid is None:
            return
        if pid in self._order:
            self._order.remove(pid)
        if self._focused == pid:
            self._focused = self._order[0] if self._order else None

    def set_focused(self, element_or_path) -> Optional[str]:
        pid = element_or_path if isinstance(element_or_path, str) else getattr(element_or_path, "path", None)
        if pid is None:
            return None
        if pid not in self._order:
            return None
        if self._trap_set is not None and pid not in self._trap_set:
            return None
        self._focused = pid
        return self._focused

    def get_focused(self) -> Optional[str]:
        return self._focused

    def _effective_order(self) -> List[str]:
        if self._trap_set is None:
            return list(self._order)
        return [p for p in self._order if p in self._trap_set]

    def focus_next(self) -> Optional[str]:
        eff = self._effective_order()
        if not eff:
            return None
        if self._focused not in eff:
            self._focused = eff[0]
            return self._focused
        idx = eff.index(self._focused)
        idx = (idx + 1) % len(eff)
        self._focused = eff[idx]
        return self._focused

    def focus_prev(self) -> Optional[str]:
        eff = self._effective_order()
        if not eff:
            return None
        if self._focused not in eff:
            self._focused = eff[-1]
            return self._focused
        idx = eff.index(self._focused)
        idx = (idx - 1) % len(eff)
        self._focused = eff[idx]
        return self._focused

    @contextmanager
    def modal_trap(self, element_paths):
        """Temporarily restrict traversal to provided element_paths (iterable of ids).

        Usage:
            with registry.modal_trap(["page.header.btn1", "page.header.btn2"]):
                registry.focus_next()
        """
        prev = self._trap_set
        try:
            self._trap_set = set(element_paths)
            # If current focus is outside trap, set to first trapped item if present
            eff = self._effective_order()
            if eff and self._focused not in eff:
                self._focused = eff[0]
            yield
        finally:
            self._trap_set = prev
