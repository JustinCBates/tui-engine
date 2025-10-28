"""
Card class for questionary-extended.

The Card class provides visual grouping of related components with styling options,
dynamic show/hide capabilities, and responsive layout management.
Enhanced with universal spatial awareness and event-driven architecture.
"""

from typing import TYPE_CHECKING, Any, List, OrderedDict, Callable, Optional
from collections import OrderedDict as OrderedDictClass

from .interfaces import CardInterface, CardChildInterface, PageChildInterface, ElementChangeEvent, SpaceRequirement, BufferDelta
from .base_classes import CardBase
from .debug_mode import debug_prefix, is_debug_mode

if TYPE_CHECKING:
    from .page_base import PageBase


class Card(CardBase, CardInterface):
    """
    Visual grouping container for related components.

    Provides:
    - Visual styling options (minimal, bordered, highlighted, collapsible)
    - Dynamic show/hide with smooth transitions
    - Horizontal/vertical layout with responsive fallback
    - Component overflow handling and scrolling
    - Universal spatial awareness and event-driven architecture
    """

    def __init__(self, title: str, parent: "PageBase", style: str = "minimal") -> None:
        """
        Initialize a new Card.

        Args:
            title: Card title/header
            parent: Parent Page instance
            style: Visual style (minimal, bordered, highlighted, collapsible)
        """
        # Initialize base classes
        super().__init__()
        
        self.title = title
        self.parent_page = parent
        self.style = style
        
        # Spatial awareness and event system
        self._change_listeners: List[Callable[[ElementChangeEvent], None]] = []
        self._last_space_requirement: Optional[SpaceRequirement] = None
        self._content_dirty = True
        
        # Note: components are now managed by base class as elements
    
    # ElementInterface implementation
    @property
    def name(self) -> str:
        """Unique identifier for this card."""
        return self.title or "untitled_card"
    
    @property
    def element_type(self) -> str:
        """Type of element (always 'card')."""
        return "card"
    
    # CardInterface implementation
    def is_completed(self) -> bool:
        """Whether all required elements in this card are completed."""
        for element in self.get_elements().values():
            if hasattr(element, 'is_completed') and callable(getattr(element, 'is_completed')):
                if not element.is_completed():  # type: ignore
                    return False
        return True
    
    def is_valid(self) -> bool:
        """Whether all elements in this card have valid state."""
        for element in self.get_elements().values():
            if hasattr(element, 'is_valid') and callable(getattr(element, 'is_valid')):
                if not element.is_valid():  # type: ignore
                    return False
        return True
    
    # =================================================================
    # SPATIAL AWARENESS IMPLEMENTATION (REQUIRED BY ElementInterface)
    # =================================================================
    
    def calculate_space_requirements(self) -> SpaceRequirement:
        """Calculate space requirements for this card."""
        if not self.visible:
            return SpaceRequirement(min_lines=0, current_lines=0, max_lines=0, preferred_lines=0)
        
        # Calculate header lines based on style
        header_lines = self._calculate_header_lines()
        
        # Calculate content lines from child elements
        content_lines = 0
        content_min_lines = 0
        content_max_lines = 0
        
        for element in self.get_elements().values():
            if hasattr(element, 'calculate_space_requirements'):
                elem_req = element.calculate_space_requirements()  # type: ignore
                content_lines += elem_req.current_lines
                content_min_lines += elem_req.min_lines
                content_max_lines += elem_req.max_lines
            elif hasattr(element, 'get_render_lines'):
                elem_lines = len(element.get_render_lines())  # type: ignore
                content_lines += elem_lines
                content_min_lines += elem_lines
                content_max_lines += elem_lines
        
        # Add footer lines based on style
        footer_lines = self._calculate_footer_lines()
        
        # Total requirements
        total_current = header_lines + content_lines + footer_lines
        total_min = header_lines + content_min_lines + footer_lines
        total_max = header_lines + content_max_lines + footer_lines
        
        requirement = SpaceRequirement(
            min_lines=max(total_min, 3),  # Cards need at least 3 lines (header + content + footer)
            current_lines=total_current,
            max_lines=total_max,
            preferred_lines=total_current
        )
        
        self._last_space_requirement = requirement
        return requirement
    
    def calculate_buffer_changes(self) -> BufferDelta:
        """Calculate buffer changes for this card."""
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
        """Check if card can be compressed to fit in given lines."""
        req = self.calculate_space_requirements()
        return req.min_lines <= lines
    
    def compress_to_lines(self, lines: int) -> None:
        """Compress card content to fit in specified lines."""
        req = self.calculate_space_requirements()
        if lines < req.min_lines:
            raise ValueError(f"Cannot compress card '{self.name}' to {lines} lines (minimum: {req.min_lines})")
        
        # Mark for re-calculation with compression
        self._content_dirty = True
    
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
                # Don't let listener exceptions break the card
                pass
    
    def register_change_listener(self, listener: Callable[[ElementChangeEvent], None]) -> None:
        """Register listener for change events."""
        if listener not in self._change_listeners:
            self._change_listeners.append(listener)
    
    # =================================================================
    # CONTAINER INTERFACE IMPLEMENTATION (REQUIRED)
    # =================================================================
    
    def on_child_changed(self, child_event: ElementChangeEvent) -> None:
        """
        Handle change events from child elements.
        
        Cards process child changes and propagate upward if needed.
        """
        # Mark ourselves as dirty when children change
        self._content_dirty = True
        
        # Propagate event to our listeners (typically the parent Page)
        for listener in self._change_listeners:
            try:
                listener(child_event)
            except Exception:
                # Don't let listener exceptions break the card
                pass
    
    def calculate_aggregate_space_requirements(self) -> SpaceRequirement:
        """
        Calculate aggregate space requirements from all children.
        
        This is the same as calculate_space_requirements for cards.
        """
        return self.calculate_space_requirements()
    
    def allocate_child_space(self, child_name: str, requirement: SpaceRequirement) -> bool:
        """
        Attempt to allocate space to a child element.
        
        For cards, we currently use simple vertical stacking,
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
        
        Calculates position based on header and previous children.
        """
        current_position = self._calculate_header_lines()
        
        for element in self.get_elements().values():
            if hasattr(element, 'name') and element.name == child_name:
                return current_position
            
            # Add this element's height
            if hasattr(element, 'get_render_lines') and callable(getattr(element, 'get_render_lines')):
                element_lines = element.get_render_lines()  # type: ignore
                current_position += len(element_lines)
        
        return current_position  # If not found, return current position
    
    # =================================================================
    # SECTION CHILD INTERFACE IMPLEMENTATION (REQUIRED)
    # =================================================================
    
    def get_name(self) -> str:
        """Return the unique name of this element (for SectionChildInterface)."""
        return self.name
    
    def get_content(self) -> List[str]:
        """Return the rendered content lines (for SectionChildInterface)."""
        return self.get_render_lines()
    
    # =================================================================
    # UTILITY METHODS FOR SPATIAL CALCULATIONS
    # =================================================================
    
    def _calculate_header_lines(self) -> int:
        """Calculate number of lines needed for header based on style."""
        if self.style == "bordered":
            return 1  # Just the top border line
        elif self.style == "highlighted":
            return 1  # Title line with stars
        else:  # minimal
            return 2  # Title line + separator line
    
    def _calculate_footer_lines(self) -> int:
        """Calculate number of lines needed for footer based on style."""
        if self.style == "bordered":
            return 1  # Just the bottom border line
        else:
            return 0  # No footer for other styles
    
    # Renderable implementation
    def get_render_lines(self) -> List[str]:
        """Get the lines this card should output."""
        if not self.visible:
            return []
        
        lines = []
        
        # Collect content first to determine border width
        content_lines = []
        for element in self.get_elements().values():
            if hasattr(element, 'get_render_lines') and callable(getattr(element, 'get_render_lines')):
                element_lines = element.get_render_lines()  # type: ignore
                content_lines.extend(element_lines)
        
        # Calculate border width based on content and title
        title_length = len(self.title) if self.title else 0
        content_max_length = max((len(line) for line in content_lines), default=0)
        border_width = max(title_length + 6, content_max_length + 4, 20)  # Minimum 20 chars
        
        # Add card header based on style
        if self.style == "bordered":
            # Add debug prefix to title in debug mode
            if is_debug_mode():
                display_title = f"{debug_prefix('card')}{self.title}"
            else:
                display_title = self.title
            
            # Create top border with title
            title_padding = border_width - len(display_title) - 4  # Account for ┌ ┐ and spaces around title
            left_padding = title_padding // 2
            right_padding = title_padding - left_padding
            top_border = f"┌{'─' * left_padding} {display_title} {'─' * right_padding}┐"
            lines.append(top_border)
            
            # Calculate inner content width to match the top border total length
            # Top border structure: ┌ + dashes + space + title + space + dashes + ┐
            # Side border structure: │ + space + content + space + │
            # So inner content width = top_border_length - 4 (for │ + space + space + │)
            top_border_length = len(top_border)
            inner_content_width = top_border_length - 4
            
            # Add content with side borders
            if content_lines:
                for line in content_lines:
                    # Pad content line to fit exactly within border
                    content_padded = line.ljust(inner_content_width)
                    lines.append(f"│ {content_padded} │")
            else:
                # Empty content area
                empty_line = " " * inner_content_width
                lines.append(f"│ {empty_line} │")
            
            # Add bottom border - must match the top border width exactly
            # Bottom border structure: └ + dashes + ┘
            bottom_dashes = "─" * (top_border_length - 2)
            bottom_border = f"└{bottom_dashes}┘"
            lines.append(bottom_border)
            
        elif self.style == "highlighted":
            if is_debug_mode():
                display_title = f"{debug_prefix('card')}{self.title}"
            else:
                display_title = self.title
            lines.append(f"*** {display_title} ***")
            # Add indented content for highlighted style
            for line in content_lines:
                lines.append(f"    {line}")
                
        else:  # minimal or default
            if is_debug_mode():
                display_title = f"{debug_prefix('card')}{self.title}"
            else:
                display_title = f"🎴 [CARD] {self.title}"
            lines.append(display_title)
            lines.append("-" * 50)
            # Add indented content for minimal style
            for line in content_lines:
                lines.append(f"  {line}")
        
        return lines
    
    def mark_dirty(self) -> None:
        """Mark this card as needing re-render."""
        super().mark_dirty()
        self._content_dirty = True
    
    # Backwards compatibility property
    @property
    def components(self) -> OrderedDict[int, CardChildInterface]:
        """Get the elements OrderedDict (for backwards compatibility)."""
        return self.get_elements()  # type: ignore

    def text_prompt(self, name: str, **kwargs: Any) -> "Card":
        """
        Add a text input component that prompts user for text input.

        Args:
            name: Component name for state storage
            **kwargs: Component configuration options

        Returns:
            Self for method chaining
        """
        if not hasattr(self.parent_page, "state"):
            raise NotImplementedError(
                "Card.text_prompt requires a parent Page with state management"
            )

        from .component_wrappers import text_prompt as _text_prompt_component

        comp = _text_prompt_component(name, **kwargs)
        self.add_element(comp)  # type: ignore - TODO: Update component to implement CardChildInterface
        return self

    def text_display(self, content: str, **kwargs: Any) -> "Card":
        """
        Add a display-only text component (like print() but page-controlled).

        Args:
            content: Text content to display
            **kwargs: Component configuration options

        Returns:
            Self for method chaining
        """
        from .component_wrappers import text_display as _text_display_component

        comp = _text_display_component(content, **kwargs)
        self.add_element(comp)  # type: ignore - TODO: Update component to implement CardChildInterface
        return self

    def text_section(self, content: str, title: str | None = None, **kwargs: Any) -> "Card":
        """
        Add a multi-line text block component.

        Args:
            content: Text content to display
            title: Optional section title
            **kwargs: Component configuration options

        Returns:
            Self for method chaining
        """
        from .component_wrappers import text_section as _text_section_component

        comp = _text_section_component(content, title=title, **kwargs)
        self.add_element(comp)  # type: ignore - TODO: Update component to implement CardChildInterface
        return self

    def text_status(self, content: str, status_type: str = "info", **kwargs: Any) -> "Card":
        """
        Add a status/progress message component.

        Args:
            content: Status message to display
            status_type: Type of status (info, success, warning, error)
            **kwargs: Component configuration options

        Returns:
            Self for method chaining
        """
        from .component_wrappers import text_status as _text_status_component

        comp = _text_status_component(content, status_type=status_type, **kwargs)
        self.add_element(comp)  # type: ignore - TODO: Update component to implement CardChildInterface
        return self

    def select_prompt(self, name: str, choices: List[str], **kwargs: Any) -> "Card":
        """
        Add a selection component that prompts user to choose from options.

        Args:
            name: Component name for state storage
            choices: List of selection options
            **kwargs: Component configuration options

        Returns:
            Self for method chaining
        """
        if not hasattr(self.parent_page, "state"):
            raise NotImplementedError(
                "Card.select_prompt requires a parent Page with state management"
            )

        from .component_wrappers import select_prompt as _select_prompt_component

        comp = _select_prompt_component(name, choices=choices, **kwargs)
        self.add_element(comp)  # type: ignore - TODO: Update component to implement CardChildInterface
        return self

    def assembly(self, name: str) -> "Any":
        """
        Add an Assembly for interactive component groups within this card.

        Args:
            name: Assembly namespace for state management

        Returns:
            Assembly instance for method chaining
        """
        # TODO: AssemblyBase needs to be updated with spatial awareness
        # For now, this will fail at runtime until AssemblyBase is updated
        from .assembly_base import AssemblyBase

        assembly = AssemblyBase(name, self.parent_page)
        self.add_element(assembly)  # type: ignore - TODO: Update assembly to implement CardChildInterface
        return assembly

    def show(self) -> None:
        """Make this card visible and notify parent of the change."""
        was_visible = self.visible
        super().show()
        
        # Fire change event if visibility actually changed
        if not was_visible:
            self.fire_change_event('visibility', space_delta=0, visible=True)

    def hide(self) -> None:
        """Hide this card and notify parent of the change."""
        was_visible = self.visible
        super().hide()
        
        # Fire change event if visibility actually changed  
        if was_visible:
            self.fire_change_event('visibility', space_delta=0, visible=False)

    def parent(self) -> "PageBase":
        """Return parent Page for navigation."""
        return self.parent_page


__all__ = ["Card"]
