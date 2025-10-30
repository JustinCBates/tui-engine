from typing import Any, List, Optional

from .element import Element
from .interfaces import IElement


class ContainerElement(IElement):
    def __init__(self, name: str, variant: str = "container", *, layout_hint: str = "vertical"):
        super().__init__(name, variant=variant)
        self.children: List[IElement] = []
        self.layout_hint = layout_hint
        self.focus_scope: bool = False
        self.include_hidden_in_validity: bool = False

    def add(self, child: IElement) -> "ContainerElement":
        child.parent = self
        self.children.append(child)
        self.mark_dirty()
        return self

    def remove(self, child: IElement) -> None:
        if child in self.children:
            self.children.remove(child)
            child.parent = None
            self.mark_dirty()

    def child(self, name: str, variant: str = "container", **kwargs: Any) -> "ContainerElement":
        # kwargs are accepted for forward-compatibility with factory-style
        # constructors; keep them typed as Any to avoid mypy disallow_untyped_defs
        # errors while preserving runtime flexibility.
        c = ContainerElement(name, variant=variant)
        self.add(c)
        return c
    # NOTE: previously this class exposed convenience constructors for
    # concrete widgets (text/input/button). Those were removed to keep
    # `ContainerElement` strictly structural. Use the factories in
    # `tui_engine.widgets` and `container.add(...)` to attach widgets.

    def get_focusable_children(self) -> List[IElement]:
        return [c for c in self.children if getattr(c, "focusable", False)]

    def get_render_lines(self, width: int = 80) -> List[str]:
        lines: List[str] = []
        # simple header for container
        if self.variant and self.variant != "container":
            lines.append(f"[{self.variant.upper()}] {self.name}")
        for child in self.children:
            if not getattr(child, "visible", True):
                continue
            child_lines = child.get_render_lines(width)
            for ln in child_lines:
                lines.append("  " + ln)
        return lines
