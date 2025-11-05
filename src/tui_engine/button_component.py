"""
Button component for user interactions in the TUI Engine.

This module provides ButtonComponent, which creates clickable buttons
that integrate with prompt-toolkit's Button widget.
"""

from typing import Optional, Callable, Any
from prompt_toolkit.widgets import Button
from prompt_toolkit.formatted_text import FormattedText
from .component_base import ComponentBase


class ButtonComponent(ComponentBase):
    """Button component that wraps prompt-toolkit's Button widget.
    
    Provides clickable buttons with custom text, styling, and event handling.
    """
    
    def __init__(self, name: str, text: str = "", variant: str = "button"):
        super().__init__(name, variant)
        self.text = text or name
        self.width: Optional[int] = None
        self.left_symbol: str = "< "
        self.right_symbol: str = " >"
        self._button: Optional[Button] = None
        self._click_handler: Optional[Callable] = None
        
    def set_text(self, text: str) -> "ButtonComponent":
        """Set the button text."""
        self.text = text
        # Update existing button if it exists
        if self._button:
            self._button.text = text
        return self
        
    def set_width(self, width: Optional[int]) -> "ButtonComponent":
        """Set the button width. None for auto-width."""
        self.width = width
        return self
        
    def set_symbols(self, left: str = "< ", right: str = " >") -> "ButtonComponent":
        """Set the left and right symbols around button text."""
        self.left_symbol = left
        self.right_symbol = right
        return self
        
    def on_click(self, handler: Callable[["ButtonComponent"], Any]) -> "ButtonComponent":
        """Set the click handler for this button.
        
        The handler will be called with the button component as argument.
        """
        self._click_handler = handler
        return self
        
    def click(self) -> "ButtonComponent":
        """Programmatically trigger a button click."""
        if self.is_enabled and self._click_handler:
            try:
                self._click_handler(self)
                self.trigger_event("clicked")
            except Exception as e:
                self.trigger_event("click_error", e)
        return self
        
    def _handle_button_click(self) -> None:
        """Internal handler for prompt-toolkit button clicks."""
        if self.is_enabled:
            self.trigger_event("focus")  # Button gets focus when clicked
            self.click()
            
    def to_prompt_toolkit(self) -> Button:
        """Convert this button to a prompt-toolkit Button widget."""
        if self._button is None:
            # Ensure width is proper for prompt-toolkit
            # If no width is set, calculate based on text length
            button_width = self.width
            if button_width is None:
                # Calculate width based on text + symbols + padding
                text_len = len(self.text)
                symbol_len = len(self.left_symbol) + len(self.right_symbol)
                button_width = text_len + symbol_len + 2  # +2 for padding
            
            # Create the button with click handler
            self._button = Button(
                text=self.text,
                handler=self._handle_button_click,
                width=button_width,
                left_symbol=self.left_symbol,
                right_symbol=self.right_symbol,
            )
            
        return self._button
        
    def focus(self) -> None:
        """Give focus to this button."""
        super().focus()
        # The actual focus will be handled by the prompt-toolkit layout
        
    def set_enabled(self, enabled: bool = True) -> "ButtonComponent":
        """Enable or disable this button."""
        super().set_enabled(enabled)
        # Update button appearance if needed
        if self._button and not enabled:
            # Could modify button styling here to show disabled state
            pass
        return self


class PrimaryButton(ButtonComponent):
    """Primary action button with emphasis styling."""
    
    def __init__(self, name: str, text: str = "", variant: str = "primary-button"):
        super().__init__(name, text, variant)
        self.set_symbols("[ ", " ]")  # Different symbols for primary buttons
        

class SecondaryButton(ButtonComponent):
    """Secondary action button with subdued styling."""
    
    def __init__(self, name: str, text: str = "", variant: str = "secondary-button"):
        super().__init__(name, text, variant)
        self.set_symbols("( ", " )")  # Different symbols for secondary buttons
        

class DangerButton(ButtonComponent):
    """Danger/destructive action button with warning styling."""
    
    def __init__(self, name: str, text: str = "", variant: str = "danger-button"):
        super().__init__(name, text, variant)
        self.set_symbols("{ ", " }")  # Different symbols for danger buttons
        

class LinkButton(ButtonComponent):
    """Link-style button that appears like clickable text."""
    
    def __init__(self, name: str, text: str = "", variant: str = "link-button"):
        super().__init__(name, text, variant)
        self.set_symbols("", "")  # No symbols for link buttons
        

class IconButton(ButtonComponent):
    """Button with an icon/symbol and optional text."""
    
    def __init__(self, name: str, icon: str, text: str = "", variant: str = "icon-button"):
        self.icon = icon
        display_text = f"{icon} {text}".strip() if text else icon
        super().__init__(name, display_text, variant)
        
    def set_icon(self, icon: str) -> "IconButton":
        """Set the icon for this button."""
        self.icon = icon
        # Update display text
        text_part = self.text.split(" ", 1)[1] if " " in self.text else ""
        self.set_text(f"{icon} {text_part}".strip())
        return self


# Common button factory functions
class Buttons:
    """Factory class for creating common button types."""
    
    @staticmethod
    def ok(name: str = "ok", handler: Optional[Callable] = None) -> PrimaryButton:
        """Create an OK button."""
        btn = PrimaryButton(name, "OK")
        if handler:
            btn.on_click(handler)
        return btn
        
    @staticmethod
    def cancel(name: str = "cancel", handler: Optional[Callable] = None) -> SecondaryButton:
        """Create a Cancel button."""
        btn = SecondaryButton(name, "Cancel")
        if handler:
            btn.on_click(handler)
        return btn
        
    @staticmethod
    def save(name: str = "save", handler: Optional[Callable] = None) -> PrimaryButton:
        """Create a Save button."""
        btn = PrimaryButton(name, "Save")
        if handler:
            btn.on_click(handler)
        return btn
        
    @staticmethod
    def delete(name: str = "delete", handler: Optional[Callable] = None) -> DangerButton:
        """Create a Delete button."""
        btn = DangerButton(name, "Delete")
        if handler:
            btn.on_click(handler)
        return btn
        
    @staticmethod
    def submit(name: str = "submit", handler: Optional[Callable] = None) -> PrimaryButton:
        """Create a Submit button."""
        btn = PrimaryButton(name, "Submit")
        if handler:
            btn.on_click(handler)
        return btn
        
    @staticmethod
    def reset(name: str = "reset", handler: Optional[Callable] = None) -> SecondaryButton:
        """Create a Reset button."""
        btn = SecondaryButton(name, "Reset")
        if handler:
            btn.on_click(handler)
        return btn
        
    @staticmethod
    def close(name: str = "close", handler: Optional[Callable] = None) -> LinkButton:
        """Create a Close button."""
        btn = LinkButton(name, "Close")
        if handler:
            btn.on_click(handler)
        return btn
        
    @staticmethod
    def help(name: str = "help", handler: Optional[Callable] = None) -> IconButton:
        """Create a Help button with question mark icon."""
        btn = IconButton(name, "?", "Help")
        if handler:
            btn.on_click(handler)
        return btn