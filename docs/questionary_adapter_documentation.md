# Questionary Style Adapter Documentation

## Overview

The `QuestionaryStyleAdapter` is a crucial bridge component that seamlessly integrates TUI Engine's existing styling system with Questionary's professional theme system. This adapter enables existing TUI Engine applications to benefit from enhanced styling while maintaining full backward compatibility.

## Key Features

- **Seamless Integration**: Bridges TUI Engine variants with Questionary style classes
- **Theme Management**: Dynamic theme switching and professional color schemes
- **Legacy Migration**: Easy migration from existing TUI Engine styling
- **Component-Specific Styling**: Specialized styling for different UI components
- **Backward Compatibility**: Preserves existing TUI Engine styling logic
- **Performance Optimized**: Caching for efficient style resolution

## Basic Usage

### Initialize the Adapter

```python
from tui_engine.questionary_adapter import QuestionaryStyleAdapter

# Initialize with default theme (Professional Blue)
adapter = QuestionaryStyleAdapter()

# Initialize with specific theme
adapter = QuestionaryStyleAdapter('dark_mode')

# Initialize with custom Style object
from tui_engine.themes import TUIEngineThemes
custom_theme = TUIEngineThemes.HIGH_CONTRAST
adapter = QuestionaryStyleAdapter(custom_theme)
```

### Basic Style Integration

```python
# Get Questionary style for prompts
style = adapter.get_questionary_style()

# Use with Questionary prompts
import questionary
name = questionary.text("Your name:", style=style).ask()
```

### TUI Engine Variant Mapping

```python
# Get style for TUI Engine variants
card_style = adapter.get_style_for_variant('card')
button_style = adapter.get_style_for_variant('button')

# Create complete variant mapping
all_variants = adapter.create_variant_style_mapping()
```

## Advanced Features

### Component-Specific Styling

```python
# Create style optimized for specific components
input_style = adapter.create_component_style('input')
button_style = adapter.create_component_style('button')

# Create style with custom overrides
custom_input_style = adapter.create_component_style('input', {
    'input_focused': 'fg:#00ff00 bold',  # Green focus
    'placeholder': 'fg:#888888 italic'   # Gray placeholder
})

# Use component-specific style
questionary.text("Username:", style=input_style).ask()
```

### Dynamic Theme Switching

```python
# Switch themes at runtime
adapter.set_theme('dark_mode')
adapter.set_theme('high_contrast')

# Get current theme name
current_theme = adapter.get_theme_name()
print(f"Current theme: {current_theme}")

# Switch to custom theme
custom = TUIEngineThemes.create_custom_theme('minimal', {
    'question': 'fg:#ff0000 bold'
})
adapter.set_theme(custom)
```

### Legacy Style Migration

```python
# Migrate existing TUI Engine styles
legacy_styles = {
    'card_title': 'fg:#0066cc bold',
    'input_text': 'fg:#333333',
    'button': {
        'default': 'fg:#ffffff bg:#0066cc',
        'hover': 'fg:#ffffff bg:#0033cc bold'
    }
}

# Convert to Questionary-compatible style
migrated_style = adapter.migrate_legacy_style(legacy_styles)

# Use migrated style
questionary.text("Input:", style=migrated_style).ask()
```

## Variant to Style Class Mapping

The adapter provides automatic mapping between TUI Engine variants and Questionary style classes:

| TUI Engine Variant | Primary Questionary Class | Use Case |
|-------------------|--------------------------|----------|
| `card` | `container_title` | Card headers and containers |
| `section` | `section_title` | Section headers |
| `header` | `container_title` | Page headers |
| `footer` | `text_muted` | Page footers |
| `button` | `button` | Interactive buttons |
| `input` | `input` | Text input fields |
| `select` | `selected` | Selection lists |
| `checkbox` | `checkbox` | Checkbox controls |
| `validation` | `validation_error` | Validation messages |
| `navigation` | `button` | Navigation elements |
| `form` | `input` | Form elements |
| `status` | `success` | Status messages |

## Specialized Style Collections

### Validation Styles

```python
# Get validation-specific styles
validation_styles = adapter.get_validation_styles()
# Returns: {
#     'valid': 'class:validation_success',
#     'invalid': 'class:validation_error',
#     'warning': 'class:warning',
#     'info': 'class:info'
# }

# Use validation styles
error_style = validation_styles['invalid']
```

