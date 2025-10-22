"""
Core components for questionary-extended.

This module contains the fundamental building blocks:
- Page: Top-level container for multi-component UIs
- Card: Visual grouping of related components  
- Assembly: Interactive component groups with conditional logic
- Component: Enhanced questionary component wrappers
- State: Page-scoped state management with assembly namespacing
"""

from .page import Page
from .card import Card  
from .assembly import Assembly
from .component import Component, text, select, confirm, password, checkbox
from .state import PageState

__all__ = [
    "Page",
    "Card", 
    "Assembly",
    "Component",
    "PageState",
    # Component convenience functions
    "text",
    "select", 
    "confirm",
    "password",
    "checkbox",
]