"""tui_engine package - Phase A scaffolding

Minimal exports for the early scaffold. This file lets tests import `tui_engine`.
"""

from .page import Page
from .container import ContainerElement, Element
from .events import EventBus
from .page_state import PageState
from .ptk_widget_factory import map_element_to_widget

__all__ = ["Page", "ContainerElement", "Element", "EventBus", "PageState", "map_element_to_widget"]
