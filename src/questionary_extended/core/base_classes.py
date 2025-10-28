"""
Base implementation classes for questionary-extended architecture.

Provides concrete implementations of interfaces that can be inherited by
Page, Card, Assembly, and Component classes. These base classes implement
common functionality like rendering, state management, and container operations.
"""

import os
import sys
from typing import Any, Dict, List, Optional, OrderedDict, TYPE_CHECKING, Callable
from collections import OrderedDict as OrderedDictClass

from .interfaces import (
    ElementInterface, Renderable, Stateful, ContainerInterface,
    PageInterface, CardInterface, AssemblyInterface, ComponentInterface,
    PageChildInterface, CardChildInterface, AssemblyChildInterface,
    RenderDelta
)

if TYPE_CHECKING:
    from typing import Union


# =============================================================================
# BASE RENDERABLE IMPLEMENTATION
# =============================================================================

class RenderableBase(Renderable):
    """
    Concrete base implementation of Renderable interface.
    
    Provides delta-aware rendering with ANSI escape sequences for
    incremental terminal updates.
    """
    
    def __init__(self):
        # Visibility control
        self._visible: bool = True
        
        # Render state tracking
        self._last_rendered_lines: List[str] = []
        self._needs_render: bool = True
        self._relative_position: int = 0
    
    @property
    def visible(self) -> bool:
        """Whether this element is currently visible."""
        return self._visible
    
    def show(self) -> None:
        """Make this element visible."""
        self._visible = True
        self.mark_dirty()
    
    def hide(self) -> None:
        """Hide this element."""
        self._visible = False
        self.mark_dirty()
    
    def mark_dirty(self) -> None:
        """Mark this renderable as needing re-render."""
        self._needs_render = True
    
    def has_changes(self) -> bool:
        """Check if this renderable needs re-rendering."""
        return self._needs_render
    
    def calculate_delta(self) -> RenderDelta:
        """Calculate changes since last render."""
        current_lines = self.get_render_lines()
        previous_lines = self._last_rendered_lines
        
        # Simple delta calculation
        lines_to_clear = len(previous_lines)
        lines_to_add = current_lines
        
        return RenderDelta(
            lines_to_clear=lines_to_clear,
            lines_to_add=lines_to_add
        )
    
    def render_delta(self, relative_start: int = 0) -> int:
        """
        Render this renderable's changes at relative position.
        
        Args:
            relative_start: Starting line position relative to parent container
            
        Returns:
            Number of lines used by this render
        """
        if not self.visible:
            return self._clear_previous_content(relative_start)
        
        delta = self.calculate_delta()
        
        # Clear old content
        for i in range(delta.lines_to_clear):
            line_pos = relative_start + i
            print(f"\\x1b[{line_pos + 1};1H\\x1b[2K", end="")
        
        # Render new content
        for i, line in enumerate(delta.lines_to_add):
            line_pos = relative_start + i
            print(f"\\x1b[{line_pos + 1};1H{line}", end="")
        
        # Update tracking
        self._last_rendered_lines = delta.lines_to_add.copy()
        self._needs_render = False
        self._relative_position = relative_start
        
        return len(delta.lines_to_add)
    
    def _clear_previous_content(self, relative_start: int) -> int:
        """Clear this renderable's previous content."""
        for i in range(len(self._last_rendered_lines)):
            line_pos = relative_start + i
            print(f"\\x1b[{line_pos + 1};1H\\x1b[2K", end="")
        
        self._last_rendered_lines = []
        return 0
    
    # ANSI escape sequence helpers
    def _move_cursor_up(self, lines: int) -> None:
        """Move cursor up by specified number of lines."""
        if lines > 0:
            print(f"\\x1b[{lines}A", end="")

    def _clear_line(self) -> None:
        """Clear the current line."""
        print("\\x1b[2K", end="")

    def _save_cursor(self) -> None:
        """Save current cursor position."""
        print("\\x1b[s", end="")

    def _restore_cursor(self) -> None:
        """Restore saved cursor position."""
        print("\\x1b[u", end="")

    # Abstract method that must be implemented by subclasses
    def get_render_lines(self) -> List[str]:
        """
        Get the lines this renderable should output.
        
        Must be implemented by subclasses.
        """
        raise NotImplementedError("Subclasses must implement get_render_lines()")


# =============================================================================
# BASE CONTAINER IMPLEMENTATION
# =============================================================================

