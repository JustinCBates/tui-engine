"""
Input component for text entry in the TUI Engine.

This module provides InputComponent, which creates text input fields
that integrate with prompt-toolkit's TextArea widget.
"""

from typing import Optional, Callable
from prompt_toolkit.widgets import TextArea
from prompt_toolkit.buffer import Buffer
from prompt_toolkit.document import Document
from .component_base import ComponentBase


class InputComponent(ComponentBase):
    """Text input component that wraps prompt-toolkit's TextArea widget.
    
    Provides single-line and multi-line text input with validation,
    placeholder text, and event handling.
    """
    
    def __init__(self, name: str, variant: str = "input"):
        super().__init__(name, variant)
        self.placeholder: str = ""
        self.is_multiline: bool = False
        self.is_password: bool = False
        self.max_length: Optional[int] = None
        self.wrap_lines: bool = True
        self.scrollbar: bool = False
        self._text_area: Optional[TextArea] = None
        self._buffer: Optional[Buffer] = None
        
    def set_placeholder(self, placeholder: str) -> "InputComponent":
        """Set placeholder text shown when input is empty."""
        self.placeholder = placeholder
        return self
        
    def set_multiline(self, multiline: bool = True) -> "InputComponent":
        """Enable or disable multi-line text input."""
        self.is_multiline = multiline
        return self
        
    def set_password(self, password: bool = True) -> "InputComponent":
        """Enable or disable password mode (shows asterisks)."""
        self.is_password = password
        return self
        
    def set_max_length(self, max_length: Optional[int]) -> "InputComponent":
        """Set maximum number of characters allowed."""
        self.max_length = max_length
        return self
        
    def set_wrap_lines(self, wrap: bool = True) -> "InputComponent":
        """Enable or disable line wrapping for multi-line inputs."""
        self.wrap_lines = wrap
        return self
        
    def set_scrollbar(self, scrollbar: bool = True) -> "InputComponent":
        """Enable or disable scrollbar for multi-line inputs."""
        self.scrollbar = scrollbar
        return self
        
    def get_text(self) -> str:
        """Get the current text content."""
        if self._text_area:
            return self._text_area.text
        return self.current_value or ""
        
    def set_text(self, text: str) -> "InputComponent":
        """Set the text content."""
        if self._text_area:
            self._text_area.text = text
        self.set_value(text)
        return self
        
    def clear(self) -> "InputComponent":
        """Clear the input text."""
        return self.set_text("")
        
    def select_all(self) -> "InputComponent":
        """Select all text in the input."""
        if self._text_area and self._text_area.buffer:
            self._text_area.buffer.cursor_position = 0
            self._text_area.buffer.start_selection()
            self._text_area.buffer.cursor_position = len(self._text_area.buffer.text)
        return self
        
    def _create_buffer(self) -> Buffer:
        """Create and configure the text buffer."""
        def on_text_changed(_):
            """Handle text changes."""
            if self._text_area:
                new_text = self._text_area.buffer.text
                old_value = self.current_value
                self.current_value = new_text
                
                # Trigger validation
                errors = self.validate()
                if errors:
                    self.trigger_event("validation_error", errors)
                else:
                    self.trigger_event("validation_success")
                
                # Trigger value changed event
                if old_value != new_text:
                    self.trigger_event("value_changed", old_value, new_text)
                    self.trigger_event("text_changed", new_text)
        
        def on_cursor_position_changed(_):
            """Handle cursor movement."""
            self.trigger_event("cursor_moved")
            
        # Create buffer with initial text
        initial_text = self.current_value or self.default_value or ""
        if initial_text is None:
            initial_text = ""
            
        buffer = Buffer(
            document=Document(initial_text),
            on_text_changed=on_text_changed,
            on_cursor_position_changed=on_cursor_position_changed,
            multiline=self.is_multiline,
            completer=None,  # Could add auto-completion later
            validator=None,  # We handle validation separately
        )
        
        return buffer
        
    def to_prompt_toolkit(self) -> TextArea:
        """Convert this input to a prompt-toolkit TextArea widget."""
        if self._text_area is None:
            # Get initial text
            initial_text = self.current_value or self.default_value or ""
            if initial_text is None:
                initial_text = ""
            
            # Create the TextArea widget directly
            self._text_area = TextArea(
                text=str(initial_text),
                multiline=self.is_multiline,
                password=self.is_password,
                wrap_lines=self.wrap_lines,
                scrollbar=self.scrollbar,
                style=self.style_class,
                read_only=not self.is_enabled,
            )
            
            # Set up event handlers
            def on_text_changed():
                """Handle text changes."""
                if self._text_area:
                    new_text = self._text_area.text
                    old_value = self.current_value
                    self.current_value = new_text
                    
                    # Trigger validation
                    errors = self.validate()
                    if errors:
                        self.trigger_event("validation_error", errors)
                    else:
                        self.trigger_event("validation_success")
                    
                    # Trigger value changed event
                    if old_value != new_text:
                        self.trigger_event("value_changed", old_value, new_text)
                        self.trigger_event("text_changed", new_text)
            
            # Note: prompt-toolkit TextArea doesn't have direct event handlers like Buffer
            # For now, we'll implement a simpler version without real-time events
                
        return self._text_area
        
    def focus(self) -> None:
        """Give focus to this input component."""
        super().focus()
        if self._text_area:
            # The actual focus will be handled by the prompt-toolkit layout
            pass
            
    def validate(self) -> list[str]:
        """Validate the current input text."""
        errors = super().validate()
        
        # Check max length if set
        current_text = self.get_text()
        if self.max_length and len(current_text) > self.max_length:
            errors.append(f"Text must be no more than {self.max_length} characters")
            
        return errors
        
    def set_value(self, value) -> "InputComponent":
        """Override to ensure text area stays in sync."""
        super().set_value(value)
        # If we have a text area, update it too
        if self._text_area and value is not None:
            self._text_area.text = str(value)
        return self


class SingleLineInput(InputComponent):
    """Convenience class for single-line text inputs."""
    
    def __init__(self, name: str, variant: str = "single-line-input"):
        super().__init__(name, variant)
        self.set_multiline(False)
        

class MultiLineInput(InputComponent):
    """Convenience class for multi-line text inputs (text areas)."""
    
    def __init__(self, name: str, variant: str = "multi-line-input"):
        super().__init__(name, variant)
        self.set_multiline(True)
        self.set_scrollbar(True)
        

class PasswordInput(InputComponent):
    """Convenience class for password inputs."""
    
    def __init__(self, name: str, variant: str = "password-input"):
        super().__init__(name, variant)
        self.set_multiline(False)
        self.set_password(True)