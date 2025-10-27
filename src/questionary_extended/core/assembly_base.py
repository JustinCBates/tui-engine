"""
Assembly class for questionary-extended.

The Assembly class provides interactive component groups with event-driven logic,
conditional behavior, cross-field validation, and state management.
"""

from typing import TYPE_CHECKING, Any, Callable, Dict, List, Tuple, Union, OrderedDict
from collections import OrderedDict as OrderedDictClass

from .interfaces import AssemblyInterface, AssemblyChildInterface, PageChildInterface, CardChildInterface
from .base_classes import AssemblyBase as AssemblyBaseImpl

if TYPE_CHECKING:
    from .page_base import PageBase


class AssemblyBase(AssemblyBaseImpl, AssemblyInterface):
    """
    Interactive component group with event-driven behavior.

    Provides:
    - Event hooks (.on_change, .on_validate, .on_complete)
    - Dynamic component visibility and interaction
    - Cross-field validation and state management
    - Reusable template patterns
    """

    def __init__(self, name: str, parent: "PageBase") -> None:
        """
        Initialize a new Assembly.

        Args:
            name: Assembly namespace for state management
            parent: Parent Page instance
        """
        # Initialize base classes
        super().__init__()
        
        self._name = name
        self.parent_page = parent
        # Note: components are now managed by base class as elements
        # Event handlers may be simple callables or (field, handler) tuples
        self.event_handlers: Dict[
            str, List[Union[Callable[..., Any], Tuple[str, Callable[..., Any]]]]
        ] = {"change": [], "validate": [], "complete": []}
    
    # ElementInterface implementation
    @property
    def name(self) -> str:
        """Unique identifier for this assembly."""
        return self._name
    
    @property
    def element_type(self) -> str:
        """Type of element (always 'assembly')."""
        return "assembly"
    
    # AssemblyInterface implementation
    def is_completed(self) -> bool:
        """Whether all required elements in this assembly are completed."""
        for element in self.get_elements().values():
            if hasattr(element, 'is_completed') and callable(getattr(element, 'is_completed')):
                if not element.is_completed():  # type: ignore
                    return False
        return True
    
    def is_valid(self) -> bool:
        """Whether all elements in this assembly have valid state."""
        for element in self.get_elements().values():
            if hasattr(element, 'is_valid') and callable(getattr(element, 'is_valid')):
                if not element.is_valid():  # type: ignore
                    return False
        return True
    
    def is_interactive(self) -> bool:
        """Whether this assembly requires user interaction."""
        for element in self.get_elements().values():
            if hasattr(element, 'is_interactive') and callable(getattr(element, 'is_interactive')):
                if element.is_interactive():  # type: ignore
                    return True
        return False
    
    # Renderable implementation
    def get_render_lines(self) -> List[str]:
        """Get the lines this assembly should output."""
        if not self.visible:
            return []
        
        lines = []
        
        # Add assembly header
        lines.append(f"--- {self.name} ---")
        
        # Add elements content
        for element in self.get_elements().values():
            if hasattr(element, 'get_render_lines') and callable(getattr(element, 'get_render_lines')):
                element_lines = element.get_render_lines()  # type: ignore
                lines.extend(element_lines)
        
        return lines
    
    # Backwards compatibility property
    @property
    def components(self) -> OrderedDict[int, AssemblyChildInterface]:
        """Get the elements OrderedDict (for backwards compatibility)."""
        return self.get_elements()  # type: ignore

    def text(self, name: str, **kwargs: Any) -> "AssemblyBase":
        """
        Add a text input component.

        Args:
            name: Component name for state storage
            **kwargs: Component configuration options (when, default, etc.)

        Returns:
            Self for method chaining
        """
        # Implementation pending Component system update to interfaces
        # from .component_wrappers import text
        # component = text(name, **kwargs)
        # self.add_element(component)  # type: ignore - TODO: Update component to implement AssemblyChildInterface
        
        # Temporary placeholder until components are updated
        print(f"TODO: Add text component '{name}' to assembly '{self.name}'")
        return self

    def select(self, name: str, choices: List[str], **kwargs: Any) -> "AssemblyBase":
        """
        Add a select input component.

        Args:
            name: Component name for state storage
            choices: List of selectable options
            **kwargs: Component configuration options (when, default, etc.)

        Returns:
            Self for method chaining
        """
        # Implementation pending Component system update to interfaces
        # from .component_wrappers import select
        # component = select(name, choices=choices, **kwargs)
        # self.add_element(component)  # type: ignore - TODO: Update component to implement AssemblyChildInterface
        
        # Temporary placeholder until components are updated
        print(f"TODO: Add select component '{name}' to assembly '{self.name}'")
        return self

    def on_change(self, field: str, handler: Callable[..., Any]) -> "AssemblyBase":
        """
        Register handler for field change events.

        Args:
            field: Field name to monitor for changes
            handler: Callback function (value, assembly) -> None

        Returns:
            Self for method chaining
        """
        # Implementation pending Event system
        self.event_handlers["change"].append((field, handler))
        return self

    def on_validate(self, handler: Callable[..., Any]) -> "AssemblyBase":
        """
        Register handler for assembly validation.

        Args:
            handler: Validation function (assembly) -> Optional[str]

        Returns:
            Self for method chaining
        """
        # Implementation pending Event system
        self.event_handlers["validate"].append(handler)
        return self

    def on_complete(self, field: str, handler: Callable[..., Any]) -> "AssemblyBase":
        """
        Register handler for field completion events.

        Args:
            field: Field name to monitor for completion
            handler: Callback function (value, assembly) -> None

        Returns:
            Self for method chaining
        """
        # Implementation pending Event system
        self.event_handlers["complete"].append((field, handler))
        return self

    def execute(self) -> Dict[str, Any]:
        """Execute the assembly and return collected results."""
        raise NotImplementedError("Assembly execution requires a QuestionaryBridge")

    def show_components(self, component_names: List[str]) -> None:
        """Show specified components."""
        raise NotImplementedError("Assembly show_components is not implemented")

    def hide_components(self, component_names: List[str]) -> None:
        """Hide specified components."""
        raise NotImplementedError("Assembly hide_components is not implemented")

    def show(self) -> None:
        """Make this assembly visible."""
        super().show()

    def hide(self) -> None:
        """Hide this assembly."""
        super().hide()

    def get_value(self, field: str) -> Any:
        """Get value from assembly's local state."""
        raise NotImplementedError("Assembly get_value is not implemented")

    def get_related_value(self, field_path: str) -> Any:
        """Get value from other assemblies (cross-boundary access)."""
        raise NotImplementedError("Assembly get_related_value is not implemented")

    def parent(self) -> "PageBase":
        """Return parent Page for navigation."""
        return self.parent_page


__all__ = ["AssemblyBase"]
