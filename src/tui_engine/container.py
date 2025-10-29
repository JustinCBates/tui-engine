from typing import List, Optional, Any

class IElement:
    """Minimal interface for elements"""
    def __init__(self, name: str, variant: str = "container"):
        self.name = name
        self.variant = variant
        self.parent: Optional["ContainerElement"] = None
        self.visible: bool = True
        self.metadata: dict = {}
        self._dirty = True

    @property
    def path(self) -> str:
        parts = []
        node = self
        while node is not None and getattr(node, "name", None) is not None:
            parts.append(node.name)
            node = node.parent
        return ".".join(reversed(parts))

    def get_render_lines(self, width: int = 80) -> List[str]:
        raise NotImplementedError()

    def to_ptk_container(self, adapter: Any):
        raise NotImplementedError()

    def mark_dirty(self):
        self._dirty = True

    def clear_dirty(self):
        self._dirty = False

    def is_dirty(self) -> bool:
        return self._dirty

    def on_mount(self, page_state: Any):
        pass

    def on_unmount(self, page_state: Any):
        pass


class Element(IElement):
    def __init__(self, name: str, variant: str = "text", *, focusable: bool = False, value: Optional[str] = None):
        super().__init__(name, variant=variant)
        self.focusable = focusable
        self._value = value
        self.validators = []

    def get_value(self):
        return self._value

    def set_value(self, v):
        self._value = v
        self.mark_dirty()

    def get_render_lines(self, width: int = 80) -> List[str]:
        text = str(self._value) if self._value is not None else ""
        return [text]


class ContainerElement(IElement):
    def __init__(self, name: str, variant: str = "container", *, layout_hint: str = "vertical"):
        super().__init__(name, variant=variant)
        self.children: List[IElement] = []
        self.layout_hint = layout_hint
        self.focus_scope = False
        self.include_hidden_in_validity = False

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

    def child(self, name: str, variant: str = "container", **kwargs) -> "ContainerElement":
        c = ContainerElement(name, variant=variant)
        self.add(c)
        return c

    def text(self, name: str, value: str = "") -> Element:
        e = Element(name, variant="text", value=value)
        self.add(e)
        return e

    def input(self, name: str, value: str = "") -> Element:
        e = Element(name, variant="input", value=value, focusable=True)
        self.add(e)
        return e

    def button(self, label: str, *, on_click=None) -> Element:
        e = Element(label, variant="button", focusable=True)
        # attach a simple on_click handler if provided so adapters/factories
        # can wire it into real widgets
        if on_click is not None:
            try:
                setattr(e, 'on_click', on_click)
            except Exception:
                e.metadata['on_click'] = on_click
        self.add(e)
        return e

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
