# TUI Engine Themes System

## Overview

The TUI Engine Themes system provides a comprehensive set of professional color schemes and styling options that integrate seamlessly with both TUI Engine components and Questionary prompts. This system ensures consistent, accessible, and visually appealing interfaces across all TUI applications.

## Features

- **5 Professional Themes**: Carefully crafted color schemes for different use cases
- **Accessibility Compliant**: High contrast ratios and readable color combinations
- **Questionary Integration**: Full compatibility with Questionary's styling system
- **Custom Theme Creation**: Easy customization and theme extension
- **Dynamic Theme Switching**: Runtime theme changes and global coordination

## Available Themes

### 1. Professional Blue (`PROFESSIONAL_BLUE`)
- **Use Case**: Business applications, corporate environments
- **Colors**: Blue-based palette with professional appearance
- **Accessibility**: WCAG AA compliant contrast ratios
- **Best For**: Enterprise software, client-facing applications

### 2. Dark Mode (`DARK_MODE`)
- **Use Case**: Extended use, low-light environments
- **Colors**: Dark backgrounds with bright accents
- **Accessibility**: Reduced eye strain, high contrast
- **Best For**: Development tools, late-night coding sessions

### 3. High Contrast (`HIGH_CONTRAST`)
- **Use Case**: Maximum accessibility, visual impairments
- **Colors**: Black and white with minimal color usage
- **Accessibility**: Maximum contrast ratios, screen reader friendly
- **Best For**: Accessibility-required applications, kiosks

### 4. Classic Terminal (`CLASSIC_TERMINAL`)
- **Use Case**: Retro computing feel, system administration
- **Colors**: Green-on-black traditional terminal styling
- **Accessibility**: High contrast, familiar to sysadmins
- **Best For**: System tools, DevOps interfaces, nostalgic applications

### 5. Minimal (`MINIMAL`)
- **Use Case**: Clean, distraction-free interfaces
- **Colors**: Black and white with minimal visual elements
- **Accessibility**: Simple, clear, easy to read
- **Best For**: Documentation tools, text-heavy applications

## Basic Usage

### Import and Use Predefined Theme

```python
from tui_engine.themes import TUIEngineThemes
import questionary

# Use a predefined theme
theme = TUIEngineThemes.PROFESSIONAL_BLUE

# Apply to Questionary prompt
name = questionary.text(
    "What's your name?",
    style=theme
).ask()
```

### Dynamic Theme Selection

```python
# Get theme by name
theme_name = 'dark_mode'
theme = TUIEngineThemes.get_theme(theme_name)

if theme:
    choice = questionary.select(
        "Choose an option:",
        choices=["Option 1", "Option 2", "Option 3"],
        style=theme
    ).ask()
```

### List Available Themes

```python
# Get all available themes
themes = TUIEngineThemes.list_themes()
for theme_name in themes:
    description = TUIEngineThemes.get_theme_description(theme_name)
    print(f"{theme_name}: {description}")
```

## Custom Theme Creation

### Basic Customization

```python
# Create custom theme based on existing theme
custom_theme = TUIEngineThemes.create_custom_theme(
    'professional_blue',  # Base theme
    {
        'question': 'fg:#ff0000 bold',      # Red questions
        'answer': 'fg:#00ff00 bold',        # Green answers
        'success': 'fg:#0000ff bold',       # Blue success messages
    }
)

# Use custom theme
prompt = questionary.confirm(
    "Do you like this custom theme?",
    style=custom_theme
).ask()
```

### Advanced Customization

```python
# Create theme with extensive customization
advanced_custom = TUIEngineThemes.create_custom_theme(
    'dark_mode',
    {
        # Questions and prompts
        'question': 'fg:#ffffff bg:#1e40af bold',
        'instruction': 'fg:#94a3b8 italic',
        'answer': 'fg:#34d399 bold',
        
        # Status messages
        'success': 'fg:#10b981 bold',
        'error': 'fg:#ef4444 bold',
        'warning': 'fg:#f59e0b bold',
        
        # UI elements
        'highlighted': 'bg:#7c3aed fg:#ffffff bold',
        'selected': 'fg:#a78bfa bold',
        'button': 'fg:#ffffff bg:#7c3aed',
        'button_focused': 'fg:#ffffff bg:#6d28d9 bold',
    }
)
```

