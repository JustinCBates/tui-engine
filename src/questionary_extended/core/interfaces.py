"""
Comprehensive interfaces for questionary-extended architecture.

This file contains all core interfaces that define the contract for elements,
containers, rendering, and state management within the TUI engine.

Architecture:
- ElementInterface: Base for all displayable items
- PageChildInterface: Elements that can be placed in Page containers
- CardChildInterface: Elements that can be placed in Card containers  
- AssemblyChildInterface: Elements that can be placed in Assembly containers
- ComponentInterface: Interactive elements (buttons, inputs, etc.)
- ContainerInterface: Elements that hold other elements
- Renderable: Delta-aware rendering capabilities
- Stateful: State management capabilities

Containment Rules:
- Page can contain: Component, Card, Assembly (PageChildInterface)
- Card can contain: Component, Assembly (CardChildInterface) 
- Assembly can contain: Component (AssemblyChildInterface)
- Component cannot contain other elements
- Pages cannot be nested (prevents Page-in-Page)
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, OrderedDict, Union
from collections import OrderedDict as OrderedDictClass


# =============================================================================
# CORE BASE INTERFACES
# =============================================================================

class ElementInterface(ABC):
    """
    Base interface for all displayable elements in the TUI system.
    
    This is the foundation interface that all components, cards, assemblies,
    and pages must implement. It provides basic identification, visibility,
    and lifecycle management.
    """
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Unique identifier for this element."""
        pass
    
    @property
    @abstractmethod
    def element_type(self) -> str:
        """Type of element (component, card, assembly, page)."""
        pass
    
    @property
    @abstractmethod
    def visible(self) -> bool:
        """Whether this element is currently visible."""
        pass
    
    @abstractmethod
    def show(self) -> None:
        """Make this element visible."""
        pass
    
    @abstractmethod
    def hide(self) -> None:
        """Hide this element."""
        pass


class Renderable(ABC):
    """
    Interface for elements that can render content to the terminal.
    
    Provides delta-aware rendering capabilities with relative positioning
    and incremental refresh support using ANSI escape sequences.
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


class Stateful(ABC):
    """
    Interface for elements that manage state values.
    
    Provides state storage, retrieval, validation, and completion tracking.
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
        """Check if this stateful element has completed its requirements."""
        pass
    
    @abstractmethod
    def is_valid(self) -> bool:
        """Check if this stateful element's current state is valid."""
        pass


class ContainerInterface(ABC):
    """
    Interface for elements that can contain other elements.
    
    Provides child management with OrderedDict structure using integer keys
    and name-based lookup capabilities.
    """
    
    @abstractmethod
    def add_element(self, element: "ElementInterface") -> int:
        """
        Add an element to this container.
        
        Args:
            element: Element to add
            
        Returns:
            Integer key assigned to the element
            
        Raises:
            TypeError: If element type is not allowed in this container
        """
        pass
    
    @abstractmethod
    def remove_element(self, element_id: int) -> None:
        """Remove an element from this container by ID."""
        pass
    
    @abstractmethod
    def get_elements(self) -> OrderedDict[int, "ElementInterface"]:
        """Get all elements in this container."""
        pass
    
    @abstractmethod
    def get_element_by_name(self, name: str) -> Optional["ElementInterface"]:
        """Get an element by its name."""
        pass
    
    @abstractmethod
    def has_element(self, name: str) -> bool:
        """Check if container has an element with given name."""
        pass


# =============================================================================
# CONTAINMENT HIERARCHY INTERFACES
# =============================================================================

class PageChildInterface(ElementInterface):
    """
    Interface for elements that can be children of Page containers.
    
    Only Component, Card, and Assembly should inherit from this interface.
    This prevents invalid compositions like Page-in-Page.
    """
    pass


class CardChildInterface(ElementInterface):
    """
    Interface for elements that can be children of Card containers.
    
    Typically Component and Assembly elements. May allow nested Cards
    in future versions.
    """
    
    @abstractmethod
    def is_completed(self) -> bool:
        """Whether this child has completed its required input/validation."""
        pass
    
    @abstractmethod
    def is_valid(self) -> bool:
        """Whether this child's current state is valid."""
        pass


class AssemblyChildInterface(ElementInterface):
    """
    Interface for elements that can be children of Assembly containers.
    
    Most restrictive - typically only Component elements should inherit
    from this interface.
    """
    
    @abstractmethod
    def is_completed(self) -> bool:
        """Whether this child has completed its required input/validation."""
        pass
    
    @abstractmethod
    def is_valid(self) -> bool:
        """Whether this child's current state is valid."""
        pass
    
    @abstractmethod
    def is_interactive(self) -> bool:
        """Whether this child requires user interaction."""
        pass


# =============================================================================
# SPECIALIZED ELEMENT INTERFACES
# =============================================================================

class ComponentInterface(PageChildInterface, CardChildInterface, AssemblyChildInterface):
    """
    Interface for individual interactive/display components.
    
    Components are the most flexible elements - they can be placed in any
    container type (Page, Card, Assembly) and provide the actual UI functionality.
    """
    
    @property
    @abstractmethod
    def component_type(self) -> str:
        """Specific type of component (text_input, select, text_display, etc.)."""
        pass
    
    @abstractmethod
    def is_interactive(self) -> bool:
        """Whether this component requires user interaction."""
        pass


class PageInterface(ElementInterface, ContainerInterface):
    """
    Interface for Page containers - top-level UI containers.
    
    Pages cannot be children of other containers (no Page-in-Page).
    """
    
    @abstractmethod
    def add_element(self, element: "PageChildInterface") -> int:
        """Add an element that can be a child of a Page."""
        pass


