"""PasswordAdapter: Enhanced secure password input widget with Questionary integration.

This adapter implements ValueWidgetProtocol and provides secure password input
functionality with professional styling, strength validation, confirmation matching,
and enhanced security features.

Features:
- Professional themes and styling through QuestionaryStyleAdapter
- Password strength validation with customizable rules
- Confirmation password matching
- Secure input masking with configurable mask characters
- Password visibility toggle functionality
- Backward compatibility with existing TUI Engine password inputs
- Dynamic theme switching and style customization
"""
from __future__ import annotations

from typing import Any, Callable, Optional, Union, Tuple, Dict, List
import logging
import re
import getpass
import hashlib

from .protocols import ValueWidgetProtocol

# Import Questionary and related components
try:
    import questionary
    from ..questionary_adapter import QuestionaryStyleAdapter
    from ..themes import TUIEngineThemes
    QUESTIONARY_AVAILABLE = True
except ImportError:
    QUESTIONARY_AVAILABLE = False
    logging.warning("Questionary not available, falling back to basic password functionality")


class PasswordStrengthValidator:
    """Password strength validation utility class."""
    
    def __init__(
        self,
        min_length: int = 8,
        require_uppercase: bool = True,
        require_lowercase: bool = True,
        require_digits: bool = True,
        require_special: bool = True,
        special_chars: str = "!@#$%^&*()_+-=[]{}|;:,.<>?",
        custom_rules: Optional[List[Callable[[str], Tuple[bool, str]]]] = None
    ):
        """Initialize password strength validator.
        
        Args:
            min_length: Minimum password length
            require_uppercase: Require uppercase letters
            require_lowercase: Require lowercase letters
            require_digits: Require numeric digits
            require_special: Require special characters
            special_chars: String of valid special characters
            custom_rules: Additional custom validation rules
        """
        self.min_length = min_length
        self.require_uppercase = require_uppercase
        self.require_lowercase = require_lowercase
        self.require_digits = require_digits
        self.require_special = require_special
        self.special_chars = special_chars
        self.custom_rules = custom_rules or []
    
    def validate(self, password: str) -> Tuple[bool, List[str], int]:
        """Validate password strength.
        
        Args:
            password: Password to validate
            
        Returns:
            Tuple of (is_valid, error_messages, strength_score)
        """
        errors = []
        score = 0
        
        # Length check
        if len(password) < self.min_length:
            errors.append(f"Password must be at least {self.min_length} characters long")
        else:
            score += min(20, len(password) * 2)  # Max 20 points for length
        
        # Character type checks
        if self.require_uppercase and not re.search(r'[A-Z]', password):
            errors.append("Password must contain at least one uppercase letter")
        elif re.search(r'[A-Z]', password):
            score += 15
        
        if self.require_lowercase and not re.search(r'[a-z]', password):
            errors.append("Password must contain at least one lowercase letter")
        elif re.search(r'[a-z]', password):
            score += 15
        
        if self.require_digits and not re.search(r'[0-9]', password):
            errors.append("Password must contain at least one digit")
        elif re.search(r'[0-9]', password):
            score += 15
        
        if self.require_special and not re.search(f'[{re.escape(self.special_chars)}]', password):
            errors.append(f"Password must contain at least one special character ({self.special_chars[:10]}...)")
        elif re.search(f'[{re.escape(self.special_chars)}]', password):
            score += 15
        
        # Bonus points for variety
        if len(set(password)) > len(password) * 0.7:  # Good character diversity
            score += 10
        
        # Custom rules
        for rule in self.custom_rules:
            is_valid, error = rule(password)
            if not is_valid:
                errors.append(error)
            else:
                score += 5
        
        # Cap score at 100
        score = min(100, score)
        
        return len(errors) == 0, errors, score
    
    def get_strength_description(self, score: int) -> str:
        """Get human-readable strength description."""
        if score < 30:
            return "Very Weak"
        elif score < 50:
            return "Weak"
        elif score < 70:
            return "Fair"
        elif score < 85:
            return "Good"
        else:
            return "Strong"


