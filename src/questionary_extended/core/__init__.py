"""
Core components for questionary-extended.

This module contains the fundamental building blocks:
- Page: Top-level container for multi-component UIs

- Card: Visual grouping of related components
- Assembly: Interactive component groups with conditional logic
- Component: Enhanced questionary component wrappers
- State: Page-scoped state management with assembly namespacing
"""

from .assembly_base import AssemblyBase
from .card import Card
from .component_wrappers import (
    Component,
    # Prompt components (require user input)
    text_prompt,
    select_prompt,
    confirm_prompt,
    password_prompt,
    checkbox_prompt,
    autocomplete_prompt,
    path_prompt,
    # Display components (information only)
    text_display,
    text_section,
    text_status,
)
from .page_base import PageBase
from .state import PageState

__all__ = [
    "PageBase",
    "Card",
    "AssemblyBase",
    "Component",
    "PageState",
    # Prompt components (require user input)
    "text_prompt",
    "select_prompt",
    "confirm_prompt",
    "password_prompt",
    "checkbox_prompt",
    "autocomplete_prompt",
    "path_prompt",
    # Display components (information only)
    "text_display",
    "text_section",
    "text_status",
]
