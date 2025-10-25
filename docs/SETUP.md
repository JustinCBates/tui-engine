# Questionary Extended - Development Setup

## Quick Start

This package extends the excellent `questionary` library with advanced input types, enhanced UI components, and workflow management features.

## Installation for Development

1. **Install Poetry** (if not already installed):

   ```powershell
   (Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | python -
   ```

2. **Install dependencies**:

   ```powershell
   poetry install --with dev,test
   ```

3. **Activate the virtual environment**:

   ```powershell
   poetry shell
   ```

4. **Test the installation**:
   ```powershell
   python test_package.py
   ```

## Package Structure

```
questionary-extended/
├── src/questionary_extended/     # Main package code
│   ├── __init__.py              # Package exports
│   ├── prompts.py               # Enhanced prompt types
│   ├── components.py            # UI components
│   ├── validators.py            # Input validation
│   ├── styles.py                # Themes and styling
│   ├── utils.py                 # Utility functions
│   └── cli.py                   # Command-line interface
├── tests/                       # Test suite
├── examples/                    # Usage examples
├── pyproject.toml              # Poetry configuration
├── README.md                   # Package documentation
└── CONTRIBUTING.md             # Contribution guidelines
```

## Key Features

### 🎯 Advanced Input Types

- **Numeric Input**: `qe.number()`, `qe.integer()`, `qe.percentage()`
- **Date/Time**: `qe.date()`, `qe.time()`, `qe.datetime_input()`
- **Enhanced Text**: `qe.rich_text()`, `qe.enhanced_text()`
- **Rating**: `qe.rating()`, `qe.slider()`

### 🎨 Enhanced Selection

- **Tree Navigation**: `qe.tree_select()`, `qe.multi_level_select()`
- **Fuzzy Search**: `qe.fuzzy_select()`
- **Grouped Choices**: `qe.grouped_select()`
- **Tag Selection**: `qe.tag_select()`

### 🎪 Advanced Features

- **Forms**: `qe.form()` with validation and conditional logic
- **Wizards**: `qe.wizard()` with progress tracking
- **Themes**: Multiple built-in themes and custom styling
- **Validation**: Comprehensive validators for all input types

### 🔗 Integration

- **CLI Tool**: `qext` command for demos and testing
- **Rich Integration**: Beautiful formatting with the `rich` library
- **Async Support**: All prompts support async/await

## Usage Examples

### Basic Usage

```python
import questionary_extended as qe

# Enhanced numeric input
age = qe.number("Age?", min_value=0, max_value=150).ask()

# Date picker
from datetime import date
birthday = qe.date("Birthday?", max_date=date.today()).ask()

# Rating input
rating = qe.rating("Rate this (1-5):", max_rating=5).ask()
```

### Advanced Forms

```python
# Complex form with validation
result = qe.form([
    {
        "type": "text",
        "name": "name",
        "message": "Name:",
        "validate": lambda x: len(x) > 0
    },
    {
        "type": "number",
        "name": "age",
        "message": "Age:",
        "min_value": 18
    }
]).ask()
```

### Tree Selection

```python
choice = qe.tree_select(
    "Choose technology:",
    choices={
        "Frontend": ["React", "Vue", "Angular"],
        "Backend": ["Django", "Flask", "FastAPI"],
        "Database": ["PostgreSQL", "MongoDB"]
    }
).ask()
```

## Testing the Package

Run the test script to verify everything works:

```powershell
poetry run python test_package.py
```

Or run the CLI demo:

```powershell
poetry run qext demo
```

## Development Commands

```powershell
# Install package in development mode
poetry install

# Run tests
poetry run pytest

# Format code
poetry run black src/ tests/

# Type checking
poetry run mypy src/

# Build package
poetry build

# Publish to PyPI (when ready)
poetry publish
```

## Next Steps

1. **Implement Core Features**: Complete the prompt implementations
2. **Add Tests**: Comprehensive test coverage
3. **Documentation**: Detailed API docs and tutorials
4. **Examples**: Real-world usage examples
5. **Publishing**: Prepare for PyPI release

This package is designed to be a comprehensive extension to questionary, providing everything needed for sophisticated CLI applications.
