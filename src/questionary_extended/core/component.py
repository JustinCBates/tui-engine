"""
Component wrappers for questionary-extended.

This module provides enhanced wrappers around questionary components,
maintaining full API compatibility while adding new capabilities.
"""

from typing import Any, Callable, Dict, List, Optional, Union
import questionary


class Component:
    """
    Base wrapper class for questionary components.
    
    Provides enhanced functionality while maintaining questionary compatibility:
    - Conditional display with 'when' expressions
    - Enhanced validation with multiple validators
    - State integration and event hooks
    """
    
    def __init__(self, name: str, component_type: str, **kwargs):
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
        self.when_condition: Optional[str] = kwargs.get('when')
        self.validators: List[Callable] = []
        
        # Extract questionary-compatible config
        self.questionary_config = {k: v for k, v in kwargs.items() 
                                 if k not in ['when', 'enhanced_validation']}
        
    def add_validator(self, validator: Callable) -> None:
        """Add a validator function."""
        self.validators.append(validator)
        
    def is_visible(self, state: Dict[str, Any]) -> bool:
        """Check if component should be visible based on 'when' condition."""
        if not self.when_condition:
            return True
        # Implementation pending condition evaluation
        return True
        
    def create_questionary_component(self):
        """Create the underlying questionary component."""
        component_map = {
            'text': questionary.text,
            'select': questionary.select,
            'confirm': questionary.confirm,
            'password': questionary.password,
            'checkbox': questionary.checkbox,
            'autocomplete': questionary.autocomplete,
            'path': questionary.path,
        }
        
        if self.component_type not in component_map:
            raise ValueError(f"Unsupported component type: {self.component_type}")
            
        component_func = component_map[self.component_type]
        return component_func(**self.questionary_config)


# Convenience wrapper functions matching questionary API
def text(name: str, message: str = None, **kwargs) -> Component:
    """Create a text input component."""
    if message is None:
        message = f"{name.replace('_', ' ').title()}:"
    return Component(name, 'text', message=message, **kwargs)


def select(name: str, message: str = None, choices: List[str] = None, **kwargs) -> Component:
    """Create a selection component."""
    if message is None:
        message = f"Choose {name.replace('_', ' ')}:"
    if choices is None:
        choices = []
    return Component(name, 'select', message=message, choices=choices, **kwargs)


def confirm(name: str, message: str = None, **kwargs) -> Component:
    """Create a confirmation component."""
    if message is None:
        message = f"Confirm {name.replace('_', ' ')}?"
    return Component(name, 'confirm', message=message, **kwargs)


def password(name: str, message: str = None, **kwargs) -> Component:
    """Create a password input component."""
    if message is None:
        message = f"{name.replace('_', ' ').title()}:"
    return Component(name, 'password', message=message, **kwargs)


def checkbox(name: str, message: str = None, choices: List[str] = None, **kwargs) -> Component:
    """Create a checkbox component."""
    if message is None:
        message = f"Select {name.replace('_', ' ')}:"
    if choices is None:
        choices = []
    return Component(name, 'checkbox', message=message, choices=choices, **kwargs)


def autocomplete(name: str, message: str = None, choices: List[str] = None, **kwargs) -> Component:
    """Create an autocomplete component."""
    if message is None:
        message = f"Choose {name.replace('_', ' ')}:"
    if choices is None:
        choices = []
    return Component(name, 'autocomplete', message=message, choices=choices, **kwargs)


def path(name: str, message: str = None, **kwargs) -> Component:
    """Create a path selection component."""
    if message is None:
        message = f"{name.replace('_', ' ').title()}:"
    return Component(name, 'path', message=message, **kwargs)


__all__ = [
    "Component",
    "text", 
    "select",
    "confirm", 
    "password",
    "checkbox",
    "autocomplete",
    "path",
]