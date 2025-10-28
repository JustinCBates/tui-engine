#!/usr/bin/env python3
"""Spatial form navigation system for interactive components."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from typing import List, Dict, Any, Optional
from questionary_extended.core.interfaces import SpaceRequirement, BufferDelta


class SpatialFormNavigator:
    """
    Manages tab navigation between multiple interactive components within a spatial layout.
    
    This system:
    1. Tracks all interactive components in a card/page
    2. Handles tab navigation between them
    3. Coordinates with buffer manager for positioning
    4. Manages form state and validation
    """
    
    def __init__(self, buffer_manager):
        self.buffer_manager = buffer_manager
        self.interactive_components: List[Any] = []  # List of SpatiallyAwareInteractiveComponent
        self.current_component_index: int = 0
        self.form_state: Dict[str, Any] = {}
        self.is_form_active: bool = False
    
    def register_interactive_component(self, component) -> None:
        """Register an interactive component for form navigation."""
        if component.is_interactive() and component not in self.interactive_components:
            self.interactive_components.append(component)
            # Sort by visual order (could be based on buffer position)
            self.interactive_components.sort(key=lambda c: c.name)  # Simple name-based sort for now
    
    def start_form_navigation(self) -> Dict[str, Any]:
        """
        Start interactive form navigation with tab support.
        
        Returns:
            Dictionary of component values after form completion
        """
        if not self.interactive_components:
            return {}
        
        self.is_form_active = True
        self.current_component_index = 0
        
        print("\\n📝 Starting form navigation (Tab to move between fields, Enter to submit)")
        print("=" * 60)
        
        try:
            while self.is_form_active and self.current_component_index < len(self.interactive_components):
                current_component = self.interactive_components[self.current_component_index]
                
                # Activate current component
                current_component.activate_for_input(buffer_position=0)  # Position managed by buffer manager
                
                print(f"\\n📍 Field {self.current_component_index + 1} of {len(self.interactive_components)}")
                print(f"Component: {current_component.name}")
                
                # Render the interactive prompt
                try:
                    result = current_component.render_interactive_prompt()
                    
                    if result is not None:
                        # Store the result
                        self.form_state[current_component.name] = result
                        current_component.set_value(result)
                        
                        # Move to next component
                        self.current_component_index += 1
                    else:
                        # User cancelled - might want to go back
                        break
                        
                except KeyboardInterrupt:
                    print("\\n❌ Form cancelled by user")
                    break
                finally:
                    # Deactivate current component
                    current_component.deactivate()
            
            print("\\n✅ Form navigation complete!")
            return self.form_state
            
        finally:
            self.is_form_active = False
            # Deactivate all components
            for component in self.interactive_components:
                component.deactivate()
    
    def navigate_to_component(self, index: int) -> bool:
        """Navigate directly to a specific component by index."""
        if 0 <= index < len(self.interactive_components):
            # Deactivate current
            if 0 <= self.current_component_index < len(self.interactive_components):
                self.interactive_components[self.current_component_index].deactivate()
            
            # Activate new
            self.current_component_index = index
            current_component = self.interactive_components[self.current_component_index]
            current_component.activate_for_input(buffer_position=0)
            return True
        return False
    
    def get_form_summary(self) -> str:
        """Get a summary of the current form state."""
        if not self.interactive_components:
            return "No interactive components"
        
        lines = ["Form Summary:"]
        for i, component in enumerate(self.interactive_components):
            status = "✅" if component.name in self.form_state else "⏸️"
            current = "👉" if i == self.current_component_index else "  "
            value = self.form_state.get(component.name, component.get_value())
            lines.append(f"{current} {status} {component.name}: {value}")
        
        return "\\n".join(lines)


def test_form_navigation():
    """Test the spatial form navigation system."""
    print("=== Testing Spatial Form Navigation ===")
    
    # Mock buffer manager
    class MockBufferManager:
        def __init__(self):
            pass
    
    # Import our prototype component
    sys.path.insert(0, '/home/vpsuser/projects/tui-engine')
    from prototype_spatial_interactive import SpatiallyAwareInteractiveComponent
    
    # Create form navigator
    navigator = SpatialFormNavigator(MockBufferManager())
    
    # Create multiple interactive components
    username_input = SpatiallyAwareInteractiveComponent(
        name="username",
        component_type="text",
        message="What's your username?",
        default=""
    )
    
    email_input = SpatiallyAwareInteractiveComponent(
        name="email", 
        component_type="text",
        message="What's your email?",
        default=""
    )
    
    newsletter_confirm = SpatiallyAwareInteractiveComponent(
        name="newsletter",
        component_type="confirm",
        message="Subscribe to newsletter?",
        default=True
    )
    
    # Register components
    navigator.register_interactive_component(username_input)
    navigator.register_interactive_component(email_input)
    navigator.register_interactive_component(newsletter_confirm)
    
    print(f"Registered {len(navigator.interactive_components)} interactive components")
    print(navigator.get_form_summary())
    
    # Simulate form navigation (without actually prompting for input)
    print("\\n🔄 Simulating form navigation...")
    navigator.form_state = {
        "username": "alice_doe",
        "email": "alice@example.com", 
        "newsletter": True
    }
    
    print(navigator.get_form_summary())
    
    print("\\n✅ Form navigation test complete!")


if __name__ == "__main__":
    test_form_navigation()