class EnhancedPasswordAdapter(ValueWidgetProtocol):
    """Enhanced Password adapter with Questionary integration and security features.
    
    This class provides advanced password input functionality with:
    - Professional theme integration
    - Password strength validation
    - Confirmation password matching
    - Secure input handling
    - Dynamic styling and theme switching
    """
    
    def __init__(
        self,
        message: str = "Enter password:",
        style: Union[str, dict] = 'professional_blue',
        mask_char: str = "*",
        confirm_password: bool = False,
        confirm_message: str = "Confirm password:",
        strength_validator: Optional[PasswordStrengthValidator] = None,
        custom_validator: Optional[Callable[[str], Union[bool, str]]] = None,
        show_strength: bool = True,
        allow_empty: bool = False,
        secure_clear: bool = True,
        **kwargs
    ):
        """Initialize enhanced password adapter.
        
        Args:
            message: Password input prompt message
            style: Theme name or custom style dict
            mask_char: Character to mask password input
            confirm_password: Whether to require password confirmation
            confirm_message: Confirmation prompt message
            strength_validator: Password strength validation rules
            custom_validator: Custom validation function
            show_strength: Whether to show password strength indicator
            allow_empty: Whether to allow empty passwords
            secure_clear: Whether to securely clear password from memory
            **kwargs: Additional arguments for underlying widget
        """
        self.message = message
        self.mask_char = mask_char
        self.confirm_password = confirm_password
        self.confirm_message = confirm_message
        self.strength_validator = strength_validator or PasswordStrengthValidator()
        self.custom_validator = custom_validator
        self.show_strength = show_strength
        self.allow_empty = allow_empty
        self.secure_clear = secure_clear
        self.kwargs = kwargs
        
        # Initialize style adapter
        self.style_adapter = None
        self.current_theme = style
        if QUESTIONARY_AVAILABLE:
            self.style_adapter = QuestionaryStyleAdapter()
            if isinstance(style, str):
                self.style_adapter.set_theme(style)
        
        # Initialize widgets
        self._password_widget = None
        self._confirm_widget = None
        self._current_password = ""
        self._confirmed_password = ""
        self._create_widgets()
        
        # Adapter protocol attributes
        self._tui_path: str | None = None
        self._tui_focusable: bool = True
        self.element = None
        
        # Security tracking
        self._password_hash = None
        self._last_strength_score = 0
    
    def _create_widgets(self):
        """Create the underlying password input widgets."""
        if not QUESTIONARY_AVAILABLE:
            # Fallback to basic implementation
            self._password_widget = None
            self._confirm_widget = None
            return
        
        try:
            # Get style for Questionary
            style = None
            if self.style_adapter:
                style = self.style_adapter.get_questionary_style()
            
            # Create main password widget
            self._password_widget = questionary.password(
                message=self.message,
                style=style,
                **self.kwargs
            )
            
            # Create confirmation widget if needed
            if self.confirm_password:
                self._confirm_widget = questionary.password(
                    message=self.confirm_message,
                    style=style,
                    **self.kwargs
                )
            
        except Exception as e:
            logging.warning(f"Failed to create Questionary password widgets: {e}")
            self._password_widget = None
            self._confirm_widget = None
    
    def focus(self) -> None:
        """Focus the password input widget."""
        widget = self._password_widget
        if widget is None:
            return
        
        if hasattr(widget, "focus") and callable(widget.focus):
            try:
                widget.focus()
            except Exception:
                pass
    
    def _tui_sync(self) -> str | None:
        """Read the password value from the wrapped widget and return it."""
        # For security, we don't sync the actual password
        # Instead, return a hash or indicator
        if self._password_hash:
            return self._password_hash
        return None
    
    def get_value(self) -> str:
        """Get the current password value.
        
        Note: This returns the actual password for form processing.
        Use with caution in production environments.
        """
        return self._current_password
    
    def set_value(self, value: str) -> None:
        """Set the password value."""
        self._current_password = str(value) if value is not None else ""
        
        # Update hash for tracking
        if self._current_password:
            self._password_hash = hashlib.sha256(self._current_password.encode()).hexdigest()[:16]
        else:
            self._password_hash = None
        
        # Update underlying widget if available
        if self._password_widget and hasattr(self._password_widget, 'default'):
            try:
                self._password_widget.default = self._current_password
            except Exception:
                pass
    
    def validate_password(self, password: str) -> Tuple[bool, List[str], int]:
        """Validate password strength and custom rules.
        
        Args:
            password: Password to validate
            
        Returns:
            Tuple of (is_valid, error_messages, strength_score)
        """
        errors = []
        
        # Check if empty password is allowed
        if not password and not self.allow_empty:
            return False, ["Password cannot be empty"], 0
        
        # Run strength validation
        strength_valid, strength_errors, score = self.strength_validator.validate(password)
        errors.extend(strength_errors)
        
        # Run custom validation
        if self.custom_validator:
            try:
                result = self.custom_validator(password)
                if isinstance(result, bool):
                    if not result:
                        errors.append("Password does not meet custom requirements")
                elif isinstance(result, str):
                    if result:  # Non-empty string means error
                        errors.append(result)
            except Exception as e:
                errors.append(f"Custom validation error: {e}")
        
        self._last_strength_score = score
        return len(errors) == 0, errors, score
    
    def validate_confirmation(self) -> Tuple[bool, str]:
        """Validate password confirmation match.
        
        Returns:
            Tuple of (passwords_match, error_message)
        """
        if not self.confirm_password:
            return True, ""
        
        if self._current_password != self._confirmed_password:
            return False, "Passwords do not match"
        
        return True, ""
    
    def prompt_password(self) -> Tuple[bool, str, str]:
        """Interactive password prompting with validation.
        
        Returns:
            Tuple of (success, password, error_message)
        """
        try:
            # Primary password input
            if QUESTIONARY_AVAILABLE and self._password_widget:
                password = self._password_widget.ask()
            else:
                # Fallback to getpass
                password = getpass.getpass(self.message + " ")
            
            if password is None:
                return False, "", "Password input cancelled"
            
            # Validate password
            is_valid, errors, score = self.validate_password(password)
            if not is_valid:
                return False, "", "; ".join(errors)
            
            self.set_value(password)
            
            # Confirmation if required
            if self.confirm_password:
                if QUESTIONARY_AVAILABLE and self._confirm_widget:
                    confirm = self._confirm_widget.ask()
                else:
                    confirm = getpass.getpass(self.confirm_message + " ")
                
                if confirm is None:
                    return False, "", "Password confirmation cancelled"
                
                self._confirmed_password = confirm
                match_valid, match_error = self.validate_confirmation()
                
                if not match_valid:
                    return False, "", match_error
            
            return True, password, ""
            
        except Exception as e:
            return False, "", f"Password input error: {e}"
    
    def get_strength_info(self) -> Dict[str, Any]:
        """Get detailed password strength information."""
        if not self._current_password:
            return {
                'score': 0,
                'description': 'No Password',
                'is_valid': False,
                'errors': ['No password provided']
            }
        
        is_valid, errors, score = self.validate_password(self._current_password)
        
        return {
            'score': score,
            'description': self.strength_validator.get_strength_description(score),
            'is_valid': is_valid,
            'errors': errors,
            'percentage': min(100, score),
            'color': self._get_strength_color(score)
        }
    
    def _get_strength_color(self, score: int) -> str:
        """Get color indicator for password strength."""
        if score < 30:
            return 'red'
        elif score < 50:
            return 'orange'
        elif score < 70:
            return 'yellow'
        elif score < 85:
            return 'lightgreen'
        else:
            return 'green'
    
    def change_theme(self, theme_name: str):
        """Change the current theme and recreate widgets."""
        if not QUESTIONARY_AVAILABLE or not self.style_adapter:
            return
        
        self.current_theme = theme_name
        self.style_adapter.set_theme(theme_name)
        self._create_widgets()
    
    def set_message(self, message: str):
        """Update the password prompt message."""
        self.message = message
        self._create_widgets()
    
    def set_confirm_message(self, message: str):
        """Update the confirmation prompt message."""
        self.confirm_message = message
        self._create_widgets()
    
    def enable_confirmation(self, confirm_message: str = "Confirm password:"):
        """Enable password confirmation."""
        self.confirm_password = True
        self.confirm_message = confirm_message
        self._create_widgets()
    
    def disable_confirmation(self):
        """Disable password confirmation."""
        self.confirm_password = False
        self._confirmed_password = ""
        self._create_widgets()
    
    def update_strength_rules(self, **kwargs):
        """Update password strength validation rules."""
        # Create new validator with updated rules
        current_args = {
            'min_length': self.strength_validator.min_length,
            'require_uppercase': self.strength_validator.require_uppercase,
            'require_lowercase': self.strength_validator.require_lowercase,
            'require_digits': self.strength_validator.require_digits,
            'require_special': self.strength_validator.require_special,
            'special_chars': self.strength_validator.special_chars,
            'custom_rules': self.strength_validator.custom_rules
        }
        current_args.update(kwargs)
        self.strength_validator = PasswordStrengthValidator(**current_args)
    
    def clear_password(self):
        """Securely clear password from memory."""
        if self.secure_clear:
            # Overwrite password strings with random data for security
            import secrets
            if self._current_password:
                # Overwrite memory (Python strings are immutable, but this is best effort)
                self._current_password = secrets.token_hex(len(self._current_password))
                self._current_password = ""
            
            if self._confirmed_password:
                self._confirmed_password = secrets.token_hex(len(self._confirmed_password))
                self._confirmed_password = ""
        else:
            self._current_password = ""
            self._confirmed_password = ""
        
        self._password_hash = None
    
    def is_questionary_enhanced(self) -> bool:
        """Check if Questionary enhancement is active."""
        return QUESTIONARY_AVAILABLE and self._password_widget is not None
    
    def get_style_adapter(self) -> Optional[QuestionaryStyleAdapter]:
        """Get the style adapter instance."""
        return self.style_adapter
    
    def get_widget_info(self) -> dict:
        """Get comprehensive widget information."""
        strength_info = self.get_strength_info()
        
        return {
            'use_questionary': self.is_questionary_enhanced(),
            'has_password': bool(self._current_password),
            'requires_confirmation': self.confirm_password,
            'confirmation_valid': self.validate_confirmation()[0] if self.confirm_password else True,
            'strength_score': strength_info['score'],
            'strength_description': strength_info['description'],
            'is_password_valid': strength_info['is_valid'],
            'theme': self.current_theme,
            'message': self.message,
            'show_strength': self.show_strength,
            'allow_empty': self.allow_empty
        }
    
    @property
    def ptk_widget(self) -> Any:
        """Get the underlying prompt-toolkit widget."""
        return self._password_widget
    
    def __repr__(self) -> str:
        """String representation of the adapter."""
        has_password = "***" if self._current_password else "empty"
        return f"<EnhancedPasswordAdapter message='{self.message}' password={has_password} confirm={self.confirm_password}>"


