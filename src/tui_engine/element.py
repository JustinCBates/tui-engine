from typing import Any, List, Optional

from .interfaces import IElement


class Element(IElement):
    validators: list[Any]
    on_click: Any | None
    on_enter: Any | None
    def __init__(self, name: str, variant: str = "text", *, focusable: bool = False, value: Optional[str] = None) -> None:
        super().__init__(name, variant=variant)
        self.focusable = focusable
        self._value = value
        self.validators = []
        # Optional user-provided handlers/hooks
        self.on_click = None
        self.on_enter = None

    def get_value(self) -> Optional[str]:
        return self._value

    def set_value(self, v: Optional[str]) -> None:
        self._value = v
        self.mark_dirty()

    def get_render_lines(self, width: int = 80) -> List[str]:
        text = str(self._value) if self._value is not None else ""
        return [text]
