"""
Page class for questionary-extended.

The Page class serves as the top-level container for complex multi-component UIs,
providing state management, navigation, and orchestration of Cards and Assemblies.
Enhanced with spatial awareness and section-based layout management.
"""

import os
from typing import TYPE_CHECKING, Any, Dict, List, Optional, OrderedDict, Set, Union, Callable
from collections import OrderedDict as OrderedDictClass

from .state import PageState
from .interfaces import PageInterface, PageChildInterface, ElementChangeEvent, SpaceRequirement, BufferDelta
from .base_classes import PageBase as PageBaseImpl
from .debug_mode import debug_prefix, is_debug_mode
from .spatial import SpatiallyAware, LayoutEngine
from .buffer_manager import ANSIBufferManager, FallbackBufferManager

# For backwards compatibility during transition
PageChild = PageChildInterface

if TYPE_CHECKING:
    from .assembly_base import AssemblyBase
    from .card import Card
    from .section import Section


class PageBase(PageBaseImpl, PageInterface, SpatiallyAware):
    """
    Top-level container for questionary-extended multi-component interfaces.

    Provides:
    - Component orchestration and method chaining
    - Page-scoped state management with assembly namespacing
    - Progress tracking and navigation
    - Responsive layout and scrolling management
    - Central visibility management with refresh capability
    - Spatial awareness and section-based layout management
    - Advanced buffer management for flicker-free updates
    """

    def __init__(self, title: str = "", use_spatial_layout: bool = True, **kwargs: Any):
        """Initialize a new page.
        
        Args:
            title: Optional page title to display
            use_spatial_layout: Enable spatial layout management
            **kwargs: Additional page configuration
        """
        # Initialize base classes (provides element management)
        super().__init__()
        
        self.title = title
        self._last_component_lines = 0  # Track only component lines for cursor movement
        self._current_status_id: Optional[int] = None  # Track current status component
        
        # Spatial layout management
        self.use_spatial_layout = use_spatial_layout
        self._change_listeners: List[Callable[[ElementChangeEvent], None]] = []
        if use_spatial_layout:
            self._buffer_manager = self._create_buffer_manager()
            self._layout_engine = LayoutEngine()
            self._sections: Dict[str, "Section"] = {}
        else:
            self._buffer_manager = None
            self._layout_engine = None
            self._sections = {}
    
    def _create_buffer_manager(self):
        """Create appropriate buffer manager based on environment."""
        # For now, always use ANSI since we confirmed it works
        # Could add detection logic here later
        return ANSIBufferManager()
    
    # SpatiallyAware implementation
    def calculate_space_requirements(self) -> SpaceRequirement:
        """Calculate space requirements for the entire page."""
        if not self.use_spatial_layout:
            # Fallback to line counting
            lines = self.get_render_lines()
            line_count = len(lines)
            return SpaceRequirement(
                min_lines=line_count,
                current_lines=line_count,
                max_lines=line_count,
                preferred_lines=line_count
            )
        
        # Calculate based on sections
        total_min = 0
        total_current = 0
        total_max = 0
        total_preferred = 0
        
        # Add title lines
        if self.title:
            title_lines = 4  # separator + title + separator + spacing
            total_min += title_lines
            total_current += title_lines
            total_max += title_lines
            total_preferred += title_lines
        
        # Add section requirements
        for section in self._sections.values():
            if section.visible:
                req = section.calculate_space_requirements()
                total_min += req.min_lines
                total_current += req.current_lines
                total_max += req.max_lines
                total_preferred += req.preferred_lines
        
        # Add regular elements (fallback)
        for element in self.get_elements().values():
            if hasattr(element, 'get_render_lines') and callable(getattr(element, 'get_render_lines')):
                lines = element.get_render_lines()  # type: ignore
                line_count = len(lines)
                total_min += line_count
                total_current += line_count
                total_max += line_count
                total_preferred += line_count
        
        return SpaceRequirement(
            min_lines=total_min,
            current_lines=total_current,
            max_lines=total_max,
            preferred_lines=total_preferred
        )
    
    def calculate_buffer_changes(self) -> BufferDelta:
        """Calculate buffer changes for the page."""
        if not self.use_spatial_layout:
            # Fallback: full refresh
            lines = self.get_render_lines()
            return BufferDelta(
                line_updates=[(i, line) for i, line in enumerate(lines)],
                space_change=0,
                clear_lines=[]
            )
        
        # Aggregate changes from sections
        all_line_updates = []
        total_space_change = 0
        all_clear_lines = []
        
        current_line = 0
        
        # Handle title
        if self.title:
            # Title is typically static, only update if changed
            title_lines = self._get_title_lines()
            for i, line in enumerate(title_lines):
                all_line_updates.append((current_line + i, line))
            current_line += len(title_lines)
        
        # Handle sections
        for section in self._sections.values():
            if section.visible:
                section_delta = section.calculate_buffer_changes()
                
                # Offset line updates by current position
                for rel_line, content in section_delta.line_updates:
                    all_line_updates.append((current_line + rel_line, content))
                
                # Offset clear lines
                for rel_line in section_delta.clear_lines:
                    all_clear_lines.append(current_line + rel_line)
                
                total_space_change += section_delta.space_change
                
                # Move to next section position
                section_req = section.calculate_space_requirements()
                current_line += section_req.current_lines
        
        return BufferDelta(
            line_updates=all_line_updates,
            space_change=total_space_change,
            clear_lines=all_clear_lines
        )
    
    def can_compress_to(self, lines: int) -> bool:
        """Check if page can be compressed to given lines."""
        req = self.calculate_space_requirements()
        return req.min_lines <= lines
    
    def compress_to_lines(self, lines: int) -> None:
        """Compress page content to fit in specified lines."""
        # Implementation would compress sections as needed
        pass
    
    # Section management
    def create_section(self, name: str, static: bool = False, **kwargs: Any) -> "Section":
        """Create a new section in this page."""
        if not self.use_spatial_layout:
            raise ValueError("Sections require spatial layout to be enabled")
        
        from .section import Section
        section = Section(name, static=static, **kwargs)
        self._sections[name] = section
        return section
    
    def get_section(self, name: str) -> Optional["Section"]:
        """Get a section by name."""
        return self._sections.get(name)
    
    def header_section(self, **kwargs: Any) -> "Section":
        """Get or create the header section (static by default)."""
        if "header" not in self._sections:
            return self.create_section("header", static=True, **kwargs)
        return self._sections["header"]
    
    def body_section(self, **kwargs: Any) -> "Section":
        """Get or create the body section (dynamic by default)."""
        if "body" not in self._sections:
            return self.create_section("body", static=False, **kwargs)
        return self._sections["body"]
    
    def footer_section(self, **kwargs: Any) -> "Section":
        """Get or create the footer section (static by default)."""
        if "footer" not in self._sections:
            return self.create_section("footer", static=True, **kwargs)
        return self._sections["footer"]
    
    def _get_title_lines(self) -> List[str]:
        """Get the title lines for rendering."""
        if not self.title:
            return []
        
        # Add debug prefix only in debug mode
        if is_debug_mode():
            display_title = f"{debug_prefix('page')}{self.title}"
        else:
            display_title = self.title
            
        return [
            "=" * 60,
            display_title,
            "=" * 60,
            ""
        ]
    
    @property
    def components(self) -> OrderedDict[int, PageChildInterface]:
        """Get the elements OrderedDict (for backwards compatibility)."""
        # Safe cast since PageBase enforces only PageChildInterface elements
        return self.get_elements()  # type: ignore
    
    # =================================================================
    # CONTAINER INTERFACE IMPLEMENTATION (REQUIRED)
    # =================================================================
    
    def on_child_changed(self, child_event: ElementChangeEvent) -> None:
        """
        Handle change events from child elements.
        
        Pages process child changes and can update the display.
        Since pages are top-level, they don't propagate further up.
        """
        # Mark ourselves for potential re-render
        if self._buffer_manager:
            # Could trigger incremental update here
            pass
        
        # Notify our listeners (typically for testing or external monitoring)
        for listener in self._change_listeners:
            try:
                listener(child_event)
            except Exception:
                # Don't let listener exceptions break the page
                pass
    
    def calculate_aggregate_space_requirements(self) -> SpaceRequirement:
        """
        Calculate aggregate space requirements from all children.
        
        This is the same as calculate_space_requirements for pages.
        """
        return self.calculate_space_requirements()
    
    def allocate_child_space(self, child_name: str, requirement: SpaceRequirement) -> bool:
        """
        Attempt to allocate space to a child element.
        
        Pages have flexible space allocation for their children.
        """
        # Find the child by name
        for element in self.get_elements().values():
            if hasattr(element, 'name') and element.name == child_name:
                # Pages can typically accommodate any reasonable child space request
                return True
        
        # Check sections too
        for section in self._sections.values():
            if section.name == child_name:
                return True
        
        return False  # Child not found
    
    def get_child_render_position(self, child_name: str) -> int:
        """
        Get the relative starting line position for a child element.
        
        Calculates position based on title, sections, and elements.
        """
        current_position = 0
        
        # Add title lines
        if self.title:
            current_position += len(self._get_title_lines())
        
        # Check sections first
        section_order = ["header", "body", "footer"]
        for section_name in section_order:
            if section_name in self._sections:
                section = self._sections[section_name]
                if section.name == child_name:
                    return current_position
                
                if section.visible:
                    section_req = section.calculate_space_requirements()
                    current_position += section_req.current_lines
                    current_position += 1  # Spacing after section
        
        # Check regular elements
        for element in self.get_elements().values():
            if hasattr(element, 'name') and element.name == child_name:
                return current_position
            
            if hasattr(element, 'get_render_lines') and callable(getattr(element, 'get_render_lines')):
                element_lines = element.get_render_lines()  # type: ignore
                current_position += len(element_lines)
                current_position += 1  # Spacing between elements
        
        return current_position  # If not found, return current position
    
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
                # Don't let listener exceptions break the page
                pass
    
    def register_change_listener(self, listener: Callable[[ElementChangeEvent], None]) -> None:
        """Register listener for change events."""
        if listener not in self._change_listeners:
            self._change_listeners.append(listener)

    # =================================================================
    # ELEMENT INTERFACE IMPLEMENTATION
    # =================================================================
    
    # ElementInterface implementation
    @property
    def name(self) -> str:
        """Unique identifier for this page."""
        return self.title or "untitled_page"
    
    @property
    def element_type(self) -> str:
        """Type of element (always 'page')."""
        return "page"
    
    # PageInterface implementation - add_element is inherited from base class
    def add_element(self, element: PageChildInterface) -> int:
        """Add an element that can be a child of a Page."""
        return super().add_element(element)
    
    # Renderable implementation
    def get_render_lines(self) -> List[str]:
        """Get the lines this page should output."""
        if not self.visible:
            return []
        
        lines = []
        
        # Add title
        if self.title:
            lines.extend(self._get_title_lines())
        
        # Handle spatial layout vs traditional layout
        if self.use_spatial_layout and self._sections:
            # Render sections in order: header, body, footer (if they exist)
            section_order = ["header", "body", "footer"]
            
            for section_name in section_order:
                if section_name in self._sections:
                    section = self._sections[section_name]
                    if section.visible:
                        section_lines = section.get_render_lines()
                        lines.extend(section_lines)
                        # Add spacing after section if it has content
                        if section_lines:
                            lines.append("")
            
            # Also add any regular elements for backward compatibility
            for element in self.get_elements().values():
                if hasattr(element, 'get_render_lines') and callable(getattr(element, 'get_render_lines')):
                    child_lines = element.get_render_lines()  # type: ignore
                    lines.extend(child_lines)
                    if child_lines:  # Add spacing between elements
                        lines.append("")
        else:
            # Traditional layout - just add child elements
            for element in self.get_elements().values():
                if hasattr(element, 'get_render_lines') and callable(getattr(element, 'get_render_lines')):
                    child_lines = element.get_render_lines()  # type: ignore
                    lines.extend(child_lines)
                    if child_lines:  # Add spacing between elements
                        lines.append("")
        
        return lines
    
    def _add_child(self, child: Any) -> int:
        """Add a child component/container with interface enforcement.
        
        Args:
            child: Component, Card, or Assembly that implements PageChild interface
            
        Returns:
            The assigned component ID
            
        Raises:
            ValueError: If name already exists
            TypeError: If child doesn't have required interface methods
        """
        # Use the base class add_element method which enforces interface validation
        return self.add_element(child)

    def card(self, title: str, **kwargs: Any) -> "Card":
        """Add a Card for visual grouping of components.

        Args:
            title: Card title/header
            **kwargs: Card styling and behavior options

        Returns:
            Card instance for method chaining
        """
        from .card import Card

        card = Card(title, self, **kwargs)
        self._add_child(card)
        return card

    def assembly(self, name: str) -> "AssemblyBase":
        """Add an Assembly for interactive component groups.

        Args:
            name: Assembly namespace for state management

        Returns:
            Assembly instance for method chaining
        """
        from .assembly_base import AssemblyBase

        assembly = AssemblyBase(name, self)
        self._add_child(assembly)
        return assembly

    def text_display(self, content: str, **kwargs: Any) -> "PageBase":
        """Add a display-only text component to the page.

        Args:
            content: Text content to display
            **kwargs: Component configuration options

        Returns:
            Self for method chaining
        """
        from .component_wrappers import text_display

        comp = text_display(content, **kwargs)
        self._add_child(comp)
        return self

    def text_status(self, content: str, status_type: str = "info", **kwargs: Any) -> "PageBase":
        """Add or replace a status/progress message component on the page.

        Args:
            content: Status message to display
            status_type: Type of status (info, success, warning, error)
            **kwargs: Component configuration options

        Returns:
            Self for method chaining
        """
        from .component_wrappers import text_status

        # Remove previous status component if it exists
        if self._current_status_id is not None:
            self.remove_element(self._current_status_id)
            self._current_status_id = None

        # Add new status component
        comp = text_status(content, status_type=status_type, **kwargs)
        status_id = self._add_child(comp)
        self._current_status_id = status_id
        return self

    def clear_screen(self) -> None:
        """Clear the terminal screen."""
        os.system('clear' if os.name == 'posix' else 'cls')

    def _move_cursor_up(self, lines: int) -> None:
        """Move cursor up by specified number of lines."""
        if lines > 0:
            print(f"\x1b[{lines}A", end="")

    def _clear_line(self) -> None:
        """Clear the current line."""
        print("\x1b[2K", end="")

    def _save_cursor(self) -> None:
        """Save current cursor position."""
        print("\x1b[s", end="")

    def _restore_cursor(self) -> None:
        """Restore saved cursor position."""
        print("\x1b[u", end="")

    def _render_header(self) -> int:
        """Render the page header if title is set.
        
        Returns:
            Number of lines rendered
        """
        if self.title:
            self._clear_line()
            print("=" * 60)
            self._clear_line()
            print(f"📄 [PAGE] {self.title}")
            self._clear_line()
            print("=" * 60)
            return 3
        return 0

    def _render_component(self, component: Any) -> int:
        """Render a single component if visible.
        
        Returns:
            Number of lines rendered
        """
        # Check if component has visibility (default to True if not set)
        visible = getattr(component, 'visible', True)
        if not visible:
            return 0

        # Render based on component type
        if hasattr(component, 'title') and hasattr(component, 'components'):
            # This is a Card - render title and its components
            return self._render_card(component)
        elif hasattr(component, 'name') and hasattr(component, 'components'):
            # This is an Assembly - render its components
            return self._render_assembly(component)
        elif hasattr(component, 'name'):
            # This is a standalone Component - render placeholder
            return self._render_standalone_component(component)
        
        return 0

    def _render_card(self, card: Any) -> int:
        """Render a Card with its components.
        
        Returns:
            Number of lines rendered
        """
        self._clear_line()
        print(f"\n🎴 [CARD] {card.title}")
        self._clear_line()
        print("-" * 50)
        lines_rendered = 2
        
        for component in card.components:
            lines_rendered += self._render_component(component)
        
        return lines_rendered

    def _render_assembly(self, assembly: Any) -> int:
        """Render an Assembly's components.
        
        Returns:
            Number of lines rendered
        """
        self._clear_line()
        print(f"\n🔧 Assembly: {assembly.name}")
        lines_rendered = 1
        
        for component in assembly.components:
            lines_rendered += self._render_component(component)
        
        return lines_rendered

    def _render_standalone_component(self, component: Any) -> int:
        """Render a standalone component placeholder.
        
        Returns:
            Number of lines rendered
        """
        self._clear_line()
        print(f"📝 Component: {component.name}")
        return 1

    def _get_component_lines(self, component: Any) -> List[str]:
        """Get the lines that would be rendered for a component.
        
        Returns:
            List of strings representing the component output
        """
        lines = []
        
        # Check visibility
        if not getattr(component, 'visible', True):
            return lines

        # Handle different component types
        if hasattr(component, 'title') and hasattr(component, 'components'):
            # This is a Card
            lines.append("")  # Empty line before card
            lines.append(f"🎴 [CARD] {component.title}")
            lines.append("-" * 50)
            
            for subcomponent in component.components:
                lines.extend(self._get_component_lines(subcomponent))
                
        elif hasattr(component, 'name') and hasattr(component, 'components'):
            # This is an Assembly
            lines.append("")  # Empty line before assembly
            lines.append(f"🔧 Assembly: {component.name}")
            
            for subcomponent in component.components:
                lines.extend(self._get_component_lines(subcomponent))
                
        elif hasattr(component, 'name'):
            # This is a standalone Component - check if it's a display component
            if hasattr(component, 'component_type'):
                if component.component_type == "text_display":
                    lines.append(component.config.get("content", ""))
                elif component.component_type == "text_section":
                    if component.config.get("title"):
                        lines.append(f"📄 {component.config['title']}")
                        lines.append("-" * 30)
                    content = component.config.get("content", "")
                    lines.extend(content.split('\n'))
                elif component.component_type == "text_status":
                    status_type = component.config.get("status_type", "info")
                    content = component.config.get("content", "")
                    status_icons = {
                        "info": "ℹ️",
                        "success": "✅", 
                        "warning": "⚠️",
                        "error": "❌"
                    }
                    icon = status_icons.get(status_type, "ℹ️")
                    lines.append(f"{icon} {content}")
                else:
                    # Regular questionary component (placeholder)
                    lines.append(f"📝 Component: {component.name}")
            else:
                lines.append(f"📝 Component: {component.name}")
        
        return lines

    def refresh(self) -> None:
        """Questionary-style incremental refresh - no screen clearing."""
        
        # Render header only on first call
        if self.title and not self._header_rendered:
            print("=" * 60)
            if is_debug_mode():
                print(f"📄 [PAGE] {self.title}")
            else:
                print(self.title)
            print("=" * 60)
            self._header_rendered = True
        
        # Build component lines using proper get_render_lines method
        component_lines = []
        for component in self.components.values():
            if hasattr(component, 'get_render_lines') and callable(getattr(component, 'get_render_lines')):
                # Use the component's get_render_lines which handles visibility internally
                child_lines = component.get_render_lines()  # type: ignore
                component_lines.extend(child_lines)
                if child_lines:  # Add spacing between visible elements
                    component_lines.append("")
        
        # For incremental refresh mode
        if hasattr(self, '_safe_incremental') and self._safe_incremental:
            # Move cursor up to overwrite previous component content
            if self._last_component_lines > 0:
                self._move_cursor_up(self._last_component_lines)
            
            # Render each component line, clearing it first
            for line in component_lines:
                self._clear_line()
                print(line)
            
            # Clear any remaining lines from previous component render
            lines_to_clear = self._last_component_lines - len(component_lines)
            for _ in range(lines_to_clear):
                self._clear_line()
                print()  # Move to next line to clear it
        else:
            # Fallback: print content normally (no cursor manipulation)
            for line in component_lines:
                print(line)
                
        self._last_component_lines = len(component_lines)

    def enable_safe_incremental(self) -> None:
        """Enable incremental refresh mode (only when no external output)."""
        self._safe_incremental = True
        
    def disable_safe_incremental(self) -> None:
        """Disable incremental refresh mode (fallback to normal printing)."""
        self._safe_incremental = False

    def show(self) -> None:
        """Make this page visible."""
        super().show()

    def hide(self) -> None:
        """Hide this page."""
        super().hide()

    def run(self) -> Dict[str, Any]:
        """Execute the page and return collected results.

        Returns:
            Flat dictionary with component results
        """
        raise NotImplementedError("Page execution requires a QuestionaryBridge")


__all__ = ["PageBase"]
