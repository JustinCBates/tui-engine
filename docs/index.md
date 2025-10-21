# Questionary Extended Documentation

Welcome to the documentation for **Questionary Extended**, an advanced extension library for the popular `questionary` CLI prompt package.

## Quick Links

- [Installation Guide](installation.md)
- [Quick Start Tutorial](quickstart.md)
- [API Reference](api/index.md)
- [Examples](examples/index.md)
- [Contributing](../CONTRIBUTING.md)

## Overview

Questionary Extended builds upon the excellent [questionary](https://github.com/tmbo/questionary) library to provide:

### 🎯 Advanced Input Types
- **Numeric Input**: Integer/float with range validation and formatting
- **Date/Time Input**: Smart date pickers with validation
- **Color Input**: Hex, RGB, HSL color selection with preview
- **Rating Input**: Star ratings, sliders, and scales
- **Rich Text**: Markdown-enabled text with syntax highlighting

### 🎨 Enhanced Selection
- **Tree Navigation**: Hierarchical menu systems
- **Fuzzy Search**: Smart search with ranking
- **Grouped Choices**: Categorized selections
- **Multi-Tag Input**: Tag selection with auto-completion

### 🎪 Advanced Features
- **Forms**: Complex forms with validation and conditional logic
- **Wizards**: Multi-step workflows with progress tracking
- **Table Input**: Spreadsheet-like data entry
- **Theming**: Beautiful built-in themes and custom styling

### 🔗 Integration
- **Drop-in Compatibility**: Works alongside existing questionary code
- **Rich Integration**: Beautiful formatting with the rich library
- **Async Support**: Full async/await compatibility
- **Type Safety**: Complete type hints for better development

## Getting Started

### Installation

```bash
pip install questionary-extended
```

### Basic Usage

```python
import questionary_extended as qe

# Enhanced numeric input
age = qe.number(
    "What's your age?",
    min_value=0,
    max_value=150,
    allow_float=False
).ask()

# Tree-based selection
language = qe.tree_select(
    "Choose a technology:",
    choices={
        "Frontend": ["React", "Vue.js", "Angular"],
        "Backend": ["Django", "Flask", "FastAPI"],
        "Database": ["PostgreSQL", "MongoDB", "Redis"]
    }
).ask()

# Advanced forms
profile = qe.form([
    {
        "type": "text",
        "name": "name",
        "message": "Full Name:",
        "validate": lambda x: len(x) > 0
    },
    {
        "type": "date",
        "name": "birthday",
        "message": "Birthday:",
        "format": "%Y-%m-%d"
    },
    {
        "type": "rating",
        "name": "satisfaction",
        "message": "Satisfaction (1-5):",
        "max_rating": 5
    }
]).ask()
```

## Architecture

Questionary Extended is designed with modularity and extensibility in mind:

```
questionary_extended/
├── prompts.py          # Core prompt implementations
├── components.py       # Reusable UI components
├── validators.py       # Input validation system
├── styles.py          # Theming and styling
├── utils.py           # Utility functions
└── cli.py            # Command-line interface
```

## Philosophy

1. **Compatibility First**: Works seamlessly with existing questionary code
2. **Type Safety**: Full type hints for better developer experience
3. **Extensibility**: Easy to add new prompt types and validators
4. **Performance**: Efficient rendering and minimal dependencies
5. **Accessibility**: Support for screen readers and keyboard navigation

## Community

- **GitHub**: [questionary-extended](https://github.com/yourusername/questionary-extended)
- **PyPI**: [questionary-extended](https://pypi.org/project/questionary-extended/)
- **Issues**: Report bugs and request features
- **Discussions**: Community help and showcase

## License

Questionary Extended is released under the [MIT License](../LICENSE).