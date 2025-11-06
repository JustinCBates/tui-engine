"""
TUI Engine Theme System

This module provides a comprehensive theme system for TUI Engine applications,
offering professional color schemes and styling that integrate seamlessly with
both TUI Engine components and Questionary prompts.

The theme system provides:
- Professional color schemes for different use cases
- Accessibility-compliant contrast ratios
- Consistent styling across all components
- Easy theme switching and customization
"""

from typing import Dict, Any, Optional, Union
from questionary import Style


class TUIEngineThemes:
    """
    Professional theme collection for TUI Engine applications.
    
    Provides carefully crafted color schemes that work well in terminal environments
    and maintain accessibility standards. Themes are designed to be:
    
    - Professional and visually appealing
    - Accessible with proper contrast ratios
    - Consistent across all components
    - Suitable for different use cases and environments
    """
    
    # Professional Blue Theme - Modern, professional appearance
    PROFESSIONAL_BLUE = Style([
        # Question and prompt styling
        ('question', 'fg:#2563eb bold'),           # Professional blue for questions
        ('answered_question', 'fg:#1e40af'),       # Darker blue for answered questions
        ('instruction', 'fg:#64748b italic'),      # Slate gray for instructions
        ('answer', 'fg:#0ea5e9 bold'),            # Bright blue for answers
        
        # UI Element styling
        ('highlighted', 'bg:#2563eb fg:#ffffff bold'),  # Blue highlight
        ('selected', 'fg:#0ea5e9 bold'),          # Selected items
        ('pointer', 'fg:#2563eb bold'),           # Selection pointer
        ('checkbox', 'fg:#2563eb'),               # Checkbox styling
        ('checkbox-selected', 'fg:#0ea5e9 bold'), # Selected checkbox
        
        # Status and feedback
        ('success', 'fg:#059669 bold'),           # Green for success
        ('error', 'fg:#dc2626 bold'),             # Red for errors
        ('warning', 'fg:#d97706 bold'),           # Orange for warnings
        ('info', 'fg:#0ea5e9'),                   # Blue for information
        
        # Container and layout
        ('container_title', 'fg:#1e40af bold underline'),  # Container titles
        ('section_title', 'fg:#2563eb bold'),     # Section titles
        ('border', 'fg:#64748b'),                 # Border elements
        ('separator', 'fg:#e2e8f0'),              # Separators
        
        # Navigation and controls
        ('button', 'fg:#ffffff bg:#2563eb'),      # Button styling
        ('button_focused', 'fg:#ffffff bg:#1e40af bold'),  # Focused button
        ('button_disabled', 'fg:#94a3b8 bg:#e2e8f0'),     # Disabled button
        
        # Text and content
        ('text', 'fg:#334155'),                   # Primary text
        ('text_secondary', 'fg:#64748b'),         # Secondary text
        ('text_muted', 'fg:#94a3b8'),            # Muted text
        ('text_inverse', 'fg:#ffffff'),           # Inverse text
        
        # Form elements
        ('input', 'fg:#334155'),                  # Input text
        ('input_focused', 'fg:#1e40af bold'),     # Focused input
        ('placeholder', 'fg:#94a3b8 italic'),     # Placeholder text
        ('validation_error', 'fg:#dc2626'),       # Validation errors
        ('validation_success', 'fg:#059669'),     # Validation success
    ])
    
    # Dark Mode Theme - Easy on the eyes for extended use
    DARK_MODE = Style([
        # Question and prompt styling
        ('question', 'fg:#60a5fa bold'),           # Light blue for questions
        ('answered_question', 'fg:#3b82f6'),       # Bright blue for answered questions
        ('instruction', 'fg:#94a3b8 italic'),      # Light gray for instructions
        ('answer', 'fg:#34d399 bold'),            # Green for answers
        
        # UI Element styling
        ('highlighted', 'bg:#1e40af fg:#ffffff bold'),  # Blue highlight
        ('selected', 'fg:#34d399 bold'),          # Green for selected items
        ('pointer', 'fg:#60a5fa bold'),           # Light blue pointer
        ('checkbox', 'fg:#60a5fa'),               # Checkbox styling
        ('checkbox-selected', 'fg:#34d399 bold'), # Selected checkbox
        
        # Status and feedback
        ('success', 'fg:#10b981 bold'),           # Bright green for success
        ('error', 'fg:#f87171 bold'),             # Light red for errors
        ('warning', 'fg:#fbbf24 bold'),           # Yellow for warnings
        ('info', 'fg:#60a5fa'),                   # Light blue for information
        
        # Container and layout
        ('container_title', 'fg:#60a5fa bold underline'),  # Container titles
        ('section_title', 'fg:#3b82f6 bold'),     # Section titles
        ('border', 'fg:#6b7280'),                 # Border elements
        ('separator', 'fg:#374151'),              # Separators
        
        # Navigation and controls
        ('button', 'fg:#ffffff bg:#1e40af'),      # Button styling
        ('button_focused', 'fg:#ffffff bg:#1d4ed8 bold'),  # Focused button
        ('button_disabled', 'fg:#6b7280 bg:#374151'),     # Disabled button
        
        # Text and content
        ('text', 'fg:#e5e7eb'),                   # Primary text (light)
        ('text_secondary', 'fg:#d1d5db'),         # Secondary text
        ('text_muted', 'fg:#9ca3af'),            # Muted text
        ('text_inverse', 'fg:#111827'),           # Inverse text (dark)
        
        # Form elements
        ('input', 'fg:#f3f4f6'),                  # Input text
        ('input_focused', 'fg:#60a5fa bold'),     # Focused input
        ('placeholder', 'fg:#6b7280 italic'),     # Placeholder text
        ('validation_error', 'fg:#f87171'),       # Validation errors
        ('validation_success', 'fg:#10b981'),     # Validation success
    ])
    
    # High Contrast Theme - Maximum accessibility and readability
    HIGH_CONTRAST = Style([
        # Question and prompt styling
        ('question', 'fg:#000000 bg:#ffffff bold'),        # Black on white
        ('answered_question', 'fg:#000000 bg:#e5e7eb'),    # Black on light gray
        ('instruction', 'fg:#374151 italic'),              # Dark gray for instructions
        ('answer', 'fg:#ffffff bg:#000000 bold'),          # White on black
        
        # UI Element styling
        ('highlighted', 'bg:#000000 fg:#ffffff bold'),     # Black background, white text
        ('selected', 'fg:#ffffff bg:#000000 bold'),        # High contrast selection
        ('pointer', 'fg:#000000 bold'),                    # Black pointer
        ('checkbox', 'fg:#000000'),                        # Black checkbox
        ('checkbox-selected', 'fg:#ffffff bg:#000000 bold'), # Selected checkbox
        
        # Status and feedback
        ('success', 'fg:#ffffff bg:#059669 bold'),         # White on green
        ('error', 'fg:#ffffff bg:#dc2626 bold'),           # White on red
        ('warning', 'fg:#000000 bg:#fbbf24 bold'),         # Black on yellow
        ('info', 'fg:#ffffff bg:#0ea5e9 bold'),            # White on blue
        
        # Container and layout
        ('container_title', 'fg:#000000 bold underline'),  # Black container titles
        ('section_title', 'fg:#000000 bold'),              # Black section titles
        ('border', 'fg:#000000'),                          # Black borders
        ('separator', 'fg:#6b7280'),                       # Gray separators
        
        # Navigation and controls
        ('button', 'fg:#ffffff bg:#000000 bold'),          # White on black buttons
        ('button_focused', 'fg:#000000 bg:#ffffff bold'),  # Focused button (inverted)
        ('button_disabled', 'fg:#6b7280 bg:#f3f4f6'),     # Disabled button
        
        # Text and content
        ('text', 'fg:#000000'),                            # Black text
        ('text_secondary', 'fg:#374151'),                  # Dark gray text
        ('text_muted', 'fg:#6b7280'),                     # Muted gray text
        ('text_inverse', 'fg:#ffffff'),                    # White text
        
        # Form elements
        ('input', 'fg:#000000'),                           # Black input text
        ('input_focused', 'fg:#000000 bg:#f3f4f6 bold'),  # Focused input
        ('placeholder', 'fg:#6b7280 italic'),              # Gray placeholder
        ('validation_error', 'fg:#ffffff bg:#dc2626'),     # White on red
        ('validation_success', 'fg:#ffffff bg:#059669'),   # White on green
    ])
    
    # Classic Terminal Theme - Traditional green-on-black terminal look
    CLASSIC_TERMINAL = Style([
        # Question and prompt styling
        ('question', 'fg:#00ff00 bold'),           # Bright green for questions
        ('answered_question', 'fg:#00cc00'),       # Slightly dimmer green
        ('instruction', 'fg:#888888 italic'),      # Gray for instructions
        ('answer', 'fg:#ffffff bold'),            # White for answers
        
        # UI Element styling
        ('highlighted', 'bg:#00ff00 fg:#000000 bold'),  # Green highlight
        ('selected', 'fg:#00ff00 bold'),          # Green selection
        ('pointer', 'fg:#00ff00 bold'),           # Green pointer
        ('checkbox', 'fg:#00ff00'),               # Green checkbox
        ('checkbox-selected', 'fg:#ffffff bold'), # White selected checkbox
        
        # Status and feedback
        ('success', 'fg:#00ff00 bold'),           # Green for success
        ('error', 'fg:#ff0000 bold'),             # Red for errors
        ('warning', 'fg:#ffff00 bold'),           # Yellow for warnings
        ('info', 'fg:#00ffff'),                   # Cyan for information
        
        # Container and layout
        ('container_title', 'fg:#00ff00 bold underline'),  # Green container titles
        ('section_title', 'fg:#00cc00 bold'),     # Green section titles
        ('border', 'fg:#888888'),                 # Gray borders
        ('separator', 'fg:#444444'),              # Dark gray separators
        
        # Navigation and controls
        ('button', 'fg:#000000 bg:#00ff00'),      # Black on green buttons
        ('button_focused', 'fg:#000000 bg:#ffffff bold'),  # Focused button
        ('button_disabled', 'fg:#666666 bg:#333333'),     # Disabled button
        
        # Text and content
        ('text', 'fg:#ffffff'),                   # White text
        ('text_secondary', 'fg:#cccccc'),         # Light gray text
        ('text_muted', 'fg:#888888'),            # Muted gray text
        ('text_inverse', 'fg:#000000'),           # Black text
        
        # Form elements
        ('input', 'fg:#ffffff'),                  # White input text
        ('input_focused', 'fg:#00ff00 bold'),     # Green focused input
        ('placeholder', 'fg:#888888 italic'),     # Gray placeholder
        ('validation_error', 'fg:#ff0000'),       # Red validation errors
        ('validation_success', 'fg:#00ff00'),     # Green validation success
    ])
    
    # Minimal Theme - Clean, understated appearance
    MINIMAL = Style([
        # Question and prompt styling
        ('question', 'fg:#000000 bold'),           # Black for questions
        ('answered_question', 'fg:#333333'),       # Dark gray for answered
        ('instruction', 'fg:#666666 italic'),      # Gray for instructions
        ('answer', 'fg:#000000'),                 # Black for answers
        
        # UI Element styling
        ('highlighted', 'fg:#000000 bold'),        # Bold black highlight
        ('selected', 'fg:#000000 bold'),          # Bold black selection
        ('pointer', 'fg:#000000'),                # Black pointer
        ('checkbox', 'fg:#000000'),               # Black checkbox
        ('checkbox-selected', 'fg:#000000 bold'), # Bold selected checkbox
        
        # Status and feedback
        ('success', 'fg:#000000'),                # Black for success
        ('error', 'fg:#000000 bold'),             # Bold black for errors
        ('warning', 'fg:#000000'),                # Black for warnings
        ('info', 'fg:#000000'),                   # Black for information
        
        # Container and layout
        ('container_title', 'fg:#000000 bold'),    # Black container titles
        ('section_title', 'fg:#000000 bold'),     # Black section titles
        ('border', 'fg:#cccccc'),                 # Light gray borders
        ('separator', 'fg:#eeeeee'),              # Very light separators
        
        # Navigation and controls
        ('button', 'fg:#000000'),                 # Black buttons
        ('button_focused', 'fg:#000000 bold'),    # Bold focused button
        ('button_disabled', 'fg:#cccccc'),        # Gray disabled button
        
        # Text and content
        ('text', 'fg:#000000'),                   # Black text
        ('text_secondary', 'fg:#333333'),         # Dark gray text
        ('text_muted', 'fg:#666666'),            # Muted gray text
        ('text_inverse', 'fg:#ffffff'),           # White text
        
        # Form elements
        ('input', 'fg:#000000'),                  # Black input text
        ('input_focused', 'fg:#000000 bold'),     # Bold focused input
        ('placeholder', 'fg:#999999 italic'),     # Light gray placeholder
        ('validation_error', 'fg:#000000'),       # Black validation errors
        ('validation_success', 'fg:#000000'),     # Black validation success
    ])
    
    @classmethod
    def get_theme(cls, theme_name: str) -> Optional[Style]:
        """
        Get a theme by name.
        
        Args:
            theme_name: Name of the theme to retrieve
            
        Returns:
            Style object or None if theme not found
        """
        theme_mapping = {
            'professional_blue': cls.PROFESSIONAL_BLUE,
            'dark_mode': cls.DARK_MODE,
            'high_contrast': cls.HIGH_CONTRAST,
            'classic_terminal': cls.CLASSIC_TERMINAL,
            'minimal': cls.MINIMAL,
        }
        
        return theme_mapping.get(theme_name.lower())
    
    @classmethod
    def list_themes(cls) -> list[str]:
        """
        Get a list of all available theme names.
        
        Returns:
            List of theme names
        """
        return [
            'professional_blue',
            'dark_mode', 
            'high_contrast',
            'classic_terminal',
            'minimal'
        ]
    
    @classmethod
    def get_theme_description(cls, theme_name: str) -> Optional[str]:
        """
        Get a description of a theme.
        
        Args:
            theme_name: Name of the theme
            
        Returns:
            Description string or None if theme not found
        """
        descriptions = {
            'professional_blue': 'Modern, professional blue color scheme suitable for business applications',
            'dark_mode': 'Dark theme easy on the eyes for extended use in low-light environments',
            'high_contrast': 'Maximum accessibility theme with high contrast ratios for better readability',
            'classic_terminal': 'Traditional green-on-black terminal appearance with retro computing feel',
            'minimal': 'Clean, understated black and white theme with minimal visual distraction'
        }
        
        return descriptions.get(theme_name.lower())
    
    @classmethod
    def create_custom_theme(cls, base_theme: str, overrides: Dict[str, str]) -> Style:
        """
        Create a custom theme based on an existing theme with style overrides.
        
        Args:
            base_theme: Name of the base theme to start with
            overrides: Dictionary of style overrides
            
        Returns:
            New Style object with custom styling
            
        Example:
            custom_theme = TUIEngineThemes.create_custom_theme(
                'professional_blue',
                {
                    'question': 'fg:#ff0000 bold',  # Red questions
                    'answer': 'fg:#00ff00'          # Green answers
                }
            )
        """
        base = cls.get_theme(base_theme)
        if not base:
            raise ValueError(f"Base theme '{base_theme}' not found")
        
        # Get existing styles
        existing_styles = base.style_rules
        
        # Create new style rules with overrides
        new_rules = []
        for rule in existing_styles:
            token_name = rule[0] if isinstance(rule[0], str) else str(rule[0])
            if token_name in overrides:
                new_rules.append((rule[0], overrides[token_name]))
            else:
                new_rules.append(rule)
        
        # Add any new styles that weren't in the base theme
        existing_tokens = {rule[0] if isinstance(rule[0], str) else str(rule[0]) for rule in existing_styles}
        for token, style in overrides.items():
            if token not in existing_tokens:
                new_rules.append((token, style))
        
        return Style(new_rules)
    
    @classmethod
    def get_theme_preview(cls, theme_name: str) -> str:
        """
        Get a preview string showing how the theme looks.
        
        Args:
            theme_name: Name of the theme to preview
            
        Returns:
            Multi-line string showing theme colors
        """
        theme = cls.get_theme(theme_name)
        if not theme:
            return f"Theme '{theme_name}' not found"
        
        # Get style information for key elements
        preview_lines = [
            f"Theme Preview: {theme_name.upper()}",
            "=" * 40,
            "Sample UI Elements:",
            "",
            "❓ Question text (question style)",
            "✓ Answer text (answer style)", 
            "ℹ  Instruction text (instruction style)",
            "",
            "Status Messages:",
            "✅ Success message (success style)",
            "❌ Error message (error style)",
            "⚠️  Warning message (warning style)",
            "ℹ️  Info message (info style)",
            "",
            "UI Components:",
            "▶ Selected item (selected style)",
            "☐ Checkbox unchecked (checkbox style)",
            "☑ Checkbox checked (checkbox-selected style)",
            "[Button] (button style)",
            "",
            f"Description: {cls.get_theme_description(theme_name) or 'No description available'}"
        ]
        
        return "\n".join(preview_lines)