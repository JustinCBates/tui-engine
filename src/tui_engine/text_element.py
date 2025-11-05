from typing import Any, List, Optional

from .interfaces import IElement


class TextElement(IElement):
    """Static or dynamic text content element."""
    
    def __init__(self, name: str, text: str = "", variant: str = "text"):
        super().__init__(name, variant=variant)
        self.text = text
        self.style_class: str = ""
        self.focusable = False
        
    def set_text(self, text: str) -> "TextElement":
        """Set the text content."""
        self.text = text
        self.mark_dirty()
        return self
        
    def set_style(self, style_class: str) -> "TextElement":
        """Set the CSS-like style class for this text element."""
        self.style_class = style_class
        return self

    def get_render_lines(self, width: int = 80) -> List[str]:
        """Render text content as lines."""
        if not self.text:
            return []
        
        # Simple text wrapping for long lines
        lines = []
        for line in self.text.split('\n'):
            if len(line) <= width:
                lines.append(line)
            else:
                # Basic word wrapping
                words = line.split(' ')
                current_line = ""
                for word in words:
                    if len(current_line + " " + word) <= width:
                        current_line += (" " if current_line else "") + word
                    else:
                        if current_line:
                            lines.append(current_line)
                        current_line = word
                if current_line:
                    lines.append(current_line)
        
        return lines

    def to_prompt_toolkit(self) -> Any:
        """Convert to a prompt-toolkit Label widget."""
        from prompt_toolkit.widgets import Label
        from prompt_toolkit.formatted_text import HTML
        from prompt_toolkit.layout.containers import Window
        from prompt_toolkit.layout.controls import FormattedTextControl
        from prompt_toolkit.layout.dimension import Dimension
        
        if self.style_class:
            # For title style, use a Window with FormattedTextControl for proper centering and full width
            if self.style_class == "title":
                # Create full-width background by getting container width and padding
                # We'll pad the text to fill the available width within the container
                
                # Get a reasonable container width estimate (container minus borders)
                try:
                    import os
                    terminal_width = os.get_terminal_size().columns
                    # Account for container borders and padding
                    container_width = terminal_width - 4  # 2 chars for each side border
                except OSError:
                    container_width = 116  # Default fallback
                
                # Create a full-width line with the text centered and background color
                padded_text = self.text.center(container_width)
                formatted_text = HTML(f'<{self.style_class}>{padded_text}</{self.style_class}>')
                
                return Window(
                    content=FormattedTextControl(text=formatted_text),
                    width=Dimension(weight=1),
                    height=Dimension(min=1, max=1)
                )
            else:
                formatted_text = HTML(f'<{self.style_class}>{self.text}</{self.style_class}>')
                return Label(text=formatted_text)
        else:
            return Label(text=self.text)

    def to_ptk_container(self, adapter: Any) -> Any:
        """Implementation of IElement interface method."""
        return self.to_prompt_toolkit()


class DynamicTextElement(TextElement):
    """Text element that can respond to events and update its content dynamically."""
    
    def __init__(self, name: str, text: str = "", variant: str = "dynamic-text"):
        super().__init__(name, text, variant)
        self.event_handlers: dict = {}
        
    def on_update(self, event_type: str, handler: callable) -> "DynamicTextElement":
        """Register an event handler that updates the text content.
        
        The handler should return the new text content or None to keep current text.
        """
        self.event_handlers[event_type] = handler
        return self
    
    def handle_event(self, event_type: str, *args, **kwargs) -> bool:
        """Handle an event and update text if handler exists.
        
        Returns True if text was updated, False otherwise.
        """
        if event_type in self.event_handlers:
            handler = self.event_handlers[event_type]
            try:
                new_text = handler(*args, **kwargs)
                if new_text is not None:
                    self.set_text(str(new_text))
                    return True
            except Exception:
                # Silently ignore handler errors to avoid crashing the UI
                pass
        return False
    
    def update_text_from_data(self, data: dict) -> "DynamicTextElement":
        """Convenience method to update text based on data dictionary.
        
        This can be used for common patterns like progress indicators.
        """
        # Example: progress indicator pattern
        if 'current' in data and 'total' in data:
            current = data['current']
            total = data['total']
            percentage = int((current / total) * 100) if total > 0 else 0
            progress_text = f"Progress: {current}/{total} ({percentage}%)"
            self.set_text(progress_text)
        elif 'status' in data:
            self.set_text(f"Status: {data['status']}")
        elif 'message' in data:
            self.set_text(data['message'])
        
        return self