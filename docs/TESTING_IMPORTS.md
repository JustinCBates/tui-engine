# Testing import-resolution & questionary mocking strategy

## Purpose

This document records the single, repository-wide contract for how the
`questionary` dependency is resolved at runtime and how tests should mock
interactive prompts in headless CI/Windows environments. Follow this
contract to avoid flaky tests and to prevent ad-hoc changes to import
resolution strategies across the codebase.

## Design goals

- Single source of truth: one runtime accessor that production code and
  tests rely on.
- Robustness: tests should work independent of import ordering.
- Explicitness: production code must decide how to behave when `questionary`
  isn't available (raise or fallback explicitly).

## Key pieces

- `src/questionary_extended/_runtime.py`

  - Exposes `get_questionary()`, `set_questionary_for_tests(obj)`, and
    `clear_questionary_for_tests()`.
  - Resolution order used by `get_questionary()`:
    1. If tests set an explicit runtime object via `set_questionary_for_tests`,
       return it.
    2. If `sys.modules['questionary']` exists, return that object.
    3. Attempt `importlib.import_module('questionary')` and return the module.
    4. If none of the above succeed, return `None`.

- `tests/conftest_questionary.py`
  - Provides `setup_questionary_mocks(monkeypatch, responses=None)` which
    installs a lightweight fake `questionary` into `sys.modules` and also
    calls `questionary_extended._runtime.set_questionary_for_tests(mock_q)` so
    modules that use the runtime accessor immediately see the mock.

## Contract for production code

1. Do not hold permanent references to `questionary` at module import time
   for modules that will be exercised by the test-suite (especially core
   components and bridges). Instead, obtain the runtime object at call-time
   using the runtime accessor. Example pattern:

```py
def some_function(...):
    import importlib

    _rt = importlib.import_module("questionary_extended._runtime")
    q = _rt.get_questionary()
    if q is None:
        raise ImportError("questionary not available; tests should install a mock via setup_questionary_mocks()")

    prompt = q.text("Enter name:")
    return prompt.ask()
```

### Component contract & factory-resolution guidance

The `Component` wrapper (in `src/questionary_extended/core/component.py`) has a small, well-defined contract that library code and tests should follow. Keep this behavior in mind when refactoring or adding new components.

- Purpose: represent a single input field and construct the underlying
  questionary prompt when requested by calling code.
- Public API:

  - `Component(name: str, component_type: str, **kwargs)` — stores `name`,
    `component_type` and `config`.

  from `tests/conftest_questionary.py`. This does everything tests need:

  - Inserts the fake object into `sys.modules['questionary']` so regular
    imports pick it up.
  - Calls `questionary_extended._runtime.set_questionary_for_tests(mock_q)`.
  - Optionally monkeypatches a few internal module attributes for
    backward-compatibility with older tests.

2. Backwards-compatible alternatives (discouraged):

   - Directly set `sys.modules['questionary'] = fake_q` _before_ importing
     code that imports `questionary` at module-level.
   - Explicitly call `questionary_extended._runtime.set_questionary_for_tests(fake_q)`.

3. Avoid brittle patterns like `monkeypatch.setattr('questionary.text', ...)`
   unless you control the import ordering in the test and understand the
   implications. These patterns rely on a specific import order and are
   harder to maintain.

## Migration steps for modules that currently import questionary at module scope

1. Prefer refactoring to the runtime accessor (call-time resolution). This is
   the safest and most future-proof option.

2. If immediate refactor is impractical, ensure tests call
   `setup_questionary_mocks()` before importing the module or explicitly
   call `questionary_extended._runtime.set_questionary_for_tests(fake_q)` in
   those tests.

## Examples

- Test (preferred):

```py
from tests.conftest_questionary import setup_questionary_mocks

def test_my_behavior(monkeypatch):
    mock_q = setup_questionary_mocks(monkeypatch, {'text': 'Alice'})

    # Now import the module under test — it will see the fake via get_questionary
    import importlib
    mod = importlib.import_module('questionary_extended.some_module')

    assert mod.ask_user_name() == 'Alice'
```

- Production code pattern (safe):

```py
def ask_name():
    import importlib

    rt = importlib.import_module('questionary_extended._runtime')
    q = rt.get_questionary()
    if q is None:
        raise RuntimeError('Interactive prompts require the `questionary` package')

    return q.text("Name:").ask()
```

## FAQ / Pitfalls

- Q: I changed a test to monkeypatch `questionary.text` and it still flaked.
  A: That pattern is fragile because it depends on when modules were imported.
  Prefer `setup_questionary_mocks()`.

- Q: Why can't we always import `questionary` at module-level?
  A: On CI/Windows headless environments, importing or creating prompt
  sessions can cause prompt_toolkit to access console APIs that are not
  available and raise errors during import. Lazy call-time resolution avoids
  creating prompt sessions when not needed and makes tests easier to mock.

## Appendix: recommended code review checklist

- If a change adds `import questionary` at module scope, include a short
  justification and a test ensuring the module still works in headless tests
  (i.e., tests call `setup_questionary_mocks()` before importing).
- Prefer `get_questionary()` in shared library code used by tests.

## Document history

- 2025-10-24: Created — central runtime accessor + conftest integration.