class CardInterface(PageChildInterface, ContainerInterface):
    """
    Interface for Card containers - mid-level grouping containers.
    
    Cards can be children of Pages and can contain Components and Assemblies.
    """
    
    @abstractmethod
    def add_element(self, element: "CardChildInterface") -> int:
        """Add an element that can be a child of a Card."""
        pass
    
    @abstractmethod
    def is_completed(self) -> bool:
        """Whether all required elements in this card are completed."""
        pass
    
    @abstractmethod
    def is_valid(self) -> bool:
        """Whether all elements in this card have valid state."""
        pass


class AssemblyInterface(PageChildInterface, CardChildInterface, ContainerInterface):
    """
    Interface for Assembly containers - low-level grouping containers.
    
    Assemblies can be children of Pages and Cards, and contain Components.
    Most restrictive container type.
    """
    
    @abstractmethod
    def add_element(self, element: "AssemblyChildInterface") -> int:
        """Add an element that can be a child of an Assembly."""
        pass
    
    @abstractmethod
    def is_completed(self) -> bool:
        """Whether all required elements in this assembly are completed."""
        pass
    
    @abstractmethod
    def is_valid(self) -> bool:
        """Whether all elements in this assembly have valid state."""
        pass


# =============================================================================
# RENDER DELTA SUPPORT
# =============================================================================

class RenderDelta:
    """Represents changes between render states for incremental updates."""
    
    def __init__(
        self,
        lines_to_clear: int = 0,
        lines_to_add: Optional[List[str]] = None,
        lines_to_update: Optional[List[tuple]] = None  # [(line_index, new_content), ...]
    ):
        self.lines_to_clear = lines_to_clear
        self.lines_to_add = lines_to_add or []
        self.lines_to_update = lines_to_update or []


# =============================================================================
# CONVENIENCE COMBINATION INTERFACES
# =============================================================================

class RenderableElement(ElementInterface, Renderable):
    """Combined interface for elements that can render themselves."""
    pass


class StatefulElement(ElementInterface, Stateful):
    """Combined interface for elements that manage state."""
    pass


class RenderableContainer(ContainerInterface, Renderable):
    """Combined interface for containers that can render their contents."""
    pass


class StatefulContainer(ContainerInterface, Stateful):
    """Combined interface for containers that manage collective state."""
    pass


class FullElement(ElementInterface, Renderable, Stateful):
    """Combined interface for fully-featured elements with all capabilities."""
    pass


class FullContainer(ContainerInterface, Renderable, Stateful):
    """Combined interface for fully-featured containers with all capabilities."""
    pass


class RenderableComponent(ComponentInterface, Renderable):
    """Combined interface for components that can render themselves."""
    pass


class StatefulComponent(ComponentInterface, Stateful):
    """Combined interface for components that manage state."""
    pass


class FullComponent(ComponentInterface, Renderable, Stateful):
    """Combined interface for fully-featured components."""
    pass


class RenderablePage(PageInterface, Renderable):
    """Combined interface for pages that can render themselves."""
    pass


class StatefulPage(PageInterface, Stateful):
    """Combined interface for pages that manage state."""
    pass


class FullPage(PageInterface, Renderable, Stateful):
    """Combined interface for fully-featured pages."""
    pass


class RenderableCard(CardInterface, Renderable):
    """Combined interface for cards that can render themselves."""
    pass


class StatefulCard(CardInterface, Stateful):
    """Combined interface for cards that manage state."""
    pass


class FullCard(CardInterface, Renderable, Stateful):
    """Combined interface for fully-featured cards."""
    pass


class RenderableAssembly(AssemblyInterface, Renderable):
    """Combined interface for assemblies that can render themselves."""
    pass


class StatefulAssembly(AssemblyInterface, Stateful):
    """Combined interface for assemblies that manage state."""
    pass


class FullAssembly(AssemblyInterface, Renderable, Stateful):
    """Combined interface for fully-featured assemblies."""
    pass


# =============================================================================
# TYPE ALIASES FOR CONTAINMENT VALIDATION
# =============================================================================

# Type aliases for container child validation
PageChild = PageChildInterface
CardChild = CardChildInterface  
AssemblyChild = AssemblyChildInterface

# Union types for multiple inheritance checking
AnyContainer = Union["PageInterface", "CardInterface", "AssemblyInterface"]
AnyElement = Union["ComponentInterface", "CardInterface", "AssemblyInterface", "PageInterface"]


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Core base interfaces
    "ElementInterface",
    "Renderable", 
    "Stateful",
    "ContainerInterface",
    
    # Containment hierarchy
    "PageChildInterface",
    "CardChildInterface", 
    "AssemblyChildInterface",
    
    # Specialized element interfaces
    "ComponentInterface",
    "PageInterface",
    "CardInterface", 
    "AssemblyInterface",
    
    # Render support
    "RenderDelta",
    
    # Convenience combinations
    "RenderableElement",
    "StatefulElement",
    "RenderableContainer",
    "StatefulContainer", 
    "FullElement",
    "FullContainer",
    "RenderableComponent",
    "StatefulComponent",
    "FullComponent",
    "RenderablePage",
    "StatefulPage",
    "FullPage",
    "RenderableCard", 
    "StatefulCard",
    "FullCard",
    "RenderableAssembly",
    "StatefulAssembly", 
    "FullAssembly",
    
    # Type aliases
    "PageChild",
    "CardChild",
    "AssemblyChild", 
    "AnyContainer",
    "AnyElement"
]