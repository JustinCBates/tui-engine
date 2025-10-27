"""
Component wrappers for questionary-extended.

This module provides enhanced wrappers around questionary components,
maintaining full API compatibility while adding new capabilities.
"""

from typing import Any, Callable, Dict, List, Optional


class Component:
    """
    Base wrapper class for questionary components.

    Provides enhanced functionality while maintaining questionary compatibility:
    - Enhanced validation with multiple validators
    - State integration and event hooks
    """

    def __init__(self, name: str, component_type: str, **kwargs: Any) -> None:
        """
        Initialize a component wrapper.

        Args:
            name: Component name for state management
            component_type: Type of questionary component (text, select, etc.)
            **kwargs: Component configuration options
        """
        self.name = name
        self.component_type = component_type
        self.config = kwargs
        self.when_condition: Optional[str] = kwargs.get("when")
        self.validators: List[Callable[..., Any]] = []
        self.visible: bool = True  # Default visibility

        # Extract questionary-compatible config
        self.questionary_config = {
            k: v for k, v in kwargs.items() if k not in ["when", "enhanced_validation"]
        }

    def add_validator(self, validator: Callable[..., Any]) -> None:
        """Add a validator function."""
        self.validators.append(validator)

    def is_visible(self, state: Dict[str, Any]) -> bool:
        """Check if component should be visible based on 'when' condition."""
        # Direct visibility check (no dynamic attribute access needed)
        if not self.visible:
            return False

        if not self.when_condition:
            return True

        # TODO: implement expression evaluation of `when` conditions safely
        # For now, default to visible to avoid accidental hiding while the
        # expression evaluator is implemented.
        return True

    def show(self) -> None:
        """Make this component visible."""
        self.visible = True

    def hide(self) -> None:
        """Hide this component."""
        self.visible = False

    def create_questionary_component(self) -> Any:
        """Create the underlying questionary component."""
        
        # Handle display-only components separately
        if self.component_type in ["text_display", "text_section", "text_status"]:
            # These are display-only components, not questionary prompts
            return self
        
        # Use DI system for clean, fast, testable resolution
        from src.tui_engine.questionary_factory import get_questionary
        questionary_module = get_questionary()
        
        if questionary_module is None:
            raise ImportError("questionary is not available")
        
        # Validate supported component types early
        supported = {
            "text", "select", "confirm", "password", 
            "checkbox", "autocomplete", "path"
        }
        if self.component_type not in supported:
            raise ValueError(f"Unsupported component type: {self.component_type}")
        
        # Get component factory from DI-resolved questionary module
        if not hasattr(questionary_module, self.component_type):
            raise ValueError(f"Questionary module missing component type: {self.component_type}")
            
        component_func = getattr(questionary_module, self.component_type)
        if not callable(component_func):
            raise ValueError(f"Component type {self.component_type} is not callable")

        try:
            # Use questionary_config which excludes non-questionary options
            return component_func(**self.questionary_config)
        except Exception as exc:
            # Handle console availability issues in CI/headless environments
            if (
                hasattr(exc, "__class__")
                and exc.__class__.__name__ == "NoConsoleScreenBufferError"
            ):
                raise RuntimeError("No console available for questionary") from exc
            raise


# Convenience wrapper functions matching questionary API
def text_prompt(name: str, message: Optional[str] = None, **kwargs: Any) -> Component:
    """Create a text input component that prompts user for text input."""
    if message is None:
        message = f"{name.replace('_', ' ').title()}:"
    return Component(name, "text", message=message, **kwargs)


def text_display(content: str, name: Optional[str] = None, **kwargs: Any) -> Component:
    """Create a display-only text component (like print() but page-controlled)."""
    if name is None:
        name = f"display_{id(content)}"  # Generate unique name
    return Component(name, "text_display", content=content, **kwargs)


def text_section(content: str, title: Optional[str] = None, name: Optional[str] = None, **kwargs: Any) -> Component:
    """Create a multi-line text block component."""
    if name is None:
        name = f"section_{id(content)}"
    return Component(name, "text_section", content=content, title=title, **kwargs)


def text_status(content: str, status_type: str = "info", name: Optional[str] = None, **kwargs: Any) -> Component:
    """Create a status/progress message component."""
    if name is None:
        name = f"status_{id(content)}"
    return Component(name, "text_status", content=content, status_type=status_type, **kwargs)


def select_prompt(
    name: str,
    message: Optional[str] = None,
    choices: Optional[List[str]] = None,
    **kwargs: Any,
) -> Component:
    """Create a selection component that prompts user to choose from options."""
    if message is None:
        message = f"Choose {name.replace('_', ' ')}:"
    if choices is None:
        choices = []
    return Component(name, "select", message=message, choices=choices, **kwargs)


def confirm_prompt(name: str, message: Optional[str] = None, **kwargs: Any) -> Component:
    """Create a confirmation component that prompts user for yes/no."""
    if message is None:
        message = f"Confirm {name.replace('_', ' ')}?"
    return Component(name, "confirm", message=message, **kwargs)


def password_prompt(name: str, message: Optional[str] = None, **kwargs: Any) -> Component:
    """Create a password input component that prompts user for secure text."""
    if message is None:
        message = f"{name.replace('_', ' ').title()}:"
    return Component(name, "password", message=message, **kwargs)


def checkbox_prompt(
    name: str,
    message: Optional[str] = None,
    choices: Optional[List[str]] = None,
    **kwargs: Any,
) -> Component:
    """Create a checkbox component that prompts user for multiple selections."""
    if message is None:
        message = f"Select {name.replace('_', ' ')}:"
    if choices is None:
        choices = []
    return Component(name, "checkbox", message=message, choices=choices, **kwargs)


def autocomplete_prompt(
    name: str,
    message: Optional[str] = None,
    choices: Optional[List[str]] = None,
    **kwargs: Any,
) -> Component:
    """Create an autocomplete component that prompts user with suggested options."""
    if message is None:
        message = f"Choose {name.replace('_', ' ')}:"
    if choices is None:
        choices = []
    return Component(name, "autocomplete", message=message, choices=choices, **kwargs)


def path_prompt(name: str, message: Optional[str] = None, **kwargs: Any) -> Component:
    """Create a path selection component that prompts user for file/directory path."""
    if message is None:
        message = f"{name.replace('_', ' ').title()}:"
    return Component(name, "path", message=message, **kwargs)


__all__ = [
    "Component",
    # Interactive prompt components (require user input)
    "text_prompt",
    "select_prompt", 
    "confirm_prompt",
    "password_prompt",
    "checkbox_prompt",
    "autocomplete_prompt",
    "path_prompt",
    # Display components (show information only)
    "text_display",
    "text_section",
    "text_status",
]
