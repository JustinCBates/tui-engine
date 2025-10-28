"""
Section container for logical grouping of TUI elements.

Provides spatial-aware containers that can manage header/body/footer sections
with independent refresh capabilities and proper space management.
"""

from typing import List, Dict, Any, Optional, TYPE_CHECKING, Callable
from collections import OrderedDict as OrderedDictClass

from .spatial import SpatiallyAware
from .interfaces import ElementInterface, PageChildInterface, Renderable, SectionInterface, SectionChildInterface, ElementChangeEvent, SpaceRequirement, BufferDelta
from .base_classes import RenderableBase, ContainerBase, RenderableContainerBase

if TYPE_CHECKING:
    from .component_wrappers import Component


class Section(RenderableContainerBase, SectionInterface):
    """
    Spatial-aware section container for logical grouping of elements.
    
    Sections can be marked as static (header) or dynamic (body) to control
    when they trigger re-renders and how they manage space.
    
    Containment Rules:
    - Can contain: Components, Cards, Assemblies (SectionChildInterface)
    - Cannot contain: Pages, other Sections
    """
    
    def __init__(self, name: str, static: bool = False, **kwargs: Any):
        """
        Initialize a section container.
        
        Args:
            name: Section identifier
            static: If True, section content rarely changes (like headers)
            **kwargs: Additional configuration options
        """
        # Initialize combined container base which wires Renderable + Container
        super().__init__()
        
        self._name = name
        self.static = static
        self.config = kwargs
        
        # Spatial tracking
        self._last_space_requirement: Optional[SpaceRequirement] = None
        self._content_dirty = True
        self._change_listeners: List[Callable[[ElementChangeEvent], None]] = []
        
        # Section-specific settings
        self.spacing_between_elements = kwargs.get('spacing', 1)
        self.min_lines_override = kwargs.get('min_lines')
        self.max_lines_override = kwargs.get('max_lines')
    
    # =================================================================
    # CONTAINER INTERFACE IMPLEMENTATION (REQUIRED)
    # =================================================================
    
    def on_child_changed(self, child_event: ElementChangeEvent) -> None:
        """
        Handle change events from child elements.
        
        Sections process child changes and propagate upward if needed.
        """
        # Mark ourselves as dirty when children change
        if not self.static:  # Static sections don't auto-refresh
            self.mark_dirty()
        
        # Propagate event to our listeners (typically the parent Page)
        for listener in self._change_listeners:
            try:
                listener(child_event)
            except Exception:
                # Don't let listener exceptions break the section
                pass
    
    def calculate_aggregate_space_requirements(self) -> SpaceRequirement:
        """
        Calculate aggregate space requirements from all children.
        
        This is the same as calculate_space_requirements for sections.
        """
        return self.calculate_space_requirements()
    
    def allocate_child_space(self, child_name: str, requirement: SpaceRequirement) -> bool:
        """
        Attempt to allocate space to a child element.
        
        For sections, we currently use simple vertical stacking,
        so we accept all child space requests.
        """
        # Find the child by name
        for element in self.get_elements().values():
            if hasattr(element, 'name') and element.name == child_name:
                # In simple vertical layout, we can accommodate any child space request
                return True
        
        return False  # Child not found
    
    def get_child_render_position(self, child_name: str) -> int:
        """
        Get the relative starting line position for a child element.
        
        Calculates position based on vertical stacking with spacing.
        """
        current_position = 0
        elements = list(self.get_elements().values())
        
        for element in elements:
            if hasattr(element, 'name') and element.name == child_name:
                return current_position
            
            # Add this element's height and spacing
            if hasattr(element, 'get_render_lines') and callable(getattr(element, 'get_render_lines')):
                element_lines = element.get_render_lines()  # type: ignore
                current_position += len(element_lines)
                current_position += self.spacing_between_elements
        
        return current_position  # If not found, return current position
    
    # =================================================================
    # ELEMENT INTERFACE IMPLEMENTATION
    # =================================================================
    
    # ElementInterface implementation
    @property
    def name(self) -> str:
        """Return section name for element interface."""
        return self._name
    
    @property
    def element_type(self) -> str:
        """Type of element."""
        return "section"
    
    # SectionInterface implementation
    def add_element(self, element: SectionChildInterface) -> int:
        """Add an element that can be a child of a Section."""
        # Validate that element can be a child of a section
        if not isinstance(element, SectionChildInterface):
            raise TypeError(f"Element must implement SectionChildInterface, got {type(element)}")
        eid = super().add_element(element)  # type: ignore
        # Mark section as needing re-render when new elements are added
        try:
            self.mark_dirty()
        except Exception:
            pass
        return eid

    def _validate_element_type(self, element: ElementInterface) -> None:
        """Validate that element can be a child of a Section."""
        if not isinstance(element, SectionChildInterface):
            raise TypeError(
                f"Section can only contain SectionChildInterface elements. Got {type(element)} which does not implement SectionChildInterface."
            )
    
    # SpatiallyAware implementation
    def calculate_space_requirements(self) -> SpaceRequirement:
        """Calculate space requirements based on contained elements."""
        if not self.visible:
            return SpaceRequirement(min_lines=0, current_lines=0, max_lines=0, preferred_lines=0)
        
        element_lines = []
        element_min_lines = []
        element_max_lines = []
        
        for element in self.get_elements().values():
            if hasattr(element, 'get_render_lines') and callable(getattr(element, 'get_render_lines')):
                lines = element.get_render_lines()  # type: ignore
                element_lines.append(len(lines))
                
                # Try to get spatial info if available
                if hasattr(element, 'calculate_space_requirements'):
                    elem_req = element.calculate_space_requirements()  # type: ignore
                    element_min_lines.append(elem_req.min_lines)
                    element_max_lines.append(elem_req.max_lines)
                else:
                    # Fallback: assume element is fixed size
                    line_count = len(lines)
                    element_min_lines.append(line_count)
                    element_max_lines.append(line_count)
        
        # Calculate totals including spacing
        total_elements = len(element_lines)
        spacing_lines = max(0, (total_elements - 1) * self.spacing_between_elements)
        
        current_lines = sum(element_lines) + spacing_lines
        min_lines = sum(element_min_lines) + spacing_lines
        max_lines = sum(element_max_lines) + spacing_lines
        
        # Apply overrides if specified
        if self.min_lines_override is not None:
            min_lines = self.min_lines_override
        if self.max_lines_override is not None:
            max_lines = self.max_lines_override
        
        # Preferred lines (could be configurable)
        preferred_lines = current_lines
        
        requirement = SpaceRequirement(
            min_lines=min_lines,
            current_lines=current_lines,
            max_lines=max_lines,
            preferred_lines=preferred_lines
        )
        
        self._last_space_requirement = requirement
        return requirement
    
    def calculate_buffer_changes(self) -> BufferDelta:
        """Calculate what changes are needed within this section's allocated space."""
        if not self._content_dirty and not any(
            hasattr(elem, 'has_changes') and callable(getattr(elem, 'has_changes')) and elem.has_changes()  # type: ignore
            for elem in self.get_elements().values()
        ):
            # No changes needed
            return BufferDelta(line_updates=[], space_change=0, clear_lines=[])
        
        # Get current content lines
        current_content = self.get_render_lines()
        
        # Calculate space change
        current_req = self.calculate_space_requirements()
        space_change = 0
        if self._last_space_requirement:
            space_change = current_req.current_lines - self._last_space_requirement.current_lines
        
        # Generate line updates
        line_updates = [(i, line) for i, line in enumerate(current_content)]
        
        # Mark as clean
        self._content_dirty = False
        for element in self.get_elements().values():
            if hasattr(element, '_needs_render'):
                element._needs_render = False  # type: ignore
        
        return BufferDelta(
            line_updates=line_updates,
            space_change=space_change,
            clear_lines=[]
        )
    
    def can_compress_to(self, lines: int) -> bool:
        """Check if section can be compressed to fit in given lines."""
        req = self.calculate_space_requirements()
        return req.min_lines <= lines
    
    def compress_to_lines(self, lines: int) -> None:
        """Compress section content to fit in specified lines."""
        # For now, implement basic compression by truncating content
        # More sophisticated compression could hide less important elements
        req = self.calculate_space_requirements()
        if lines < req.min_lines:
            raise ValueError(f"Cannot compress section '{self.name}' to {lines} lines (minimum: {req.min_lines})")
        
        # Mark for re-calculation with compression
        self._content_dirty = True
    
    # Renderable implementation
    def get_render_lines(self) -> List[str]:
        """Get the lines this section should output."""
        if not self.visible:
            return []
        
        lines = []
        elements = list(self.get_elements().values())
        
        for i, element in enumerate(elements):
            if hasattr(element, 'get_render_lines') and callable(getattr(element, 'get_render_lines')):
                element_lines = element.get_render_lines()  # type: ignore
                lines.extend(element_lines)
                
                # Add spacing between elements (except after last)
                if i < len(elements) - 1 and element_lines:
                    for _ in range(self.spacing_between_elements):
                        lines.append("")
        
        return lines
    
    def mark_dirty(self) -> None:
        """Mark this section as needing re-render."""
        super().mark_dirty()
        self._content_dirty = True
    
    # Container operations
    def add_text(self, content: str, **kwargs: Any) -> "Section":
        """Add a text display element to this section."""
        from .component_wrappers import Component
        import time
        
        text_component = Component(
            name=f"{self._name}_text_{int(time.time() * 1000000)}",  # Unique timestamp-based name
            component_type="text_display",
            content=content,
            **kwargs
        )
        
        self.add_element(text_component)
        self.mark_dirty()
        return self
    
    def add_status(self, content: str, status_type: str = "info", **kwargs: Any) -> "Section":
        """Add a status message element to this section."""
        from .component_wrappers import Component
        import time
        
        status_component = Component(
            name=f"{self._name}_status_{int(time.time() * 1000000)}",  # Unique timestamp-based name
            component_type="text_status", 
            content=content,
            status_type=status_type,
            **kwargs
        )
        
        self.add_element(status_component)
        self.mark_dirty()
        return self
    
    def clear_content(self) -> "Section":
        """Clear all content from this section."""
        self._elements.clear()
        self._next_element_id = 0  # Reset element counter
        self.mark_dirty()
        return self
    
    def is_static_section(self) -> bool:
        """Check if this is a static section (header/footer)."""
        return self.static
    
    def is_completed(self) -> bool:
        """Whether all required elements in this section are completed."""
        for element in self.get_elements().values():
            if hasattr(element, 'is_completed') and callable(getattr(element, 'is_completed')):
                if not element.is_completed():  # type: ignore
                    return False
        return True
    
    def is_valid(self) -> bool:
        """Whether all elements in this section have valid state."""
        for element in self.get_elements().values():
            if hasattr(element, 'is_valid') and callable(getattr(element, 'is_valid')):
                if not element.is_valid():  # type: ignore
                    return False
        return True
    
    # Event handling for spatial awareness
    def on_element_changed(self, element_id: str) -> None:
        """Called when a child element changes and may need re-rendering."""
        if not self.static:  # Static sections don't auto-refresh
            self.mark_dirty()
    
    # =================================================================
    # EVENT SYSTEM IMPLEMENTATION (REQUIRED BY ElementInterface)
    # =================================================================
    
    def fire_change_event(self, change_type: str, space_delta: int = 0, **metadata: Any) -> None:
        """Fire change event to notify listeners."""
        event = ElementChangeEvent(
            element_name=self.name,
            element_type=self.element_type,
            change_type=change_type,
            space_delta=space_delta,
            metadata=metadata
        )
        
        for listener in self._change_listeners:
            try:
                listener(event)
            except Exception:
                # Don't let listener exceptions break the section
                pass
    
    def register_change_listener(self, listener: Callable[[ElementChangeEvent], None]) -> None:
        """Register listener for change events."""
        if listener not in self._change_listeners:
            self._change_listeners.append(listener)
    
    def __repr__(self) -> str:
        """String representation for debugging."""
        static_marker = " [STATIC]" if self.static else ""
        return f"Section(name='{self._name}', elements={len(self.get_elements())}{static_marker})"