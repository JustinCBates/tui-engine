# Questionary Extended

[![PyPI version](https://badge.fury.io/py/questionary-extended.svg)](https://badge.fury.io/py/questionary-extended)
[![Python Support](https://img.shields.io/pypi/pyversions/questionary-extended.svg)](https://pypi.org/project/questionary-extended/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

🚀 **Advanced extensions for the questionary CLI prompt library**

Questionary Extended builds upon the excellent [questionary](https://github.com/tmbo/questionary) library to provide advanced input types, enhanced UI components, workflow management, and data integration features for building sophisticated command-line interfaces.

## ✨ Features

### 🎯 Advanced Input Types

- **Numeric Input**: Integer/float inputs with range validation and increment controls
- **Date/Time Input**: Date picker, time picker, datetime picker with smart validation
- **Color Picker**: Terminal-based color selection (hex, RGB, HSL, named colors)
- **Rating/Scale**: Star ratings, slider inputs, Likert scales
- **Table Input**: Spreadsheet-like data entry for structured data
- **Rich Text**: Markdown-enabled text input with syntax highlighting

### 🎨 Enhanced Selection & Navigation

- **Multi-level Menus**: Hierarchical navigation with breadcrumbs
- **Tree Browser**: File system tree, nested data structure explorer
- **Tag Input**: Multi-tag selection with fuzzy auto-completion
- **Fuzzy Search**: Enhanced search with ranking and highlighting
- **Grouped Choices**: Categorized selections with collapsible sections

### 🎪 Visual Enhancements

- **Rich Text Support**: Markdown rendering, syntax highlighting
- **Icons & Emojis**: Built-in icon sets for common actions and types
- **Charts & Graphs**: ASCII charts, progress bars, sparklines
- **Layout Engine**: Multi-column layouts, panels, borders, and frames

### ⚡ Workflow & Logic Extensions

- **Form Builder**: Declarative form definitions with complex validation rules
- **Conditional Logic**: Advanced branching, loops, dynamic question generation
- **State Management**: Session persistence, undo/redo, bookmarks
- **Template System**: Reusable question templates with parameter substitution

### 🔗 Data Integration

- **File Operations**: CSV/JSON import/export, configuration loading
- **External APIs**: REST API integration for dynamic choices
- **Database Connections**: Simple database queries for data-driven prompts
- **Configuration Management**: Settings files, environment variables

## 🚀 Quick Start

### Installation

```bash
pip install questionary-extended
```

### Basic Usage

```python
import questionary_extended as qe

# Advanced numeric input with validation
age = qe.number(
    "What's your age?",
    min_value=0,
    max_value=150,
    step=1,
    allow_float=False
).ask()

# Date picker with smart validation
birthday = qe.date(
    "When is your birthday?",
    min_date="1900-01-01",
    max_date="today",
    format="%Y-%m-%d"
).ask()

# Multi-level menu navigation
choice = qe.tree_select(
    "Choose a programming language:",
    choices={
        "Web Development": {
            "Frontend": ["JavaScript", "TypeScript", "Vue.js", "React"],
            "Backend": ["Node.js", "Python", "PHP", "Ruby"]
        },
        "Data Science": ["Python", "R", "Julia", "Scala"],
        "Mobile": ["Swift", "Kotlin", "Flutter", "React Native"]
    }
).ask()

# Rich form with validation and conditional logic
form_result = qe.form([
    {
        "name": "project_type",
        "type": "select",
        "message": "Project type:",
        "choices": ["Web App", "Mobile App", "Desktop App", "CLI Tool"]
    },
    {
        "name": "framework",
        "type": "select",
        "message": "Choose framework:",
        "choices": lambda answers: {
            "Web App": ["Django", "Flask", "FastAPI"],
            "Mobile App": ["Flutter", "React Native", "Ionic"],
            "Desktop App": ["Tkinter", "PyQt", "Electron"],
            "CLI Tool": ["Click", "Typer", "Fire"]
        }[answers["project_type"]],
        "when": lambda answers: answers["project_type"] is not None
    }
]).ask()
```

### Advanced Features

```python
# Table input for structured data
data = qe.table(
    "Enter user information:",
    columns=[
        {"name": "name", "type": "text", "width": 20},
        {"name": "age", "type": "number", "width": 10, "min": 0, "max": 120},
        {"name": "email", "type": "email", "width": 30}
    ],
    min_rows=1,
    max_rows=10
).ask()

# Color picker with multiple format support
color = qe.color(
    "Choose a theme color:",
    formats=["hex", "rgb", "hsl"],
    preview=True,
    palette=["red", "green", "blue", "yellow", "purple"]
).ask()

# Progress tracking for multi-step workflows
with qe.progress_tracker("Setting up project", total_steps=5) as progress:
    progress.step("Creating directory structure...")
    # ... do work ...
    progress.step("Installing dependencies...")
    # ... do work ...
    progress.complete("Project setup finished!")
```

## 📚 Documentation

Full documentation is available at: [questionary-extended.readthedocs.io](https://questionary-extended.readthedocs.io)

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built on top of the excellent [questionary](https://github.com/tmbo/questionary) library by Tom Bocklisch
- UI enhancements powered by [rich](https://github.com/Textualize/rich)
- Terminal interactions via [prompt-toolkit](https://github.com/prompt-toolkit/python-prompt-toolkit)

## 🔗 Related Projects

- [questionary](https://github.com/tmbo/questionary) - The base library this extends
- [rich](https://github.com/Textualize/rich) - Rich text and beautiful formatting
- [typer](https://github.com/tiangolo/typer) - Modern CLI framework
- [click](https://github.com/pallets/click) - Command line interface creation kit
