"""
Comprehensive interfaces for questionary-extended architecture.

This file contains all core interfaces that define the contract for elements,
containers, rendering, and state management within the TUI engine.

Architecture:
- ElementInterface: Base for all displayable items with spatial awareness
- PageChildInterface: Elements that can be placed in Page containers
- CardChildInterface: Elements that can be placed in Card containers  
- AssemblyChildInterface: Elements that can be placed in Assembly containers
- SectionChildInterface: Elements that can be placed in Section containers
- ComponentInterface: Interactive elements (buttons, inputs, etc.)
- ContainerInterface: Elements that hold other elements with event propagation
- Renderable: Delta-aware rendering capabilities
- Stateful: State management capabilities

Containment Rules:
- Page can contain: Component, Card, Assembly, Section (PageChildInterface)
- Card can contain: Component, Assembly (CardChildInterface) 
- Assembly can contain: Component (AssemblyChildInterface)
- Section can contain: Component, Card, Assembly (SectionChildInterface)
- Component cannot contain other elements
- Pages cannot be nested (prevents Page-in-Page)
- Sections cannot be nested (prevents Section-in-Section)
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, OrderedDict, Union, Callable, Tuple
from collections import OrderedDict as OrderedDictClass


# =============================================================================
# SPATIAL AWARENESS DATA STRUCTURES
# =============================================================================

class SpaceRequirement:
    """Represents an element's space requirements and constraints."""
    
    def __init__(self, min_lines: int, current_lines: int, max_lines: int, preferred_lines: int):
        self.min_lines = min_lines          # Minimum lines needed to render (compressed)
        self.current_lines = current_lines  # Current lines being used
        self.max_lines = max_lines         # Maximum lines this element could ever need
        self.preferred_lines = preferred_lines   # Ideal lines for optimal display
    
    def can_fit_in(self, available_lines: int) -> bool:
        """Check if this element can fit in the given space."""
        return self.min_lines <= available_lines
    
    def is_compressed(self) -> bool:
        """Check if element is currently using less than preferred space."""
        return self.current_lines < self.preferred_lines
    
    def can_expand(self) -> bool:
        """Check if element could use more space."""
        return self.current_lines < self.max_lines


class BufferDelta:
    """Represents changes to an element's buffer content."""
    
    def __init__(self, line_updates: Optional[List[Tuple[int, str]]] = None, space_change: int = 0, clear_lines: Optional[List[int]] = None):
        self.line_updates = line_updates or []  # [(relative_line, new_content), ...]
        self.space_change = space_change        # Change in lines needed (+/- from current)
        self.clear_lines = clear_lines or []    # Relative lines to clear completely
    
    def has_space_change(self) -> bool:
        """Check if this delta requires space reallocation."""
        return self.space_change != 0
    
    def has_content_changes(self) -> bool:
        """Check if this delta has content updates."""
        return bool(self.line_updates or self.clear_lines)


class ElementChangeEvent:
    """Event fired when an element changes and may need re-rendering."""
    
    def __init__(self, element_name: str, change_type: str, space_delta: int = 0, **metadata: Any):
        self.element_name = element_name
        self.change_type = change_type  # 'content', 'visibility', 'space', 'state'
        self.space_delta = space_delta  # Change in space requirements
        self.metadata = metadata        # Additional event data
        self.timestamp = self._get_timestamp()
    
    def _get_timestamp(self) -> float:
        import time
        return time.time()


# =============================================================================
# CORE BASE INTERFACES
# =============================================================================

