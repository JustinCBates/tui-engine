"""Enhanced Number Input Adapter for TUI Engine with Questionary Integration.

This module provides a sophisticated number input widget that supports various numeric
formats (integers, floats, currency, percentages), validation, range constraints,
and professional styling integration.

Key Features:
- Multiple numeric formats (int, float, currency, percentage, scientific)
- Range validation and constraints (min/max values)
- Precision control and decimal places
- Input formatting and display formatting
- Professional styling with TUI Engine themes
- Increment/decrement controls
- Currency symbol and locale support
- Validation with custom rules
- Backward compatibility with legacy widgets

Author: TUI Engine Team
License: MIT
"""

import re
import locale
from typing import Any, Optional, Union, Callable, Dict, List, Tuple
from decimal import Decimal, ROUND_HALF_UP, InvalidOperation
from dataclasses import dataclass

try:
    import questionary
    from prompt_toolkit.shortcuts import prompt
    from prompt_toolkit.validation import Validator, ValidationError
    from prompt_toolkit.formatted_text import HTML
    QUESTIONARY_AVAILABLE = True
except ImportError:
    QUESTIONARY_AVAILABLE = False


@dataclass
class NumberFormat:
    """Configuration for number formatting and display."""
    
    # Format type
    format_type: str = 'float'  # 'int', 'float', 'currency', 'percentage', 'scientific'
    
    # Precision and rounding
    decimal_places: Optional[int] = 2
    round_mode: str = ROUND_HALF_UP
    
    # Display formatting
    thousands_separator: bool = True
    decimal_separator: str = '.'
    currency_symbol: str = '$'
    currency_position: str = 'prefix'  # 'prefix' or 'suffix'
    percentage_symbol: str = '%'
    
    # Scientific notation
    scientific_precision: int = 2
    
    # Validation
    allow_negative: bool = True
    allow_zero: bool = True
    
    # Locale support
    use_locale: bool = False


class NumberValidator(Validator):
    """Validator for numeric input with comprehensive validation rules."""
    
    def __init__(self, 
                 format_config: NumberFormat,
                 min_value: Optional[Union[int, float, Decimal]] = None,
                 max_value: Optional[Union[int, float, Decimal]] = None,
                 custom_validator: Optional[Callable] = None):
        """Initialize number validator.
        
        Args:
            format_config: Number formatting configuration
            min_value: Minimum allowed value
            max_value: Maximum allowed value 
            custom_validator: Custom validation function
        """
        self.format_config = format_config
        self.min_value = min_value
        self.max_value = max_value
        self.custom_validator = custom_validator
    
    def validate(self, document):
        """Validate the numeric input."""
        text = document.text.strip()
        
        if not text:
            if self.format_config.allow_zero:
                return  # Empty is valid if zero is allowed
            else:
                raise ValidationError(message="Number is required")
        
        try:
            # Parse the number based on format type
            parsed_number = self._parse_number(text)
            
            # Validate range constraints
            if self.min_value is not None and parsed_number < self.min_value:
                raise ValidationError(message=f"Value must be at least {self.min_value}")
            
            if self.max_value is not None and parsed_number > self.max_value:
                raise ValidationError(message=f"Value must be at most {self.max_value}")
            
            # Validate sign constraints
            if not self.format_config.allow_negative and parsed_number < 0:
                raise ValidationError(message="Negative values are not allowed")
            
            if not self.format_config.allow_zero and parsed_number == 0:
                raise ValidationError(message="Zero is not allowed")
            
            # Custom validation
            if self.custom_validator:
                validation_result = self.custom_validator(parsed_number)
                if validation_result is not True:
                    error_msg = validation_result if isinstance(validation_result, str) else "Invalid number"
                    raise ValidationError(message=error_msg)
                    
        except (ValueError, InvalidOperation) as e:
            raise ValidationError(message=f"Invalid number format: {str(e)}")
    
    def _parse_number(self, text: str) -> Union[int, float, Decimal]:
        """Parse number from text based on format configuration."""
        # Remove formatting characters
        clean_text = self._clean_input_text(text)
        
        if self.format_config.format_type == 'int':
            return int(clean_text)
        elif self.format_config.format_type == 'float':
            return float(clean_text)
        elif self.format_config.format_type in ('currency', 'percentage'):
            return Decimal(clean_text)
        elif self.format_config.format_type == 'scientific':
            return float(clean_text)
        else:
            return float(clean_text)
    
    def _clean_input_text(self, text: str) -> str:
        """Clean input text by removing formatting characters."""
        # Remove currency symbols
        if self.format_config.format_type == 'currency':
            text = text.replace(self.format_config.currency_symbol, '')
        
        # Remove percentage symbols
        if self.format_config.format_type == 'percentage':
            text = text.replace(self.format_config.percentage_symbol, '')
        
        # Remove thousands separators
        if self.format_config.thousands_separator:
            text = text.replace(',', '')
        
        # Handle decimal separator
        if self.format_config.decimal_separator != '.':
            text = text.replace(self.format_config.decimal_separator, '.')
        
        return text.strip()


