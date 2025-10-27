"""
Page class for questionary-extended.

The Page class serves as the top-level container for complex multi-component UIs,
providing state management, navigation, and orchestration of Cards and Assemblies.
"""

import os
from typing import TYPE_CHECKING, Any, Dict, List, OrderedDict, Set, Union
from collections import OrderedDict as OrderedDictClass

from .state import PageState
from .interfaces import PageInterface, PageChildInterface
from .base_classes import PageBase as PageBaseImpl

# For backwards compatibility during transition
PageChild = PageChildInterface

if TYPE_CHECKING:
    from .assembly_base import AssemblyBase
    from .card import Card


class PageBase(PageBaseImpl, PageInterface):
    """
    Top-level container for questionary-extended multi-component interfaces.

    Provides:
    - Component orchestration and method chaining
    - Page-scoped state management with assembly namespacing
    - Progress tracking and navigation
    - Responsive layout and scrolling management
    - Central visibility management with refresh capability
    """

    def __init__(self, title: str = "", **kwargs: Any):
        """Initialize a new page.
        
        Args:
            title: Optional page title to display
            **kwargs: Additional page configuration
        """
        # Initialize base classes (provides element management)
        super().__init__()
        
        self.title = title
        self._last_component_lines = 0  # Track only component lines for cursor movement
    
    @property
    def components(self) -> OrderedDict[int, PageChildInterface]:
        """Get the elements OrderedDict (for backwards compatibility)."""
        # Safe cast since PageBase enforces only PageChildInterface elements
        return self.get_elements()  # type: ignore
    
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
        if self.title:
            lines.append(f"=== {self.title} ===")
            lines.append("")
        
        # Add child content lines
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
        """Add a status/progress message component to the page.

        Args:
            content: Status message to display
            status_type: Type of status (info, success, warning, error)
            **kwargs: Component configuration options

        Returns:
            Self for method chaining
        """
        from .component_wrappers import text_status

        comp = text_status(content, status_type=status_type, **kwargs)
        self._add_child(comp)
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
            print(f"📄 [PAGE] {self.title}")
            print("=" * 60)
            self._header_rendered = True
        
        # Build component lines
        component_lines = []
        for component in self.components.values():
            if getattr(component, 'visible', True):
                component_lines.extend(self._get_component_lines(component))
        
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
