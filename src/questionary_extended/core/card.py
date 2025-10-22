"""
Card class for questionary-extended.

The Card class provides visual grouping of related components with styling options,
dynamic show/hide capabilities, and responsive layout management.
"""

from typing import Any, Dict, List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from .page import Page


class Card:
    """
    Visual grouping container for related components.
    
    Provides:
    - Visual styling options (minimal, bordered, highlighted, collapsible)
    - Dynamic show/hide with smooth transitions
    - Horizontal/vertical layout with responsive fallback
    - Component overflow handling and scrolling
    """
    
    def __init__(self, title: str, parent: "Page", style: str = "minimal"):
        """
        Initialize a new Card.
        
        Args:
            title: Card title/header
            parent: Parent Page instance
            style: Visual style (minimal, bordered, highlighted, collapsible)
        """
        self.title = title
        self.parent_page = parent
        self.style = style
        self.components: List[Any] = []
        self.visible = True
        
    def text(self, name: str, **kwargs) -> "Card":
        """
        Add a text input component.
        
        Args:
            name: Component name for state storage
            **kwargs: Component configuration options
            
        Returns:
            Self for method chaining
        """
        # Implementation pending Component wrappers
        raise NotImplementedError("Component wrappers not yet implemented")
        
    def select(self, name: str, choices: List[str], **kwargs) -> "Card":
        """
        Add a selection component.
        
        Args:
            name: Component name for state storage  
            choices: List of selection options
            **kwargs: Component configuration options
            
        Returns:
            Self for method chaining
        """
        # Implementation pending Component wrappers
        raise NotImplementedError("Component wrappers not yet implemented")
        
    def show(self) -> None:
        """Make this card visible."""
        self.visible = True
        
    def hide(self) -> None:
        """Hide this card."""
        self.visible = False
        
    def parent(self) -> "Page":
        """Return parent Page for navigation."""
        return self.parent_page


__all__ = ["Card"]