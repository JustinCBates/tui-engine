"""
Page class for questionary-extended.

The Page class serves as the top-level container for complex multi-component UIs,
providing state management, navigation, and orchestration of Cards and Assemblies.
"""

import os
from typing import TYPE_CHECKING, Any, Dict, List

from .state import PageState

if TYPE_CHECKING:
    from .assembly_base import AssemblyBase
    from .card import Card


class PageBase:
    """
    Top-level container for questionary-extended multi-component interfaces.

    Provides:
    - Component orchestration and method chaining
    - Page-scoped state management with assembly namespacing
    - Progress tracking and navigation
    - Responsive layout and scrolling management
    - Central visibility management with refresh capability
    """

    def __init__(self, title: str = "") -> None:
        """Initialize a new Page.

        Args:
            title: Optional page title for display
        """
        self.title = title
        self.components: List[Any] = []
        self.state = PageState()
        self.visible = True

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
        self.components.append(card)
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
        self.components.append(assembly)
        return assembly

    def clear_screen(self) -> None:
        """Clear the terminal screen."""
        os.system('clear' if os.name == 'posix' else 'cls')

    def _render_header(self) -> None:
        """Render the page header if title is set."""
        if self.title:
            print("=" * 60)
            print(f"📄 {self.title}")
            print("=" * 60)

    def _render_component(self, component: Any) -> None:
        """Render a single component if visible."""
        # Check if component has visibility (default to True if not set)
        visible = getattr(component, 'visible', True)
        if not visible:
            return

        # Render based on component type
        if hasattr(component, 'title') and hasattr(component, 'components'):
            # This is a Card - render title and its components
            self._render_card(component)
        elif hasattr(component, 'name') and hasattr(component, 'components'):
            # This is an Assembly - render its components
            self._render_assembly(component)
        elif hasattr(component, 'name'):
            # This is a standalone Component - render placeholder
            self._render_standalone_component(component)

    def _render_card(self, card: Any) -> None:
        """Render a Card with its components."""
        print(f"\n🎴 {card.title}")
        print("-" * 50)
        
        for component in card.components:
            self._render_component(component)

    def _render_assembly(self, assembly: Any) -> None:
        """Render an Assembly's components."""
        print(f"\n🔧 Assembly: {assembly.name}")
        
        for component in assembly.components:
            self._render_component(component)

    def _render_standalone_component(self, component: Any) -> None:
        """Render a standalone component placeholder."""
        print(f"📝 Component: {component.name}")

    def refresh(self) -> None:
        """Clear screen and reprint all visible elements in order."""
        self.clear_screen()
        
        # Render page header
        self._render_header()
        
        # Render all visible components in order
        for component in self.components:
            self._render_component(component)

    def show(self) -> None:
        """Make this page visible."""
        self.visible = True

    def hide(self) -> None:
        """Hide this page."""
        self.visible = False

    def run(self) -> Dict[str, Any]:
        """Execute the page and return collected results.

        Returns:
            Flat dictionary with component results
        """
        raise NotImplementedError("Page execution requires a QuestionaryBridge")


__all__ = ["PageBase"]
