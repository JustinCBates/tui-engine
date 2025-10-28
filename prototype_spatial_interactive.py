#!/usr/bin/env python3
"""Prototype for spatially-aware interactive components."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from questionary_extended.core.interfaces import SpaceRequirement, BufferDelta, ElementChangeEvent
from questionary_extended.core.component_wrappers import Component
from typing import Any, List, Optional, Dict


class SpatiallyAwareInteractiveComponent(Component):
    """
    Enhanced component that can render interactive prompts within spatial layouts.
    
    This component:
    1. Reserves space in the buffer manager for interactive area
    2. Coordinates with questionary to render prompts at specific positions
    3. Handles state changes and updates spatial layout
    4. Supports tab navigation between components
    """
    
    def __init__(self, name: str, component_type: str, **kwargs: Any) -> None:
        super().__init__(name, component_type, **kwargs)
        self._prompt_position: Optional[int] = None  # Buffer position for interactive prompt
        self._is_active: bool = False  # Whether this component is currently active for input
        self._current_value: Any = kwargs.get("default", "")
        self._prompt_text: str = kwargs.get("message", f"Enter {name}:")
    
    def calculate_space_requirements(self) -> SpaceRequirement:
        """Calculate space needed for this interactive component."""
        if not self._visible:
            return SpaceRequirement(min_lines=0, current_lines=0, max_lines=0, preferred_lines=0)
        
        if self.is_interactive():
            # Interactive components need space for:
            # 1. The prompt text
            # 2. The input area (could be multi-line for some types)
            # 3. Potential validation messages
            
            base_lines = 1  # Prompt line
            
            if self._component_type in ["text", "password"]:
                lines_needed = 1  # Single line input
            elif self._component_type == "select":
                # Select might need space for dropdown (but we'll handle that dynamically)
                lines_needed = 1
            elif self._component_type == "confirm":
                lines_needed = 1
            elif self._component_type == "checkbox":
                # Multiple options might need more space
                options = self.config.get("choices", [])
                lines_needed = min(len(options), 5)  # Max 5 visible options
            else:
                lines_needed = 1
            
            total_lines = base_lines + lines_needed
            return SpaceRequirement(
                min_lines=base_lines,
                current_lines=total_lines,
                max_lines=total_lines + 2,  # Extra space for validation messages
                preferred_lines=total_lines
            )
        else:
            # Display-only components
            lines = self.get_render_lines()
            line_count = len(lines)
            return SpaceRequirement(
                min_lines=line_count,
                current_lines=line_count,
                max_lines=line_count,
                preferred_lines=line_count
            )
    
    def get_render_lines(self) -> List[str]:
        """Get the display content for this component."""
        if not self._visible:
            return []
        
        if not self.is_interactive():
            # Use parent implementation for display-only components
            return super().get_render_lines()
        
        # For interactive components, render the prompt and current state
        lines = []
        
        # Add the prompt text
        if self._is_active:
            lines.append(f"? {self._prompt_text}")
        else:
            lines.append(f"  {self._prompt_text}")
        
        # Add current value display (if any)
        if self._current_value:
            if self._component_type == "password":
                lines.append(f"  {'*' * len(str(self._current_value))}")
            else:
                lines.append(f"  {self._current_value}")
        else:
            lines.append(f"  [Enter {self._component_type}]")
        
        return lines
    
    def activate_for_input(self, buffer_position: int) -> None:
        """Activate this component for interactive input at the given buffer position."""
        self._is_active = True
        self._prompt_position = buffer_position
        self.mark_dirty()
        
        # Fire change event to notify parent containers
        self.fire_change_event("state", metadata={"activated": True, "position": buffer_position})
    
    def deactivate(self) -> None:
        """Deactivate this component."""
        self._is_active = False
        self.mark_dirty()
        
        # Fire change event
        self.fire_change_event("state", metadata={"activated": False})
    
    def set_value(self, value: Any) -> None:
        """Set the current value of this component."""
        old_value = self._current_value
        self._current_value = value
        
        if old_value != value:
            self.mark_dirty()
            self.fire_change_event("content", metadata={"old_value": old_value, "new_value": value})
    
    def get_value(self) -> Any:
        """Get the current value of this component."""
        return self._current_value
    
    def render_interactive_prompt(self) -> Any:
        """
        Render the actual interactive prompt using questionary.
        
        This method should be called by the form navigation system
        when this component is active.
        """
        if not self.is_interactive() or not self._is_active:
            return self._current_value
        
        # Import questionary here to avoid circular dependencies
        try:
            import questionary
            
            # Create the appropriate questionary prompt
            if self._component_type == "text":
                prompt = questionary.text(
                    message=self._prompt_text,
                    default=str(self._current_value) if self._current_value else ""
                )
            elif self._component_type == "password":
                prompt = questionary.password(
                    message=self._prompt_text
                )
            elif self._component_type == "confirm":
                prompt = questionary.confirm(
                    message=self._prompt_text,
                    default=bool(self._current_value) if self._current_value else True
                )
            elif self._component_type == "select":
                choices = self.config.get("choices", [])
                prompt = questionary.select(
                    message=self._prompt_text,
                    choices=choices,
                    default=self._current_value if self._current_value in choices else None
                )
            else:
                # Fallback to text input
                prompt = questionary.text(
                    message=self._prompt_text,
                    default=str(self._current_value) if self._current_value else ""
                )
            
            # Execute the prompt and update value
            result = prompt.ask()
            if result is not None:
                self.set_value(result)
            
            return result
            
        except ImportError:
            # Fallback if questionary not available
            print(f"{self._prompt_text} ", end="")
            result = input()
            self.set_value(result)
            return result


def test_spatial_interactive_component():
    """Test the spatially-aware interactive component."""
    print("=== Testing Spatially-Aware Interactive Component ===")
    
    # Create an interactive text input
    text_input = SpatiallyAwareInteractiveComponent(
        name="username",
        component_type="text",
        message="What's your username?",
        default="john_doe"
    )
    
    print("Component created")
    print(f"Is interactive: {text_input.is_interactive()}")
    
    # Check space requirements
    space_req = text_input.calculate_space_requirements()
    print(f"Space requirements: min={space_req.min_lines}, current={space_req.current_lines}, max={space_req.max_lines}")
    
    # Get render lines
    lines = text_input.get_render_lines()
    print("Initial render lines:")
    for i, line in enumerate(lines):
        print(f"  {i+1}: {line}")
    
    # Activate for input
    print("\nActivating for input...")
    text_input.activate_for_input(buffer_position=10)
    
    # Get updated render lines
    lines = text_input.get_render_lines()
    print("Active render lines:")
    for i, line in enumerate(lines):
        print(f"  {i+1}: {line}")
    
    # Update value
    text_input.set_value("alice_smith")
    lines = text_input.get_render_lines()
    print("After setting value:")
    for i, line in enumerate(lines):
        print(f"  {i+1}: {line}")
    
    print("\n✅ Test complete!")


if __name__ == "__main__":
    test_spatial_interactive_component()