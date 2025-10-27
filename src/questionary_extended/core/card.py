"""
Card class for questionary-extended.

The Card class provides visual grouping of related components with styling options,
dynamic show/hide capabilities, and responsive layout management.
"""

from typing import TYPE_CHECKING, Any, List

if TYPE_CHECKING:
    from .page_base import PageBase


class Card:
    """
    Visual grouping container for related components.

    Provides:
    - Visual styling options (minimal, bordered, highlighted, collapsible)
    - Dynamic show/hide with smooth transitions
    - Horizontal/vertical layout with responsive fallback
    - Component overflow handling and scrolling
    """

    def __init__(self, title: str, parent: "PageBase", style: str = "minimal") -> None:
        """
        Initialize a new Card.

        Args:
            title: Card title/header
            parent: Parent Page instance
            style: Visual style (minimal, bordered, highlighted, collapsible)
        """
        self.title = title
        self.parent_page = parent
        self.style = style
        self.components: List[Any] = []
        self.visible = True

    def text(self, name: str, **kwargs: Any) -> "Card":
        """
        Add a text input component.

        Args:
            name: Component name for state storage
            **kwargs: Component configuration options

        Returns:
            Self for method chaining
        """
        if not hasattr(self.parent_page, "state"):
            raise NotImplementedError(
                "Card.text requires a parent Page with state management"
            )

        from .component_wrappers import text as _text_component

        comp = _text_component(name, **kwargs)
        self.components.append(comp)
        return self

    def select(self, name: str, choices: List[str], **kwargs: Any) -> "Card":
        """
        Add a selection component.

        Args:
            name: Component name for state storage
            choices: List of selection options
            **kwargs: Component configuration options

        Returns:
            Self for method chaining
        """
        if not hasattr(self.parent_page, "state"):
            raise NotImplementedError(
                "Card.select requires a parent Page with state management"
            )

        from .component_wrappers import select as _select_component

        comp = _select_component(name, choices=choices, **kwargs)
        self.components.append(comp)
        return self

    def assembly(self, name: str) -> "Any":
        """
        Add an Assembly for interactive component groups within this card.

        Args:
            name: Assembly namespace for state management

        Returns:
            Assembly instance for method chaining
        """
        from .assembly_base import AssemblyBase

        assembly = AssemblyBase(name, self.parent_page)
        self.components.append(assembly)
        return assembly

    def show(self) -> None:
        """Make this card visible."""
        self.visible = True

    def hide(self) -> None:
        """Hide this card."""
        self.visible = False

    def parent(self) -> "PageBase":
        """Return parent Page for navigation."""
        return self.parent_page


__all__ = ["Card"]