class ElementInterface(ABC):
    """
    Base interface for all displayable elements in the TUI system.
    
    This is the foundation interface that all components, cards, assemblies,
    sections, and pages must implement. It provides basic identification, 
    visibility, lifecycle management, and REQUIRED spatial awareness.
    
    All elements must be spatially aware and participate in event propagation.
    """
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Unique identifier for this element."""
        pass
    
    @property
    @abstractmethod
    def element_type(self) -> str:
        """Type of element (component, card, assembly, section, page)."""
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
    
    # =================================================================
    # SPATIAL AWARENESS - REQUIRED FOR ALL ELEMENTS
    # =================================================================
    
    @abstractmethod
    def calculate_space_requirements(self) -> SpaceRequirement:
        """
        Calculate this element's space requirements.
        
        Every element must know:
        - Minimum lines needed (compressed state)
        - Current lines being used
        - Maximum lines it could ever need
        - Preferred lines for optimal display
        
        Returns:
            SpaceRequirement with current space needs
        """
        pass
    
    @abstractmethod
    def calculate_buffer_changes(self) -> BufferDelta:
        """
        Calculate what buffer changes are needed for this element.
        
        Elements must determine:
        - Which lines need updating with new content
        - Whether space allocation needs to change
        - Which lines need to be cleared
        
        Returns:
            BufferDelta describing the changes needed
        """
        pass
    
    @abstractmethod
    def can_compress_to(self, lines: int) -> bool:
        """
        Check if element can be compressed to fit in given lines.
        
        Args:
            lines: Available lines for this element
            
        Returns:
            True if element can fit, False otherwise
        """
        pass
    
    @abstractmethod
    def compress_to_lines(self, lines: int) -> None:
        """
        Compress element content to fit in specified lines.
        
        Args:
            lines: Target lines to compress to
            
        Raises:
            ValueError: If cannot compress to given lines
        """
        pass
    
    # =================================================================
    # EVENT SYSTEM - REQUIRED FOR ALL ELEMENTS
    # =================================================================
    
    @abstractmethod
    def fire_change_event(self, change_type: str, space_delta: int = 0, **metadata: Any) -> None:
        """
        Fire a change event that bubbles up to parent containers.
        
        Args:
            change_type: Type of change ('content', 'visibility', 'space', 'state')
            space_delta: Change in space requirements (+/- lines)
            **metadata: Additional event data
        """
        pass
    
    @abstractmethod
    def register_change_listener(self, listener: Callable[["ElementChangeEvent"], None]) -> None:
        """
        Register a listener for change events from this element.
        
        Args:
            listener: Function that accepts ElementChangeEvent
        """
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
    
    Provides child management with OrderedDict structure using integer keys,
    name-based lookup capabilities, and EVENT-DRIVEN CHILD MANAGEMENT.
    
    All containers must handle child change events and aggregate spatial requirements.
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
    
    # =================================================================
    # EVENT-DRIVEN CHILD MANAGEMENT - REQUIRED FOR ALL CONTAINERS
    # =================================================================
    
    @abstractmethod
    def on_child_changed(self, child_event: "ElementChangeEvent") -> None:
        """
        Handle change events from child elements.
        
        Containers must:
        1. Process the child's change
        2. Update their own spatial requirements if needed
        3. Propagate events upward to their parent (if any)
        4. Trigger selective re-rendering of affected regions
        
        Args:
            child_event: Event from a child element
        """
        pass
    
    @abstractmethod
    def calculate_aggregate_space_requirements(self) -> SpaceRequirement:
        """
        Calculate aggregate space requirements from all children.
        
        Containers must:
        1. Query each child's space requirements
        2. Apply layout logic (vertical stack, grid, etc.)
        3. Account for spacing, borders, headers
        4. Return total space needed
        
        Returns:
            Aggregate space requirements for this container
        """
        pass
    
    @abstractmethod
    def allocate_child_space(self, child_name: str, requirement: SpaceRequirement) -> bool:
        """
        Attempt to allocate space to a child element.
        
        Args:
            child_name: Name of child requesting space
            requirement: Child's space requirements
            
        Returns:
            True if space allocated successfully, False if insufficient space
        """
        pass
    
    @abstractmethod
    def get_child_render_position(self, child_name: str) -> int:
        """
        Get the relative starting line position for a child element.
        
        Args:
            child_name: Name of child element
            
        Returns:
            Relative line position where child should start rendering
        """
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


class SectionChildInterface(ABC):
    """
    Interface for elements that can be contained within a Section.
    
    CONTAINMENT VALIDATION: Enforces that only Components, Cards, and Assemblies
    can be contained within Sections. Prevents Section-in-Section and Page-in-Section
    nesting which would create management complexity.
    
    All Section children must be spatially self-aware and event-capable.
    """
    
    # Elements implementing this interface can be contained in Sections
    # This is enforced at:
    # 1. Compile time - through interface implementation
    # 2. Runtime - through isinstance() checks in Section.add_element()
    
    @abstractmethod
    def get_name(self) -> str:
        """Return the unique name of this element."""
        pass
    
    @abstractmethod
    def get_content(self) -> List[str]:
        """Return the rendered content lines."""
        pass
    
    # =================================================================
    # REQUIRED SPATIAL AWARENESS FOR SECTION CHILDREN
    # =================================================================
    
    @abstractmethod
    def calculate_space_requirements(self) -> SpaceRequirement:
        """Calculate space requirements for this section child."""
        pass
    
    @abstractmethod
    def calculate_buffer_changes(self, target_lines: int) -> BufferDelta:
        """Calculate buffer changes needed for target line count."""
        pass
    
    @abstractmethod
    def can_compress_to(self, target_lines: int) -> bool:
        """Check if element can compress to target line count."""
        pass
    
    @abstractmethod
    def compress_to_lines(self, target_lines: int) -> List[str]:
        """Compress element content to specific line count."""
        pass
    
    # =================================================================
    # REQUIRED EVENT SYSTEM FOR SECTION CHILDREN
    # =================================================================
    
    @abstractmethod
    def fire_change_event(self, change_type: str, metadata: Optional[Dict] = None) -> None:
        """Fire change event to notify parent Section."""
        pass
    
    @abstractmethod
    def register_change_listener(self, listener: Callable[["ElementChangeEvent"], None]) -> None:
        """Register listener for change events."""
        pass


# =============================================================================
# SPECIALIZED ELEMENT INTERFACES
# =============================================================================

class ComponentInterface(PageChildInterface, CardChildInterface, AssemblyChildInterface, SectionChildInterface):
    """
    Interface for individual interactive/display components.
    
    Components are the most flexible elements - they can be placed in any
    container type (Page, Card, Assembly, Section) and provide the actual UI functionality.
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


