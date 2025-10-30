# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- Initial package structure
- Advanced prompt types (number, date, rating, tree_select, etc.)
- Enhanced validators with comprehensive validation rules
- Theming system with 6 built-in themes
- CLI interface with demo and testing commands
- Comprehensive documentation and examples
- Full test suite with pytest
- Type hints throughout the codebase

### Changed
- The public API was refactored for internal-only development:

- Removed legacy container-level helper constructors (e.g. `container.text`,
  `container.input`, `container.button`). Widgets are now provided by the
  domain factories in `tui_engine.factories` and should be attached via
  `container.add(widget)`.

  This was a deliberate hard-move for internal development; see
  `INTERNAL_ONLY.md` for the repository policy on breaking changes.

### Deprecated

- N/A (initial release)

### Removed

- N/A (initial release)

### Fixed

- N/A (initial release)

### Security

- N/A (initial release)

## [0.1.0] - 2025-10-21

### Added

- Initial release of questionary-extended
- Core package structure following Python packaging best practices
- Foundation for advanced CLI prompts and forms
