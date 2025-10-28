"""
Assembly class for questionary-extended.

The Assembly class provides interactive component groups with event-driven logic,
conditional behavior, cross-field validation, and state management.
"""

from typing import TYPE_CHECKING, Any, Callable, Dict, List, Tuple, Union, OrderedDict
from collections import OrderedDict as OrderedDictClass

from .interfaces import (
    AssemblyInterface,
    AssemblyChildInterface,
    PageChildInterface,
    CardChildInterface,
    BufferDelta,
    SpaceRequirement,
    ElementChangeEvent,
)
from .base_classes import AssemblyBase as AssemblyBaseImpl

if TYPE_CHECKING:
    from .page_base import PageBase


class AssemblyBase(AssemblyBaseImpl, AssemblyInterface):
    """
    Interactive component group with event-driven behavior.

    Provides:
    - Event hooks (.on_change, .on_validate, .on_complete)
    - Dynamic component visibility and interaction
    - Cross-field validation and state management
    - Reusable template patterns
    """

    def __init__(self, name: str, parent: "PageBase") -> None:
        """
        Initialize a new Assembly.

        Args:
            name: Assembly namespace for state management
            parent: Parent Page instance
        """
        # Initialize base classes
        super().__init__()
        
        self._name = name
        self.parent_page = parent
        # Note: components are now managed by base class as elements
        # Event handlers may be simple callables or (field, handler) tuples
        self.event_handlers: Dict[
            str, List[Union[Callable[..., Any], Tuple[str, Callable[..., Any]]]]
        ] = {"change": [], "validate": [], "complete": []}
        # Change listeners for parent/container event propagation
        self._change_listeners: List[Callable[[ElementChangeEvent], None]] = []
    
    # ElementInterface implementation
    @property
    def name(self) -> str:
        """Unique identifier for this assembly."""
        return self._name
    
    @property
    def element_type(self) -> str:
        """Type of element (always 'assembly')."""
        return "assembly"
    
    # AssemblyInterface implementation
    def is_completed(self) -> bool:
        """Whether all required elements in this assembly are completed."""
        for element in self.get_elements().values():
            if hasattr(element, 'is_completed') and callable(getattr(element, 'is_completed')):
                if not element.is_completed():  # type: ignore
                    return False
        return True
    
    def is_valid(self) -> bool:
        """Whether all elements in this assembly have valid state."""
        for element in self.get_elements().values():
            if hasattr(element, 'is_valid') and callable(getattr(element, 'is_valid')):
                if not element.is_valid():  # type: ignore
                    return False
        return True
    
    def is_interactive(self) -> bool:
        """Whether this assembly requires user interaction."""
        for element in self.get_elements().values():
            if hasattr(element, 'is_interactive') and callable(getattr(element, 'is_interactive')):
                if element.is_interactive():  # type: ignore
                    return True
        return False
    
    # Renderable implementation
    def get_render_lines(self) -> List[str]:
        """Get the lines this assembly should output."""
        if not self.visible:
            return []
        
        lines = []
        
        # Add assembly header
        lines.append(f"--- {self.name} ---")
        
        # Add elements content
        for element in self.get_elements().values():
            if hasattr(element, 'get_render_lines') and callable(getattr(element, 'get_render_lines')):
                element_lines = element.get_render_lines()  # type: ignore
                lines.extend(element_lines)
        
        return lines
    
    # Backwards compatibility property
    @property
    def components(self) -> OrderedDict[int, AssemblyChildInterface]:
        """Get the elements OrderedDict (for backwards compatibility)."""
        return self.get_elements()  # type: ignore

    def text(self, name: str, **kwargs: Any) -> "AssemblyBase":
        """
        Add a text input component.

        Args:
            name: Component name for state storage
            **kwargs: Component configuration options (when, default, etc.)

        Returns:
            Self for method chaining
        """
        # Implementation pending Component system update to interfaces
        # from .component_wrappers import text
        # component = text(name, **kwargs)
        # self.add_element(component)  # type: ignore - TODO: Update component to implement AssemblyChildInterface
        
        # Temporary placeholder until components are updated
        print(f"TODO: Add text component '{name}' to assembly '{self.name}'")
        return self

    def select(self, name: str, choices: List[str], **kwargs: Any) -> "AssemblyBase":
        """
        Add a select input component.

        Args:
            name: Component name for state storage
            choices: List of selectable options
            **kwargs: Component configuration options (when, default, etc.)

        Returns:
            Self for method chaining
        """
        # Implementation pending Component system update to interfaces
        # from .component_wrappers import select
        # component = select(name, choices=choices, **kwargs)
        # self.add_element(component)  # type: ignore - TODO: Update component to implement AssemblyChildInterface
        
        # Temporary placeholder until components are updated
        print(f"TODO: Add select component '{name}' to assembly '{self.name}'")
        return self

    def on_change(self, field: str, handler: Callable[..., Any]) -> "AssemblyBase":
        """
        Register handler for field change events.

        Args:
            field: Field name to monitor for changes
            handler: Callback function (value, assembly) -> None

        Returns:
            Self for method chaining
        """
        # Implementation pending Event system
        self.event_handlers["change"].append((field, handler))
        return self

    def on_validate(self, handler: Callable[..., Any]) -> "AssemblyBase":
        """
        Register handler for assembly validation.

        Args:
            handler: Validation function (assembly) -> Optional[str]

        Returns:
            Self for method chaining
        """
        # Implementation pending Event system
        self.event_handlers["validate"].append(handler)
        return self

    def on_complete(self, field: str, handler: Callable[..., Any]) -> "AssemblyBase":
        """
        Register handler for field completion events.

        Args:
            field: Field name to monitor for completion
            handler: Callback function (value, assembly) -> None

        Returns:
            Self for method chaining
        """
        # Implementation pending Event system
        self.event_handlers["complete"].append((field, handler))
        return self

    def execute(self) -> Dict[str, Any]:
        """Execute the assembly and return collected results."""
        raise NotImplementedError("Assembly execution requires a QuestionaryBridge")

    def show_components(self, component_names: List[str]) -> None:
        """Show specified components."""
        raise NotImplementedError("Assembly show_components is not implemented")

    def hide_components(self, component_names: List[str]) -> None:
        """Hide specified components."""
        raise NotImplementedError("Assembly hide_components is not implemented")

    def show(self) -> None:
        """Make this assembly visible."""
        super().show()

    def hide(self) -> None:
        """Hide this assembly."""
        super().hide()

    def get_value(self, field: str) -> Any:
        """Get value from assembly's local state."""
        raise NotImplementedError("Assembly get_value is not implemented")

    def get_related_value(self, field_path: str) -> Any:
        """Get value from other assemblies (cross-boundary access)."""
        raise NotImplementedError("Assembly get_related_value is not implemented")

    def parent(self) -> "PageBase":
        """Return parent Page for navigation."""
        return self.parent_page

    # ------------------------------------------------------------------
    # Implementations for several abstract/container methods so this
    # AssemblyBase can be instantiated as a concrete, minimal assembly
    # used by test fixtures and simple pages.
    # ------------------------------------------------------------------
    def register_change_listener(self, listener: Callable[[ElementChangeEvent], None]) -> None:
        """Register a listener for change events from this assembly."""
        if listener not in self._change_listeners:
            self._change_listeners.append(listener)

    def fire_change_event(self, change_type: str, space_delta: int = 0, **metadata: Any) -> None:
        """Fire a change event and notify registered listeners (parent bubbling)."""
        evt = ElementChangeEvent(self.name, change_type, space_delta, **metadata)
        for l in list(self._change_listeners):
            try:
                l(evt)
            except Exception:
                # Don't let listener exceptions break assembly flow
                pass

    def calculate_space_requirements(self) -> SpaceRequirement:
        """Calculate simple space requirements based on rendered lines."""
        lines = self.get_render_lines()
        count = len(lines)
        return SpaceRequirement(min_lines=0, current_lines=count, max_lines=count, preferred_lines=count)

    def calculate_buffer_changes(self) -> BufferDelta:
        """Return a BufferDelta with a full update of current rendered lines."""
        lines = self.get_render_lines()
        updates = [(i, line) for i, line in enumerate(lines)]
        return BufferDelta(line_updates=updates, space_change=0, clear_lines=[])

    def calculate_aggregate_space_requirements(self) -> SpaceRequirement:
        """Alias for calculate_space_requirements used by containers."""
        return self.calculate_space_requirements()

    def can_compress_to(self, lines: int) -> bool:
        """Naive compressability check: allow non-negative targets."""
        return lines >= 0

    def compress_to_lines(self, lines: int) -> None:
        """Attempt to compress to the requested line count.

        This is a no-op for the minimal implementation; raise for invalid
        negative inputs.
        """
        if lines < 0:
            raise ValueError("lines must be >= 0")

    def get_content(self) -> List[str]:
        """Return rendered content lines (compat shim)."""
        return self.get_render_lines()

    def get_name(self) -> str:
        """Return the assembly's name (compat shim)."""
        return self.name

    def on_child_changed(self, child_event: ElementChangeEvent) -> None:
        """Handle child change events by marking dirty and bubbling up."""
        try:
            # Mark this assembly as requiring re-render
            self.mark_dirty()
        except Exception:
            pass

        # Bubble a simplified event upward
        try:
            self.fire_change_event("child_change", space_delta=child_event.space_delta, child=child_event)
        except Exception:
            pass

    def allocate_child_space(self, child_name: str, requirement: SpaceRequirement) -> bool:
        """Attempt to allocate space to a child; minimal implementation just
        returns True if child exists."""
        for e in self.get_elements().values():
            if hasattr(e, 'name') and e.name == child_name:
                return True
        return False

    def get_child_render_position(self, child_name: str) -> int:
        """Compute relative render start for a named child by summing previous
        children's rendered lines."""
        pos = 0
        for e in self.get_elements().values():
            if hasattr(e, 'name') and e.name == child_name:
                return pos
            if hasattr(e, 'get_render_lines') and callable(getattr(e, 'get_render_lines')):
                pos += len(e.get_render_lines())
                pos += 1
        return pos


__all__ = ["AssemblyBase"]
