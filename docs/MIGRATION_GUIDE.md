# Migration Guide: From Questionary to TUI Engine

This guide helps you migrate from standalone questionary usage to TUI Engine's integrated questionary system with enhanced features.

## Table of Contents

1. [Why Migrate?](#why-migrate)
2. [Installation](#installation)
3. [Basic Migration](#basic-migration)
4. [Advanced Features](#advanced-features)
5. [Common Patterns](#common-patterns)
6. [Breaking Changes](#breaking-changes)
7. [Best Practices](#best-practices)
8. [Troubleshooting](#troubleshooting)

---

## Why Migrate?

TUI Engine's questionary integration provides:

- **Professional Themes**: 5 polished themes with accessibility features
- **Comprehensive Validation**: Built-in validators with fluent chaining
- **Dynamic Forms**: Schema-based forms with conditional logic
- **State Management**: Persistent form state with export/import
- **Performance**: Optimized for large forms and concurrent usage
- **Integration**: Seamless integration with existing TUI Engine components

---

## Installation

### Replace Questionary Dependency

**Before (questionary only):**
```bash
pip install questionary
```

**After (TUI Engine with questionary integration):**
```bash
pip install tui-engine
```

TUI Engine includes questionary compatibility, so no separate questionary installation is needed.

---

## Basic Migration

### Simple Prompts

**Before (questionary):**
```python
import questionary

name = questionary.text("What's your name?").ask()
email = questionary.text("What's your email?").ask()
```

**After (TUI Engine):**
```python
from tui_engine.form_builder import FormBuilder, FieldDefinition, FieldType

# Create form builder
builder = FormBuilder("professional_blue")
schema = builder.create_form("user_info", "User Information")

# Add fields
builder.add_field("user_info", FieldDefinition("name", FieldType.TEXT, label="What's your name?"))
builder.add_field("user_info", FieldDefinition("email", FieldType.EMAIL, label="What's your email?"))

# Build and use form
form = builder.build_form("user_info")

# In a real interactive session, this would prompt the user
# For now, we'll simulate with direct value setting
form.set_field_value("name", "John Doe")
form.set_field_value("email", "john@example.com")

# Get values
name = form.get_field_value("name")
email = form.get_field_value("email")
```

### Select Prompts

**Before (questionary):**
```python
import questionary

choice = questionary.select(
    "What's your favorite color?",
    choices=["Red", "Green", "Blue"]
).ask()
```

**After (TUI Engine):**
```python
from tui_engine.form_builder import FormBuilder, FieldDefinition, FieldType

builder = FormBuilder("professional_blue")
schema = builder.create_form("preferences", "Preferences")

builder.add_field("preferences", FieldDefinition(
    "color",
    FieldType.SELECT,
    label="What's your favorite color?",
    choices={"red": "Red", "green": "Green", "blue": "Blue"}
))

form = builder.build_form("preferences")
form.set_field_value("color", "blue")
choice = form.get_field_value("color")
```

### Checkbox Prompts

**Before (questionary):**
```python
import questionary

features = questionary.checkbox(
    "Select features:",
    choices=["Feature A", "Feature B", "Feature C"]
).ask()
```

**After (TUI Engine):**
```python
from tui_engine.form_builder import FormBuilder, FieldDefinition, FieldType

builder = FormBuilder("professional_blue")
schema = builder.create_form("features", "Feature Selection")

builder.add_field("features", FieldDefinition(
    "selected_features",
    FieldType.MULTI_SELECT,
    label="Select features:",
    choices={"a": "Feature A", "b": "Feature B", "c": "Feature C"}
))

form = builder.build_form("features")
form.set_field_value("selected_features", ["a", "c"])
features = form.get_field_value("selected_features")
```

### Confirmation Prompts

**Before (questionary):**
```python
import questionary

confirmed = questionary.confirm("Do you want to continue?").ask()
```

**After (TUI Engine):**
```python
from tui_engine.form_builder import FormBuilder, FieldDefinition, FieldType

builder = FormBuilder("professional_blue")
schema = builder.create_form("confirmation", "Confirmation")

builder.add_field("confirmation", FieldDefinition(
    "continue",
    FieldType.CONFIRM,
    label="Do you want to continue?"
))

form = builder.build_form("confirmation")
form.set_field_value("continue", True)
confirmed = form.get_field_value("continue")
```

---

## Advanced Features

### Validation

**Before (questionary with custom validation):**
```python
import questionary

def validate_email(text):
    return "@" in text or "Please enter a valid email"

email = questionary.text(
    "Email:",
    validate=validate_email
).ask()
```

**After (TUI Engine with built-in validation):**
```python
from tui_engine.form_builder import FormBuilder, FieldDefinition, FieldType

builder = FormBuilder("professional_blue")
schema = builder.create_form("contact", "Contact Info")

builder.add_field("contact", FieldDefinition(
    "email",
    FieldType.EMAIL,  # Built-in email validation
    label="Email:",
    required=True,
    validation_message="Please enter a valid email"
))

form = builder.build_form("contact")
form.set_field_value("email", "user@example.com")

# Validation happens automatically
is_valid = form.validate_form()
```

### Theming

**Before (questionary with custom styles):**
```python
import questionary
from questionary import Style

custom_style = Style([
    ('question', 'fg:#ff0066 bold'),
    ('answer', 'fg:#44ff00 bold'),
])

name = questionary.text("Name:", style=custom_style).ask()
```

**After (TUI Engine with professional themes):**
```python
from tui_engine.form_builder import FormBuilder, FieldDefinition, FieldType
from tui_engine.themes import TUIEngineThemes

# Use professional theme
builder = FormBuilder("dark_mode")  # or any other theme

# Or create custom theme
custom_theme = TUIEngineThemes.create_custom_theme(
    "professional_blue",
    {
        'question': 'fg:#ff0066 bold',
        'answer': 'fg:#44ff00 bold'
    }
)

schema = builder.create_form("styled", "Styled Form")
builder.add_field("styled", FieldDefinition("name", FieldType.TEXT, label="Name:"))

form = builder.build_form("styled")
```

### Conditional Logic

**Before (questionary with manual flow control):**
```python
import questionary

user_type = questionary.select(
    "User type:",
    choices=["Individual", "Business"]
).ask()

if user_type == "Business":
    company = questionary.text("Company name:").ask()
```

**After (TUI Engine with declarative conditions):**
```python
from tui_engine.form_builder import FormBuilder, FieldDefinition, FieldType

builder = FormBuilder("professional_blue")
schema = builder.create_form("registration", "Registration")

# User type field
builder.add_field("registration", FieldDefinition(
    "user_type",
    FieldType.SELECT,
    label="User type:",
    choices={"individual": "Individual", "business": "Business"}
))

# Conditional company field
builder.add_field("registration", FieldDefinition(
    "company",
    FieldType.TEXT,
    label="Company name:",
    condition={
        "field": "user_type",
        "operator": "equals",
        "value": "business"
    }
))

form = builder.build_form("registration")
form.set_field_value("user_type", "business")
# Company field automatically becomes visible
```

---

## Common Patterns

### Multi-Question Workflows

**Before (questionary sequence):**
```python
import questionary

def collect_user_info():
    answers = {}
    
    answers['name'] = questionary.text("Name:").ask()
    answers['email'] = questionary.text("Email:").ask()
    answers['age'] = questionary.text("Age:").ask()
    
    if int(answers['age']) >= 18:
        answers['newsletter'] = questionary.confirm("Subscribe to newsletter?").ask()
    
    return answers

user_info = collect_user_info()
```

**After (TUI Engine form):**
```python
from tui_engine.form_builder import FormBuilder, FieldDefinition, FieldType

def create_user_info_form():
    builder = FormBuilder("professional_blue")
    schema = builder.create_form("user_info", "User Information")
    
    fields = [
        FieldDefinition("name", FieldType.TEXT, label="Name:", required=True),
        FieldDefinition("email", FieldType.EMAIL, label="Email:", required=True),
        FieldDefinition("age", FieldType.INTEGER, label="Age:", required=True, min_value=1, max_value=120),
        FieldDefinition(
            "newsletter",
            FieldType.CONFIRM,
            label="Subscribe to newsletter?",
            condition={
                "field": "age",
                "operator": "greater_equal",
                "value": 18
            }
        )
    ]
    
    for field in fields:
        builder.add_field("user_info", field)
    
    return builder.build_form("user_info")

form = create_user_info_form()

# Set values (in real usage, this would be interactive)
form.set_field_value("name", "John Doe")
form.set_field_value("email", "john@example.com")
form.set_field_value("age", 25)
form.set_field_value("newsletter", True)

# Export all data
user_info = form.export_data()
```

### Complex Validation

**Before (questionary with multiple validation functions):**
```python
import questionary
import re

def validate_password(password):
    if len(password) < 8:
        return "Password must be at least 8 characters"
    if not re.search(r'[A-Z]', password):
        return "Password must contain uppercase letter"
    if not re.search(r'[0-9]', password):
        return "Password must contain number"
    return True

def validate_confirm_password(confirm):
    if confirm != password:
        return "Passwords don't match"
    return True

password = questionary.password("Password:", validate=validate_password).ask()
confirm = questionary.password("Confirm:", validate=validate_confirm_password).ask()
```

**After (TUI Engine with validation chains):**
```python
from tui_engine.form_builder import FormBuilder, FieldDefinition, FieldType
from tui_engine.validation import create_form_validator

builder = FormBuilder("professional_blue")
schema = builder.create_form("password_form", "Set Password")

# Add fields
builder.add_field("password_form", FieldDefinition(
    "password",
    FieldType.PASSWORD,
    label="Password:",
    required=True,
    min_length=8
))

builder.add_field("password_form", FieldDefinition(
    "confirm_password",
    FieldType.PASSWORD,
    label="Confirm Password:",
    required=True
))

form = builder.build_form("password_form")

# Set values
form.set_field_value("password", "MyStr0ngP@ss")
form.set_field_value("confirm_password", "MyStr0ngP@ss")

# Validation with custom cross-field validation
def validate_passwords():
    password = form.get_field_value("password")
    confirm = form.get_field_value("confirm_password")
    
    # Built-in validation first
    if not form.validate_form():
        return False
    
    # Custom cross-field validation
    if password != confirm:
        # In real implementation, you'd add this error to the form
        print("Passwords don't match")
        return False
    
    return True

is_valid = validate_passwords()
```

### Data Persistence

**Before (questionary with manual saving):**
```python
import questionary
import json

def save_answers(answers, filename):
    with open(filename, 'w') as f:
        json.dump(answers, f)

def load_answers(filename):
    try:
        with open(filename, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

# Load previous answers
previous = load_answers('config.json')

name = questionary.text("Name:", default=previous.get('name', '')).ask()
email = questionary.text("Email:", default=previous.get('email', '')).ask()

answers = {'name': name, 'email': email}
save_answers(answers, 'config.json')
```

**After (TUI Engine with built-in serialization):**
```python
from tui_engine.form_builder import FormBuilder, FieldDefinition, FieldType
import json
import os

def create_config_form():
    builder = FormBuilder("professional_blue")
    schema = builder.create_form("config", "Configuration")
    
    fields = [
        FieldDefinition("name", FieldType.TEXT, label="Name:"),
        FieldDefinition("email", FieldType.EMAIL, label="Email:")
    ]
    
    for field in fields:
        builder.add_field("config", field)
    
    return builder.build_form("config")

def save_form_data(form, filename):
    data = form.export_data()
    with open(filename, 'w') as f:
        json.dump(data, f)

def load_form_data(form, filename):
    if os.path.exists(filename):
        with open(filename, 'r') as f:
            data = json.load(f)
            form.import_data(data)

# Create form
form = create_config_form()

# Load previous data
load_form_data(form, 'config.json')

# Set new values (in real usage, this would be interactive)
form.set_field_value("name", "John Doe")
form.set_field_value("email", "john@example.com")

# Save data
save_form_data(form, 'config.json')
```

---

## Breaking Changes

### Import Changes

**Before:**
```python
import questionary
from questionary import Style, Choice
```

**After:**
```python
from tui_engine.form_builder import FormBuilder, FieldDefinition, FieldType
from tui_engine.themes import TUIEngineThemes
from tui_engine.questionary_adapter import QuestionaryStyleAdapter
```

### Style Definition Changes

**Before:**
```python
style = Style([
    ('question', 'fg:#ff0066 bold'),
    ('answer', 'fg:#44ff00 bold'),
])
```

**After:**
```python
# Use predefined theme
form = FormBuilder("professional_blue")

# Or create custom theme
custom_style = TUIEngineThemes.create_custom_theme(
    "professional_blue",
    {
        'question': 'fg:#ff0066 bold',
        'answer': 'fg:#44ff00 bold'
    }
)
```

### Validation Changes

**Before:**
```python
def validate_email(text):
    return "@" in text or "Invalid email"

email = questionary.text("Email:", validate=validate_email).ask()
```

**After:**
```python
# Built-in validation
field = FieldDefinition("email", FieldType.EMAIL, required=True)

# Or custom validation
from tui_engine.validation import create_form_validator

validator = create_form_validator()
email_chain = validator.add_field("email")
email_chain.required().email()
```

### Choice Definition Changes

**Before:**
```python
from questionary import Choice

choices = [
    Choice("Option 1", value="opt1"),
    Choice("Option 2", value="opt2"),
]

selection = questionary.select("Choose:", choices=choices).ask()
```

**After:**
```python
field = FieldDefinition(
    "selection",
    FieldType.SELECT,
    label="Choose:",
    choices={"opt1": "Option 1", "opt2": "Option 2"}
)
```

---

## Best Practices

### 1. Use Professional Themes

**Recommended:**
```python
# Use built-in professional themes
builder = FormBuilder("professional_blue")  # or "dark_mode", "high_contrast"
```

**Avoid:**
```python
# Don't create forms without themes
builder = FormBuilder()  # Uses default but not optimized
```

### 2. Leverage Built-in Validation

**Recommended:**
```python
# Use typed fields with built-in validation
FieldDefinition("email", FieldType.EMAIL, required=True)
FieldDefinition("phone", FieldType.PHONE, required=True)
FieldDefinition("url", FieldType.URL)
```

**Avoid:**
```python
# Don't use generic text fields for structured data
FieldDefinition("email", FieldType.TEXT)  # No validation
```

### 3. Use Conditional Logic

**Recommended:**
```python
# Declarative conditional logic
FieldDefinition(
    "company_details",
    FieldType.TEXT,
    condition={"field": "user_type", "operator": "equals", "value": "business"}
)
```

**Avoid:**
```python
# Manual flow control
if user_type == "business":
    # Create additional form...
```

### 4. Validate Early and Often

**Recommended:**
```python
# Validate on form submission
if form.validate_form():
    result = form.submit()
else:
    errors = form.get_validation_errors()
    # Handle errors
```

**Avoid:**
```python
# Don't skip validation
result = form.submit()  # Could submit invalid data
```

### 5. Use Form Serialization

**Recommended:**
```python
# Save and restore form state
data = form.export_data()
# ... later ...
form.import_data(data)
```

**Avoid:**
```python
# Don't manually track form state
name = form.get_field_value("name")
email = form.get_field_value("email")
# Manual state tracking...
```

---

## Troubleshooting

### Common Issues

#### 1. Theme Not Applied

**Problem:**
```python
builder = FormBuilder("invalid_theme_name")
```

**Solution:**
```python
# Check available themes
from tui_engine.themes import TUIEngineThemes
themes = TUIEngineThemes.list_themes()
print("Available themes:", themes)

# Use valid theme
builder = FormBuilder("professional_blue")
```

#### 2. Validation Not Working

**Problem:**
```python
field = FieldDefinition("email", FieldType.TEXT)  # No validation
```

**Solution:**
```python
field = FieldDefinition("email", FieldType.EMAIL, required=True)  # Built-in validation
```

#### 3. Conditional Fields Not Showing

**Problem:**
```python
# Incorrect condition syntax
condition={"field": "type", "operator": "equal", "value": "business"}  # Wrong operator
```

**Solution:**
```python
# Correct condition syntax
condition={"field": "type", "operator": "equals", "value": "business"}  # Correct operator
```

#### 4. Form Data Not Persisting

**Problem:**
```python
form.set_field_value("name", "John")
# Form reset elsewhere loses data
```

**Solution:**
```python
# Export data before operations that might reset
data = form.export_data()
# ... do operations ...
form.import_data(data)  # Restore if needed
```

### Migration Checklist

- [ ] Replace questionary imports with TUI Engine imports
- [ ] Convert prompt calls to form field definitions
- [ ] Replace custom styles with TUI Engine themes
- [ ] Update validation to use built-in validators
- [ ] Convert manual flow control to conditional logic
- [ ] Add proper error handling for form validation
- [ ] Test with all target themes
- [ ] Verify data persistence if needed
- [ ] Update documentation and examples

### Getting Help

1. **Check API Documentation**: See `docs/API_REFERENCE.md`
2. **Review Examples**: Look at `demos/` directory
3. **Run Integration Tests**: Use `demos/integration_test.py`
4. **Performance Benchmarks**: Run `demos/performance_benchmark.py`

---

## Summary

TUI Engine's questionary integration provides a significant upgrade over standalone questionary usage:

- **Enhanced Developer Experience**: Type-safe field definitions, built-in validation, professional themes
- **Advanced Features**: Conditional logic, form serialization, state management
- **Better Performance**: Optimized for large forms and concurrent usage
- **Professional Polish**: Accessibility-compliant themes and comprehensive error handling

The migration effort is worthwhile for any serious terminal application development, providing a solid foundation for building sophisticated user interfaces.