## Style Classes Reference

### Core Prompt Elements
- `question`: Main question text
- `answered_question`: Questions that have been answered
- `instruction`: Helper text and instructions
- `answer`: User's answer text

### UI Components
- `highlighted`: Highlighted/focused items
- `selected`: Selected items in lists
- `pointer`: Selection pointer/cursor
- `checkbox`: Checkbox styling
- `checkbox-selected`: Selected checkbox styling

### Status and Feedback
- `success`: Success messages and indicators
- `error`: Error messages and validation failures
- `warning`: Warning messages
- `info`: Information messages

### Layout and Structure
- `container_title`: Container/section titles
- `section_title`: Section headers
- `border`: Border elements
- `separator`: Visual separators

### Navigation and Controls
- `button`: Button styling
- `button_focused`: Focused button styling
- `button_disabled`: Disabled button styling

### Text and Content
- `text`: Primary text content
- `text_secondary`: Secondary text
- `text_muted`: Muted/disabled text
- `text_inverse`: Inverse text (light on dark)

### Form Elements
- `input`: Input field text
- `input_focused`: Focused input field
- `placeholder`: Placeholder text
- `validation_error`: Validation error messages
- `validation_success`: Validation success indicators

## Integration with TUI Engine Components

### Using Themes in TUI Engine Applications

```python
from tui_engine import Page, Container, TUIEngineThemes
from tui_engine.app import Application

# Create application with theme
app = Application()
theme = TUIEngineThemes.PROFESSIONAL_BLUE

# Apply theme to application
app.set_style(theme)

# Create page with themed components
page = Page("My Application")
container = Container("main_content")

# Components will automatically use the application theme
page.add(container)
app.add_page("main", page)
```

### Theme-Aware Component Creation

```python
# Custom component that respects theme settings
class ThemedComponent:
    def __init__(self, name: str, theme=None):
        self.name = name
        self.theme = theme or TUIEngineThemes.PROFESSIONAL_BLUE
    
    def render(self):
        return questionary.text(
            f"Enter {self.name}:",
            style=self.theme
        )
```

## Theme Preview and Testing

### Generate Theme Preview

```python
# Get a preview of how a theme looks
preview = TUIEngineThemes.get_theme_preview('professional_blue')
print(preview)
```

### Test Theme with Different Components

```python
def test_theme(theme_name: str):
    theme = TUIEngineThemes.get_theme(theme_name)
    
    # Test different prompt types
    questionary.text("Text input test", style=theme).ask()
    questionary.select("Select test", choices=["A", "B"], style=theme).ask()
    questionary.confirm("Confirm test", style=theme).ask()
```

## Best Practices

### 1. Theme Selection Guidelines

- **Professional Blue**: Business applications, client interfaces
- **Dark Mode**: Developer tools, extended-use applications
- **High Contrast**: Accessibility-critical applications
- **Classic Terminal**: System administration, DevOps tools
- **Minimal**: Documentation, text-heavy interfaces

### 2. Accessibility Considerations

```python
# Always consider accessibility when customizing themes
accessible_theme = TUIEngineThemes.create_custom_theme(
    'high_contrast',  # Start with accessible base
    {
        # Ensure sufficient contrast ratios
        'question': 'fg:#000000 bg:#ffffff bold',
        'error': 'fg:#ffffff bg:#dc2626 bold',
    }
)
```

### 3. Consistent Application Theming

```python
class ThemedApplication:
    def __init__(self, theme_name='professional_blue'):
        self.theme = TUIEngineThemes.get_theme(theme_name)
        self.setup_components()
    
    def setup_components(self):
        # Apply theme consistently across all components
        self.login_prompt = questionary.text("Username:", style=self.theme)
        self.menu = questionary.select("Choose:", choices=[], style=self.theme)
        
    def change_theme(self, new_theme_name: str):
        self.theme = TUIEngineThemes.get_theme(new_theme_name)
        self.setup_components()  # Recreate with new theme
```

