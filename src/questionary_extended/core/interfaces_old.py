"""
Core interfaces for questionary-extended architecture.

Defines single-responsibility interfaces that classes can inherit from
based on their specific capabilities and requirements.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, OrderedDict
from collections import OrderedDict as OrderedDictClass


class Renderable(ABC):
    """
    Interface for objects that can render content to the terminal.
    
    Provides delta-aware rendering capabilities with relative positioning.
    """
    
    @abstractmethod
    def get_render_lines(self) -> List[str]:
        """
        Get the lines this renderable should output.
        
        Returns:
            List of strings representing the content to render.
            Empty list if not visible.
        """
        pass
    
    @abstractmethod
    def has_changes(self) -> bool:
        """Check if this renderable needs re-rendering."""
        pass
    
    @abstractmethod
    def render_delta(self, relative_start: int = 0) -> int:
        """
        Render this renderable's changes at relative position.
        
        Args:
            relative_start: Starting line position relative to parent container
            
        Returns:
            Number of lines used by this render
        """
        pass
    
    @abstractmethod
    def mark_dirty(self) -> None:
        """Mark this renderable as needing re-render."""
        pass


class Container(ABC):
    """
    Interface for objects that can contain other objects.
    
    Provides child management and orchestration capabilities.
    """
    
    @abstractmethod
    def add_child(self, child: Any) -> int:
        """Add a child to this container."""
        pass
    
    @abstractmethod
    def remove_child(self, child_id: int) -> None:
        """Remove a child from this container."""
        pass
    
    @abstractmethod
    def get_children(self) -> OrderedDict[int, Any]:
        """Get all children in this container."""
        pass
    
    @abstractmethod
    def has_child(self, name: str) -> bool:
        """Check if container has a child with given name."""
        pass


class Stateful(ABC):
    """
    Interface for objects that manage state values.
    
    Provides state storage, retrieval, and validation capabilities.
    """
    
    @abstractmethod
    def get_state_value(self, key: str, default: Any = None) -> Any:
        """Get a state value."""
        pass
    
    @abstractmethod
    def set_state_value(self, key: str, value: Any) -> None:
        """Set a state value."""
        pass
    
    @abstractmethod
    def is_completed(self) -> bool:
        """Check if this stateful object has completed its requirements."""
        pass
    
    @abstractmethod
    def is_valid(self) -> bool:
        """Check if this stateful object's current state is valid."""
        pass


class Component(ABC):
    """
    Interface for individual interactive/display components.
    
    Provides component identification, visibility, and lifecycle management.
    """
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Unique identifier for this component."""
        pass
    
    @property
    @abstractmethod
    def component_type(self) -> str:
        """Type of component (text_input, select, text_display, etc.)."""
        pass
    
    @property
    @abstractmethod
    def visible(self) -> bool:
        """Whether this component is currently visible."""
        pass
    
    @abstractmethod
    def show(self) -> None:
        """Make this component visible."""
        pass
    
    @abstractmethod
    def hide(self) -> None:
        """Hide this component."""
        pass
    
    @abstractmethod
    def is_interactive(self) -> bool:
        """Whether this component requires user interaction."""
        pass


# Convenience type aliases for common interface combinations
class RenderableContainer(Renderable, Container):
    """Combined interface for containers that can render."""
    pass


class StatefulComponent(Component, Stateful):
    """Combined interface for components that manage state."""
    pass


class RenderableComponent(Component, Renderable):
    """Combined interface for components that can render."""
    pass


class FullComponent(Component, Renderable, Stateful):
    """Combined interface for fully-featured components."""
    pass


class FullContainer(Container, Renderable, Stateful):
    """Combined interface for fully-featured containers."""
    pass


__all__ = [
    # Core interfaces
    "Renderable",
    "Container", 
    "Stateful",
    "Component",
    # Convenience combinations
    "RenderableContainer",
    "StatefulComponent",
    "RenderableComponent", 
    "FullComponent",
    "FullContainer"
]