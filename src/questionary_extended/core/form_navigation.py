"""
Spatial form navigation system for interactive components.

This module provides form navigation capabilities that work with the spatial
buffer system, allowing for embedded interactive prompts within cards and pages.
"""

from typing import List, Dict, Any, Optional, TYPE_CHECKING
from .interfaces import ElementChangeEvent

if TYPE_CHECKING:
    from .component_wrappers import Component


class SpatialFormNavigator:
    """
    Manages tab navigation between multiple interactive components within a spatial layout.
    
    This system:
    1. Tracks all interactive components in a card/page
    2. Handles tab navigation between them
    3. Coordinates with buffer manager for positioning
    4. Manages form state and validation
    """
    
    def __init__(self, buffer_manager=None):
        self.buffer_manager = buffer_manager
        self.interactive_components: List["Component"] = []
        self.current_component_index: int = 0
        self.form_state: Dict[str, Any] = {}
        self.is_form_active: bool = False
    
    def register_interactive_component(self, component: "Component") -> None:
        """Register an interactive component for form navigation."""
        if component.is_interactive() and component not in self.interactive_components:
            self.interactive_components.append(component)
            # Sort by name for consistent order (could be enhanced with explicit ordering)
            self.interactive_components.sort(key=lambda c: c.name)
    
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

        # Do not print diagnostic messages here; position the cursor so external
        # interactive prompts (questionary) appear after the rendered content.
        try:
            while self.is_form_active and self.current_component_index < len(self.interactive_components):
                current_component = self.interactive_components[self.current_component_index]

                # Activate current component
                current_component.activate_for_input(buffer_position=0)

                # If a buffer manager is available, move the cursor to the end of
                # rendered content so the interactive prompt doesn't corrupt the
                # spatial buffer area.
                try:
                    if self.buffer_manager is not None and hasattr(self.buffer_manager, '_position_cursor_at_end'):
                        try:
                            self.buffer_manager._position_cursor_at_end()
                        except Exception:
                            # Best-effort cursor positioning; ignore failures
                            pass
                except Exception:
                    pass

                # Render the interactive prompt (this will use questionary or fall
                # back to input()). The prompt output will appear after the page
                # content because we positioned the cursor above.
                try:
                    result = current_component.render_interactive_prompt()

                    if result is not None:
                        # Store the result
                        self.form_state[current_component.name] = result
                        current_component.set_value(result)
                        # Move to next component
                        self.current_component_index += 1
                    else:
                        # User cancelled - exit the form loop
                        break

                except KeyboardInterrupt:
                    # Treat keyboard interrupt as cancellation of form
                    break
                finally:
                    # Deactivate current component
                    try:
                        current_component.deactivate()
                    except Exception:
                        pass

            return self.form_state

        finally:
            self.is_form_active = False
            # Deactivate all components
            for component in self.interactive_components:
                try:
                    component.deactivate()
                except Exception:
                    pass
    
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
    
    def collect_all_values(self) -> Dict[str, Any]:
        """Collect current values from all interactive components."""
        values = {}
        for component in self.interactive_components:
            if component.is_interactive():
                values[component.name] = component.get_value()
        return values