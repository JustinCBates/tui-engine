"""
Page class for questionary-extended.

The Page class serves as the top-level container for complex multi-component UIs,
providing state management, navigation, and orchestration of Cards and Assemblies.
"""

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
    """

    def __init__(self, title: str = "") -> None:
        """Initialize a new Page.

        Args:
            title: Optional page title for display
        """
        self.title = title
        self.components: List[Any] = []
        self.state = PageState()

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

    def run(self) -> Dict[str, Any]:
        """Execute the page and return collected results.

        Returns:
            Flat dictionary with component results
        """
        raise NotImplementedError("Page execution requires a QuestionaryBridge")


__all__ = ["PageBase"]