### Navigation Styles

```python
# Get navigation-specific styles
nav_styles = adapter.get_navigation_styles()
# Returns: {
#     'button': 'class:button',
#     'button_focused': 'class:button_focused',
#     'button_disabled': 'class:button_disabled',
#     'selected': 'class:selected',
#     'highlighted': 'class:highlighted'
# }
```

## Integration with TUI Engine Components

### Enhanced Widget Styling

```python
from tui_engine.questionary_adapter import QuestionaryStyleAdapter
from tui_engine import Page, Container

# Create application with style adapter
adapter = QuestionaryStyleAdapter('professional_blue')

# Apply styling to TUI Engine components
page = Page("Styled Application")
container = Container("main_content")

# Use adapter for consistent styling
card_style = adapter.get_style_for_variant('card')
# Apply card_style to container...
```

### Form Integration

```python
class StyledForm:
    def __init__(self, theme='professional_blue'):
        self.adapter = QuestionaryStyleAdapter(theme)
        self.style = self.adapter.get_questionary_style()
    
    def get_user_input(self):
        name = questionary.text(
            "Name:", 
            style=self.style
        ).ask()
        
        email = questionary.text(
            "Email:", 
            style=self.style,
            validate=lambda x: '@' in x or "Valid email required"
        ).ask()
        
        return {'name': name, 'email': email}
```

## Performance Optimization

### Style Caching

The adapter includes built-in caching for optimal performance:

```python
# Styles are automatically cached
adapter = QuestionaryStyleAdapter('dark_mode')

# First call - computed and cached
style1 = adapter.get_style_for_variant('button')

# Second call - retrieved from cache
style2 = adapter.get_style_for_variant('button')

# Clear cache when changing themes
adapter.set_theme('high_contrast')  # Automatically clears cache
```

### Efficient Style Resolution

```python
# Pre-compute variant mappings for better performance
class OptimizedApp:
    def __init__(self):
        self.adapter = QuestionaryStyleAdapter('professional_blue')
        self.variant_map = self.adapter.create_variant_style_mapping()
        self.base_style = self.adapter.get_questionary_style()
    
    def get_style(self, variant):
        return self.variant_map.get(variant, 'class:text')
```

## Integration Examples

### Complete Application Example

```python
#!/usr/bin/env python3
from tui_engine.questionary_adapter import QuestionaryStyleAdapter
import questionary

class ThemedApplication:
    def __init__(self, theme='professional_blue'):
        self.adapter = QuestionaryStyleAdapter(theme)
        self.style = self.adapter.get_questionary_style()
    
    def run_configuration_wizard(self):
        # Project setup
        project_name = questionary.text(
            "Project name:",
            style=self.style,
            validate=lambda x: len(x) > 0 or "Name required"
        ).ask()
        
        # Environment selection
        environment = questionary.select(
            "Target environment:",
            choices=["Development", "Staging", "Production"],
            style=self.style
        ).ask()
        
        # Feature selection
        features = questionary.checkbox(
            "Select features:",
            choices=[
                "Authentication",
                "Database",
                "Caching",
                "Monitoring"
            ],
            style=self.style
        ).ask()
        
        # Confirmation
        confirm = questionary.confirm(
            f"Create '{project_name}' for {environment}?",
            style=self.style
        ).ask()
        
        if confirm:
            return {
                'name': project_name,
                'environment': environment,
                'features': features
            }
        return None
    
    def change_theme(self, new_theme):
        self.adapter.set_theme(new_theme)
        self.style = self.adapter.get_questionary_style()

# Usage
app = ThemedApplication('dark_mode')
config = app.run_configuration_wizard()
if config:
    print(f"Configuration: {config}")
```

### Legacy Migration Example

```python
# Before: Legacy TUI Engine styling
legacy_config = {
    'card_style': 'fg:#0066cc bold',
    'input_style': 'fg:#333333',
    'button_styles': {
        'primary': 'fg:#ffffff bg:#0066cc',
        'secondary': 'fg:#0066cc bg:#ffffff'
    }
}

# After: Migrated with adapter
adapter = QuestionaryStyleAdapter('professional_blue')
modern_style = adapter.migrate_legacy_style(legacy_config)

# Use migrated style
questionary.text("Input:", style=modern_style).ask()
```

