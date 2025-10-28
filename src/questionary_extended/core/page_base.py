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
from .interfaces import PageInterface, PageChildInterface, ElementChangeEvent
from .spatial import SpaceRequirement, BufferDelta, SpatiallyAware, LayoutEngine
from .base_classes import PageBase as PageBaseImpl
from .debug_mode import debug_prefix, is_debug_mode
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

    def __init__(self, title: str = "", use_spatial_layout: bool = True, header: Optional[Union[str, List[str]]] = None, **kwargs: Any):
        """Initialize a new page.
        
        Args:
            title: Optional page title to display
            use_spatial_layout: Enable spatial layout management
            **kwargs: Additional page configuration
        """
        # Initialize base classes (provides element management)
        super().__init__()
        
        self.title = title
        # Visibility controls: allow toggling title and header independently
        self.title_visible = True

        self._last_component_lines = 0  # Track only component lines for cursor movement
        self._current_status_id: Optional[int] = None  # Track current status component
        # Track last prompt-clear handled timestamp to avoid re-asserting
        # the same prompt clear multiple times.
        self._last_prompt_clear_handled_ts: float = 0.0

        # Spatial layout management
        self.use_spatial_layout = use_spatial_layout
        self._change_listeners: List[Callable[[ElementChangeEvent], None]] = []
        self._last_rendered_content: List[str] = []  # Track last rendered content
        if use_spatial_layout:
            self._buffer_manager = self._create_buffer_manager()
            self._layout_engine = LayoutEngine()
            # Use an ordered dict to ensure title appears before header/body/footer
            self._sections: Dict[str, "Section"] = OrderedDictClass()
            # Ensure a reserved title and header section exist (static) and are visible by default
            try:
                from .section import Section
                from .component_wrappers import text_display

                # Create title section and populate with title lines
                title_section = Section('title', static=True)
                for line in self._get_title_lines():
                    title_section.add_element(text_display(line))
                title_section.show()
                title_section.mark_dirty()
                try:
                    setattr(title_section, '_parent', self)
                except Exception:
                    pass
                self._sections['title'] = title_section

                # Create header section (separate from title)
                hdr = Section('header', static=True)
                # If header content was provided to constructor, populate it
                if header is not None:
                    if isinstance(header, list):
                        lines = header
                    else:
                        lines = str(header).split('\n')
                    for line in lines:
                        hdr.add_element(text_display(line))
                hdr.show()
                hdr.mark_dirty()
                try:
                    setattr(hdr, '_parent', self)
                except Exception:
                    pass
                self._sections['header'] = hdr

                # Create body section (dynamic) to hold cards/components
                body = Section('body', static=False)
                body.show()
                body.mark_dirty()
                try:
                    setattr(body, '_parent', self)
                except Exception:
                    pass
                self._sections['body'] = body

                # Create footer section (static) reserved for end-of-page content
                footer = Section('footer', static=True)
                footer.show()
                footer.mark_dirty()
                try:
                    setattr(footer, '_parent', self)
                except Exception:
                    pass
                self._sections['footer'] = footer
            except Exception:
                # If Section or component factories cannot be imported for some edge case, leave sections empty
                self._sections = OrderedDictClass()
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
        
        # Calculate changes for spatial layout
        all_line_updates = []
        total_space_change = 0
        all_clear_lines = []
        current_line = 0
        
        # Sections (title, header, body, footer) produce their own deltas.
        # We rely on the reserved 'title' and 'header' sections existing in
        # self._sections (created at init) so they are handled below in order.
        
        # Handle sections if we have section-based layout
        if self._sections:
            for section_name, section in self._sections.items():
                if section.visible:
                    section_delta = section.calculate_buffer_changes()

                    # Debug: report per-section delta counts
                    if is_debug_mode():
                        try:
                            print(f"DEBUG: Section '{section_name}' -> {len(section_delta.line_updates)} updates, {len(section_delta.clear_lines)} clears, space_change={section_delta.space_change}")
                        except Exception:
                            pass

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
                    # Page rendering adds a blank spacer line after a section
                    # when the section has visible content (see `get_render_lines`).
                    # Ensure our position accounting matches that behavior so
                    # subsequent sections/components are offset correctly.
                    try:
                        if section.get_render_lines():
                            current_line += 1
                    except Exception:
                        # Conservative: if we cannot query render lines, skip spacer
                        pass
        else:
            # Handle direct components (no sections)
            # Get all component render lines
            component_lines = []
            for component in self.components.values():
                if hasattr(component, 'get_render_lines') and callable(getattr(component, 'get_render_lines')):
                    child_lines = component.get_render_lines()  # type: ignore
                    component_lines.extend(child_lines)
                    if child_lines:  # Add spacing between visible elements
                        component_lines.append("")
            
            # Only add lines that have actually changed
            if hasattr(self, '_last_rendered_content') and self._last_rendered_content == component_lines:
                # Content hasn't changed, no line updates needed
                pass
            else:
                # Content has changed, add line updates
                for i, line in enumerate(component_lines):
                    all_line_updates.append((current_line + i, line))

                # If previous content existed and was longer, schedule clear lines
                prev_len = len(self._last_rendered_content) if hasattr(self, '_last_rendered_content') else 0
                curr_len = len(component_lines)
                if prev_len > curr_len:
                    for i in range(curr_len, prev_len):
                        all_clear_lines.append(current_line + i)

                # Remember what we rendered
                self._last_rendered_content = component_lines.copy()
        
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
        """Create a new section in this page.

        Sections historically required the spatial layout engine. For
        compatibility we create and return a Section object regardless of
        whether spatial layout is enabled. When spatial layout is disabled
        the Section will behave as a lightweight renderable container (like
        a Card) and the Page will render its lines using the non-spatial
        fallback rendering path.
        """
        from .section import Section
        section = Section(name, static=static, **kwargs)
        # Ensure our sections dict exists and register the section so callers
        # can retrieve it via get_section/body_section/etc.
        try:
            self._sections[name] = section
        except Exception:
            # If _sections isn't available for some reason, create it.
            self._sections = OrderedDictClass()
            self._sections[name] = section
        # Attach parent for potential event propagation
        try:
            setattr(section, '_parent', self)
        except Exception:
            pass
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
        if not getattr(self, 'title_visible', True):
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

    # -----------------------------------------------------------------
    # Title/Header visibility controls
    # -----------------------------------------------------------------
    def set_title_visible(self, visible: bool) -> None:
        """Show or hide the page title. Defaults to True."""
        # Title is represented by the reserved 'title' section; toggle its visibility
        if 'title' in self._sections:
            if bool(visible):
                try:
                    self._sections['title'].show()
                except Exception:
                    pass
            else:
                try:
                    self._sections['title'].hide()
                except Exception:
                    pass
        else:
            # Fallback to attribute flag
            self.title_visible = bool(visible)

    def set_header_visible(self, visible: bool) -> None:
        """Show or hide the header section (creates it if missing)."""
        if 'header' not in self._sections:
            # Lazily create header if not present
            try:
                from .section import Section
                self._sections['header'] = Section('header', static=True)
            except Exception:
                return
        if bool(visible):
            self._sections['header'].show()
        else:
            self._sections['header'].hide()

    def is_title_visible(self) -> bool:
        """Return whether the title is visible."""
        if 'title' in self._sections:
            sec = self._sections.get('title')
            return bool(sec.visible) if sec is not None else False
        return bool(getattr(self, 'title_visible', True))

    def is_header_visible(self) -> bool:
        """Return whether the header section is visible."""
        sec = self._sections.get('header')
        return bool(sec.visible) if sec is not None else False

    # -----------------------------------------------------------------
    # Title / Header update helpers
    # -----------------------------------------------------------------
    def update_title(self, new_title: str) -> None:
        """Update the page title and refresh the reserved title section."""
        self.title = new_title
        # Rebuild title section content
        try:
            from .component_wrappers import text_display
            if 'title' not in self._sections:
                from .section import Section
                self._sections['title'] = Section('title', static=True)

            title_sec = self._sections['title']
            # Remove all existing elements
            for eid in list(title_sec.get_elements().keys()):
                title_sec.remove_element(eid)

            # Add new title lines
            for line in self._get_title_lines():
                title_sec.add_element(text_display(line))

            title_sec.mark_dirty()
            self.mark_dirty()
        except Exception:
            # Fallback: nothing
            pass

    def update_header(self, content: Union[str, List[str]]) -> None:
        """Update the header section content. Accepts string or list of lines."""
        try:
            from .component_wrappers import text_display
            if 'header' not in self._sections:
                from .section import Section
                self._sections['header'] = Section('header', static=True)

            hdr = self._sections['header']
            # Normalize content to list of lines
            lines: List[str]
            if isinstance(content, list):
                lines = content
            else:
                lines = str(content).split('\n')

            # Clear existing header elements
            for eid in list(hdr.get_elements().keys()):
                hdr.remove_element(eid)

            # Add new header lines
            for line in lines:
                hdr.add_element(text_display(line))

            hdr.mark_dirty()
            self.mark_dirty()
        except Exception:
            pass

    def show_title(self) -> None:
        """Show the title section."""
        if 'title' in self._sections:
            try:
                self._sections['title'].show()
            except Exception:
                pass

    def hide_title(self) -> None:
        """Hide the title section."""
        if 'title' in self._sections:
            try:
                self._sections['title'].hide()
            except Exception:
                pass

    def show_header(self) -> None:
        """Show the header section."""
        if 'header' in self._sections:
            try:
                self._sections['header'].show()
            except Exception:
                pass

    def hide_header(self) -> None:
        """Hide the header section."""
        if 'header' in self._sections:
            try:
                self._sections['header'].hide()
            except Exception:
                pass
    
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
        # Mark ourselves as needing a render; do not perform a synchronous refresh
        # here to avoid re-entrancy and blocking issues (which can make the
        # process unresponsive to interrupts). The top-level application loop
        # or caller should decide when to call `refresh()`.
        try:
            self.mark_dirty()
        except Exception:
            # If mark_dirty isn't available for some reason, fall back to setting
            # the internal flag directly.
            try:
                self._needs_render = True
            except Exception:
                pass

        # Notify any external listeners (for telemetry/tests)
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
            # Traditional layout - include any sections created even when
            # spatial layout is disabled (Sections should behave like
            # regular renderables/cards in non-spatial mode), then add
            # direct child elements for backward compatibility.
            if getattr(self, '_sections', None):
                for section in self._sections.values():
                    try:
                        if section.visible:
                            section_lines = section.get_render_lines()
                            lines.extend(section_lines)
                            if section_lines:
                                lines.append("")
                    except Exception:
                        # If a section misbehaves, skip it to avoid breaking page render
                        pass

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
        # If we have sections (title/header/body/footer), place cards into body section
        try:
            if isinstance(self._sections, dict) and 'body' in self._sections:
                body_sec = self._sections['body']
                body_sec.add_element(card)
                return card
        except Exception:
            # Fallback to legacy behavior
            pass

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

    def clear_status(self) -> None:
        """Clear any current status/progress message from the page."""
        status_id = getattr(self, '_current_status_id', None)
        if isinstance(status_id, int):
            try:
                self.remove_element(status_id)
            except Exception:
                pass
            self._current_status_id = None

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
        """
        Modern spatial-aware incremental refresh using buffer management.
        
        Uses the new universal spatial awareness system for flicker-free updates.
        """
        # Use spatial layout if enabled and buffer manager available
        # When a caller explicitly requests a refresh, treat it as an
        # authoritative redraw: mark sections dirty so their content is
        # recomputed and re-applied even if nothing has changed since the
        # last spatial delta. This fixes cases where the spatial machinery
        # produced an initial render but subsequent refreshes report no
        # delta (and therefore do not re-assert the visual state).
        if hasattr(self, '_sections') and self._sections:
            for sec in self._sections.values():
                try:
                    sec.mark_dirty()
                except Exception:
                    pass

        if (self.use_spatial_layout and 
            hasattr(self, '_buffer_manager') and 
            self._buffer_manager is not None):
            self._spatial_refresh()
        else:
            # If spatial layout is disabled or buffer manager missing,
            # still attempt to render by calculating buffer changes and
            # writing them sequentially using the buffer manager fallback.
            # We avoid calling legacy rendering and instead use the
            # fallback buffer manager if available.
            if not hasattr(self, '_buffer_manager') or self._buffer_manager is None:
                # No buffer manager at all; nothing to do.
                return
            # Use calculate_buffer_changes to get the full render and apply
            page_delta = self.calculate_buffer_changes()
            # Allocate space if needed
            try:
                if not hasattr(self, '_page_position') or not self._page_position:
                    space_req = self.calculate_space_requirements()
                    self._page_position = self._buffer_manager.allocate_space(self.name, space_req)
                self._buffer_manager.apply_buffer_delta(self._page_position, page_delta)
            except Exception:
                if is_debug_mode():
                    print("DEBUG: fallback apply failed in refresh")
                return
    
    def _spatial_refresh(self) -> None:
        """Spatial-aware refresh using buffer management and event system."""
        # Spatial refresh should always try to compute and apply buffer
        # deltas; do not fall back to legacy rendering here.
        # Ensure we have a buffer manager
        if not self._buffer_manager:
            if is_debug_mode():
                print("DEBUG: Buffer manager not available for spatial refresh")
            return

        if is_debug_mode():
            print("DEBUG: Using spatial refresh with buffer management")

        # Calculate what changes are needed
        page_delta = self.calculate_buffer_changes()

        if is_debug_mode():
            print(f"DEBUG: Buffer delta - {len(page_delta.line_updates)} line updates, space change: {page_delta.space_change}")

        # If there are no computed content changes but the page still has
        # visible content, we only force a full reassert/redraw if a prompt
        # emitted clear-like ANSI sequences since the last time we handled
        # such an event. This avoids unnecessary redraws while still
        # recovering after prompt-toolkit/questionary clears the terminal.
        if not page_delta.has_content_changes() and not page_delta.has_space_change() and not page_delta.clear_lines:
            try:
                # Import lazily to avoid circular import at module load
                from .component_wrappers import get_last_prompt_clear_ts

                last_ts = get_last_prompt_clear_ts()
                handled_ts = getattr(self, '_last_prompt_clear_handled_ts', 0.0)
                current_lines = self.get_render_lines()
                if current_lines and last_ts and last_ts > handled_ts:
                    if is_debug_mode():
                        print("DEBUG: No delta detected and prompt clear detected - forcing full redraw of page content")
                    page_delta = BufferDelta(
                        line_updates=[(i, line) for i, line in enumerate(current_lines)],
                        space_change=0,
                        clear_lines=[]
                    )
                    # Mark we've handled this prompt clear
                    try:
                        self._last_prompt_clear_handled_ts = float(last_ts)
                    except Exception:
                        self._last_prompt_clear_handled_ts = time.time()
            except Exception:
                # If anything goes wrong while forcing the redraw, fall back
                # to the previously computed (empty) delta and continue.
                pass
        # Handle space changes first (allocate/reallocate as needed)
        if page_delta.has_space_change():
            space_req = self.calculate_space_requirements()
            if hasattr(self, '_page_position') and self._page_position:
                # Reallocate existing space
                self._page_position = self._buffer_manager.reallocate_space(self.name, space_req)
            else:
                # Initial allocation
                self._page_position = self._buffer_manager.allocate_space(self.name, space_req)

        # If we don't yet have a page position, allocate based on current requirements
        if not hasattr(self, '_page_position') or not self._page_position:
            try:
                space_req = self.calculate_space_requirements()
                self._page_position = self._buffer_manager.allocate_space(self.name, space_req)
            except Exception:
                # Allocation failed; nothing further to do
                return

        # Apply the buffer changes if any
        if page_delta.has_content_changes() or page_delta.has_space_change() or page_delta.clear_lines:
            try:
                self._buffer_manager.apply_buffer_delta(self._page_position, page_delta)
            except Exception:
                if is_debug_mode():
                    print("DEBUG: apply_buffer_delta failed")
                return

        # Expose a public method for components to notify the page that a
        # prompt cleared the terminal while this page was active. This allows
        # the page to avoid reasserting unless it actually needs to.
    def mark_prompt_cleared(self, ts: float) -> None:
        """Record that a prompt clear occurred at timestamp `ts` and update
        the per-page handled timestamp if this is newer.
        """
        try:
            tsf = float(ts)
        except Exception:
            tsf = 0.0
        if tsf and tsf > getattr(self, '_last_prompt_clear_handled_ts', 0.0):
            try:
                self._last_prompt_clear_handled_ts = tsf
            except Exception:
                pass

        # Position cursor after rendered content
        try:
            if hasattr(self._buffer_manager, '_position_cursor_at_end'):
                try:
                    self._buffer_manager._position_cursor_at_end()
                except Exception:
                    pass
        except Exception:
            pass
    
    # Legacy printing path has been removed; PageBase is spatial-only.
    # If necessary, fallback behavior is provided by the buffer manager
    # implementations (FallbackBufferManager) which print sequentially.

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
