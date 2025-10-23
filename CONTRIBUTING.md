# Contributing to Questionary Extended

Thank you for your interest in contributing to Questionary Extended! This document provides guidelines and information for contributors.

## 🚀 Getting Started

### Prerequisites

- Python 3.8 or higher
- Poetry for dependency management
- Git for version control

### Development Setup

1. **Fork and clone the repository:**

   ```bash
   git clone https://github.com/yourusername/questionary-extended.git
   cd questionary-extended
   ```

2. **Install dependencies with Poetry:**

   ```bash
   poetry install --with dev,test
   ```

3. **Activate the virtual environment:**

   ```bash
   poetry shell
   ```

4. **Install pre-commit hooks:**

   ```bash
   pre-commit install
   ```

5. **Run tests to verify setup:**
   ```bash
   pytest
   ```

## 🧪 Development Workflow

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=questionary_extended

# Run specific test file
pytest tests/test_validators.py

# Run with verbose output
pytest -v
```

### Code Quality

We use several tools to maintain code quality:

```bash
# Format code with black
black src/ tests/

# Sort imports with isort
isort src/ tests/

# Lint with flake8
flake8 src/ tests/

# Type checking with mypy
mypy src/
```

### Building Documentation

```bash
# Build documentation
cd docs/
make html

# Serve documentation locally
python -m http.server 8000 -d _build/html/
```

## 📝 Contributing Guidelines

### Code Style

- Follow PEP 8 Python style guide
- Use type hints for all function parameters and return values
- Write docstrings for all public functions and classes
- Maximum line length: 88 characters (black default)

### Commit Messages

Use conventional commit format:

```
type(scope): description

[optional body]

[optional footer]
```

Types:

- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or modifying tests
- `chore`: Maintenance tasks

Examples:

```
feat(prompts): add color picker with preview support
fix(validators): handle edge case in number validation
docs: update README with new examples
```

### Pull Request Process

1. **Create a feature branch:**

   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes:**

   - Write tests for new functionality
   - Update documentation as needed
   - Follow coding standards

3. **Test your changes:**

   ```bash
   pytest
   black --check src/ tests/
   flake8 src/ tests/
   mypy src/
   ```

4. **Commit and push:**

   ```bash
   git add .
   git commit -m "feat: add amazing new feature"
   git push origin feature/your-feature-name
   ```

5. **Create a Pull Request:**
   - Provide a clear description of changes
   - Reference any related issues
   - Include screenshots for UI changes
   - Ensure CI checks pass

## 🎯 Areas for Contribution

### High Priority

- **New Prompt Types:** Date/time pickers, color selectors, table editors
- **Enhanced Validation:** More validator types and better error messages
- **Styling Improvements:** New themes and better customization options
- **Documentation:** More examples, tutorials, and API documentation

### Medium Priority

- **Performance Optimizations:** Faster rendering and reduced memory usage
- **Accessibility:** Better screen reader support and keyboard navigation
- **Platform Support:** Windows, macOS, and Linux compatibility improvements
- **Integration Examples:** Usage with popular CLI frameworks

### Low Priority

- **Advanced Features:** Plugin system, custom widgets, animations
- **Developer Tools:** Debug mode, performance profiling
- **Internationalization:** Multi-language support

## 🐛 Bug Reports

When reporting bugs, please include:

- **Environment:** Python version, OS, terminal emulator
- **Steps to Reproduce:** Clear, minimal example
- **Expected Behavior:** What should happen
- **Actual Behavior:** What actually happens
- **Code Sample:** Minimal reproducing code
- **Screenshots:** If applicable

Use this template:

````markdown
## Bug Report

### Environment

- Python version: 3.10.0
- OS: Windows 11
- Terminal: Windows Terminal

### Description

Brief description of the issue.

### Steps to Reproduce

1. Step one
2. Step two
3. Step three

### Expected Behavior

What you expected to happen.

### Actual Behavior

What actually happened.

### Code Sample

```python
# Minimal reproducing code
import questionary_extended as qe
result = qe.number("Test").ask()
```
````

### Additional Context

Any other relevant information.

````

## 💡 Feature Requests

For feature requests, please:

1. **Check existing issues** to avoid duplicates
2. **Provide use case** - why is this feature needed?
3. **Describe the solution** - what should it look like?
4. **Consider alternatives** - are there other approaches?
5. **Provide examples** - show how it would be used

## 🏆 **A+ Testing Standards (REQUIRED)**

This project maintains **A+ grade testing architecture**. All contributions must meet these standards:

### **Mandatory Coverage Requirements**
- **New Code**: 95%+ coverage required (enforced in CI/CD)
- **Overall Project**: Must maintain 85%+ coverage (A+ standard)
- **No Regression**: Zero tolerance for coverage reduction
- **Critical Paths**: 100% coverage for error handling

### **Test-Driven Development (TDD) Workflow**

**All new features must follow TDD:**
1. **Write Tests First** - Create comprehensive test suite before implementation
2. **Red Phase** - Verify tests fail appropriately  
3. **Green Phase** - Implement minimal code to pass tests
4. **Refactor Phase** - Improve while maintaining coverage
5. **Validation** - Ensure A+ standards met

### **Quality Validation Commands**

**Before submitting PR, run:**
```bash
# Windows PowerShell
.\dev.ps1 validate-aplus     # Complete A+ validation

# Unix/Linux/macOS  
make validate-aplus         # Complete A+ validation
```

### Writing Tests

- Write tests for all new features and bug fixes
- Use descriptive test names that explain what is being tested
- Follow AAA pattern: Arrange, Act, Assert
- Use pytest fixtures for common setup
- Mock external dependencies
- **Target 15-20 tests per module for 95%+ coverage**

### Test Structure

```python
class TestNewFeature:
    """Test the new feature functionality."""

    def test_basic_usage(self):
        """Test basic usage of the feature."""
        # Arrange
        input_data = "test_input"

        # Act
        result = process_input(input_data)

        # Assert
        assert result == expected_output

    def test_edge_case(self):
        """Test edge case handling."""
        # Test implementation
        pass
````

### **A+ Coverage Standards (Enforced)**

- **New Code**: 95%+ coverage required (no exceptions)
- **Overall Project**: Maintain 85%+ coverage (A+ grade)
- **Critical Paths**: 100% coverage for error handling
- **Edge Cases**: Comprehensive boundary condition testing
- **Integration**: End-to-end workflow coverage required

**Coverage is automatically validated in CI/CD - PRs failing coverage requirements will be blocked from merging.**

## 📚 Documentation

### Documentation Types

- **API Documentation:** Comprehensive docstrings
- **User Guide:** How-to guides and tutorials
- **Examples:** Real-world usage examples
- **Contributing Guide:** This document

### Writing Guidelines

- Use clear, concise language
- Include code examples
- Provide context and motivation
- Update documentation with code changes

## 🏆 Recognition

Contributors will be recognized in:

- `CONTRIBUTORS.md` file
- Release notes for significant contributions
- GitHub contributor statistics
- Special mentions for outstanding contributions

## 📞 Getting Help

- **GitHub Issues:** For bugs and feature requests
- **GitHub Discussions:** For questions and general discussion
- **Email:** For security issues or private matters

## 📄 License

By contributing to Questionary Extended, you agree that your contributions will be licensed under the MIT License.

---

Thank you for contributing to Questionary Extended! 🎉
