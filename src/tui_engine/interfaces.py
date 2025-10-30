from typing import Any, List, Optional


class IElement:
    """Minimal interface for elements.

    Kept intentionally lightweight so adapters and other modules can import
    the interface without pulling in concrete implementations.
    """
    def __init__(self, name: str, variant: str = "container"):
        self.name = name
        self.variant = variant
        # Use Any here to avoid circular import with ContainerElement.
        self.parent: Optional[Any] = None
        self.visible: bool = True
        self.metadata: dict = {}
        self._dirty = True

    @property
    def path(self) -> str:
        parts = []
        from typing import Any

        node: Any = self
        while node is not None and getattr(node, "name", None) is not None:
            parts.append(node.name)
            node = node.parent
        return ".".join(reversed(parts))

    def get_render_lines(self, width: int = 80) -> List[str]:
        raise NotImplementedError()

    def to_ptk_container(self, adapter: Any) -> Any:
        raise NotImplementedError()

    def mark_dirty(self) -> None:
        self._dirty = True

    def clear_dirty(self) -> None:
        self._dirty = False

    def is_dirty(self) -> bool:
        return self._dirty

    def on_mount(self, page_state: Any) -> None:
        pass

    def on_unmount(self, page_state: Any) -> None:
        pass
