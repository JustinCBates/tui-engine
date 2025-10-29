from .container import ContainerElement
from .page_state import PageState
from .events import EventBus
from typing import List, Optional

class Page:
    def __init__(self, title: str = ""):
        self.title = title
        self.root = ContainerElement("root", variant="page")
        self.page_state = PageState()
        self.events = EventBus()

    def add(self, element: ContainerElement):
        self.root.add(element)
        return self

    def container(self, name: str, variant: str = "container", **kwargs) -> ContainerElement:
        return self.root.child(name, variant=variant)

    def render(self, width: int = 80) -> List[str]:
        lines: List[str] = []
        if self.title:
            lines.append(self.title)
            lines.append("=" * min(len(self.title), width))
        lines.extend(self.root.get_render_lines(width))
        return lines

    def run_application(self, fullscreen: bool = False, **adapter_opts):
        raise RuntimeError("PTK adapter not implemented in Phase A scaffold")
