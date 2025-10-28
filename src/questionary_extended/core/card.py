"""
Card class for questionary-extended.

The Card class provides visual grouping of related components with styling options,
dynamic show/hide capabilities, and responsive layout management.
"""

from typing import TYPE_CHECKING, Any, List, OrderedDict
from collections import OrderedDict as OrderedDictClass

from .interfaces import CardInterface, CardChildInterface, PageChildInterface
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
