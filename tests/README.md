# Test helpers and guidelines

## Purpose

This short note explains the project's small testing helpers that make it safe
to load individual source files into tests without importing the whole package
tree (which can pull heavy third-party dependencies or trigger side effects).

## Key helpers

- `tests/helpers/test_helpers.py::load_module_from_path(qualname, file_path)`

  - Loads a Python file as a module using `importlib.util.spec_from_file_location`,
    sets `module.__package__` to the spec parent, and creates a minimal fake
    package module in `sys.modules` when needed. This prevents DeprecationWarning
    and makes relative imports inside the file work while avoiding executing
    unrelated package `__init__` logic.

- `tests/helpers/test_helpers.py::_find_repo_root()`

  - Utility to locate the repository root from a test file. Use this when
    constructing paths to `src/...` files in tests.

- `tests/helpers/test_helpers.py::skip_if_coverage_excluded(rel_path)`
  - Check a target source file for a `COVERAGE_EXCLUDE` marker and skip the
    calling test if present. Use this to respect intentionally excluded
    wrapper files.

## Why use `load_module_from_path`

- Consistency: centralizes the small boilerplate needed to safely execute a
  single file during tests.
- Avoids warnings: sets `__package__` to the spec parent to avoid
  `__package__ != __spec__.parent` DeprecationWarning during imports.
- Keeps tests hermetic: a minimal package is injected into `sys.modules` so
  relative imports inside the target file succeed without importing the real
  package `__init__` or its dependencies.

## Examples

Load `src/questionary_extended/utils.py` as a standalone module and use it in a
test:

```python
from tests.helpers.test_helpers import load_module_from_path, _find_repo_root

repo_root = _find_repo_root()
utils_path = str(repo_root / "src" / "questionary_extended" / "utils.py")
mod = load_module_from_path("questionary_extended._file_utils", utils_path)

# Now call functions defined in the file
assert hasattr(mod, "format_number")
```

Skip a test when a file is intentionally excluded from coverage:

```python
from tests.helpers.test_helpers import skip_if_coverage_excluded

skip_if_coverage_excluded("src/questionary_extended/prompts.py")
# test body will be skipped if prompts.py contains COVERAGE_EXCLUDE
```

## `conftest.py` shim

The repository's top-level `tests/conftest.py` patches
`importlib.util.module_from_spec` at collection time to set `module.__package__`
for modules created from specs. This is a low-risk shim used to suppress
DeprecationWarnings that arise when tests create modules from file specs. You
should prefer `load_module_from_path` in new tests instead of manually calling
`spec_from_file_location`/`module_from_spec`.

## Guidance

- Prefer `load_module_from_path` for tests that need to execute a single
  source file in isolation.
- If a test only needs to assert the presence of a symbol (and not execute the
  module), prefer reading the file and performing a text assertion to avoid
  execution side-effects.
- Use `skip_if_coverage_excluded` to respect the project's exclusion policy for
  thin wrappers that delegate to `questionary`.

If you need more examples, open an issue or add a short example test file in
`tests/unit/` following the pattern above.

## Testing import-resolution

Also see `docs/TESTING_IMPORTS.md` for the repository-wide policy on how to
mock `questionary` and how production code should resolve the dependency.
Prefer the `tests/conftest_questionary.setup_questionary_mocks()` helper in
tests — it inserts a fake into `sys.modules` and sets the runtime cache used
by modules that call `questionary_extended._runtime.get_questionary()`.
