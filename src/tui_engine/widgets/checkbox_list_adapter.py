"""CheckboxListAdapter: Enhanced wrapper for multi-select checkbox-list widgets with Questionary integration.

This adapter implements ChoiceWidgetProtocol and provides both traditional TUI Engine
functionality and enhanced Questionary integration with professional styling, advanced
keyboard shortcuts, and multi-selection validation support.

Features:
- Professional themes and styling through QuestionaryStyleAdapter
- Enhanced keyboard navigation with toggle-all functionality
- Multi-selection validation and constraints
- Backward compatibility with existing TUI Engine CheckboxList usage
- Dynamic theme switching and style customization
- Advanced selection management (select all, clear all, toggle selection)
"""
from __future__ import annotations

from typing import Any, Iterable, Sequence, Callable, Optional, Union, List, Tuple, Set
import logging

from .protocols import ChoiceWidgetProtocol

# Import Questionary and related components
try:
    import questionary
    from questionary import Choice
    from ..questionary_adapter import QuestionaryStyleAdapter
    from ..themes import TUIEngineThemes
    QUESTIONARY_AVAILABLE = True
except ImportError:
    QUESTIONARY_AVAILABLE = False
    logging.warning("Questionary not available, falling back to basic CheckboxList functionality")


class EnhancedCheckboxListAdapter(ChoiceWidgetProtocol):
    """Enhanced CheckboxList adapter with Questionary integration and professional styling.
    
    This class provides advanced checkbox list functionality with:
    - Professional theme integration
    - Enhanced keyboard navigation and shortcuts
    - Multi-selection validation and constraints
    - Dynamic styling and theme switching
    - Advanced selection management
    """
    
    def __init__(
        self,
        choices: Optional[List[Union[str, Tuple[str, Any], Choice]]] = None,
        message: str = "Select options:",
        style: Union[str, dict] = 'professional_blue',
        default: Optional[List[Any]] = None,
        validator: Optional[Callable[[List[Any]], Union[bool, str]]] = None,
        min_selections: Optional[int] = None,
        max_selections: Optional[int] = None,
        pointer: str = "❯",
        selected_pointer: str = "●",
        unselected_pointer: str = "○",
        instruction: str = "(Use arrow keys to move, Space to select, Enter to confirm)",
        **kwargs
    ):
        """Initialize enhanced checkbox list adapter.
        
        Args:
            choices: List of choices (strings, tuples, or Choice objects)
            message: Question/prompt message
            style: Theme name or custom style dict
            default: Default selected values
            validator: Function to validate selection list
            min_selections: Minimum number of selections required
            max_selections: Maximum number of selections allowed
            pointer: Pointer character for current selection
            selected_pointer: Character for selected options
            unselected_pointer: Character for unselected options
            instruction: Instruction text for user
            **kwargs: Additional arguments for underlying widget
        """
        self.message = message
        self.choices = self._process_choices(choices or [])
        self.default = default or []
        self.validator = validator
        self.min_selections = min_selections
        self.max_selections = max_selections
        self.pointer = pointer
        self.selected_pointer = selected_pointer
        self.unselected_pointer = unselected_pointer
        self.instruction = instruction
        self.kwargs = kwargs
        
        # Initialize style adapter
        self.style_adapter = None
        self.current_theme = style
        if QUESTIONARY_AVAILABLE:
            self.style_adapter = QuestionaryStyleAdapter()
            if isinstance(style, str):
                self.style_adapter.set_theme(style)
        
        # Initialize widget
        self._widget = None
        self._current_values = set(self.default)
        self._create_widget()
        
        # Adapter protocol attributes
        self._tui_path: str | None = None
        self._tui_focusable: bool = True
        self.element = None
        
        # Cache for processed choices
        self._choice_mapping = {}
        self._update_choice_mapping()
    
    def _process_choices(self, choices: List[Union[str, Tuple[str, Any], Choice]]) -> List[Choice]:
        """Process various choice formats into Questionary Choice objects."""
        processed = []
        
        for choice in choices:
            if QUESTIONARY_AVAILABLE and isinstance(choice, Choice):
                processed.append(choice)
            elif isinstance(choice, tuple) and len(choice) == 2:
                # (title, value) tuple
                title, value = choice
                if QUESTIONARY_AVAILABLE:
                    processed.append(Choice(title=str(title), value=value))
                else:
                    processed.append((title, value))
            elif isinstance(choice, str):
                # Simple string choice
                if QUESTIONARY_AVAILABLE:
                    processed.append(Choice(title=choice, value=choice))
                else:
                    processed.append((choice, choice))
            else:
                # Fallback: convert to string
                choice_str = str(choice)
                if QUESTIONARY_AVAILABLE:
                    processed.append(Choice(title=choice_str, value=choice))
                else:
                    processed.append((choice_str, choice))
        
        return processed
    
    def _update_choice_mapping(self):
        """Update internal choice mapping for value lookup."""
        self._choice_mapping = {}
        for i, choice in enumerate(self.choices):
            if QUESTIONARY_AVAILABLE and hasattr(choice, 'value'):
                self._choice_mapping[choice.value] = i
                self._choice_mapping[choice.title] = i
            elif isinstance(choice, tuple):
                title, value = choice
                self._choice_mapping[value] = i
                self._choice_mapping[title] = i
    
    def _create_widget(self):
        """Create the underlying checkbox list widget."""
        if not QUESTIONARY_AVAILABLE:
            # Fallback to basic implementation
            self._widget = None
            return
        
        try:
            # Get style for Questionary
            style = None
            if self.style_adapter:
                style = self.style_adapter.get_questionary_style()
            
            # Create Questionary checkbox widget
            self._widget = questionary.checkbox(
                message=self.message,
                choices=self.choices,
                default=list(self._current_values),
                style=style,
                pointer=self.pointer,
                instruction=self.instruction,
                **self.kwargs
            )
            
        except Exception as e:
            logging.warning(f"Failed to create Questionary checkbox list widget: {e}")
            self._widget = None
    
    def focus(self) -> None:
        """Focus the checkbox list widget."""
        if self._widget is None:
            return
        
        if hasattr(self._widget, "focus") and callable(self._widget.focus):
            try:
                self._widget.focus()
            except Exception:
                pass
    
    def _tui_sync(self) -> list[Any] | None:
        """Return a list of selected values from the underlying widget."""
        if self._widget is None:
            return list(self._current_values)
        
        try:
            # For Questionary widgets
            if hasattr(self._widget, 'default'):
                return list(self._widget.default)
            
            # Common attribute names for checkbox lists
            for attr in ['checked_values', 'current_values', 'selected']:
                if hasattr(self._widget, attr):
                    value = getattr(self._widget, attr)
                    if isinstance(value, (list, set, tuple)):
                        return list(value)
                    else:
                        return [value]
                        
        except Exception:
            pass
        
        return list(self._current_values)
    
    def get_selected(self) -> Iterable[Any]:
        """Get currently selected values as iterable."""
        v = self._tui_sync()
        return [] if v is None else list(v)
    
    def set_selected(self, selected: Iterable[Any]) -> None:
        """Set the selected values."""
        # Normalize to set
        vals = set()
        try:
            for s in selected:
                vals.add(s)
        except Exception:
            # treat selected as single value
            vals = {selected}
        
        self._current_values = vals
        
        # Update underlying widget
        if self._widget is None:
            return
        
        try:
            # For Questionary widgets, update default
            if hasattr(self._widget, 'default'):
                self._widget.default = list(vals)
                return
            
            # Try common attribute names
            for attr in ['checked_values', 'current_values']:
                if hasattr(self._widget, attr):
                    setattr(self._widget, attr, list(vals))
                    return
            
            # Special handling for 'selected' attribute (may expect set)
            if hasattr(self._widget, 'selected'):
                setattr(self._widget, 'selected', vals)
                return
                    
        except Exception:
            pass
    
    def validate_selection(self, values: List[Any]) -> Tuple[bool, str]:
        """Validate the selected values.
        
        Args:
            values: List of values to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        # Check min/max constraints first
        if self.min_selections is not None and len(values) < self.min_selections:
            return False, f"Please select at least {self.min_selections} option(s)"
        
        if self.max_selections is not None and len(values) > self.max_selections:
            return False, f"Please select at most {self.max_selections} option(s)"
        
        # Run custom validator if provided
        if self.validator is None:
            return True, ""
        
        try:
            result = self.validator(values)
            if isinstance(result, bool):
                return result, "" if result else "Invalid selection"
            elif isinstance(result, str):
                return len(result) == 0, result
            else:
                return bool(result), "" if result else "Invalid selection"
        except Exception as e:
            return False, f"Validation error: {e}"
    
    def change_theme(self, theme_name: str):
        """Change the current theme and recreate widget."""
        if not QUESTIONARY_AVAILABLE or not self.style_adapter:
            return
        
        self.current_theme = theme_name
        self.style_adapter.set_theme(theme_name)
        self._create_widget()
        
        # Restore current values
        if self._current_values:
            self.set_selected(self._current_values)
    
    def add_choice(self, choice: Union[str, Tuple[str, Any], Choice]):
        """Add a new choice to the checkbox list."""
        processed_choice = self._process_choices([choice])[0]
        self.choices.append(processed_choice)
        self._update_choice_mapping()
        self._create_widget()
    
    def remove_choice(self, value: Any):
        """Remove a choice by its value."""
        self.choices = [
            choice for choice in self.choices
            if (hasattr(choice, 'value') and choice.value != value) or
               (isinstance(choice, tuple) and choice[1] != value)
        ]
        
        # Remove from current selection if it was selected
        self._current_values.discard(value)
        
        self._update_choice_mapping()
        self._create_widget()
    
    def select_all(self):
        """Select all available choices."""
        all_values = set()
        for choice in self.choices:
            if QUESTIONARY_AVAILABLE and hasattr(choice, 'value'):
                all_values.add(choice.value)
            elif isinstance(choice, tuple):
                all_values.add(choice[1])
        
        self.set_selected(all_values)
    
    def clear_all(self):
        """Clear all selections."""
        self.set_selected([])
    
    def toggle_choice(self, value: Any):
        """Toggle the selection state of a specific choice."""
        current = set(self.get_selected())
        if value in current:
            current.remove(value)
        else:
            current.add(value)
        self.set_selected(current)
    
    def is_selected(self, value: Any) -> bool:
        """Check if a specific value is selected."""
        return value in self.get_selected()
    
    def set_message(self, message: str):
        """Update the prompt message."""
        self.message = message
        self._create_widget()
    
    def set_instruction(self, instruction: str):
        """Update the instruction text."""
        self.instruction = instruction
        self._create_widget()
    
    def set_constraints(self, min_selections: Optional[int] = None, max_selections: Optional[int] = None):
        """Update selection constraints."""
        self.min_selections = min_selections
        self.max_selections = max_selections
    
    def enable_validation(self, validator: Callable[[List[Any]], Union[bool, str]]):
        """Enable validation with the given validator function."""
        self.validator = validator
    
    def disable_validation(self):
        """Disable validation."""
        self.validator = None
    
    def get_choice_count(self) -> int:
        """Get the number of available choices."""
        return len(self.choices)
    
    def get_selected_count(self) -> int:
        """Get the number of currently selected choices."""
        return len(list(self.get_selected()))
    
    def get_choices(self) -> List[Union[Choice, Tuple[str, Any]]]:
        """Get all available choices."""
        return self.choices
    
    def is_questionary_enhanced(self) -> bool:
        """Check if Questionary enhancement is active."""
        return QUESTIONARY_AVAILABLE and self._widget is not None
    
    def get_style_adapter(self) -> Optional[QuestionaryStyleAdapter]:
        """Get the style adapter instance."""
        return self.style_adapter
    
    def get_widget_info(self) -> dict:
        """Get comprehensive widget information."""
        return {
            'use_questionary': self.is_questionary_enhanced(),
            'has_validator': self.validator is not None,
            'choice_count': self.get_choice_count(),
            'selected_count': self.get_selected_count(),
            'current_values': list(self._current_values),
            'theme': self.current_theme,
            'message': self.message,
            'instruction': self.instruction,
            'min_selections': self.min_selections,
            'max_selections': self.max_selections
        }
    
    @property
    def ptk_widget(self) -> Any:
        """Get the underlying prompt-toolkit widget."""
        return self._widget
    
    @property
    def options(self) -> Sequence[tuple[Any, str]]:
        """Get options in the format expected by ChoiceWidgetProtocol."""
        result = []
        for choice in self.choices:
            if QUESTIONARY_AVAILABLE and hasattr(choice, 'value'):
                result.append((choice.value, choice.title))
            elif isinstance(choice, tuple):
                value, title = choice
                result.append((value, title))
        return result
    
    def __repr__(self) -> str:
        """String representation of the adapter."""
        return f"<EnhancedCheckboxListAdapter message='{self.message}' choices={len(self.choices)} selected={len(self._current_values)}>"


class CheckboxListAdapter(ChoiceWidgetProtocol):
    """Backward-compatible CheckboxListAdapter that automatically uses enhanced features when available.
    
    This class maintains full backward compatibility while providing access to enhanced
    Questionary features when they're available and beneficial.
    """
    
    # runtime contract attributes
    _tui_path: str | None = None
    _tui_focusable: bool = True
    
    def __init__(self, widget: Any | None = None, element: Any | None = None, **kwargs):
        """Initialize CheckboxListAdapter with backward compatibility.
        
        Args:
            widget: Legacy widget object (for backward compatibility)
            element: Element object (for backward compatibility)
            **kwargs: Additional arguments for enhanced functionality
        """
        self.element = element
        
        # If we have a legacy widget, use traditional behavior
        if widget is not None:
            self._widget = widget
            self._enhanced_adapter = None
            self._legacy_mode = True
        else:
            # Use enhanced adapter for new functionality
            self._enhanced_adapter = None
            self._widget = None
            self._legacy_mode = False
            
            # Try to create enhanced adapter if Questionary is available
            if QUESTIONARY_AVAILABLE and kwargs:
                try:
                    self._enhanced_adapter = EnhancedCheckboxListAdapter(**kwargs)
                    self._widget = self._enhanced_adapter.ptk_widget
                except Exception as e:
                    logging.warning(f"Failed to create enhanced checkbox adapter, falling back to basic: {e}")

    def focus(self) -> None:
        """Focus the checkbox list widget."""
        if self._enhanced_adapter:
            self._enhanced_adapter.focus()
            return
        
        w = self._widget
        if w is None:
            return
        if hasattr(w, "focus") and callable(w.focus):
            try:
                w.focus()
            except Exception:
                pass

    def _tui_sync(self) -> list[Any] | None:
        """Return a list of selected values from the underlying widget."""
        if self._enhanced_adapter:
            return self._enhanced_adapter._tui_sync()
        
        w = self._widget
        if w is None:
            return None
        try:
            # common names: checked_values, current_values, selected
            if hasattr(w, "checked_values"):
                return list(w.checked_values)
            if hasattr(w, "current_values"):
                return list(w.current_values)
            if hasattr(w, "selected"):
                v = w.selected
                try:
                    return list(v)
                except Exception:
                    return [v]
        except Exception:
            pass
        return None

    def get_selected(self) -> Iterable[Any]:
        """Get currently selected values."""
        if self._enhanced_adapter:
            return self._enhanced_adapter.get_selected()
        
        v = self._tui_sync()
        return [] if v is None else list(v)

    def set_selected(self, selected: Iterable[Any]) -> None:
        """Set the selected values."""
        if self._enhanced_adapter:
            self._enhanced_adapter.set_selected(selected)
            return
        
        # Normalize to list
        vals = []
        try:
            for s in selected:
                vals.append(s)
        except Exception:
            # treat selected as single value
            vals = [selected]

        w = self._widget
        if w is None:
            return
        try:
            if hasattr(w, "checked_values"):
                try:
                    w.checked_values = vals
                    return
                except Exception:
                    pass
            if hasattr(w, "current_values"):
                try:
                    w.current_values = vals
                    return
                except Exception:
                    pass
            if hasattr(w, "selected"):
                try:
                    w.selected = set(vals)
                    return
                except Exception:
                    pass
        except Exception:
            pass
    
    @property
    def options(self) -> Sequence[tuple[Any, str]]:
        """Get options in the format expected by ChoiceWidgetProtocol."""
        if self._enhanced_adapter:
            return self._enhanced_adapter.options
        return ()

    @property
    def ptk_widget(self) -> Any:
        """Get the underlying prompt-toolkit widget."""
        return self._widget
    
    # Enhanced functionality delegation (when available)
    def validate_selection(self, values: List[Any]) -> Tuple[bool, str]:
        """Validate the selected values (enhanced feature)."""
        if self._enhanced_adapter:
            return self._enhanced_adapter.validate_selection(values)
        return True, ""
    
    def change_theme(self, theme_name: str):
        """Change the current theme (enhanced feature)."""
        if self._enhanced_adapter:
            self._enhanced_adapter.change_theme(theme_name)
    
    def add_choice(self, choice: Union[str, Tuple[str, Any]]):
        """Add a new choice (enhanced feature)."""
        if self._enhanced_adapter:
            self._enhanced_adapter.add_choice(choice)
    
    def remove_choice(self, value: Any):
        """Remove a choice by value (enhanced feature)."""
        if self._enhanced_adapter:
            self._enhanced_adapter.remove_choice(value)
    
    def select_all(self):
        """Select all choices (enhanced feature)."""
        if self._enhanced_adapter:
            self._enhanced_adapter.select_all()
    
    def clear_all(self):
        """Clear all selections (enhanced feature)."""
        if self._enhanced_adapter:
            self._enhanced_adapter.clear_all()
    
    def toggle_choice(self, value: Any):
        """Toggle a specific choice (enhanced feature)."""
        if self._enhanced_adapter:
            self._enhanced_adapter.toggle_choice(value)
    
    def is_selected(self, value: Any) -> bool:
        """Check if a value is selected (enhanced feature)."""
        if self._enhanced_adapter:
            return self._enhanced_adapter.is_selected(value)
        return value in self.get_selected()
    
    def set_message(self, message: str):
        """Update the prompt message (enhanced feature)."""
        if self._enhanced_adapter:
            self._enhanced_adapter.set_message(message)
    
    def set_constraints(self, min_selections: Optional[int] = None, max_selections: Optional[int] = None):
        """Set selection constraints (enhanced feature)."""
        if self._enhanced_adapter:
            self._enhanced_adapter.set_constraints(min_selections, max_selections)
    
    def enable_validation(self, validator: Callable[[List[Any]], Union[bool, str]]):
        """Enable validation (enhanced feature)."""
        if self._enhanced_adapter:
            self._enhanced_adapter.enable_validation(validator)
    
    def disable_validation(self):
        """Disable validation (enhanced feature)."""
        if self._enhanced_adapter:
            self._enhanced_adapter.disable_validation()
    
    def get_choice_count(self) -> int:
        """Get the number of choices (enhanced feature)."""
        if self._enhanced_adapter:
            return self._enhanced_adapter.get_choice_count()
        return 0
    
    def get_selected_count(self) -> int:
        """Get the number of selected choices (enhanced feature)."""
        if self._enhanced_adapter:
            return self._enhanced_adapter.get_selected_count()
        return len(list(self.get_selected()))
    
    def is_questionary_enhanced(self) -> bool:
        """Check if Questionary enhancement is active."""
        return self._enhanced_adapter is not None and self._enhanced_adapter.is_questionary_enhanced()
    
    def get_widget_info(self) -> dict:
        """Get comprehensive widget information."""
        if self._enhanced_adapter:
            return self._enhanced_adapter.get_widget_info()
        return {
            'use_questionary': False,
            'has_validator': False,
            'choice_count': 0,
            'selected_count': self.get_selected_count(),
            'current_values': list(self.get_selected()),
            'theme': 'default',
            'legacy_mode': self._legacy_mode
        }

    def __repr__(self) -> str:  # pragma: no cover - trivial
        """String representation of the adapter."""
        if self._enhanced_adapter:
            return repr(self._enhanced_adapter)
        return f"<CheckboxListAdapter widget={self._widget!r}>"


# Convenience function for creating enhanced checkbox lists
def create_checkbox_list(
    choices: List[Union[str, Tuple[str, Any]]],
    message: str = "Select options:",
    style: str = 'professional_blue',
    min_selections: Optional[int] = None,
    max_selections: Optional[int] = None,
    **kwargs
) -> CheckboxListAdapter:
    """Create a CheckboxListAdapter with enhanced features.
    
    Args:
        choices: List of choices (strings or (title, value) tuples)
        message: Question/prompt message
        style: Theme name for styling
        min_selections: Minimum number of selections required
        max_selections: Maximum number of selections allowed
        **kwargs: Additional arguments for EnhancedCheckboxListAdapter
        
    Returns:
        CheckboxListAdapter with enhanced features when available
    """
    return CheckboxListAdapter(
        choices=choices,
        message=message,
        style=style,
        min_selections=min_selections,
        max_selections=max_selections,
        **kwargs
    )
