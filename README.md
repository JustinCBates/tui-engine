# Per-test logs and CI artifacts

This repository configures a per-test logging fixture used during pytest runs. Logs are written per test to a `test-logs/` directory by default and can be adjusted with environment variables.

## Quick local usage

- Default log directory: `test-logs/` in the repository root.
- Toggle real-time echoing to the terminal during tests:

  ```powershell
  $env:TEST_LOG_ECHO = '1'
  python -m pytest -q tests/unit/path/to/test_file.py::test_name
  ```

- Produce JSON-lines logs (useful for CI ingestion):

  ```powershell
  $env:TEST_LOG_JSON = '1'
  $env:TEST_LOG_REDACT = '1'  # enable simple regex-based redaction
  python -m pytest -q tests/unit/...
  ```

## Env vars

- `TEST_LOG_DIR` — base directory for per-test logs (default: `test-logs/`).
- `TEST_LOG_LEVEL` — logging level (DEBUG/INFO/WARNING/ERROR). Default: INFO.
- `TEST_LOG_JSON` — if set to `1` emit JSON-lines per log record.
- `TEST_LOG_REDACT` — if set to `1` run a simple regex-based redaction pass over log lines before writing.
- `TEST_LOG_ECHO` — if set to `1` also stream logs to stdout in real-time while tests run.
- `TEST_LOG_REDACT_PATTERNS` — optional JSON array or semicolon-separated regex list to customize redaction.

## Inspecting logs

Logs are organized by worker id and sanitized nodeid, e.g.: `test-logs/gw0/tests-unit-test_foo.py__test_bar.log`.

## CI integration

There is a GitHub Actions workflow that runs tests and uploads `test-logs/` as an artifact when the test job fails. See `.github/workflows/test-logs-upload.yml`.

If you want different behavior (always upload logs, or change the artifact retention), update the workflow in `.github/workflows/`.

## Contact

If you need changes to the logging format (structured fields, different redaction policy, or alternative storage), open an issue or a PR with proposed changes.

# Questionary Extended

[![CI/CD Pipeline](https://github.com/JustinCBates/tui-engine/actions/workflows/ci.yml/badge.svg)](https://github.com/JustinCBates/tui-engine/actions/workflows/ci.yml)
[![Publish to PyPI](https://github.com/JustinCBates/tui-engine/actions/workflows/publish.yml/badge.svg)](https://github.com/JustinCBates/tui-engine/actions/workflows/publish.yml)
[![Security Audit](https://github.com/JustinCBates/tui-engine/actions/workflows/security.yml/badge.svg)](https://github.com/JustinCBates/tui-engine/actions/workflows/security.yml)
[![Performance](https://github.com/JustinCBates/tui-engine/actions/workflows/performance.yml/badge.svg)](https://github.com/JustinCBates/tui-engine/actions/workflows/performance.yml)

[![PyPI version](https://badge.fury.io/py/questionary-extended.svg)](https://badge.fury.io/py/questionary-extended)
[![Python Support](https://img.shields.io/pypi/pyversions/questionary-extended.svg)](https://pypi.org/project/questionary-extended/)
[![codecov](https://codecov.io/gh/JustinCBates/tui-engine/branch/main/graph/badge.svg)](https://codecov.io/gh/JustinCBates/tui-engine)
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
with qe.ProgressTracker("Setting up project", total_steps=5) as progress:
    progress.step("Creating directory structure...")
    # ... do work ...
    progress.step("Installing dependencies...")
    # ... do work ...
    progress.complete("Project setup finished!")
```

## 📚 Documentation

Full documentation is available at: [questionary-extended.readthedocs.io](https://questionary-extended.readthedocs.io)

## 🏆 **A+ Grade Testing Architecture**

This project maintains professional-grade testing standards:

- **204 comprehensive tests** with 100% pass rate
- **85%+ code coverage** enforced in CI/CD pipeline
- **Automated quality gates** preventing regression
- **TDD workflow** with pre-commit hooks and coverage tracking

### Quick Testing Commands

```bash
# Windows PowerShell
.\dev.ps1 coverage          # Run tests with A+ coverage validation
.\dev.ps1 validate-aplus    # Complete A+ standards validation

# Unix/Linux/macOS
make coverage               # Run tests with A+ coverage validation
make validate-aplus         # Complete A+ standards validation
```

### PowerShell helper note

The repository ships `dev.ps1`, a PowerShell-first helper script that exposes session-safe functions (for example `Invoke-ModerateTests` and `Ensure-GhOnPath`). Use `.\dev.ps1 test-moderate` to run a focused subset of tests that exercise the questionary/prompt/component/cli code paths on Windows. The script will attempt to ensure the GitHub CLI (`gh`) is discoverable in the current session by prepending common install folders to `$env:PATH` if needed.

If you prefer to run the focused test subset directly, use the following PowerShell-safe command:

```powershell
python -m pytest -q tests/unit -k 'questionary or prompts or component or cli'
```

**Testing Documentation**: See [docs/TESTING_BEST_PRACTICES.md](docs/TESTING_BEST_PRACTICES.md) for complete testing standards and workflow.

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

**Development Standards**: All contributions must maintain A+ testing standards with 95%+ coverage for new code.

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