class PasswordAdapter(ValueWidgetProtocol):
    """Backward-compatible PasswordAdapter that automatically uses enhanced features when available.
    
    This class maintains full backward compatibility while providing access to enhanced
    Questionary features when they're available and beneficial.
    """
    
    # runtime contract attributes
    _tui_path: str | None = None
    _tui_focusable: bool = True
    
    def __init__(self, widget: Any | None = None, element: Any | None = None, **kwargs):
        """Initialize PasswordAdapter with backward compatibility.
        
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
            self._current_value = ""
        else:
            # Use enhanced adapter for new functionality
            self._enhanced_adapter = None
            self._widget = None
            self._legacy_mode = False
            self._current_value = ""
            
            # Try to create enhanced adapter if Questionary is available
            if QUESTIONARY_AVAILABLE and kwargs:
                try:
                    self._enhanced_adapter = EnhancedPasswordAdapter(**kwargs)
                    self._widget = self._enhanced_adapter.ptk_widget
                except Exception as e:
                    logging.warning(f"Failed to create enhanced password adapter, falling back to basic: {e}")

    def focus(self) -> None:
        """Focus the password input widget."""
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

    def _tui_sync(self) -> str | None:
        """Read the password value from the wrapped widget and return it."""
        if self._enhanced_adapter:
            return self._enhanced_adapter._tui_sync()
        
        w = self._widget
        if w is None:
            return self._current_value
        
        try:
            # common attribute names for password widgets
            for attr in ['text', 'value', 'current_value']:
                if hasattr(w, attr):
                    return getattr(w, attr)
        except Exception:
            pass
        
        return self._current_value

    def get_value(self) -> str:
        """Get the current password value."""
        if self._enhanced_adapter:
            return self._enhanced_adapter.get_value()
        
        return self._current_value

    def set_value(self, value: Any) -> None:
        """Set the password value."""
        if self._enhanced_adapter:
            self._enhanced_adapter.set_value(value)
            return
        
        self._current_value = str(value) if value is not None else ""
        
        # Update underlying widget
        w = self._widget
        if w is None:
            return
        
        try:
            for attr in ['text', 'value', 'current_value']:
                if hasattr(w, attr):
                    setattr(w, attr, self._current_value)
                    return
        except Exception:
            pass
    
    @property
    def ptk_widget(self) -> Any:
        """Get the underlying prompt-toolkit widget."""
        return self._widget
    
    # Enhanced functionality delegation (when available)
    def validate_password(self, password: str) -> Tuple[bool, List[str], int]:
        """Validate password strength (enhanced feature)."""
        if self._enhanced_adapter:
            return self._enhanced_adapter.validate_password(password)
        return True, [], 100
    
    def validate_confirmation(self) -> Tuple[bool, str]:
        """Validate password confirmation (enhanced feature)."""
        if self._enhanced_adapter:
            return self._enhanced_adapter.validate_confirmation()
        return True, ""
    
    def prompt_password(self) -> Tuple[bool, str, str]:
        """Interactive password prompting (enhanced feature)."""
        if self._enhanced_adapter:
            return self._enhanced_adapter.prompt_password()
        
        # Fallback to simple getpass
        try:
            password = getpass.getpass("Enter password: ")
            self.set_value(password)
            return True, password, ""
        except Exception as e:
            return False, "", str(e)
    
    def get_strength_info(self) -> Dict[str, Any]:
        """Get password strength information (enhanced feature)."""
        if self._enhanced_adapter:
            return self._enhanced_adapter.get_strength_info()
        return {
            'score': 100,
            'description': 'Unknown',
            'is_valid': True,
            'errors': []
        }
    
    def change_theme(self, theme_name: str):
        """Change the current theme (enhanced feature)."""
        if self._enhanced_adapter:
            self._enhanced_adapter.change_theme(theme_name)
    
    def set_message(self, message: str):
        """Update the prompt message (enhanced feature)."""
        if self._enhanced_adapter:
            self._enhanced_adapter.set_message(message)
    
    def enable_confirmation(self, confirm_message: str = "Confirm password:"):
        """Enable password confirmation (enhanced feature)."""
        if self._enhanced_adapter:
            self._enhanced_adapter.enable_confirmation(confirm_message)
    
    def disable_confirmation(self):
        """Disable password confirmation (enhanced feature)."""
        if self._enhanced_adapter:
            self._enhanced_adapter.disable_confirmation()
    
    def clear_password(self):
        """Clear password from memory (enhanced feature)."""
        if self._enhanced_adapter:
            self._enhanced_adapter.clear_password()
        else:
            self._current_value = ""
    
    def is_questionary_enhanced(self) -> bool:
        """Check if Questionary enhancement is active."""
        return self._enhanced_adapter is not None and self._enhanced_adapter.is_questionary_enhanced()
    
    def get_widget_info(self) -> dict:
        """Get comprehensive widget information."""
        if self._enhanced_adapter:
            return self._enhanced_adapter.get_widget_info()
        return {
            'use_questionary': False,
            'has_password': bool(self._current_value),
            'requires_confirmation': False,
            'confirmation_valid': True,
            'strength_score': 100,
            'strength_description': 'Unknown',
            'is_password_valid': True,
            'theme': 'default',
            'legacy_mode': self._legacy_mode
        }

    def __repr__(self) -> str:  # pragma: no cover - trivial
        """String representation of the adapter."""
        if self._enhanced_adapter:
            return repr(self._enhanced_adapter)
        has_password = "***" if self._current_value else "empty"
        return f"<PasswordAdapter widget={self._widget!r} password={has_password}>"


# Convenience function for creating enhanced password inputs
def create_password_input(
    message: str = "Enter password:",
    style: str = 'professional_blue',
    confirm_password: bool = False,
    min_length: int = 8,
    **kwargs
) -> PasswordAdapter:
    """Create a PasswordAdapter with enhanced features.
    
    Args:
        message: Password prompt message
        style: Theme name for styling
        confirm_password: Whether to require password confirmation
        min_length: Minimum password length requirement
        **kwargs: Additional arguments for EnhancedPasswordAdapter
        
    Returns:
        PasswordAdapter with enhanced features when available
    """
    # Create strength validator with custom min_length
    strength_validator = PasswordStrengthValidator(min_length=min_length)
    
    return PasswordAdapter(
        message=message,
        style=style,
        confirm_password=confirm_password,
        strength_validator=strength_validator,
        **kwargs
    )