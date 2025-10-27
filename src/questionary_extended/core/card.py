"""
Card class for questionary-extended.

The Card class provides visual grouping of related components with styling options,
dynamic show/hide capabilities, and responsive layout management.
"""

from typing import TYPE_CHECKING, Any, List, OrderedDict
from collections import OrderedDict as OrderedDictClass

from .interfaces import CardInterface, CardChildInterface, PageChildInterface
from .base_classes import CardBase

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
    
    # Renderable implementation
    def get_render_lines(self) -> List[str]:
        """Get the lines this card should output."""
        if not self.visible:
            return []
        
        lines = []
        
        # Add card header based on style
        if self.style == "bordered":
            lines.append(f"┌─ {self.title} ──")
        elif self.style == "highlighted":
            lines.append(f"*** {self.title} ***")
        else:  # minimal or default
            lines.append(f"• {self.title}")
        
        # Add elements content
        for element in self.get_elements().values():
            if hasattr(element, 'get_render_lines') and callable(getattr(element, 'get_render_lines')):
                element_lines = element.get_render_lines()  # type: ignore
                # Indent card content
                indented_lines = [f"  {line}" for line in element_lines]
                lines.extend(indented_lines)
        
        # Add card footer for bordered style
        if self.style == "bordered" and lines:
            lines.append("└─────────────")
        
        return lines
    
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
        from .assembly_base import AssemblyBase

        assembly = AssemblyBase(name, self.parent_page)
        self.add_element(assembly)  # type: ignore - TODO: Update assembly to implement CardChildInterface
        return assembly

    def show(self) -> None:
        """Make this card visible."""
        super().show()

    def hide(self) -> None:
        """Hide this card."""
        super().hide()

    def parent(self) -> "PageBase":
        """Return parent Page for navigation."""
        return self.parent_page


__all__ = ["Card"]