class ContainerBase(ContainerInterface):
    """
    Concrete base implementation of ContainerInterface.
    
    Provides OrderedDict-based element management with integer keys
    and name-based lookup.
    """
    
    def __init__(self):
        # Element storage
        self._elements: OrderedDict[int, ElementInterface] = OrderedDictClass()
        self._element_names: Dict[str, int] = {}  # name -> element_id mapping
        self._next_element_id: int = 1
        
        # For backwards compatibility during transition
        self._components = self._elements  # Alias for old code
    
    def add_element(self, element: ElementInterface) -> int:
        """
        Add an element to this container.
        
        Args:
            element: Element to add
            
        Returns:
            Integer key assigned to the element
            
        Raises:
            TypeError: If element type is not allowed in this container
            ValueError: If element name already exists
        """
        # Validate element type (subclasses should override _validate_element_type)
        self._validate_element_type(element)
        
        # Check for name conflicts
        if element.name in self._element_names:
            raise ValueError(f"Element with name '{element.name}' already exists")
        
        # Assign ID and store
        element_id = self._next_element_id
        self._next_element_id += 1
        
        self._elements[element_id] = element
        self._element_names[element.name] = element_id
        
        # Register as change listener to receive events from this child
        if hasattr(element, 'register_change_listener') and hasattr(self, 'on_child_changed'):
            element.register_change_listener(self.on_child_changed)
        # Set a parent reference on the child so it can discover its owning
        # container/page. Use a conservative try/except to avoid breaking
        # objects that don't accept new attributes.
        try:
            setattr(element, '_parent', self)
        except Exception:
            pass
        
        return element_id
    
    def remove_element(self, element_id: int) -> None:
        """Remove an element from this container by ID."""
        if element_id in self._elements:
            element = self._elements[element_id]
            # Remove from name mapping
            if element.name in self._element_names:
                del self._element_names[element.name]
            # Remove from elements
            del self._elements[element_id]
    
    def get_elements(self) -> OrderedDict[int, ElementInterface]:
        """Get all elements in this container."""
        return self._elements.copy()
    
    def get_element_by_name(self, name: str) -> Optional[ElementInterface]:
        """Get an element by its name."""
        element_id = self._element_names.get(name)
        if element_id is not None:
            return self._elements.get(element_id)
        return None
    
    def has_element(self, name: str) -> bool:
        """Check if container has an element with given name."""
        return name in self._element_names
    
    def _validate_element_type(self, element: ElementInterface) -> None:
        """
        Validate that element type is allowed in this container.
        
        Base implementation allows any ElementInterface.
        Subclasses should override to enforce containment rules.
        """
        if not isinstance(element, ElementInterface):
            raise TypeError(f"Element must implement ElementInterface, got {type(element)}")
    
    # Backwards compatibility methods
    def add_child(self, child: ElementInterface) -> int:
        """Backwards compatibility alias for add_element."""
        return self.add_element(child)
    
    def get_children(self) -> OrderedDict[int, ElementInterface]:
        """Backwards compatibility alias for get_elements."""
        return self.get_elements()
    
    def has_child(self, name: str) -> bool:
        """Backwards compatibility alias for has_element."""
        return self.has_element(name)


# =============================================================================
# BASE STATEFUL IMPLEMENTATION
# =============================================================================

class StatefulBase(Stateful):
    """
    Concrete base implementation of Stateful interface.
    
    Provides state storage and validation capabilities.
    """
    
    def __init__(self):
        self._state_values: Dict[str, Any] = {}
        self._required_keys: set = set()
        self._validation_rules: Dict[str, Callable[[Any], bool]] = {}
    
    def get_state_value(self, key: str, default: Any = None) -> Any:
        """Get a state value."""
        return self._state_values.get(key, default)
    
    def set_state_value(self, key: str, value: Any) -> None:
        """Set a state value."""
        self._state_values[key] = value
    
    def is_completed(self) -> bool:
        """Check if this stateful element has completed its requirements."""
        # Check if all required keys have values
        for key in self._required_keys:
            if key not in self._state_values or self._state_values[key] is None:
                return False
        return True
    
    def is_valid(self) -> bool:
        """Check if this stateful element's current state is valid."""
        # Run validation rules
        for key, validator in self._validation_rules.items():
            if key in self._state_values:
                try:
                    if not validator(self._state_values[key]):
                        return False
                except Exception:
                    return False
        return True
    
    def add_required_key(self, key: str) -> None:
        """Add a required state key."""
        self._required_keys.add(key)
    
    def add_validation_rule(self, key: str, validator: Callable[[Any], bool]) -> None:
        """Add a validation rule for a state key."""
        self._validation_rules[key] = validator


# =============================================================================
# COMBINED BASE CLASSES
# =============================================================================