class CardInterface(PageChildInterface, SectionChildInterface, ContainerInterface):
    """
    Interface for Card containers - mid-level grouping containers.
    
    Cards can be children of Pages and Sections, and can contain Components and Assemblies.
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


class AssemblyInterface(PageChildInterface, CardChildInterface, SectionChildInterface, ContainerInterface):
    """
    Interface for Assembly containers - low-level grouping containers.
    
    Assemblies can be children of Pages, Cards, and Sections, and contain Components.
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


class SectionInterface(PageChildInterface, ContainerInterface):
    """
    Interface for Section containers - spatial-aware grouping containers.
    
    Sections can be children of Pages and can contain Cards, Assemblies, and Components.
    Sections CANNOT contain other Sections or Pages (prevents Section-in-Section).
    Provides spatial layout management and static/dynamic refresh capabilities.
    """
    
    @abstractmethod
    def add_element(self, element: "SectionChildInterface") -> int:
        """Add an element that can be a child of a Section."""
        pass
    
    @abstractmethod
    def is_static_section(self) -> bool:
        """Whether this is a static section (header/footer) that rarely changes."""
        pass
    
    @abstractmethod
    def is_completed(self) -> bool:
        """Whether all required elements in this section are completed."""
        pass
    
    @abstractmethod
    def is_valid(self) -> bool:
        """Whether all elements in this section have valid state."""
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


class RenderableSection(SectionInterface, Renderable):
    """Combined interface for sections that can render themselves."""
    pass


class StatefulSection(SectionInterface, Stateful):
    """Combined interface for sections that manage state."""
    pass


class FullSection(SectionInterface, Renderable, Stateful):
    """Combined interface for fully-featured sections."""
    pass


# =============================================================================
# TYPE ALIASES FOR CONTAINMENT VALIDATION
# =============================================================================

# Type aliases for container child validation
PageChild = PageChildInterface
CardChild = CardChildInterface  
AssemblyChild = AssemblyChildInterface
SectionChild = SectionChildInterface

# Union types for multiple inheritance checking
AnyContainer = Union["PageInterface", "CardInterface", "AssemblyInterface", "SectionInterface"]
AnyElement = Union["ComponentInterface", "CardInterface", "AssemblyInterface", "SectionInterface", "PageInterface"]


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
    "SectionChildInterface",
    
    # Specialized element interfaces
    "ComponentInterface",
    "PageInterface",
    "CardInterface", 
    "AssemblyInterface",
    "SectionInterface",
    
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
    "RenderableSection",
    "StatefulSection",
    "FullSection",
    
    # Type aliases
    "PageChild",
    "CardChild",
    "AssemblyChild",
    "SectionChild", 
    "AnyContainer",
    "AnyElement"
]