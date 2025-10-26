"""
Assembly class for questionary-extended.

The Assembly class provides interactive component groups with event-driven logic,
conditional behavior, cross-field validation, and state management.
"""

from typing import TYPE_CHECKING, Any, Callable, Dict, List, Tuple, Union

if TYPE_CHECKING:
    from .page import Page


class Assembly:
    """
    Interactive component group with event-driven behavior.

    Provides:
    - Event hooks (.on_change, .on_validate, .on_complete)
    - Dynamic component visibility and interaction
    - Cross-field validation and state management
    - Reusable template patterns
    """

    def __init__(self, name: str, parent: "Page") -> None:
        """
        Initialize a new Assembly.

        Args:
            name: Assembly namespace for state management
            parent: Parent Page instance
        """
        self.name = name
        self.parent_page = parent
        self.components: List[Any] = []
        # Event handlers may be simple callables or (field, handler) tuples
        self.event_handlers: Dict[
            str, List[Union[Callable[..., Any], Tuple[str, Callable[..., Any]]]]
        ] = {"change": [], "validate": [], "complete": []}

    def text(self, name: str, **kwargs: Any) -> "Assembly":
        """
        Add a text input component.

        Args:
            name: Component name for state storage
            **kwargs: Component configuration options (when, default, etc.)

        Returns:
            Self for method chaining
        """
        from .component import text as _text_component

        comp = _text_component(name, **kwargs)
        # Namespace the component name with the assembly's name so that
        # PageState receives keys like 'assembly.field' when the bridge
        # persists answers. Tests expect assembly-scoped keys (e.g. 'a.x').
        comp.name = f"{self.name}.{name}"
        self.components.append(comp)
        return self

    def select(self, name: str, choices: List[str], **kwargs: Any) -> "Assembly":
        """
        Add a selection component.

        Args:
            name: Component name for state storage
            choices: List of selection options
            **kwargs: Component configuration options (when, default, etc.)

        Returns:
            Self for method chaining
        """
        from .component import select as _select_component

        comp = _select_component(name, choices=choices, **kwargs)
        # Namespace the component name with the assembly's name so that
        # answers are stored under 'assembly.field' in PageState.
        comp.name = f"{self.name}.{name}"
        self.components.append(comp)
        return self

    def on_change(self, field: str, handler: Callable[..., Any]) -> "Assembly":
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

    def on_validate(self, handler: Callable[..., Any]) -> "Assembly":
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

    def on_complete(self, field: str, handler: Callable[..., Any]) -> "Assembly":
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

    def show_components(self, component_names: List[str]) -> None:
        """Show specified components."""
        raise NotImplementedError("Assembly show_components is not implemented")

    def hide_components(self, component_names: List[str]) -> None:
        """Hide specified components."""
        raise NotImplementedError("Assembly hide_components is not implemented")

    def get_value(self, field: str) -> Any:
        """Get value from assembly's local state."""
        raise NotImplementedError("Assembly get_value is not implemented")

    def get_related_value(self, field_path: str) -> Any:
        """Get value from other assemblies (cross-boundary access)."""
        raise NotImplementedError("Assembly get_related_value is not implemented")

    def parent(self) -> "Page":
        """Return parent Page for navigation."""
        return self.parent_page


__all__ = ["Assembly"]