## Troubleshooting

### Common Issues

1. **Style not applying**
   ```python
   # Ensure style is passed to Questionary prompts
   style = adapter.get_questionary_style()
   questionary.text("Question:", style=style).ask()  # ✅ Correct
   ```

2. **Theme not found**
   ```python
   try:
       adapter = QuestionaryStyleAdapter('invalid_theme')
   except ValueError as e:
       print(f"Theme error: {e}")
       # Fall back to default
       adapter = QuestionaryStyleAdapter()
   ```

3. **Custom style issues**
   ```python
   # Verify style format
   custom_overrides = {
       'question': 'fg:#ff0000 bold',    # ✅ Correct format
       'answer': 'blue bold',            # ❌ Use fg: prefix
   }
   ```

### Debug Style Mapping

```python
def debug_adapter(adapter):
    """Debug adapter style mapping."""
    print("=== Adapter Debug Info ===")
    print(f"Current theme: {adapter.get_theme_name()}")
    
    # Show variant mappings
    mappings = adapter.create_variant_style_mapping()
    print("\nVariant mappings:")
    for variant, style in mappings.items():
        print(f"  {variant} → {style}")
    
    # Show preview
    preview = adapter.preview_style_mapping()
    print(f"\nPreview:\n{preview}")

# Usage
adapter = QuestionaryStyleAdapter('dark_mode')
debug_adapter(adapter)
```

## Best Practices

### 1. Theme Selection

```python
# Choose themes based on use case
business_app = QuestionaryStyleAdapter('professional_blue')
dev_tool = QuestionaryStyleAdapter('dark_mode')
accessible_app = QuestionaryStyleAdapter('high_contrast')
```

### 2. Component Organization

```python
class ComponentStyleManager:
    def __init__(self, theme='professional_blue'):
        self.adapter = QuestionaryStyleAdapter(theme)
        
        # Pre-create component-specific styles
        self.input_style = self.adapter.create_component_style('input')
        self.button_style = self.adapter.create_component_style('button')
        self.validation_style = self.adapter.create_component_style('validation')
    
    def get_input_prompt(self, message, **kwargs):
        return questionary.text(message, style=self.input_style, **kwargs)
    
    def get_confirm_prompt(self, message, **kwargs):
        return questionary.confirm(message, style=self.button_style, **kwargs)
```

### 3. Performance Optimization

```python
# Cache styles for better performance
class CachedStyleAdapter:
    def __init__(self, theme):
        self.adapter = QuestionaryStyleAdapter(theme)
        self._style_cache = {}
    
    def get_cached_style(self, variant):
        if variant not in self._style_cache:
            self._style_cache[variant] = self.adapter.get_style_for_variant(variant)
        return self._style_cache[variant]
```

## API Reference

### QuestionaryStyleAdapter Class

#### Constructor
- `__init__(theme=None)`: Initialize adapter with optional theme

#### Theme Management
- `get_questionary_style()`: Get current Questionary Style object
- `set_theme(theme)`: Change current theme
- `get_theme_name()`: Get current theme name (if built-in)

#### Style Mapping
- `get_style_for_variant(variant)`: Get style for TUI Engine variant
- `create_variant_style_mapping()`: Create complete variant mapping
- `get_style_for_component(component_type, state=None)`: Get component-specific style

#### Style Creation
- `create_component_style(component_type, custom_overrides=None)`: Create optimized component style
- `create_combined_style(additional_rules=None)`: Create combined style with additional rules
- `migrate_legacy_style(legacy_style)`: Migrate legacy styling

#### Specialized Styles
- `get_validation_styles()`: Get validation state styles
- `get_navigation_styles()`: Get navigation element styles

#### Utilities
- `preview_style_mapping()`: Generate style mapping preview
- `apply_variant_styling(variant, base_style=None)`: Apply variant styling

## Status

**COMPLETED** ✅ - QuestionaryStyleAdapter is ready for production use.

The adapter provides:
- ✅ Seamless TUI Engine to Questionary style bridging
- ✅ Full backward compatibility with existing code
- ✅ Professional theme integration
- ✅ Component-specific styling optimization
- ✅ Legacy migration capabilities
- ✅ Performance optimization with caching
- ✅ Comprehensive documentation and examples