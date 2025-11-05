"""
Base class for interactive components in the TUI Engine.

This module provides ComponentBase, which serves as the foundation for all
interactive user interface components like inputs, buttons, dropdowns, etc.
"""

from abc import ABC, abstractmethod
from typing import Any, Optional, Callable, Dict, List
from .interfaces import IElement


class ComponentBase(IElement, ABC):
    """Base class for all interactive components.
    
    Provides common functionality like labels, hints, validation,
    default values, and event handling that all interactive components need.
    """
    
    def __init__(self, name: str, variant: str = "component"):
        self.name = name
        self.variant = variant
        self.label: str = ""
        self.hint: str = ""
        self.default_value: Any = None
        self.current_value: Any = None
        self.is_required: bool = False
        self.is_enabled: bool = True
        self.is_visible: bool = True
        self.validation_rules: List[Callable[[Any], str]] = []
        self.event_handlers: Dict[str, List[Callable]] = {}
        self.style_class: str = ""
        
    def set_label(self, label: str) -> "ComponentBase":
        """Set the label text for this component."""
        self.label = label
        return self
        
    def set_hint(self, hint: str) -> "ComponentBase":
        """Set the hint/help text for this component."""
        self.hint = hint
        return self
        
    def set_default_value(self, value: Any) -> "ComponentBase":
        """Set the default value for this component."""
        self.default_value = value
        if self.current_value is None:
            self.current_value = value
        return self
        
    def set_required(self, required: bool = True) -> "ComponentBase":
        """Mark this component as required or optional."""
        self.is_required = required
        return self
        
    def set_enabled(self, enabled: bool = True) -> "ComponentBase":
        """Enable or disable this component."""
        self.is_enabled = enabled
        return self
        
    def set_visible(self, visible: bool = True) -> "ComponentBase":
        """Show or hide this component."""
        self.is_visible = visible
        return self
        
    def set_style_class(self, style_class: str) -> "ComponentBase":
        """Set the CSS-style class for component styling."""
        self.style_class = style_class
        return self
        
    def add_validation_rule(self, validator: Callable[[Any], str]) -> "ComponentBase":
        """Add a validation rule.
        
        The validator function should return an empty string if valid,
        or an error message if invalid.
        """
        self.validation_rules.append(validator)
        return self
        
    def on_event(self, event_type: str, handler: Callable) -> "ComponentBase":
        """Register an event handler for the specified event type."""
        if event_type not in self.event_handlers:
            self.event_handlers[event_type] = []
        self.event_handlers[event_type].append(handler)
        return self
        
    def trigger_event(self, event_type: str, *args, **kwargs) -> None:
        """Trigger all handlers for the specified event type."""
        if event_type in self.event_handlers:
            for handler in self.event_handlers[event_type]:
                try:
                    handler(self, *args, **kwargs)
                except Exception:
                    # Silently ignore handler errors to avoid crashing the UI
                    pass
                    
    def get_value(self) -> Any:
        """Get the current value of this component."""
        return self.current_value
        
    def set_value(self, value: Any) -> "ComponentBase":
        """Set the current value of this component."""
        old_value = self.current_value
        self.current_value = value
        if old_value != value:
            self.trigger_event("value_changed", old_value, value)
        return self
        
    def validate(self) -> List[str]:
        """Validate the current value against all validation rules.
        
        Returns a list of error messages. Empty list means valid.
        """
        errors = []
        
        # Check if required field is empty
        if self.is_required and (self.current_value is None or self.current_value == ""):
            errors.append(f"{self.label or self.name} is required")
            
        # Run custom validation rules
        for validator in self.validation_rules:
            try:
                error = validator(self.current_value)
                if error:
                    errors.append(error)
            except Exception:
                # Skip validators that throw exceptions
                pass
                
        return errors
        
    def is_valid(self) -> bool:
        """Check if the current value is valid."""
        return len(self.validate()) == 0
        
    def reset(self) -> "ComponentBase":
        """Reset the component to its default value."""
        self.set_value(self.default_value)
        return self
        
    def focus(self) -> None:
        """Give focus to this component (if applicable)."""
        self.trigger_event("focus")
        
    def blur(self) -> None:
        """Remove focus from this component (if applicable)."""
        self.trigger_event("blur")
        
    @abstractmethod
    def to_prompt_toolkit(self) -> Any:
        """Convert this component to a prompt-toolkit widget.
        
        Each concrete component must implement this to return the appropriate
        prompt-toolkit widget (TextArea, Button, etc.).
        """
        pass
        
    def get_render_lines(self, width: int = 80) -> List[str]:
        """Default text rendering for components."""
        lines = []
        
        # Show label if present
        if self.label:
            lines.append(f"[{self.variant.upper()}] {self.label}")
        else:
            lines.append(f"[{self.variant.upper()}] {self.name}")
            
        # Show current value if meaningful
        if hasattr(self, 'text'):
            # For button-like components
            value = getattr(self, 'text', '')
            if value:
                lines.append(f"  Text: {value}")
        elif self.current_value is not None:
            # For input-like components
            display_value = "***" if getattr(self, 'is_password', False) else str(self.current_value)
            lines.append(f"  Value: {display_value}")
            
        # Show validation status
        if hasattr(self, 'validate'):
            errors = self.validate()
            if errors:
                lines.append(f"  Validation: {len(errors)} errors")
            elif self.current_value:
                lines.append("  Validation: OK")
                
        return lines
        
    def to_ptk_container(self, adapter: Any) -> Any:
        """Implementation of IElement interface method."""
        return self.to_prompt_toolkit()


# Common validation functions that can be used with any component
class Validators:
    """Collection of common validation functions."""
    
    @staticmethod
    def min_length(min_len: int) -> Callable[[str], str]:
        """Validate minimum string length."""
        def validator(value: str) -> str:
            if value and len(value) < min_len:
                return f"Must be at least {min_len} characters long"
            return ""
        return validator
        
    @staticmethod
    def max_length(max_len: int) -> Callable[[str], str]:
        """Validate maximum string length."""
        def validator(value: str) -> str:
            if value and len(value) > max_len:
                return f"Must be no more than {max_len} characters long"
            return ""
        return validator
        
    @staticmethod
    def email() -> Callable[[str], str]:
        """Validate email format."""
        def validator(value: str) -> str:
            if value and "@" not in value:
                return "Must be a valid email address"
            return ""
        return validator
        
    @staticmethod
    def numeric() -> Callable[[str], str]:
        """Validate that value is numeric."""
        def validator(value: str) -> str:
            if value:
                try:
                    float(value)
                except ValueError:
                    return "Must be a number"
            return ""
        return validator
        
    @staticmethod
    def range_check(min_val: float, max_val: float) -> Callable[[str], str]:
        """Validate that numeric value is within range."""
        def validator(value: str) -> str:
            if value:
                try:
                    num_val = float(value)
                    if num_val < min_val or num_val > max_val:
                        return f"Must be between {min_val} and {max_val}"
                except ValueError:
                    return "Must be a number"
            return ""
        return validator