from typing import List, Optional, Callable
from prompt_toolkit.widgets import RadioList
from prompt_toolkit.layout.dimension import Dimension

from .component_base import ComponentBase


class RadioButtonGroup(ComponentBase):
    """Radio button group component for single selection from multiple options."""
    
    def __init__(self, name: str, options: List[str], default_index: int = 0):
        super().__init__(name, variant="radio-group")
        self.options = options
        self.selected_index = default_index
        self.selected_value = options[default_index] if options else None
        self._radio_list = None
        
    def get_selected_value(self) -> Optional[str]:
        """Get the currently selected option value."""
        return self.selected_value
        
    def get_selected_index(self) -> int:
        """Get the currently selected option index."""
        return self.selected_index
        
    def set_selected_index(self, index: int) -> "RadioButtonGroup":
        """Set the selected option by index."""
        if 0 <= index < len(self.options):
            old_value = self.selected_value
            self.selected_index = index
            self.selected_value = self.options[index]
            self.current_value = self.selected_value
            
            # Update prompt-toolkit widget if it exists
            if self._radio_list:
                self._radio_list.current_value = self.selected_value
            
            # Trigger events
            self.trigger_event("value_changed", old_value, self.selected_value)
            
        return self
        
    def set_selected_value(self, value: str) -> "RadioButtonGroup":
        """Set the selected option by value."""
        if value in self.options:
            index = self.options.index(value)
            self.set_selected_index(index)
        return self
        
    def add_option(self, option: str) -> "RadioButtonGroup":
        """Add a new option to the radio group."""
        self.options.append(option)
        return self
        
    def to_prompt_toolkit(self):
        """Convert to prompt-toolkit RadioList widget."""
        # Create values list for RadioList (value, label) tuples
        values = [(option, option) for option in self.options]
        
        self._radio_list = RadioList(
            values=values,
            default=self.selected_value
        )
        
        # Set up change handler
        def on_change():
            if self._radio_list.current_value != self.selected_value:
                old_value = self.selected_value
                self.selected_value = self._radio_list.current_value
                self.selected_index = self.options.index(self.selected_value)
                self.current_value = self.selected_value
                self.trigger_event("value_changed", old_value, self.selected_value)
        
        # Note: RadioList doesn't have a direct change callback, but we can monitor it
        # in the application event loop if needed
        
        return self._radio_list
        
    def get_render_lines(self, width: int = 80) -> List[str]:
        """Render radio button group as text."""
        lines = []
        if self.label:
            lines.append(f"{self.label}")
        
        lines.append(f"[{self.variant.upper()}] {self.name}")
        
        for i, option in enumerate(self.options):
            selected = "●" if i == self.selected_index else "○"
            lines.append(f"  {selected} {option}")
            
        if self.hint:
            lines.append(f"  Hint: {self.hint}")
            
        return lines


# Convenience factory functions
class RadioButtons:
    """Factory class for creating common radio button groups."""
    
    @staticmethod
    def local_remote(name: str = "deployment_type", default: str = "local") -> RadioButtonGroup:
        """Create a Local/Remote radio button group."""
        options = ["local", "remote"]
        default_index = options.index(default) if default in options else 0
        return RadioButtonGroup(name, options, default_index)
    
    @staticmethod
    def environment(name: str = "environment", default: str = "development") -> RadioButtonGroup:
        """Create a Development/Staging/Production radio button group."""
        options = ["development", "staging", "production"]
        default_index = options.index(default) if default in options else 0
        return RadioButtonGroup(name, options, default_index)
    
    @staticmethod
    def linux_distro(name: str = "linux_distro", default: str = "debian") -> RadioButtonGroup:
        """Create a Linux distribution radio button group."""
        options = ["debian", "openSuse", "Arch", "RedHat", "slack"]
        default_index = options.index(default) if default in options else 0
        return RadioButtonGroup(name, options, default_index)
    
    @staticmethod
    def yes_no(name: str, default: str = "yes") -> RadioButtonGroup:
        """Create a Yes/No radio button group."""
        options = ["yes", "no"]
        default_index = options.index(default) if default in options else 0
        return RadioButtonGroup(name, options, default_index)
    
    @staticmethod
    def custom(name: str, options: List[str], default: str = None) -> RadioButtonGroup:
        """Create a custom radio button group with specified options."""
        if not options:
            raise ValueError("Options list cannot be empty")
        
        default_index = 0
        if default and default in options:
            default_index = options.index(default)
            
        return RadioButtonGroup(name, options, default_index)