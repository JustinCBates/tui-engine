"""tui_engine package - Phase A scaffolding

Minimal exports for the early scaffold. This file lets tests import `tui_engine`.
"""

from .container import Container
from .element import Element
from .events import EventBus
from .page import Page
from .page_state import PageState
from .ptk_widget_factory import map_element_to_widget
from .themes import TUIEngineThemes
from .questionary_adapter import QuestionaryStyleAdapter

__all__ = [
    "Page", 
    "Container", 
    "Element", 
    "EventBus", 
    "PageState", 
    "map_element_to_widget",
    "TUIEngineThemes",
    "QuestionaryStyleAdapter"
]
