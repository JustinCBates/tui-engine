"""Enhanced Text input wrapper implementing ValueWidgetProtocol.

This adapter wraps either a real prompt-toolkit TextArea-like object or a
Questionary-enhanced text input with professional styling and validation support.
It provides the minimal contract expected by the PTKAdapter while offering
enhanced user experience through Questionary integration.
"""
from __future__ import annotations

from typing import Any, Optional, Callable, Union
import questionary
from questionary import Style

from .protocols import ValueWidgetProtocol

try:
    from prompt_toolkit.widgets import TextArea  # type: ignore
    _PTK_AVAILABLE = True
except Exception:
    TextArea = None  # type: ignore
    _PTK_AVAILABLE = False

# Import TUI Engine styling
try:
    from ..questionary_adapter import QuestionaryStyleAdapter
    from ..themes import TUIEngineThemes
    _QUESTIONARY_INTEGRATION_AVAILABLE = True
except ImportError:
    QuestionaryStyleAdapter = None
    TUIEngineThemes = None
    _QUESTIONARY_INTEGRATION_AVAILABLE = False


class EnhancedTextInputAdapter(ValueWidgetProtocol):
    """
    Enhanced text input adapter with Questionary integration.
    
    Provides professional styling, validation support, and enhanced user experience
    while maintaining full backward compatibility with existing TUI Engine interface.
    """
    
    # runtime contract attributes required by TuiWidgetProtocol
    _tui_path: str | None = None
    _tui_focusable: bool = True

    def __init__(
        self,
        widget: Any | None = None,
        message: str = "Enter text:",
        style: Optional[Union[str, Style]] = None,
        validator: Optional[Callable[[str], Union[bool, str]]] = None,
        placeholder: str = "",
        multiline: bool = False,
        password: bool = False,
        default: str = "",
        use_questionary: bool = True
    ) -> None:
        """
        Initialize enhanced text input adapter.
        
        Args:
            widget: Existing widget to wrap (for backward compatibility)
            message: Prompt message to display
            style: Theme name or Style object (defaults to professional_blue)
            validator: Validation function (return True if valid, error string if invalid)
            placeholder: Placeholder text
            multiline: Enable multiline input
            password: Enable password mode (hidden input)
            default: Default value
            use_questionary: Whether to use Questionary enhancement (True by default)
        """
        self.message = message
        self.placeholder = placeholder
        self.multiline = multiline
        self.password = password
        self.default = default
        self.use_questionary = use_questionary and _QUESTIONARY_INTEGRATION_AVAILABLE
        self.validator = validator
        self._current_value = default
        self._last_synced = default
        
        # Setup styling
        self._setup_styling(style)
        
        # Initialize widget
        if widget is not None:
            # Use provided widget (backward compatibility)
            self._widget = widget
            self._questionary_widget = None
            self.use_questionary = False
        elif self.use_questionary:
            # Create Questionary-enhanced widget
            self._widget = self._create_questionary_widget()
            self._questionary_widget = self._widget
        else:
            # Fall back to basic widget
            self._widget = self._create_fallback_widget()
            self._questionary_widget = None

    def _setup_styling(self, style: Optional[Union[str, Style]]) -> None:
        """Setup styling with Questionary integration."""
        if not _QUESTIONARY_INTEGRATION_AVAILABLE:
            self.style_adapter = None
            self.style = None
            return
            
        # Create style adapter
        if style is None:
            self.style_adapter = QuestionaryStyleAdapter('professional_blue')
        elif isinstance(style, str):
            self.style_adapter = QuestionaryStyleAdapter(style)
        elif isinstance(style, Style):
            self.style_adapter = QuestionaryStyleAdapter()
            self.style_adapter.set_theme(style)
        else:
            self.style_adapter = QuestionaryStyleAdapter('professional_blue')
        
        # Get input-specific style
        self.style = self.style_adapter.create_component_style('input')

    def _create_questionary_widget(self) -> Any:
        """Create Questionary-enhanced text input widget."""
        try:
            if self.password:
                # Create password input
                widget = questionary.password(
                    message=self.message,
                    style=self.style,
                    validate=self._wrap_validator(),
                    default=self.default
                )
            else:
                # Create text input
                widget = questionary.text(
                    message=self.message,
                    style=self.style,
                    validate=self._wrap_validator(),
                    default=self.default,
                    multiline=self.multiline
                )
            
            # Extract the prompt-toolkit widget from Questionary
            if hasattr(widget, '_get_prompt_session'):
                session = widget._get_prompt_session()
                if hasattr(session, 'layout') and hasattr(session.layout, 'container'):
                    return session.layout.container
            
            # Fall back to the questionary object itself
            return widget
            
        except Exception:
            # Fall back to basic widget if Questionary creation fails
            return self._create_fallback_widget()

    def _create_fallback_widget(self) -> Any:
        """Create basic fallback widget."""
        if _PTK_AVAILABLE and TextArea is not None:
            return TextArea(
                text=self.default,
                multiline=self.multiline,
                password=self.password,
                placeholder=self.placeholder
            )
        else:
            # Create minimal fallback
            return self._create_minimal_fallback()

    def _create_minimal_fallback(self) -> Any:
        """Create minimal fallback for testing environments."""
        class _EnhancedFallback:
            def __init__(self, text: str = "") -> None:
                self.text = text
                self.value = text
                
                # Buffer for compatibility
                class _Buf:
                    def __init__(self, text: str = ""):
                        self.text = text
                
                self.buffer = _Buf(text)

            def focus(self) -> None:
                return None

            def __repr__(self) -> str:
                return f"<_EnhancedFallback text={self.text!r}>"

        return _EnhancedFallback(self.default)

    def _wrap_validator(self) -> Optional[Callable]:
        """Wrap TUI Engine validator for Questionary compatibility."""
        if not self.validator:
            return None
            
        def questionary_validator(text: str) -> bool:
            try:
                result = self.validator(text)
                if isinstance(result, bool):
                    return result
                elif isinstance(result, str):
                    # Questionary expects True for valid, False for invalid
                    # We'll handle error messages differently
                    return len(result) == 0  # Empty string means valid
                else:
                    return bool(result)
            except Exception:
                return False
        
        return questionary_validator

    def validate_input(self, text: str) -> tuple[bool, str]:
        """
        Validate input and return status with error message.
        
        Args:
            text: Text to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not self.validator:
            return True, ""
        
        try:
            result = self.validator(text)
            if isinstance(result, bool):
                return result, "" if result else "Invalid input"
            elif isinstance(result, str):
                return len(result) == 0, result
            else:
                return bool(result), "" if bool(result) else "Invalid input"
        except Exception as e:
            return False, f"Validation error: {e}"

    def focus(self) -> None:
        """Focus the input widget."""
        w = self._widget
        if w is None:
            return
        if hasattr(w, "focus") and callable(w.focus):
            try:
                w.focus()
            except Exception:
                return

    def _tui_sync(self) -> None:
        """Sync current widget value."""
        self._last_synced = self.get_value() or ""

    def get_value(self) -> str:
        """Get current input value."""
        w = self._widget
        if w is None:
            return self._current_value

        # Try multiple value access patterns
        for attr in ['text', 'value']:
            if hasattr(w, attr):
                val = getattr(w, attr)
                if val is not None:
                    self._current_value = str(val)
                    return self._current_value

        # Try buffer.text
        if hasattr(w, "buffer") and hasattr(w.buffer, "text"):
            val = w.buffer.text
            if val is not None:
                self._current_value = str(val)
                return self._current_value

        # Fall back to stored value
        return self._current_value

    def set_value(self, value: str) -> None:
        """Set input value."""
        self._current_value = value
        w = self._widget
        if w is None:
            return

        # Try setting value through multiple patterns
        for attr in ['text', 'value']:
            if hasattr(w, attr):
                try:
                    setattr(w, attr, value)
                    return
                except Exception:
                    continue

        # Try buffer.text
        if hasattr(w, "buffer") and hasattr(w.buffer, "text"):
            try:
                w.buffer.text = value
                return
            except Exception:
                pass

    def set_placeholder(self, placeholder: str) -> None:
        """Set placeholder text."""
        self.placeholder = placeholder
        # Note: Changing placeholder on existing widget may require recreation

    def set_message(self, message: str) -> None:
        """Set prompt message."""
        self.message = message
        # Note: Changing message on existing widget may require recreation

    def enable_validation(self, validator: Callable[[str], Union[bool, str]]) -> None:
        """Enable or update validation."""
        self.validator = validator

    def disable_validation(self) -> None:
        """Disable validation."""
        self.validator = None

    def get_style_adapter(self) -> Optional['QuestionaryStyleAdapter']:
        """Get the style adapter for advanced styling."""
        return self.style_adapter

    def change_theme(self, theme: Union[str, Style]) -> None:
        """
        Change the input theme.
        
        Note: This requires widget recreation to take effect.
        """
        if self.style_adapter:
            if isinstance(theme, str):
                self.style_adapter.set_theme(theme)
            else:
                self.style_adapter.set_theme(theme)
            self.style = self.style_adapter.create_component_style('input')

    def is_questionary_enhanced(self) -> bool:
        """Check if this adapter is using Questionary enhancement."""
        return self.use_questionary and self._questionary_widget is not None

    def get_widget_info(self) -> dict:
        """Get information about the current widget setup."""
        return {
            'use_questionary': self.use_questionary,
            'has_questionary_widget': self._questionary_widget is not None,
            'has_validator': self.validator is not None,
            'multiline': self.multiline,
            'password': self.password,
            'theme': self.style_adapter.get_theme_name() if self.style_adapter else None,
            'current_value': self._current_value,
            'message': self.message,
            'placeholder': self.placeholder
        }

    def __repr__(self) -> str:
        """String representation of the adapter."""
        enhanced = "Enhanced" if self.use_questionary else "Basic"
        return f"<{enhanced}TextInputAdapter message={self.message!r} value={self._current_value!r}>"

    @property
    def ptk_widget(self) -> Any:
        """Return the underlying prompt-toolkit widget.

        PTKAdapter expects a `.ptk_widget` or a raw widget so it can mount
        and focus the real UI control. Exposing this keeps adapters thin.
        """
        return self._widget


# Maintain backward compatibility
class TextInputAdapter(EnhancedTextInputAdapter):
    """
    Backward compatible TextInputAdapter.
    
    Provides the same interface as the original TextInputAdapter while
    offering optional Questionary enhancement.
    """
    
    def __init__(self, widget: Any | None = None) -> None:
        """
        Initialize with backward compatibility.
        
        Args:
            widget: The real widget to wrap (for backward compatibility)
        """
        if widget is None:
            # Use enhanced version with minimal setup
            super().__init__(
                widget=None,
                message="Enter text:",
                use_questionary=_QUESTIONARY_INTEGRATION_AVAILABLE
            )
        else:
            # Use provided widget (original behavior)
            super().__init__(
                widget=widget,
                use_questionary=False
            )
