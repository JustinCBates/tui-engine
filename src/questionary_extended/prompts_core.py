"""
Core prompt implementations - fundamental working versions.
"""

from typing import Any, Dict, List, Optional, Union
import questionary
from questionary import Question


def enhanced_text(
    message: str,
    default: str = "",
    multiline: bool = False,
    validator=None,
    **kwargs
) -> Question:
    """
    Enhanced text input - starting with a simple working version.
    
    Args:
        message: The question to ask
        default: Default value
        multiline: Enable multiline input
        validator: Validation function or validator object
        **kwargs: Additional questionary arguments
    
    Returns:
        Question instance
    """
    # Handle validator parameter properly
    if validator is not None:
        kwargs['validate'] = validator
    
    return questionary.text(
        message, 
        default=default, 
        multiline=multiline,
        **kwargs
    )


def number(
    message: str,
    default: Optional[Union[int, float]] = None,
    min_value: Optional[Union[int, float]] = None,
    max_value: Optional[Union[int, float]] = None,
    allow_float: bool = True,
    **kwargs
) -> Question:
    """
    Numeric input with validation.
    
    Args:
        message: The question to ask
        default: Default numeric value
        min_value: Minimum allowed value
        max_value: Maximum allowed value
        allow_float: Allow floating point numbers
        **kwargs: Additional questionary arguments
        
    Returns:
        Question instance
    """
    from .validators import NumberValidator
    
    validator = NumberValidator(
        min_value=min_value,
        max_value=max_value,
        allow_float=allow_float
    )
    
    default_str = str(default) if default is not None else ""
    
    # Remove any conflicting validator/validate parameters
    clean_kwargs = {k: v for k, v in kwargs.items() if k not in ['validate', 'validator']}
    
    return questionary.text(
        message,
        default=default_str,
        validate=validator,
        **clean_kwargs
    )


def integer(
    message: str, 
    min_value: Optional[int] = None, 
    max_value: Optional[int] = None, 
    **kwargs
) -> Question:
    """Integer input with validation."""
    return number(
        message,
        min_value=min_value,
        max_value=max_value,
        allow_float=False,
        **kwargs
    )


def rating(
    message: str,
    max_rating: int = 5,
    icon: str = "★",
    allow_zero: bool = False,
    **kwargs
) -> Question:
    """
    Star rating input.
    
    Args:
        message: The question to ask
        max_rating: Maximum rating value
        icon: Icon to use for rating
        allow_zero: Allow zero rating
        **kwargs: Additional questionary arguments
        
    Returns:
        Question instance
    """
    min_val = 0 if allow_zero else 1
    choices = []
    
    for i in range(min_val, max_rating + 1):
        filled = icon * i
        empty = "☆" * (max_rating - i)
        display = f"{filled}{empty} ({i})"
        choices.append(questionary.Choice(title=display, value=i))
    
    return questionary.select(message, choices=choices, **kwargs)


def form(questions: List[Dict[str, Any]], **kwargs) -> Question:
    """
    Enhanced form - starting with questionary's prompt function.
    
    Args:
        questions: List of question definitions
        **kwargs: Additional questionary arguments
        
    Returns:
        Question instance that returns a dictionary of answers
    """
    return questionary.prompt(questions, **kwargs)


class progress_tracker:
    """
    Simple progress tracker for multi-step operations.
    """
    
    def __init__(self, title: str, total: int = None, total_steps: int = None):
        self.title = title
        self.total_steps = total if total is not None else total_steps
        self.current_step = 0
        self.completed_steps = []
    
    def __enter__(self):
        print(f"🚀 Starting: {self.title}")
        print(f"   Total steps: {self.total_steps}")
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is None:
            print("✅ Completed successfully!")
        else:
            print(f"❌ Failed: {exc_val}")
    
    def step(self, description: str):
        """Advance to the next step."""
        self.current_step += 1
        progress = (self.current_step / self.total_steps) * 100
        bar_length = 20
        filled_length = int(bar_length * self.current_step // self.total_steps)
        bar = "█" * filled_length + "░" * (bar_length - filled_length)
        
        print(f"   [{bar}] {self.current_step}/{self.total_steps} ({progress:.1f}%) - {description}")
        self.completed_steps.append(description)
    
    def update(self, step: int, description: str):
        """Update to a specific step."""
        self.current_step = step
        progress = (self.current_step / self.total_steps) * 100
        bar_length = 20
        filled_length = int(bar_length * self.current_step // self.total_steps)
        bar = "█" * filled_length + "░" * (bar_length - filled_length)
        
        print(f"   [{bar}] {self.current_step}/{self.total_steps} ({progress:.1f}%) - {description}")
        if description not in self.completed_steps:
            self.completed_steps.append(description)
    
    def complete(self, message: str = "All steps completed!"):
        """Mark the operation as complete."""
        print(f"🎉 {message}")


# Additional utility functions
def confirm_enhanced(message: str, default: bool = True, **kwargs) -> Question:
    """Enhanced confirmation prompt."""
    return questionary.confirm(message, default=default, **kwargs)


def select_enhanced(
    message: str, 
    choices: List[Any],
    **kwargs
) -> Question:
    """Enhanced selection prompt."""
    return questionary.select(message, choices=choices, **kwargs)


def checkbox_enhanced(
    message: str,
    choices: List[Any], 
    **kwargs
) -> Question:
    """Enhanced checkbox prompt."""
    return questionary.checkbox(message, choices=choices, **kwargs)