class RenderableContainerBase(RenderableBase, ContainerBase):
    """
    Base class for containers that can render their contents.
    
    Provides orchestration of child rendering and automatic
    delta propagation.
    """
    
    def __init__(self):
        RenderableBase.__init__(self)
        ContainerBase.__init__(self)
        self._header_rendered: bool = False
        self._safe_incremental: bool = False
    
    def has_changes(self) -> bool:
        """Check if this container or any children have changes."""
        # Check self
        if self._needs_render:
            return True
        
        # Check all children that support rendering
        for child in self._elements.values():
            if isinstance(child, Renderable) and child.has_changes():
                return True
                
        return False
    
    def render_delta(self, relative_start: int = 0) -> int:
        """Render this container and orchestrate child rendering."""
        if not self.visible:
            return self._clear_previous_content(relative_start)
        
        current_line = relative_start
        
        # Render container header/content first
        container_lines = self.get_render_lines()
        for i, line in enumerate(container_lines):
            line_pos = current_line + i
            print(f"\\x1b[{line_pos + 1};1H\\x1b[2K{line}", end="")
        
        current_line += len(container_lines)
        
        # Orchestrate child rendering
        for child in self._elements.values():
            if isinstance(child, Renderable) and child.has_changes():
                lines_used = child.render_delta(current_line)
                current_line += lines_used
        
        # Update tracking
        total_lines = current_line - relative_start
        self._last_rendered_lines = container_lines.copy()
        self._needs_render = False
        self._relative_position = relative_start
        
        return total_lines
    
    # Container-specific refresh methods
    def enable_safe_incremental(self) -> None:
        """Enable incremental refresh mode (only when no external output)."""
        self._safe_incremental = True
        
    def disable_safe_incremental(self) -> None:
        """Disable incremental refresh mode (fallback to normal printing)."""
        self._safe_incremental = False
    
    def clear_screen(self) -> None:
        """Clear the terminal screen."""
        os.system('clear' if os.name == 'posix' else 'cls')


class PageBase(RenderableContainerBase):
    """
    Base implementation for Page containers.
    
    Provides all the concrete functionality needed by Page classes
    while enforcing PageChild containment rules.
    """
    
    def _validate_element_type(self, element: ElementInterface) -> None:
        """Validate that element can be a child of a Page."""
        if not isinstance(element, PageChildInterface):
            raise TypeError(
                f"Page can only contain PageChildInterface elements. "
                f"Got {type(element)} which does not implement PageChildInterface."
            )


class CardBase(RenderableContainerBase):
    """
    Base implementation for Card containers.
    
    Provides all the concrete functionality needed by Card classes
    while enforcing CardChild containment rules.
    """
    
    def _validate_element_type(self, element: ElementInterface) -> None:
        """Validate that element can be a child of a Card."""
        if not isinstance(element, CardChildInterface):
            raise TypeError(
                f"Card can only contain CardChildInterface elements. "
                f"Got {type(element)} which does not implement CardChildInterface."
            )


class AssemblyBase(RenderableContainerBase):
    """
    Base implementation for Assembly containers.
    
    Provides all the concrete functionality needed by Assembly classes
    while enforcing AssemblyChild containment rules.
    """
    
    def _validate_element_type(self, element: ElementInterface) -> None:
        """Validate that element can be a child of an Assembly."""
        if not isinstance(element, AssemblyChildInterface):
            raise TypeError(
                f"Assembly can only contain AssemblyChildInterface elements. "
                f"Got {type(element)} which does not implement AssemblyChildInterface."
            )


class ComponentBase(RenderableBase, StatefulBase):
    """
    Base implementation for Component elements.
    
    Provides concrete functionality for components including
    rendering and state management.
    """
    
    def __init__(self, name: str, component_type: str):
        RenderableBase.__init__(self)
        StatefulBase.__init__(self)
        self._name = name
        self._component_type = component_type
        self._interactive = True
    
    @property
    def name(self) -> str:
        """Unique identifier for this component."""
        return self._name
    
    @property
    def element_type(self) -> str:
        """Type of element (always 'component')."""
        return "component"
    
    @property
    def component_type(self) -> str:
        """Specific type of component."""
        return self._component_type
    
    def is_interactive(self) -> bool:
        """Whether this component requires user interaction."""
        return self._interactive
    
    def set_interactive(self, interactive: bool) -> None:
        """Set whether this component is interactive."""
        self._interactive = interactive


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Base implementations
    "RenderableBase",
    "ContainerBase", 
    "StatefulBase",
    
    # Combined base classes
    "RenderableContainerBase",
    "PageBase",
    "CardBase",
    "AssemblyBase", 
    "ComponentBase"
]