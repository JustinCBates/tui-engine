"""SelectAdapter: Enhanced wrapper for dropdown/select widgets with Questionary integration.

This adapter implements ChoiceWidgetProtocol and provides both traditional TUI Engine
functionality and enhanced Questionary integration with professional styling, search
functionality, and group selection support.

Features:
- Professional themes and styling through QuestionaryStyleAdapter
- Search functionality with fuzzy matching
- Group selection support with separators
- Keyboard shortcuts and enhanced navigation
- Backward compatibility with existing TUI Engine Select usage
- Dynamic theme switching and style customization
"""
from __future__ import annotations

from typing import Any, Iterable, Sequence, Callable, Optional, Union, List, Tuple, Dict
import logging
import re

from .protocols import ChoiceWidgetProtocol

# Import Questionary and related components
try:
    import questionary
    from questionary import Choice, Separator
    from ..questionary_adapter import QuestionaryStyleAdapter
    from ..themes import TUIEngineThemes
    QUESTIONARY_AVAILABLE = True
except ImportError:
    QUESTIONARY_AVAILABLE = False
    logging.warning("Questionary not available, falling back to basic Select functionality")


class EnhancedSelectAdapter(ChoiceWidgetProtocol):
    """Enhanced Select adapter with Questionary integration and professional styling.
    
    This class provides advanced dropdown/select functionality with:
    - Professional theme integration
    - Search functionality with fuzzy matching
    - Group selection support
    - Enhanced keyboard navigation
    - Dynamic styling and theme switching
    """
    
    def __init__(
        self,
        choices: Optional[List[Union[str, Tuple[str, Any], Choice, Separator]]] = None,
        message: str = "Select an option:",
        style: Union[str, dict] = 'professional_blue',
        default: Optional[Any] = None,
        validator: Optional[Callable[[Any], Union[bool, str]]] = None,
        searchable: bool = False,
        show_selected: bool = True,
        pointer: str = "❯",
        instruction: str = "(Use arrow keys to move, Enter to select)",
        **kwargs
    ):
        """Initialize enhanced select adapter.
        
        Args:
            choices: List of choices (strings, tuples, Choice objects, or Separators)
            message: Question/prompt message
            style: Theme name or custom style dict
            default: Default selected value
            validator: Function to validate selection
            searchable: Enable search functionality
            show_selected: Whether to show selection indicators
            pointer: Pointer character for current selection
            instruction: Instruction text for user
            **kwargs: Additional arguments for underlying widget
        """
        self.message = message
        self.choices = self._process_choices(choices or [])
        self.default = default
        self.validator = validator
        self.searchable = searchable
        self.show_selected = show_selected
        self.pointer = pointer
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
        self._current_value = default
        self._create_widget()
        
        # Adapter protocol attributes
        self._tui_path: str | None = None
        self._tui_focusable: bool = True
        self.element = None
        
        # Cache for processed choices and search
        self._choice_mapping = {}
        self._filtered_choices = []
        self._update_choice_mapping()
    
    def _process_choices(self, choices: List[Union[str, Tuple[str, Any], Choice, Separator]]) -> List[Union[Choice, Separator]]:
        """Process various choice formats into Questionary Choice/Separator objects."""
        processed = []
        
        for choice in choices:
            if QUESTIONARY_AVAILABLE:
                if isinstance(choice, (Choice, Separator)):
                    processed.append(choice)
                elif isinstance(choice, tuple) and len(choice) == 2:
                    # (title, value) tuple
                    title, value = choice
                    processed.append(Choice(title=str(title), value=value))
                elif isinstance(choice, str):
                    if choice.startswith("---") or choice.startswith("==="):
                        # Treat as separator
                        processed.append(Separator(choice))
                    else:
                        # Regular choice
                        processed.append(Choice(title=choice, value=choice))
                else:
                    # Fallback: convert to string
                    choice_str = str(choice)
                    processed.append(Choice(title=choice_str, value=choice))
            else:
                # Fallback for when Questionary is not available
                if isinstance(choice, tuple) and len(choice) == 2:
                    processed.append(choice)
                elif isinstance(choice, str):
                    if not (choice.startswith("---") or choice.startswith("===")):
                        processed.append((choice, choice))
                else:
                    choice_str = str(choice)
                    processed.append((choice_str, choice))
        
        return processed
    
    def _update_choice_mapping(self):
        """Update internal choice mapping for value lookup."""
        self._choice_mapping = {}
        for i, choice in enumerate(self.choices):
            if QUESTIONARY_AVAILABLE:
                if hasattr(choice, 'value') and hasattr(choice, 'title'):
                    self._choice_mapping[choice.value] = i
                    self._choice_mapping[choice.title] = i
            elif isinstance(choice, tuple):
                title, value = choice
                self._choice_mapping[value] = i
                self._choice_mapping[title] = i
    
    def _create_widget(self):
        """Create the underlying select widget."""
        if not QUESTIONARY_AVAILABLE:
            # Fallback to basic implementation
            self._widget = None
            return
        
        try:
            # Get style for Questionary
            style = None
            if self.style_adapter:
                style = self.style_adapter.get_questionary_style()
            
            # Filter out separators for Questionary select (it doesn't support them directly)
            selectable_choices = []
            for choice in self.choices:
                if QUESTIONARY_AVAILABLE and isinstance(choice, Separator):
                    continue
                selectable_choices.append(choice)
            
            # Create Questionary select widget
            if self.searchable:
                # Use Questionary's autocomplete for searchable select
                self._widget = questionary.autocomplete(
                    message=self.message,
                    choices=[choice.title if hasattr(choice, 'title') else str(choice) for choice in selectable_choices],
                    default=str(self.default) if self.default is not None else None,
                    style=style,
                    **self.kwargs
                )
            else:
                # Use regular select
                self._widget = questionary.select(
                    message=self.message,
                    choices=selectable_choices,
                    default=self.default,
                    style=style,
                    pointer=self.pointer,
                    instruction=self.instruction,
                    **self.kwargs
                )
                
        except Exception as e:
            logging.warning(f"Failed to create Questionary select widget: {e}")
            self._widget = None
    
    def focus(self) -> None:
        """Focus the select widget."""
        if self._widget is None:
            return
        
        if hasattr(self._widget, "focus") and callable(self._widget.focus):
            try:
                self._widget.focus()
            except Exception:
                pass
    
    def _tui_sync(self) -> Any | None:
        """Read the selected value from the wrapped widget and return it."""
        if self._widget is None:
            return self._current_value
        
        try:
            # For Questionary widgets
            if hasattr(self._widget, 'default'):
                return self._widget.default
            
            # Common attribute names
            for attr in ['current_value', 'selected', 'value']:
                if hasattr(self._widget, attr):
                    return getattr(self._widget, attr)
                    
        except Exception:
            pass
        
        return self._current_value
    
    def get_selected(self) -> Any:
        """Get currently selected value."""
        return self._tui_sync()
    
    def set_selected(self, selected: Any) -> None:
        """Set the selected value."""
        self._current_value = selected
        
        # Update underlying widget
        if self._widget is None:
            return
        
        try:
            # For Questionary widgets, update default
            if hasattr(self._widget, 'default'):
                self._widget.default = selected
                return
            
            # Try common attribute names
            for attr in ['current_value', 'selected', 'value']:
                if hasattr(self._widget, attr):
                    setattr(self._widget, attr, selected)
                    return
                    
        except Exception:
            pass
    
    def validate_selection(self, value: Any) -> Tuple[bool, str]:
        """Validate the selected value.
        
        Args:
            value: Value to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if self.validator is None:
            return True, ""
        
        try:
            result = self.validator(value)
            if isinstance(result, bool):
                return result, "" if result else "Invalid selection"
            elif isinstance(result, str):
                return len(result) == 0, result
            else:
                return bool(result), "" if result else "Invalid selection"
        except Exception as e:
            return False, f"Validation error: {e}"
    
    def search_choices(self, query: str) -> List[Union[Choice, Tuple[str, Any]]]:
        """Search choices using fuzzy matching.
        
        Args:
            query: Search query string
            
        Returns:
            List of matching choices
        """
        if not query.strip():
            return self.choices
        
        query_lower = query.lower()
        matches = []
        
        for choice in self.choices:
            if QUESTIONARY_AVAILABLE and isinstance(choice, Separator):
                continue
            
            # Extract title for searching
            if QUESTIONARY_AVAILABLE and hasattr(choice, 'title'):
                title = choice.title
            elif isinstance(choice, tuple):
                title = choice[0]
            else:
                title = str(choice)
            
            # Simple fuzzy matching - contains query or words match
            title_lower = title.lower()
            if (query_lower in title_lower or 
                any(word in title_lower for word in query_lower.split()) or
                self._fuzzy_match(query_lower, title_lower)):
                matches.append(choice)
        
        return matches
    
    def _fuzzy_match(self, query: str, text: str) -> bool:
        """Simple fuzzy matching algorithm."""
        # Check if all characters in query appear in order in text
        query_chars = list(query)
        text_chars = list(text)
        
        q_idx = 0
        for char in text_chars:
            if q_idx < len(query_chars) and char == query_chars[q_idx]:
                q_idx += 1
        
        return q_idx == len(query_chars)
    
    def change_theme(self, theme_name: str):
        """Change the current theme and recreate widget."""
        if not QUESTIONARY_AVAILABLE or not self.style_adapter:
            return
        
        self.current_theme = theme_name
        self.style_adapter.set_theme(theme_name)
        self._create_widget()
        
        # Restore current value
        if self._current_value is not None:
            self.set_selected(self._current_value)
    
    def add_choice(self, choice: Union[str, Tuple[str, Any], Choice, Separator]):
        """Add a new choice to the select list."""
        processed_choice = self._process_choices([choice])[0]
        self.choices.append(processed_choice)
        self._update_choice_mapping()
        self._create_widget()
    
    def add_separator(self, text: str = "---"):
        """Add a visual separator to the choice list."""
        if QUESTIONARY_AVAILABLE:
            separator = Separator(text)
            self.choices.append(separator)
        self._create_widget()
    
    def add_group(self, group_title: str, group_choices: List[Union[str, Tuple[str, Any]]]):
        """Add a group of choices with a separator header."""
        self.add_separator(f"=== {group_title} ===")
        for choice in group_choices:
            self.add_choice(choice)
    
    def remove_choice(self, value: Any):
        """Remove a choice by its value."""
        self.choices = [
            choice for choice in self.choices
            if not (hasattr(choice, 'value') and choice.value == value) and
               not (isinstance(choice, tuple) and choice[1] == value)
        ]
        
        # Clear current selection if it was the removed choice
        if self._current_value == value:
            self._current_value = None
        
        self._update_choice_mapping()
        self._create_widget()
    
    def clear_choices(self):
        """Remove all choices."""
        self.choices = []
        self._current_value = None
        self._choice_mapping = {}
        self._create_widget()
    
    def set_message(self, message: str):
        """Update the prompt message."""
        self.message = message
        self._create_widget()
    
    def set_instruction(self, instruction: str):
        """Update the instruction text."""
        self.instruction = instruction
        self._create_widget()
    
    def enable_search(self):
        """Enable search functionality."""
        self.searchable = True
        self._create_widget()
    
    def disable_search(self):
        """Disable search functionality."""
        self.searchable = False
        self._create_widget()
    
    def enable_validation(self, validator: Callable[[Any], Union[bool, str]]):
        """Enable validation with the given validator function."""
        self.validator = validator
    
    def disable_validation(self):
        """Disable validation."""
        self.validator = None
    
    def get_choice_count(self) -> int:
        """Get the number of available choices (excluding separators)."""
        count = 0
        for choice in self.choices:
            if QUESTIONARY_AVAILABLE and isinstance(choice, Separator):
                continue
            count += 1
        return count
    
    def get_choices(self) -> List[Union[Choice, Separator, Tuple[str, Any]]]:
        """Get all available choices including separators."""
        return self.choices
    
    def get_selectable_choices(self) -> List[Union[Choice, Tuple[str, Any]]]:
        """Get only selectable choices (excluding separators)."""
        return [
            choice for choice in self.choices
            if not (QUESTIONARY_AVAILABLE and isinstance(choice, Separator))
        ]
    
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
            'current_value': self._current_value,
            'theme': self.current_theme,
            'message': self.message,
            'instruction': self.instruction,
            'searchable': self.searchable,
            'show_selected': self.show_selected
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
            if QUESTIONARY_AVAILABLE:
                if isinstance(choice, Separator):
                    continue
                if hasattr(choice, 'value'):
                    result.append((choice.value, choice.title))
            elif isinstance(choice, tuple):
                value, title = choice
                result.append((value, title))
        return result
    
    def __repr__(self) -> str:
        """String representation of the adapter."""
        return f"<EnhancedSelectAdapter message='{self.message}' choices={self.get_choice_count()} searchable={self.searchable}>"


class SelectAdapter(ChoiceWidgetProtocol):
    """Backward-compatible SelectAdapter that automatically uses enhanced features when available.
    
    This class maintains full backward compatibility while providing access to enhanced
    Questionary features when they're available and beneficial.
    """
    
    # runtime contract attributes
    _tui_path: str | None = None
    _tui_focusable: bool = True
    
    def __init__(self, widget: Any | None = None, element: Any | None = None, **kwargs):
        """Initialize SelectAdapter with backward compatibility.
        
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
                    self._enhanced_adapter = EnhancedSelectAdapter(**kwargs)
                    self._widget = self._enhanced_adapter.ptk_widget
                except Exception as e:
                    logging.warning(f"Failed to create enhanced select adapter, falling back to basic: {e}")

    def focus(self) -> None:
        """Focus the select widget."""
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

    def _tui_sync(self) -> Any | None:
        """Read the selected value from the wrapped widget and return it."""
        if self._enhanced_adapter:
            return self._enhanced_adapter._tui_sync()
        
        w = self._widget
        if w is None:
            return None
        try:
            # common attribute names for select widgets
            for attr in ['current_value', 'selected', 'value']:
                if hasattr(w, attr):
                    return getattr(w, attr)
        except Exception:
            pass
        return None

    def get_selected(self) -> Any:
        """Get currently selected value."""
        if self._enhanced_adapter:
            return self._enhanced_adapter.get_selected()
        
        return self._tui_sync()

    def set_selected(self, selected: Any) -> None:
        """Set the selected value."""
        if self._enhanced_adapter:
            self._enhanced_adapter.set_selected(selected)
            return
        
        w = self._widget
        if w is None:
            return
        try:
            for attr in ['current_value', 'selected', 'value']:
                if hasattr(w, attr):
                    setattr(w, attr, selected)
                    return
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
    def validate_selection(self, value: Any) -> Tuple[bool, str]:
        """Validate the selected value (enhanced feature)."""
        if self._enhanced_adapter:
            return self._enhanced_adapter.validate_selection(value)
        return True, ""
    
    def search_choices(self, query: str) -> List[Union[Choice, Tuple[str, Any]]]:
        """Search choices (enhanced feature)."""
        if self._enhanced_adapter:
            return self._enhanced_adapter.search_choices(query)
        return []
    
    def change_theme(self, theme_name: str):
        """Change the current theme (enhanced feature)."""
        if self._enhanced_adapter:
            self._enhanced_adapter.change_theme(theme_name)
    
    def add_choice(self, choice: Union[str, Tuple[str, Any]]):
        """Add a new choice (enhanced feature)."""
        if self._enhanced_adapter:
            self._enhanced_adapter.add_choice(choice)
    
    def add_separator(self, text: str = "---"):
        """Add a separator (enhanced feature)."""
        if self._enhanced_adapter:
            self._enhanced_adapter.add_separator(text)
    
    def add_group(self, group_title: str, group_choices: List[Union[str, Tuple[str, Any]]]):
        """Add a group of choices (enhanced feature)."""
        if self._enhanced_adapter:
            self._enhanced_adapter.add_group(group_title, group_choices)
    
    def remove_choice(self, value: Any):
        """Remove a choice by value (enhanced feature)."""
        if self._enhanced_adapter:
            self._enhanced_adapter.remove_choice(value)
    
    def clear_choices(self):
        """Clear all choices (enhanced feature)."""
        if self._enhanced_adapter:
            self._enhanced_adapter.clear_choices()
    
    def set_message(self, message: str):
        """Update the prompt message (enhanced feature)."""
        if self._enhanced_adapter:
            self._enhanced_adapter.set_message(message)
    
    def enable_search(self):
        """Enable search functionality (enhanced feature)."""
        if self._enhanced_adapter:
            self._enhanced_adapter.enable_search()
    
    def disable_search(self):
        """Disable search functionality (enhanced feature)."""
        if self._enhanced_adapter:
            self._enhanced_adapter.disable_search()
    
    def enable_validation(self, validator: Callable[[Any], Union[bool, str]]):
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
            'current_value': self._tui_sync(),
            'theme': 'default',
            'searchable': False,
            'legacy_mode': self._legacy_mode
        }

    def __repr__(self) -> str:  # pragma: no cover - trivial
        """String representation of the adapter."""
        if self._enhanced_adapter:
            return repr(self._enhanced_adapter)
        return f"<SelectAdapter widget={self._widget!r}>"


# Convenience function for creating enhanced select widgets
def create_select(
    choices: List[Union[str, Tuple[str, Any]]],
    message: str = "Select an option:",
    style: str = 'professional_blue',
    searchable: bool = False,
    **kwargs
) -> SelectAdapter:
    """Create a SelectAdapter with enhanced features.
    
    Args:
        choices: List of choices (strings or (title, value) tuples)
        message: Question/prompt message
        style: Theme name for styling
        searchable: Enable search functionality
        **kwargs: Additional arguments for EnhancedSelectAdapter
        
    Returns:
        SelectAdapter with enhanced features when available
    """
    return SelectAdapter(
        choices=choices,
        message=message,
        style=style,
        searchable=searchable,
        **kwargs
    )