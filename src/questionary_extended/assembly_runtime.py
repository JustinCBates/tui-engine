"""
Higher-level Assembly with runtime execution capabilities.

This extends the core Assembly foundation with actual questionary integration,
event execution, and component rendering through QuestionaryBridge.
"""

from typing import Any, Dict, List

from .core.assembly_base import AssemblyBase
from .integration.questionary_bridge import QuestionaryBridge


class Assembly(AssemblyBase):
    """
    Higher-level Assembly with runtime execution and event processing.

    This class extends the foundational Core Assembly (which provides structure
    and event hooks) and wires QuestionaryBridge to actually execute components
    and process events during interaction.
    """

    def execute(self) -> Dict[str, Any]:
        """
        Execute the assembly and return collected results.

        Returns:
            Dictionary with component results namespaced by assembly name
        """
        bridge = QuestionaryBridge(self.parent_page.state)
        
        # Execute components with event processing
        bridge.run(self.components)
        
        # Return assembly-scoped state
        try:
            return self.parent_page.state.get_assembly_state(self.name)
        except Exception:
            # Fallback if PageState doesn't implement get_assembly_state
            return {}

    def update_choices(self, component_name: str, new_choices: List[str]) -> None:
        """
        Dynamically update choices for a component.
        
        Args:
            component_name: Name of the component to update
            new_choices: New list of choices
        """
        # Implementation pending - need to find component and update its choices
        for component in self.components:
            if hasattr(component, 'name') and component.name == component_name:
                if hasattr(component, 'choices'):
                    component.choices = new_choices
                break

    def show_components(self, component_names: List[str]) -> None:
        """
        Show specified components by making them visible.
        
        Args:
            component_names: List of component names to show
        """
        # Implementation pending - need component visibility system
        for component in self.components:
            if hasattr(component, 'name') and component.name in component_names:
                if hasattr(component, 'visible'):
                    component.visible = True

    def hide_components(self, component_names: List[str]) -> None:
        """
        Hide specified components by making them invisible.
        
        Args:
            component_names: List of component names to hide
        """
        # Implementation pending - need component visibility system
        for component in self.components:
            if hasattr(component, 'name') and component.name in component_names:
                if hasattr(component, 'visible'):
                    component.visible = False

    def get_value(self, field: str) -> Any:
        """
        Get value from assembly's local state.
        
        Args:
            field: Field name to retrieve
            
        Returns:
            Value from assembly state
        """
        try:
            return self.parent_page.state.get(f"{self.name}.{field}")
        except Exception:
            return None

    def get_related_value(self, field_path: str) -> Any:
        """
        Get value from other assemblies (cross-boundary access).
        
        Args:
            field_path: Full path like "other_assembly.field_name"
            
        Returns:
            Value from specified assembly field
        """
        try:
            return self.parent_page.state.get(field_path)
        except Exception:
            return None

    def push_breadcrumb(self, value: str) -> None:
        """
        Add value to navigation breadcrumbs for hierarchical navigation.
        
        Args:
            value: Value to add to breadcrumb trail
        """
        breadcrumbs_key = f"{self.name}._breadcrumbs"
        current_breadcrumbs = self.get_value("_breadcrumbs") or []
        current_breadcrumbs.append(value)
        try:
            self.parent_page.state.set(breadcrumbs_key, current_breadcrumbs)
        except Exception:
            pass

    def pop_breadcrumb(self) -> str:
        """
        Remove and return the last breadcrumb value.
        
        Returns:
            Last breadcrumb value, or empty string if none
        """
        breadcrumbs_key = f"{self.name}._breadcrumbs"
        current_breadcrumbs = self.get_value("_breadcrumbs") or []
        if current_breadcrumbs:
            value = current_breadcrumbs.pop()
            try:
                self.parent_page.state.set(breadcrumbs_key, current_breadcrumbs)
            except Exception:
                pass
            return value
        return ""

    def reset_to_level(self, level: int) -> None:
        """
        Reset navigation to a specific breadcrumb level.
        
        Args:
            level: Breadcrumb level to reset to (0 = root)
        """
        breadcrumbs_key = f"{self.name}._breadcrumbs"
        current_breadcrumbs = self.get_value("_breadcrumbs") or []
        if level < len(current_breadcrumbs):
            new_breadcrumbs = current_breadcrumbs[:level]
            try:
                self.parent_page.state.set(breadcrumbs_key, new_breadcrumbs)
            except Exception:
                pass

    def complete_selection(self, final_value: Any) -> None:
        """
        Signal assembly completion with final result.
        
        Args:
            final_value: The final selected/computed value
        """
        try:
            self.parent_page.state.set(f"{self.name}._final_result", final_value)
        except Exception:
            pass


__all__ = ["Assembly"]