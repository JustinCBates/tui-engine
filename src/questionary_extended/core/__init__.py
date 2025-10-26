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
from .component import (
    Component,
    autocomplete,
    checkbox,
    confirm,
    password,
    path,
    select,
    text,
)
from .page_base import PageBase
from .state import PageState

__all__ = [
    "PageBase",
    "Card",
    "AssemblyBase",
    "Component",
    "PageState",
    # Component convenience functions
    "text",
    "select",
    "confirm",
    "password",
    "checkbox",
    "autocomplete",
    "path",
]