class NumberFormatter:
    """Utility class for formatting and parsing numbers."""
    
    def __init__(self, format_config: NumberFormat):
        """Initialize number formatter.
        
        Args:
            format_config: Number formatting configuration
        """
        self.format_config = format_config
        
        if format_config.use_locale:
            try:
                locale.setlocale(locale.LC_ALL, '')
            except locale.Error:
                pass  # Fall back to default formatting
    
    def format_number(self, value: Union[int, float, Decimal], for_display: bool = True) -> str:
        """Format a number for display or input.
        
        Args:
            value: The numeric value to format
            for_display: Whether this is for display (True) or input (False)
            
        Returns:
            Formatted number string
        """
        if value is None:
            return ""
        
        try:
            # Convert to appropriate type
            if self.format_config.format_type == 'int':
                value = int(value)
            elif isinstance(value, str):
                value = self._parse_from_string(value)
            
            # Apply formatting based on type
            if self.format_config.format_type == 'int':
                return self._format_integer(value, for_display)
            elif self.format_config.format_type == 'float':
                return self._format_float(value, for_display)
            elif self.format_config.format_type == 'currency':
                return self._format_currency(value, for_display)
            elif self.format_config.format_type == 'percentage':
                return self._format_percentage(value, for_display)
            elif self.format_config.format_type == 'scientific':
                return self._format_scientific(value, for_display)
            else:
                return str(value)
                
        except (ValueError, TypeError, InvalidOperation):
            return str(value)
    
    def parse_number(self, text: str) -> Union[int, float, Decimal, None]:
        """Parse a number from formatted text.
        
        Args:
            text: The formatted text to parse
            
        Returns:
            Parsed numeric value or None if invalid
        """
        if not text or not text.strip():
            return None
        
        try:
            # Clean the input
            clean_text = self._clean_formatted_text(text.strip())
            
            # Parse based on format type
            if self.format_config.format_type == 'int':
                return int(clean_text)
            elif self.format_config.format_type == 'float':
                return float(clean_text)
            elif self.format_config.format_type in ('currency', 'percentage'):
                value = Decimal(clean_text)
                # For percentage, convert back from display format
                if self.format_config.format_type == 'percentage':
                    value = value / 100
                return value
            elif self.format_config.format_type == 'scientific':
                return float(clean_text)
            else:
                return float(clean_text)
                
        except (ValueError, InvalidOperation):
            return None
    
    def _format_integer(self, value: int, for_display: bool) -> str:
        """Format an integer value."""
        if self.format_config.thousands_separator and for_display:
            if self.format_config.use_locale:
                return locale.format_string("%d", value, grouping=True)
            else:
                return f"{value:,}"
        return str(value)
    
    def _format_float(self, value: float, for_display: bool) -> str:
        """Format a float value."""
        if self.format_config.decimal_places is not None:
            if self.format_config.use_locale:
                format_str = f"%.{self.format_config.decimal_places}f"
                formatted = locale.format_string(format_str, value, grouping=self.format_config.thousands_separator and for_display)
            else:
                formatted = f"{value:.{self.format_config.decimal_places}f}"
                if self.format_config.thousands_separator and for_display and abs(value) >= 1000:
                    # Split at decimal and add thousands separators to integer part
                    parts = formatted.split('.')
                    parts[0] = f"{int(parts[0]):,}"
                    formatted = '.'.join(parts)
        else:
            formatted = str(value)
            if self.format_config.thousands_separator and for_display and abs(value) >= 1000:
                if '.' in formatted:
                    parts = formatted.split('.')
                    parts[0] = f"{int(parts[0]):,}"
                    formatted = '.'.join(parts)
                else:
                    formatted = f"{int(value):,}"
        
        # Replace decimal separator if needed
        if self.format_config.decimal_separator != '.' and for_display:
            formatted = formatted.replace('.', self.format_config.decimal_separator)
        
        return formatted
    
    def _format_currency(self, value: Union[float, Decimal], for_display: bool) -> str:
        """Format a currency value."""
        # Convert to Decimal for precision
        if not isinstance(value, Decimal):
            value = Decimal(str(value))
        
        # Round to specified decimal places
        if self.format_config.decimal_places is not None:
            quantizer = Decimal('0.1') ** self.format_config.decimal_places
            value = value.quantize(quantizer, rounding=self.format_config.round_mode)
        
        # Format the number part
        if self.format_config.use_locale:
            number_part = locale.currency(float(value), symbol=False, grouping=self.format_config.thousands_separator and for_display)
        else:
            number_part = self._format_float(float(value), for_display)
        
        # Add currency symbol
        if for_display:
            if self.format_config.currency_position == 'prefix':
                return f"{self.format_config.currency_symbol}{number_part}"
            else:
                return f"{number_part}{self.format_config.currency_symbol}"
        else:
            return number_part
    
    def _format_percentage(self, value: Union[float, Decimal], for_display: bool) -> str:
        """Format a percentage value."""
        # Convert to percentage (multiply by 100)
        if isinstance(value, Decimal):
            percent_value = value * 100
        else:
            percent_value = float(value) * 100
        
        # Format as float
        formatted = self._format_float(float(percent_value), for_display)
        
        # Add percentage symbol
        if for_display:
            return f"{formatted}{self.format_config.percentage_symbol}"
        else:
            return formatted
    
    def _format_scientific(self, value: float, for_display: bool) -> str:
        """Format a scientific notation value."""
        if for_display:
            return f"{value:.{self.format_config.scientific_precision}e}"
        else:
            return str(value)
    
    def _parse_from_string(self, text: str) -> Union[int, float, Decimal]:
        """Parse a number from a string representation."""
        clean_text = self._clean_formatted_text(text)
        
        if self.format_config.format_type == 'int':
            return int(clean_text)
        elif self.format_config.format_type in ('currency', 'percentage'):
            return Decimal(clean_text)
        else:
            return float(clean_text)
    
    def _clean_formatted_text(self, text: str) -> str:
        """Clean formatted text for parsing."""
        # Remove currency symbols
        text = text.replace(self.format_config.currency_symbol, '')
        
        # Remove percentage symbols
        text = text.replace(self.format_config.percentage_symbol, '')
        
        # Remove thousands separators
        if self.format_config.thousands_separator:
            text = text.replace(',', '')
        
        # Handle decimal separator
        if self.format_config.decimal_separator != '.':
            text = text.replace(self.format_config.decimal_separator, '.')
        
        return text.strip()
    
    def get_input_placeholder(self) -> str:
        """Get placeholder text for input field."""
        if self.format_config.format_type == 'int':
            return "Enter integer..."
        elif self.format_config.format_type == 'float':
            return f"Enter number (e.g., 123{self.format_config.decimal_separator}45)..."
        elif self.format_config.format_type == 'currency':
            example = self.format_number(1234.56, for_display=True)
            return f"Enter amount (e.g., {example})..."
        elif self.format_config.format_type == 'percentage':
            example = self.format_number(0.1234, for_display=True)
            return f"Enter percentage (e.g., {example})..."
        elif self.format_config.format_type == 'scientific':
            return "Enter number (e.g., 1.23e-4)..."
        else:
            return "Enter number..."


