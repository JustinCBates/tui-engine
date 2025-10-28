"""
Component wrappers for questionary-extended.

This module provides enhanced wrappers around questionary components,
maintaining full API compatibility while adding new capabilities.
"""

import uuid
from typing import Any, Callable, Dict, List, Optional
from .interfaces import RenderableComponent


class Component(RenderableComponent):
    """
    Base wrapper class for questionary components.

    Provides enhanced functionality while maintaining questionary compatibility:
    - Enhanced validation with multiple validators
    - State integration and event hooks
    - Interface compliance with ComponentInterface and Renderable
    """

    def __init__(self, name: str, component_type: str, **kwargs: Any) -> None:
        """
        Initialize a component wrapper.

        Args:
            name: Component name for state management
            component_type: Type of questionary component (text, select, etc.)
            **kwargs: Component configuration options
        """
        self._name = name
        self._component_type = component_type
        self.config = kwargs
        self.when_condition: Optional[str] = kwargs.get("when")
        self.validators: List[Callable[..., Any]] = []
        self._visible: bool = True  # Default visibility
        self._needs_render: bool = True
        self._last_rendered_lines: List[str] = []

        # Extract questionary-compatible config
        self.questionary_config = {
            k: v for k, v in kwargs.items() if k not in ["when", "enhanced_validation"]
        }

    # ElementInterface implementation
    @property
    def name(self) -> str:
        """Unique identifier for this component."""
        return self._name
    
    @property
    def element_type(self) -> str:
        """Type of element (always 'component')."""
        return "component"
    
    @property
    def visible(self) -> bool:
        """Whether this component is currently visible."""
        return self._visible
    
    def show(self) -> None:
        """Make this component visible."""
        if not self._visible:
            self._visible = True
            self._needs_render = True
    
    def hide(self) -> None:
        """Hide this component."""
        if self._visible:
            self._visible = False
            self._needs_render = True

    # ComponentInterface implementation
    @property
    def component_type(self) -> str:
        """Specific type of component (text_input, select, text_display, etc.)."""
        return self._component_type
    
    def is_interactive(self) -> bool:
        """Whether this component requires user interaction."""
        # Display-only components are not interactive
        return self._component_type not in ["text_display", "text_section", "text_status"]

    # Renderable implementation
    def get_render_lines(self) -> List[str]:
        """Get the lines this component should output."""
        if not self._visible:
            return []
        
        # Handle display-only components
        if self._component_type == "text_display":
            content = self.config.get("content", "")
            return [str(content)] if content else []
        
        elif self._component_type == "text_status":
            content = self.config.get("content", "")
            status_type = self.config.get("status_type", "info")
            
            # Simple status formatting
            if status_type == "error":
                prefix = "❌"
            elif status_type == "success":
                prefix = "✅"
            elif status_type == "warning":
                prefix = "⚠️"
            else:  # info
                prefix = "ℹ️"
            
            return [f"{prefix} {content}"] if content else []
        
        elif self._component_type == "text_section":
            content = self.config.get("content", "")
            return [f"📄 {content}"] if content else []
        
        # For interactive components, return placeholder text
        else:
            return [f"[{self._component_type.upper()}: {self._name}]"]
    
    def has_changes(self) -> bool:
        """Check if this component needs re-rendering."""
        return self._needs_render
    
    def render_delta(self, relative_start: int = 0) -> int:
        """Render this component's changes at relative position."""
        if not self._visible:
            return 0
        
        current_lines = self.get_render_lines()
        
        # Clear previous content if different
        if self._last_rendered_lines != current_lines:
            # Clear old lines
            for i in range(len(self._last_rendered_lines)):
                line_pos = relative_start + i
                print(f"\\x1b[{line_pos + 1};1H\\x1b[2K", end="")
            
            # Render new content
            for i, line in enumerate(current_lines):
                line_pos = relative_start + i
                print(f"\\x1b[{line_pos + 1};1H{line}", end="")
            
            self._last_rendered_lines = current_lines.copy()
        
        self._needs_render = False
        return len(current_lines)
    
    def mark_dirty(self) -> None:
        """Mark this component as needing re-render."""
        self._needs_render = True

    # CardChildInterface and AssemblyChildInterface implementation
    def is_completed(self) -> bool:
        """Whether this component has completed its required input/validation."""
        # Display components are always completed
        if not self.is_interactive():
            return True
        
        # For interactive components, check if they have a value
        # This is a simplified implementation
        return True  # For now, assume all are completed
    
    def is_valid(self) -> bool:
        """Whether this component's current state is valid."""
        # Run all validators if any
        if not self.validators:
            return True
        
        # For now, assume valid (would need actual value to validate)
        return True

    def add_validator(self, validator: Callable[..., Any]) -> None:
        """Add a validator function."""
        self.validators.append(validator)

    def is_visible(self, state: Dict[str, Any]) -> bool:
        """Check if component should be visible based on 'when' condition."""
        # Direct visibility check (no dynamic attribute access needed)
        if not self._visible:
            return False

        if not self.when_condition:
            return True

        # TODO: implement expression evaluation of `when` conditions safely
        # For now, default to visible to avoid accidental hiding while the
        # expression evaluator is implemented.
        return True

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
        name = f"display_{uuid.uuid4().hex[:8]}"  # Generate truly unique name
    return Component(name, "text_display", content=content, **kwargs)


def text_section(content: str, title: Optional[str] = None, name: Optional[str] = None, **kwargs: Any) -> Component:
    """Create a multi-line text block component."""
    if name is None:
        name = f"section_{uuid.uuid4().hex[:8]}"
    return Component(name, "text_section", content=content, title=title, **kwargs)


def text_status(content: str, status_type: str = "info", name: Optional[str] = None, **kwargs: Any) -> Component:
    """Create a status/progress message component."""
    if name is None:
        name = f"status_{uuid.uuid4().hex[:8]}"
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
