# TUI Engine Demos

This directory contains comprehensive demonstration scripts showcasing the complete TUI Engine questionary integration.

## Available Demos

### Comprehensive Showcase
- `comprehensive_demo.py` - **Complete demo suite with interactive menu**
  - All 5 professional themes
  - 20+ widgets with validation
  - Dynamic form building
  - Real-world applications
  - Performance demonstrations
  - Integration examples
  - Interactive playground

### Performance & Benchmarking
- `performance_benchmark.py` - **Performance testing suite**
  - Form creation benchmarks with varying field counts
  - Validation performance under load
  - Theme switching performance
  - Memory usage analysis
  - Concurrent form handling
  - Large dataset performance
  - Serialization/deserialization speed

### Real-World Applications
- `real_world_employee_system.py` - **Complete employee management system**
  - Multi-step employee onboarding workflow
  - Employee data management with CRUD operations
  - Performance review system
  - Reports and analytics
  - System configuration
  - Data import/export
  - Search and filtering
  - Role-based workflows

### Integration Testing
- `integration_test.py` - **Comprehensive integration test suite**
  - Theme integration testing
  - Validation system integration
  - Form builder compatibility
  - Widget compatibility across themes
  - Cross-theme validation consistency
  - Complex scenario testing
  - Performance integration testing
  - Error handling verification
  - Data persistence testing
  - Questionary compatibility verification

### Legacy Demos (Updated with New Features)
- `demo_alignment.py` - Alignment and layout with new themes
- `demo_container.py` - Container components with validation
- `demo_form.py` - Enhanced form demonstrations
- `demo_swap_cards.py` - Card swapping with new styling
- `demo_form_new.py` - Updated form examples
- `main_menu.py` - Enhanced main demo menu
- `questionary_adapter_demo.py` - Questionary integration examples
- `theme_integration_demo.py` - Theme system demonstrations

### Configuration
- `setup_env.sh` - Environment setup script
- `form_output.json` - Sample form output data

## Quick Start

### Run the Complete Demo Suite
```bash
python comprehensive_demo.py
```
This provides an interactive menu to explore all TUI Engine features.

### Run Performance Benchmarks
```bash
python performance_benchmark.py
```
Tests performance across all components with detailed metrics.

### Try the Employee Management System
```bash
python real_world_employee_system.py
```
A complete real-world application showcasing all integration patterns.

### Verify Integration
```bash
python integration_test.py
```
Comprehensive test suite verifying all components work together.

## Demo Features Showcased

### 🎨 Professional Themes (5 Themes)
- `professional_blue` - Clean corporate styling
- `elegant_dark` - Modern dark theme
- `vibrant_green` - Energy and nature inspired
- `warm_amber` - Comfortable warm tones
- `cool_slate` - Sophisticated minimalism

### 🧩 Widget Collection (20+ Widgets)
- **Text Widgets**: Text, Password, Email, URL, Phone
- **Selection Widgets**: Select, Multi-Select, Checkbox, Radio
- **Input Widgets**: Number, Date, Time, DateTime, File
- **Specialized**: Credit Card, Color Picker, Progress, Editor
- **Interactive**: Autocomplete, Path Browser, Key Press

### 📋 Form Building Capabilities
- Schema-based form creation
- Dynamic field generation
- Conditional logic (8 operators)
- Multi-step forms
- Form serialization/deserialization
- Validation integration
- Real-time field updates

### ✅ Validation Framework
- 11+ built-in validators
- Validation chains with fluent interface
- Custom validation rules
- Field-level and form-level validation
- Error messaging and themes
- Performance optimized caching

### 🏢 Real-World Scenarios
- Employee onboarding workflows
- Customer registration systems
- Contact and feedback forms
- E-commerce checkout processes
- Survey and questionnaire builders
- System configuration interfaces
- Bug reporting systems

### ⚡ Performance Features
- Large form handling (100+ fields)
- Concurrent form processing
- Memory usage optimization
- Fast validation chains
- Efficient serialization
- Background processing

### 🔗 Integration Patterns
- Theme switching at runtime
- Cross-platform compatibility
- API integration examples
- Database schema mapping
- Configuration file generation
- Export/import utilities

## Running Specific Demo Categories

### Interactive Demos
```bash
# Main comprehensive demo suite
python comprehensive_demo.py

# Employee management system
python real_world_employee_system.py
```

### Testing & Validation
```bash
# Performance benchmarks
python performance_benchmark.py

# Integration tests
python integration_test.py
```

### Legacy Compatibility
```bash
# Original demo menu
python main_menu.py

# Specific feature demos
python demo_form.py
python theme_integration_demo.py
```

## Environment Setup

1. Create a demo virtual environment and install runtime dependencies:

```bash
cd demos
./setup_env.sh
```

2. Activate the virtual environment in your shell:

```bash
source .venv/bin/activate
```

3. Run any demo script:

```bash
python comprehensive_demo.py
```

## Demo Architecture

Each demo is designed to be:
- **Self-contained**: No external dependencies beyond TUI Engine
- **Educational**: Clear code examples with comprehensive comments
- **Interactive**: User-friendly interfaces with guided workflows
- **Comprehensive**: Coverage of all major features and use cases
- **Performance-aware**: Optimized for real-world usage patterns

## Development Notes

- All demos are compatible with Python 3.8+
- Demos use mock widgets for testing (no external questionary dependency required)
- Performance benchmarks include memory profiling and timing analysis
- Integration tests verify component compatibility across all themes
- Real-world demos demonstrate production-ready patterns

## TTY and Terminal Requirements

Many of the demos use interactive terminal features and expect to run in a real TTY:
- Use a normal terminal (GNOME Terminal, xterm, Alacritty, iTerm2, etc.)
- Windows WSL/PowerShell when appropriate
- Some CI systems or limited editor consoles may not work

## Troubleshooting

- Make sure you have Python 3.8+ available as `python3` on PATH
- If `setup_env.sh` fails, try removing the venv and re-running with `--recreate`
- For development extras (linters, test deps), use `./setup_env.sh --dev`
- If demos fail to start, verify you're in a real TTY environment

## Next Steps

After exploring the demos:
1. Review the source code in `src/tui_engine/`
2. Check the documentation in `docs/`
3. Run the test suite with `pytest`
4. Build your own applications using the patterns demonstrated

## Support

For questions or issues with the demos:
- Check the main README.md for setup instructions
- Review the architecture documentation in `docs/`
- Examine the test suite for additional examples
- See the integration test for compatibility verification