### 4. Performance Considerations

```python
# Cache themes for better performance
class ThemeManager:
    def __init__(self):
        self._cache = {}
    
    def get_theme(self, name: str):
        if name not in self._cache:
            self._cache[name] = TUIEngineThemes.get_theme(name)
        return self._cache[name]
```

## Examples and Demos

### Complete Application Example

```python
#!/usr/bin/env python3
from tui_engine.themes import TUIEngineThemes
import questionary

def main():
    # Let user choose theme
    theme_choice = questionary.select(
        "Choose application theme:",
        choices=TUIEngineThemes.list_themes()
    ).ask()
    
    theme = TUIEngineThemes.get_theme(theme_choice)
    
    # Use theme throughout application
    name = questionary.text("Your name:", style=theme).ask()
    
    features = questionary.checkbox(
        "Select features:",
        choices=["Feature A", "Feature B", "Feature C"],
        style=theme
    ).ask()
    
    confirm = questionary.confirm(
        f"Hello {name}, proceed with {len(features)} features?",
        style=theme
    ).ask()
    
    if confirm:
        print("✅ Application configured successfully!")

if __name__ == "__main__":
    main()
```

### Theme Switching Example

```python
class DynamicThemeApp:
    def __init__(self):
        self.current_theme = 'professional_blue'
        
    def show_theme_menu(self):
        new_theme = questionary.select(
            "Switch to theme:",
            choices=TUIEngineThemes.list_themes(),
            style=TUIEngineThemes.get_theme(self.current_theme)
        ).ask()
        
        if new_theme:
            self.current_theme = new_theme
            print(f"Switched to {new_theme}")
    
    def run_with_current_theme(self):
        theme = TUIEngineThemes.get_theme(self.current_theme)
        questionary.text("Test input:", style=theme).ask()
```

## Migration from Existing Styling

If you're upgrading from custom styling to TUI Engine Themes:

### 1. Identify Current Colors

```python
# Old custom styling
old_style = Style([
    ('question', 'fg:#0066cc bold'),
    ('answer', 'fg:#00cc00'),
])

# Find similar TUI Engine theme
# professional_blue has similar blue-based scheme
new_theme = TUIEngineThemes.PROFESSIONAL_BLUE
```

### 2. Create Transition Theme

```python
# Create bridge theme with your existing colors
transition_theme = TUIEngineThemes.create_custom_theme(
    'professional_blue',
    {
        'question': 'fg:#0066cc bold',  # Your existing color
        'answer': 'fg:#00cc00',        # Your existing color
    }
)
```

### 3. Gradual Migration

```python
# Phase 1: Use transition theme
app.set_theme(transition_theme)

# Phase 2: Gradually adopt standard theme elements
# Phase 3: Move to full TUI Engine theme
app.set_theme(TUIEngineThemes.PROFESSIONAL_BLUE)
```

## Troubleshooting

### Common Issues

1. **Theme not applying**: Ensure theme is passed to `style` parameter
2. **Colors not showing**: Check terminal color support
3. **Custom theme errors**: Verify color format (e.g., `fg:#ffffff`)

### Debug Theme Issues

```python
def debug_theme(theme_name: str):
    theme = TUIEngineThemes.get_theme(theme_name)
    if not theme:
        print(f"❌ Theme '{theme_name}' not found")
        return
    
    print(f"✅ Theme '{theme_name}' loaded successfully")
    
    # Test basic functionality
    try:
        prompt = questionary.text("Test", style=theme)
        print("✅ Theme creates prompts successfully")
    except Exception as e:
        print(f"❌ Theme error: {e}")
```

## Status

**COMPLETED** ✅ - TUIEngineThemes system is ready for production use.

The theme system provides:
- ✅ 5 professional, accessible themes
- ✅ Full Questionary integration
- ✅ Custom theme creation capabilities
- ✅ Comprehensive documentation and examples
- ✅ Performance optimization and caching support