"""
Questionary Style Adapter for TUI Engine

This module provides seamless integration between TUI Engine's existing styling
system and Questionary's professional theme system. The adapter enables:

- Automatic conversion of TUI Engine styles to Questionary-compatible styles
- Preservation of existing TUI Engine styling logic
- Enhanced styling with Questionary's professional themes
- Backward compatibility with existing applications
"""

from typing import Dict, Any, Optional, Union, List, Tuple
from questionary import Style
from .themes import TUIEngineThemes
from .styles import get_style_for_variant, VARIANT_STYLE


class QuestionaryStyleAdapter:
    """
    Adapter that bridges TUI Engine styling with Questionary themes.
    
    This adapter provides:
    - Conversion from TUI Engine variants to Questionary style classes
    - Integration with the TUIEngineThemes system
    - Preservation of existing styling logic
    - Enhanced styling capabilities through Questionary
    """
    
    # Mapping from TUI Engine variants to Questionary style classes
    VARIANT_TO_QUESTIONARY_MAP = {
        'card': ['container_title', 'border', 'text'],
        'section': ['section_title', 'text_secondary', 'separator'],
        'header': ['container_title', 'text_inverse', 'info'],
        'footer': ['text_muted', 'button', 'separator'],
        'page': ['text', 'background'],
        'title': ['container_title', 'text_inverse'],
        'navigation': ['button', 'button_focused', 'text_secondary'],
        'content': ['text', 'text_secondary'],
        'form': ['input', 'input_focused', 'placeholder'],
        'validation': ['validation_error', 'validation_success', 'warning'],
        'button': ['button', 'button_focused', 'button_disabled'],
        'input': ['input', 'input_focused', 'placeholder'],
        'select': ['selected', 'highlighted', 'pointer'],
        'checkbox': ['checkbox', 'checkbox-selected'],
        'status': ['success', 'error', 'warning', 'info'],
    }
    
    def __init__(self, theme: Optional[Union[str, Style]] = None):
        """
        Initialize the style adapter.
        
        Args:
            theme: Theme to use (theme name string, Style object, or None for default)
        """
        self._current_theme = self._resolve_theme(theme)
        self._style_cache = {}
        self._variant_cache = {}
        
    def _resolve_theme(self, theme: Optional[Union[str, Style]]) -> Style:
        """
        Resolve theme parameter to a Style object.
        
        Args:
            theme: Theme specification
            
        Returns:
            Style object
        """
        if theme is None:
            return TUIEngineThemes.PROFESSIONAL_BLUE
        elif isinstance(theme, str):
            resolved = TUIEngineThemes.get_theme(theme)
            if resolved is None:
                raise ValueError(f"Unknown theme: {theme}")
            return resolved
        elif isinstance(theme, Style):
            return theme
        else:
            raise TypeError(f"Invalid theme type: {type(theme)}")
    
    def get_questionary_style(self) -> Style:
        """
        Get the current Questionary style object.
        
        Returns:
            Current Style object for use with Questionary prompts
        """
        return self._current_theme
    
    def get_style_for_variant(self, variant: str) -> str:
        """
        Enhanced version of TUI Engine's get_style_for_variant that includes
        Questionary styling information.
        
        Args:
            variant: TUI Engine variant name
            
        Returns:
            Style class string compatible with both TUI Engine and Questionary
        """
        # Use cache for performance
        if variant in self._variant_cache:
            return self._variant_cache[variant]
        
        # Get original TUI Engine style
        original_style = get_style_for_variant(variant)
        
        # Map to Questionary style classes if available
        questionary_classes = self.VARIANT_TO_QUESTIONARY_MAP.get(variant, [])
        
        if questionary_classes:
            # Use the primary Questionary class
            primary_class = questionary_classes[0]
            enhanced_style = f"class:{primary_class}"
        else:
            # Fall back to original style
            enhanced_style = original_style
        
        # Cache result
        self._variant_cache[variant] = enhanced_style
        return enhanced_style
    
    def create_variant_style_mapping(self) -> Dict[str, str]:
        """
        Create a complete mapping of TUI Engine variants to Questionary styles.
        
        Returns:
            Dictionary mapping variant names to style classes
        """
        mapping = {}
        
        # Include original TUI Engine variants
        for variant in VARIANT_STYLE.keys():
            mapping[variant] = self.get_style_for_variant(variant)
        
        # Add enhanced variants
        for variant in self.VARIANT_TO_QUESTIONARY_MAP.keys():
            if variant not in mapping:
                mapping[variant] = self.get_style_for_variant(variant)
        
        return mapping
    
    def get_enhanced_style_rules(self) -> List[Tuple[str, str]]:
        """
        Get enhanced style rules that combine TUI Engine and Questionary styling.
        
        Returns:
            List of (class_name, style_definition) tuples
        """
        rules = []
        
        # Add rules from current Questionary theme
        if hasattr(self._current_theme, 'style_rules'):
            rules.extend(self._current_theme.style_rules)
        
        # Add enhanced TUI Engine variant mappings
        variant_mapping = self.create_variant_style_mapping()
        for variant, style_class in variant_mapping.items():
            # Extract the class name without 'class:' prefix
            if style_class.startswith('class:'):
                class_name = style_class[6:]  # Remove 'class:' prefix
                
                # Find corresponding style in theme
                for rule in self._current_theme.style_rules:
                    rule_key = rule[0] if isinstance(rule[0], str) else str(rule[0])
                    if rule_key == class_name:
                        rules.append((f'{variant}', rule[1]))
                        break
        
        return rules
    
    def create_combined_style(self, additional_rules: Optional[Dict[str, str]] = None) -> Style:
        """
        Create a combined style that includes both Questionary theme and
        TUI Engine variant mappings.
        
        Args:
            additional_rules: Optional additional style rules to include
            
        Returns:
            Combined Style object
        """
        # Start with enhanced rules
        combined_rules = self.get_enhanced_style_rules()
        
        # Add any additional rules
        if additional_rules:
            for class_name, style_def in additional_rules.items():
                combined_rules.append((class_name, style_def))
        
        return Style(combined_rules)
    
    def set_theme(self, theme: Union[str, Style]) -> None:
        """
        Change the current theme.
        
        Args:
            theme: New theme (name string or Style object)
        """
        self._current_theme = self._resolve_theme(theme)
        self._style_cache.clear()
        self._variant_cache.clear()
    
    def get_theme_name(self) -> Optional[str]:
        """
        Get the name of the current theme if it's a built-in theme.
        
        Returns:
            Theme name or None if it's a custom theme
        """
        for theme_name in TUIEngineThemes.list_themes():
            theme_obj = TUIEngineThemes.get_theme(theme_name)
            if theme_obj == self._current_theme:
                return theme_name
        return None
    
    def apply_variant_styling(self, variant: str, base_style: Optional[str] = None) -> str:
        """
        Apply variant styling with Questionary enhancement.
        
        Args:
            variant: TUI Engine variant name
            base_style: Optional base style to combine with
            
        Returns:
            Enhanced style string
        """
        variant_style = self.get_style_for_variant(variant)
        
        if base_style:
            # Combine base style with variant style
            return f"{base_style} {variant_style}"
        else:
            return variant_style
    
    def get_style_for_component(self, component_type: str, 
                               state: Optional[str] = None) -> str:
        """
        Get appropriate style for a specific component type and state.
        
        Args:
            component_type: Type of component (input, button, select, etc.)
            state: Optional state (focused, disabled, selected, etc.)
            
        Returns:
            Style class string
        """
        # Build style key
        if state:
            style_key = f"{component_type}_{state}"
        else:
            style_key = component_type
        
        # Check if we have a direct mapping
        if style_key in self.VARIANT_TO_QUESTIONARY_MAP:
            return self.get_style_for_variant(style_key)
        
        # Try component type alone
        if component_type in self.VARIANT_TO_QUESTIONARY_MAP:
            return self.get_style_for_variant(component_type)
        
        # Fall back to generic styling
        return self.get_style_for_variant('content')
    
    def create_component_style(self, component_type: str, 
                              custom_overrides: Optional[Dict[str, str]] = None) -> Style:
        """
        Create a Style object optimized for a specific component type.
        
        Args:
            component_type: Type of component to style
            custom_overrides: Optional style overrides
            
        Returns:
            Style object optimized for the component
        """
        # Get base theme rules
        base_rules = list(self._current_theme.style_rules)
        
        # Add component-specific enhancements
        component_styles = self.VARIANT_TO_QUESTIONARY_MAP.get(component_type, [])
        
        # Apply custom overrides if provided
        if custom_overrides:
            # Create a map of existing rules for easy override
            rule_map = {rule[0]: rule[1] for rule in base_rules}
            rule_map.update(custom_overrides)
            base_rules = [(k, v) for k, v in rule_map.items()]
        
        return Style(base_rules)
    
    def migrate_legacy_style(self, legacy_style: Dict[str, Any]) -> Style:
        """
        Migrate legacy TUI Engine styling to Questionary-compatible styling.
        
        Args:
            legacy_style: Legacy style configuration
            
        Returns:
            Migrated Style object
        """
        migrated_rules = []
        
        # Start with current theme as base
        migrated_rules.extend(self._current_theme.style_rules)
        
        # Map legacy style entries
        for key, value in legacy_style.items():
            if isinstance(value, str):
                # Direct style mapping
                migrated_rules.append((key, value))
            elif isinstance(value, dict):
                # Nested style object - flatten it
                for subkey, subvalue in value.items():
                    migrated_rules.append((f"{key}_{subkey}", str(subvalue)))
        
        return Style(migrated_rules)
    
    def get_validation_styles(self) -> Dict[str, str]:
        """
        Get styles specifically for validation states.
        
        Returns:
            Dictionary of validation style mappings
        """
        return {
            'valid': 'class:validation_success',
            'invalid': 'class:validation_error', 
            'warning': 'class:warning',
            'info': 'class:info',
        }
    
    def get_navigation_styles(self) -> Dict[str, str]:
        """
        Get styles specifically for navigation elements.
        
        Returns:
            Dictionary of navigation style mappings
        """
        return {
            'button': 'class:button',
            'button_focused': 'class:button_focused',
            'button_disabled': 'class:button_disabled',
            'selected': 'class:selected',
            'highlighted': 'class:highlighted',
        }
    
    def preview_style_mapping(self) -> str:
        """
        Generate a preview of the current style mapping.
        
        Returns:
            Multi-line string showing style mappings
        """
        lines = [
            f"Questionary Style Adapter Preview",
            f"Current Theme: {self.get_theme_name() or 'Custom'}",
            "=" * 50,
            "",
            "Variant Mappings:",
        ]
        
        variant_mapping = self.create_variant_style_mapping()
        for variant, style in sorted(variant_mapping.items()):
            lines.append(f"  {variant:15} → {style}")
        
        lines.extend([
            "",
            "Validation Styles:",
        ])
        
        validation_styles = self.get_validation_styles()
        for state, style in validation_styles.items():
            lines.append(f"  {state:15} → {style}")
        
        lines.extend([
            "",
            "Navigation Styles:",
        ])
        
        nav_styles = self.get_navigation_styles()
        for element, style in nav_styles.items():
            lines.append(f"  {element:15} → {style}")
        
        return "\n".join(lines)