class EnhancedNumberAdapter:
    """Enhanced number input adapter with professional styling and advanced features."""
    
    def __init__(self,
                 message: str = "Enter number:",
                 format_type: str = 'float',
                 decimal_places: Optional[int] = 2,
                 min_value: Optional[Union[int, float, Decimal]] = None,
                 max_value: Optional[Union[int, float, Decimal]] = None,
                 default_value: Optional[Union[int, float, str]] = None,
                 currency_symbol: str = '$',
                 thousands_separator: bool = True,
                 allow_negative: bool = True,
                 allow_zero: bool = True,
                 increment_step: Optional[Union[int, float]] = None,
                 style: str = 'professional_blue',
                 show_help: bool = True,
                 custom_validator: Optional[Callable] = None):
        """Initialize enhanced number adapter.
        
        Args:
            message: Prompt message to display
            format_type: Type of number format ('int', 'float', 'currency', 'percentage', 'scientific')
            decimal_places: Number of decimal places for formatting
            min_value: Minimum allowed value
            max_value: Maximum allowed value
            default_value: Default value to display
            currency_symbol: Currency symbol for currency format
            thousands_separator: Whether to use thousands separators
            allow_negative: Whether to allow negative values
            allow_zero: Whether to allow zero values
            increment_step: Step size for increment/decrement operations
            style: Theme style to use
            show_help: Whether to show help text
            custom_validator: Custom validation function
        """
        if not QUESTIONARY_AVAILABLE:
            raise ImportError("Questionary is required for EnhancedNumberAdapter. Install with: pip install questionary")
        
        self.message = message
        self.style = style
        self.show_help = show_help
        
        # Create format configuration
        self.format_config = NumberFormat(
            format_type=format_type,
            decimal_places=decimal_places,
            currency_symbol=currency_symbol,
            thousands_separator=thousands_separator,
            allow_negative=allow_negative,
            allow_zero=allow_zero
        )
        
        # Validation constraints
        self.min_value = min_value
        self.max_value = max_value
        self.custom_validator = custom_validator
        
        # Increment/decrement functionality
        self.increment_step = increment_step or (1 if format_type == 'int' else 0.1)
        
        # Initialize formatter and validator
        self.formatter = NumberFormatter(self.format_config)
        self.validator = NumberValidator(
            self.format_config,
            min_value=min_value,
            max_value=max_value,
            custom_validator=custom_validator
        )
        
        # Current value
        self._current_value = None
        if default_value is not None:
            self.set_value(default_value)
        
        # Load TUI Engine themes
        self._load_themes()
    
    def _load_themes(self):
        """Load TUI Engine themes for styling."""
        try:
            from tui_engine.questionary_adapter import QuestionaryStyleAdapter
            
            # Create style adapter with theme name
            self.style_adapter = QuestionaryStyleAdapter(self.style)
            self._themes_available = True
        except ImportError:
            self._themes_available = False
    
    def set_value(self, value: Union[int, float, str, None]):
        """Set the current value.
        
        Args:
            value: The value to set (can be numeric or string representation)
        """
        if value is None:
            self._current_value = None
            return
        
        if isinstance(value, str):
            parsed_value = self.formatter.parse_number(value)
            self._current_value = parsed_value
        else:
            self._current_value = value
    
    def get_value(self) -> Union[int, float, Decimal, None]:
        """Get the current numeric value.
        
        Returns:
            Current numeric value or None if not set
        """
        return self._current_value
    
    def get_formatted_value(self, for_display: bool = True) -> str:
        """Get the formatted value as a string.
        
        Args:
            for_display: Whether to format for display (True) or input (False)
            
        Returns:
            Formatted value string
        """
        if self._current_value is None:
            return ""
        return self.formatter.format_number(self._current_value, for_display)
    
    def increment(self) -> bool:
        """Increment the current value by the step amount.
        
        Returns:
            True if increment was successful, False otherwise
        """
        if self._current_value is None:
            self._current_value = 0
        
        new_value = self._current_value + self.increment_step
        
        # Check constraints
        if self.max_value is not None and new_value > self.max_value:
            return False
        
        self._current_value = new_value
        return True
    
    def decrement(self) -> bool:
        """Decrement the current value by the step amount.
        
        Returns:
            True if decrement was successful, False otherwise
        """
        if self._current_value is None:
            self._current_value = 0
        
        new_value = self._current_value - self.increment_step
        
        # Check constraints
        if self.min_value is not None and new_value < self.min_value:
            return False
        
        if not self.format_config.allow_negative and new_value < 0:
            return False
        
        self._current_value = new_value
        return True
    
    def validate_current_value(self) -> Tuple[bool, str]:
        """Validate the current value.
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        if self._current_value is None:
            if self.format_config.allow_zero:
                return True, ""
            else:
                return False, "Number is required"
        
        try:
            # Check range constraints
            if self.min_value is not None and self._current_value < self.min_value:
                return False, f"Value must be at least {self.min_value}"
            
            if self.max_value is not None and self._current_value > self.max_value:
                return False, f"Value must be at most {self.max_value}"
            
            # Check sign constraints
            if not self.format_config.allow_negative and self._current_value < 0:
                return False, "Negative values are not allowed"
            
            if not self.format_config.allow_zero and self._current_value == 0:
                return False, "Zero is not allowed"
            
            # Custom validation
            if self.custom_validator:
                validation_result = self.custom_validator(self._current_value)
                if validation_result is not True:
                    error_msg = validation_result if isinstance(validation_result, str) else "Invalid number"
                    return False, error_msg
            
            return True, ""
            
        except Exception as e:
            return False, f"Validation error: {str(e)}"
    
    def enable_validation(self, validator_func: Callable):
        """Enable custom validation.
        
        Args:
            validator_func: Function that takes a number and returns True or error message
        """
        self.custom_validator = validator_func
        self.validator = NumberValidator(
            self.format_config,
            min_value=self.min_value,
            max_value=self.max_value,
            custom_validator=validator_func
        )
    
    def disable_validation(self):
        """Disable custom validation."""
        self.custom_validator = None
        self.validator = NumberValidator(
            self.format_config,
            min_value=self.min_value,
            max_value=self.max_value,
            custom_validator=None
        )
    
    def set_constraints(self, 
                       min_value: Optional[Union[int, float, Decimal]] = None,
                       max_value: Optional[Union[int, float, Decimal]] = None):
        """Set value constraints.
        
        Args:
            min_value: Minimum allowed value
            max_value: Maximum allowed value
        """
        self.min_value = min_value
        self.max_value = max_value
        self.validator = NumberValidator(
            self.format_config,
            min_value=min_value,
            max_value=max_value,
            custom_validator=self.custom_validator
        )
    
    def change_theme(self, new_style: str) -> bool:
        """Change the widget theme.
        
        Args:
            new_style: New theme style name
            
        Returns:
            True if theme was changed successfully
        """
        if self._themes_available:
            try:
                # Update style adapter with new theme
                from tui_engine.questionary_adapter import QuestionaryStyleAdapter
                self.style_adapter = QuestionaryStyleAdapter(new_style)
                self.style = new_style
                return True
            except ImportError:
                return False
        return False
    
    def get_widget_info(self) -> Dict[str, Any]:
        """Get comprehensive widget information.
        
        Returns:
            Dictionary containing widget configuration and state
        """
        return {
            'use_questionary': True,
            'has_validator': self.custom_validator is not None,
            'current_value': self.get_formatted_value(),
            'raw_value': self._current_value,
            'theme': self.style,
            'message': self.message,
            'format_type': self.format_config.format_type,
            'decimal_places': self.format_config.decimal_places,
            'min_value': self.min_value,
            'max_value': self.max_value,
            'increment_step': self.increment_step,
            'allow_negative': self.format_config.allow_negative,
            'allow_zero': self.format_config.allow_zero,
            'thousands_separator': self.format_config.thousands_separator,
            'currency_symbol': self.format_config.currency_symbol
        }
    
    def is_questionary_enhanced(self) -> bool:
        """Check if this adapter uses Questionary enhancements.
        
        Returns:
            True if using Questionary, False for legacy mode
        """
        return True
    
    def get_help_text(self) -> str:
        """Get help text for the current format.
        
        Returns:
            Help text string
        """
        help_parts = []
        
        # Format-specific help
        if self.format_config.format_type == 'int':
            help_parts.append("Enter a whole number")
        elif self.format_config.format_type == 'float':
            help_parts.append(f"Enter a decimal number (up to {self.format_config.decimal_places} decimal places)")
        elif self.format_config.format_type == 'currency':
            help_parts.append(f"Enter a currency amount (symbol: {self.format_config.currency_symbol})")
        elif self.format_config.format_type == 'percentage':
            help_parts.append("Enter a percentage (e.g., 50 for 50%)")
        elif self.format_config.format_type == 'scientific':
            help_parts.append("Enter in scientific notation (e.g., 1.23e-4)")
        
        # Constraint help
        constraints = []
        if self.min_value is not None:
            constraints.append(f"minimum: {self.min_value}")
        if self.max_value is not None:
            constraints.append(f"maximum: {self.max_value}")
        if not self.format_config.allow_negative:
            constraints.append("positive numbers only")
        if not self.format_config.allow_zero:
            constraints.append("non-zero values only")
        
        if constraints:
            help_parts.append(f"Constraints: {', '.join(constraints)}")
        
        # Increment help
        if self.increment_step:
            help_parts.append(f"Use +/- to increment by {self.increment_step}")
        
        return " • ".join(help_parts)
    
    def __str__(self) -> str:
        """String representation of the adapter."""
        return f"<EnhancedNumberAdapter format='{self.format_config.format_type}' value='{self.get_formatted_value()}'>"
    
    def __repr__(self) -> str:
        """Detailed string representation."""
        return self.__str__()


class NumberAdapter:
    """Backward-compatible number adapter that can work with or without Questionary.
    
    This adapter provides a unified interface that automatically chooses between
    enhanced Questionary-based functionality and legacy widget integration based
    on available dependencies and parameters.
    """
    
    def __init__(self, widget=None, **kwargs):
        """Initialize number adapter with automatic mode detection.
        
        Args:
            widget: If provided, uses legacy mode with existing widget
            **kwargs: Arguments passed to enhanced adapter or legacy configuration
        """
        self.widget = widget
        self._is_legacy = widget is not None
        
        if self._is_legacy:
            # Legacy mode - work with existing widget
            self._current_value = None
            self._legacy_init(**kwargs)
        else:
            # Enhanced mode - use Questionary if available
            if QUESTIONARY_AVAILABLE:
                try:
                    self._enhanced_adapter = EnhancedNumberAdapter(**kwargs)
                    self._is_enhanced = True
                except Exception as e:
                    # Fall back to legacy if enhanced mode fails
                    self._is_enhanced = False
                    self._current_value = None
                    self._legacy_init(**kwargs)
            else:
                # No Questionary - use legacy mode
                self._is_enhanced = False
                self._current_value = None
                self._legacy_init(**kwargs)
    
    def _legacy_init(self, **kwargs):
        """Initialize legacy mode configuration."""
        # Extract configuration from kwargs
        self.format_type = kwargs.get('format_type', 'float')
        self.decimal_places = kwargs.get('decimal_places', 2)
        self.min_value = kwargs.get('min_value')
        self.max_value = kwargs.get('max_value')
        self.currency_symbol = kwargs.get('currency_symbol', '$')
        self.thousands_separator = kwargs.get('thousands_separator', True)
        self.allow_negative = kwargs.get('allow_negative', True)
        self.allow_zero = kwargs.get('allow_zero', True)
        
        # Create format config for legacy mode
        self.format_config = NumberFormat(
            format_type=self.format_type,
            decimal_places=self.decimal_places,
            currency_symbol=self.currency_symbol,
            thousands_separator=self.thousands_separator,
            allow_negative=self.allow_negative,
            allow_zero=self.allow_zero
        )
        
        # Create formatter
        self.formatter = NumberFormatter(self.format_config)
        
        # Set default value if provided
        default_value = kwargs.get('default_value')
        if default_value is not None:
            self.set_value(default_value)
    
    def set_value(self, value: Union[int, float, str, None]):
        """Set the current value."""
        if hasattr(self, '_enhanced_adapter') and self._is_enhanced:
            self._enhanced_adapter.set_value(value)
        else:
            # Legacy mode
            if value is None:
                self._current_value = None
                return
            
            if isinstance(value, str):
                parsed_value = self.formatter.parse_number(value)
                self._current_value = parsed_value
            else:
                self._current_value = value
    
    def get_value(self) -> Union[int, float, Decimal, None]:
        """Get the current numeric value."""
        if hasattr(self, '_enhanced_adapter') and self._is_enhanced:
            return self._enhanced_adapter.get_value()
        else:
            return self._current_value
    
    def get_formatted_value(self, for_display: bool = True) -> str:
        """Get the formatted value as a string."""
        if hasattr(self, '_enhanced_adapter') and self._is_enhanced:
            return self._enhanced_adapter.get_formatted_value(for_display)
        else:
            if self._current_value is None:
                return ""
            return self.formatter.format_number(self._current_value, for_display)
    
    def increment(self) -> bool:
        """Increment the current value."""
        if hasattr(self, '_enhanced_adapter') and self._is_enhanced:
            return self._enhanced_adapter.increment()
        else:
            # Legacy increment
            if self._current_value is None:
                self._current_value = 0
            
            step = 1 if self.format_type == 'int' else 0.1
            new_value = self._current_value + step
            
            if self.max_value is not None and new_value > self.max_value:
                return False
            
            self._current_value = new_value
            return True
    
    def decrement(self) -> bool:
        """Decrement the current value."""
        if hasattr(self, '_enhanced_adapter') and self._is_enhanced:
            return self._enhanced_adapter.decrement()
        else:
            # Legacy decrement
            if self._current_value is None:
                self._current_value = 0
            
            step = 1 if self.format_type == 'int' else 0.1
            new_value = self._current_value - step
            
            if self.min_value is not None and new_value < self.min_value:
                return False
            
            if not self.allow_negative and new_value < 0:
                return False
            
            self._current_value = new_value
            return True
    
    def validate_current_value(self) -> Tuple[bool, str]:
        """Validate the current value."""
        if hasattr(self, '_enhanced_adapter') and self._is_enhanced:
            return self._enhanced_adapter.validate_current_value()
        else:
            # Legacy validation
            if self._current_value is None:
                if self.allow_zero:
                    return True, ""
                else:
                    return False, "Number is required"
            
            # Check range constraints
            if self.min_value is not None and self._current_value < self.min_value:
                return False, f"Value must be at least {self.min_value}"
            
            if self.max_value is not None and self._current_value > self.max_value:
                return False, f"Value must be at most {self.max_value}"
            
            # Check sign constraints
            if not self.allow_negative and self._current_value < 0:
                return False, "Negative values are not allowed"
            
            if not self.allow_zero and self._current_value == 0:
                return False, "Zero is not allowed"
            
            return True, ""
    
    def enable_validation(self, validator_func: Callable):
        """Enable custom validation."""
        if hasattr(self, '_enhanced_adapter') and self._is_enhanced:
            self._enhanced_adapter.enable_validation(validator_func)
        else:
            # Legacy mode doesn't support custom validation
            pass
    
    def disable_validation(self):
        """Disable custom validation."""
        if hasattr(self, '_enhanced_adapter') and self._is_enhanced:
            self._enhanced_adapter.disable_validation()
        else:
            # Legacy mode doesn't support custom validation
            pass
    
    def set_constraints(self, min_value=None, max_value=None):
        """Set value constraints."""
        if hasattr(self, '_enhanced_adapter') and self._is_enhanced:
            self._enhanced_adapter.set_constraints(min_value, max_value)
        else:
            # Legacy constraint setting
            self.min_value = min_value
            self.max_value = max_value
    
    def change_theme(self, new_style: str) -> bool:
        """Change the widget theme."""
        if hasattr(self, '_enhanced_adapter') and self._is_enhanced:
            return self._enhanced_adapter.change_theme(new_style)
        else:
            # Legacy mode doesn't support theme changes
            return False
    
    def get_widget_info(self) -> Dict[str, Any]:
        """Get comprehensive widget information."""
        if hasattr(self, '_enhanced_adapter') and self._is_enhanced:
            return self._enhanced_adapter.get_widget_info()
        else:
            # Legacy widget info
            return {
                'use_questionary': False,
                'has_validator': False,
                'current_value': self.get_formatted_value(),
                'raw_value': self._current_value,
                'theme': 'none',
                'format_type': self.format_type,
                'decimal_places': self.decimal_places,
                'min_value': self.min_value,
                'max_value': self.max_value,
                'legacy_widget': self.widget is not None
            }
    
    def is_questionary_enhanced(self) -> bool:
        """Check if this adapter uses Questionary enhancements."""
        return hasattr(self, '_enhanced_adapter') and self._is_enhanced
    
    def __str__(self) -> str:
        """String representation of the adapter."""
        if hasattr(self, '_enhanced_adapter') and self._is_enhanced:
            return str(self._enhanced_adapter)
        else:
            return f"<NumberAdapter widget='{self.widget}' value='{self.get_formatted_value()}'>"
    
    def __repr__(self) -> str:
        """Detailed string representation."""
        return self.__str__()


# Convenience functions for creating common number input scenarios

def create_integer_input(message: str = "Enter integer:",
                        min_value: Optional[int] = None,
                        max_value: Optional[int] = None,
                        default_value: Optional[int] = None,
                        allow_negative: bool = True,
                        **kwargs) -> NumberAdapter:
    """Create an integer input widget.
    
    Args:
        message: Prompt message
        min_value: Minimum allowed value
        max_value: Maximum allowed value  
        default_value: Default value
        allow_negative: Whether to allow negative values
        **kwargs: Additional arguments passed to NumberAdapter
        
    Returns:
        Configured NumberAdapter for integer input
    """
    return NumberAdapter(
        message=message,
        format_type='int',
        min_value=min_value,
        max_value=max_value,
        default_value=default_value,
        allow_negative=allow_negative,
        decimal_places=None,
        **kwargs
    )


def create_float_input(message: str = "Enter number:",
                      decimal_places: int = 2,
                      min_value: Optional[float] = None,
                      max_value: Optional[float] = None,
                      default_value: Optional[float] = None,
                      **kwargs) -> NumberAdapter:
    """Create a float input widget.
    
    Args:
        message: Prompt message
        decimal_places: Number of decimal places
        min_value: Minimum allowed value
        max_value: Maximum allowed value
        default_value: Default value
        **kwargs: Additional arguments passed to NumberAdapter
        
    Returns:
        Configured NumberAdapter for float input
    """
    return NumberAdapter(
        message=message,
        format_type='float',
        decimal_places=decimal_places,
        min_value=min_value,
        max_value=max_value,
        default_value=default_value,
        **kwargs
    )


def create_currency_input(message: str = "Enter amount:",
                         currency_symbol: str = '$',
                         decimal_places: int = 2,
                         min_value: Optional[float] = 0,
                         **kwargs) -> NumberAdapter:
    """Create a currency input widget.
    
    Args:
        message: Prompt message
        currency_symbol: Currency symbol to use
        decimal_places: Number of decimal places
        min_value: Minimum allowed value (defaults to 0)
        **kwargs: Additional arguments passed to NumberAdapter
        
    Returns:
        Configured NumberAdapter for currency input
    """
    return NumberAdapter(
        message=message,
        format_type='currency',
        currency_symbol=currency_symbol,
        decimal_places=decimal_places,
        min_value=min_value,
        allow_negative=False,
        thousands_separator=True,
        **kwargs
    )


def create_percentage_input(message: str = "Enter percentage:",
                           decimal_places: int = 1,
                           min_value: float = 0.0,
                           max_value: float = 1.0,
                           **kwargs) -> NumberAdapter:
    """Create a percentage input widget.
    
    Args:
        message: Prompt message
        decimal_places: Number of decimal places
        min_value: Minimum allowed value (0.0 = 0%)
        max_value: Maximum allowed value (1.0 = 100%)
        **kwargs: Additional arguments passed to NumberAdapter
        
    Returns:
        Configured NumberAdapter for percentage input
    """
    return NumberAdapter(
        message=message,
        format_type='percentage',
        decimal_places=decimal_places,
        min_value=min_value,
        max_value=max_value,
        allow_negative=False,
        **kwargs
    )


def create_scientific_input(message: str = "Enter scientific number:",
                           precision: int = 2,
                           **kwargs) -> NumberAdapter:
    """Create a scientific notation input widget.
    
    Args:
        message: Prompt message
        precision: Precision for scientific notation
        **kwargs: Additional arguments passed to NumberAdapter
        
    Returns:
        Configured NumberAdapter for scientific notation input
    """
    kwargs['scientific_precision'] = precision
    return NumberAdapter(
        message=message,
        format_type='scientific',
        **kwargs
    )


# Export public interface
__all__ = [
    'NumberAdapter',
    'EnhancedNumberAdapter', 
    'NumberFormat',
    'NumberValidator',
    'NumberFormatter',
    'create_integer_input',
    'create_float_input',
    'create_currency_input',
    'create_percentage_input',
    'create_scientific_input'
]