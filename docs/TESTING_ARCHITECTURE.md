Testing Architecture — Import resolution, timeouts, and per-test logging
===========================================================================

Purpose
-------
This document describes the testing architecture used by the project. It is
intended as a complete, reusable strategy you can copy into other projects.
It covers:

- Import-resolution contract for runtime dependencies (questionary/runtime)
- How tests avoid import-time side-effects (prompt_toolkit PromptSession etc.)
- Per-test timeouts and fallback strategies
- Per-test logging (buffered files, optional real-time echoing, replay on failure)
- Path validation for file-based test loading
- Practical guidance for CI and cross-platform (Windows PowerShell) usage

Design Goals
-----------
- Tests must be hermetic: importing modules should not create real console
  sessions, open network connections, or produce non-deterministic side effects.
- Tests should fail fast and provide clear diagnostics: missing test assets,
  long-running or hanging tests, and unexpected imports should yield readable
  error messages.
- Per-test logs should be available for debugging and attached to CI artifacts
  when failures happen. Developers should be able to see logs in real time
  during local runs when desired.
- The architecture should be portable across platforms and working directories
  (Windows PowerShell included), and be easy to copy into other projects.

Contracts and Conventions
-------------------------
1. Centralized runtime accessor
   - The package exposes a small runtime accessor module (e.g.
     `package._runtime`) with simple functions:
       - `get_questionary()` -> returns active questionary object or None
       - `set_questionary_for_tests(obj)` -> install a test runtime mock
       - `clear_questionary_for_tests()` -> clear the test runtime mock
   - Modules use a thin module-level proxy or call the runtime accessor at
     call time rather than creating expensive runtime objects at import time.
   - Tests should either insert a stub into `sys.modules['questionary']` or
     call `set_questionary_for_tests()` early (fixtures) to control runtime
     behavior.

2. Avoid import-time effects
   - Tests must not cause real `prompt_toolkit` `PromptSession` creation while
     importing code. To guarantee this:
     - Real prompt factories are resolved at call-time (lazy factories), and
       any code that may touch `prompt_toolkit` is executed inside functions
       that can be stubbed in tests.
     - Tests use `tests.helpers.setup_questionary_mocks()` which installs a
       lightweight fake `questionary` object in `sys.modules` and sets the
       runtime accessor accordingly.

3. Path validation
   - Tests that load modules directly from file paths must validate those
     paths early using `tests.helpers.path_utils.ensure_path_exists(path,
     required=True)` to fail fast when local files are missing or when the
     repository layout differs.

Timeouts and Hanging Tests
--------------------------
- Default timeout: configurable via `TEST_TIMEOUT_SECONDS` env var (default
  conservative value: 5 seconds for unit tests).
- Preferred mechanism: `pytest-timeout` plugin added to test dependencies and
  configured globally in `pytest.ini` when available.
- Fallback mechanism: a `pytest_runtest_call` hook that runs tests in a daemon
  thread and fails with a clear timeout message if the test doesn't complete
  within the timeout. This avoids hanging the entire runner when the plugin is
  not available.
- When a timeout occurs, the test harness should print a helpful message and
  — when possible — a stacktrace for where the test got stuck (pytest-timeout
  can provide a stack snapshot; the thread-based fallback will report the
  timeout and the test's output).

Per-test logging
----------------
- Goals:
  - Always capture logs to a per-test file (`test-logs/{worker}/{safe-nodeid}.log`).
  - Optionally stream logs to stdout in real time (controlled by
    `TEST_LOG_ECHO=1`).
  - When a test fails, replay the per-test log to the terminal so developers
    immediately see the context that led to the failure.
  - Keep logs structured enough to be ingested by CI systems (JSON option)
    while remaining human-friendly by default.

- Mechanics:
  - An autouse pytest fixture configures a `logging.FileHandler` with a
    formatter and attaches it to the root logger for the duration of the test.
  - Filenames are sanitized versions of the pytest nodeid. Worker id (xdist)
    is appended as a directory component to avoid collisions.
  - Environment toggles:
      - `TEST_LOG_DIR` — base output folder for logs (default: repo-root/test-logs)
      - `TEST_LOG_LEVEL` — default logging level (INFO)
      - `TEST_LOG_ECHO` — if '1', also attach a `StreamHandler` to stdout for
        real-time visibility.
      - `TEST_LOG_JSON` — if '1', emit JSON entries (optional/advanced).
  - On teardown, if the test failed (the pytest report object shows failure
    in `rep_call.failed`), the fixture emits the log file contents to stdout
    surrounded by clear header/footer markers. CI can collect these files as
    artifacts automatically.

- XDist and concurrency:
  - Per-worker subdirectories avoid inter-process contention.
  - File-by-file writing is simple and robust; no central logging queue is
    required for the common case.

Diagnostic helpers
------------------
- `tests/logging_utils.py` exposes helpers to sanitize nodeids, compute worker
  ids, and compute default log dirs. These are intentionally tiny and copyable
  into other projects.

Developer UX
------------
- Before each test runs, the runner prints a concise line:

    RUNNING <nodeid> (timeout=<n>s)

  This makes it easy to spot the currently running test in long output.
- If `TEST_LOG_ECHO=1` is set, logs stream to the terminal in real time.
- When a test fails, the test runner prints the per-test log file contents so
  developers can immediately read diagnostics without opening separate files.

CI Integration
--------------
- CI job should:
  - Set `TEST_TIMEOUT_SECONDS` to a stricter default for the entire suite
    (e.g., 10s for unit tests) or rely on pytest-timeout plugin configuration.
  - On test failure, upload the `test-logs/` directory as job artifacts so
    maintainers can inspect logs offline.
  - Optionally enable `TEST_LOG_JSON=1` to have logs ingested by structured
    log analysis systems.

Portability and PowerShell
--------------------------
- `dev.ps1` contains PowerShell-friendly helpers to run the moderate test
  subset. Scripts avoid brittle relative `Set-Location` commands and resolve
  the repository root using the script's path. The per-test logging and
  timeout facilities work on Windows and POSIX.

Copying this architecture to another project
-------------------------------------------
1. Add a `tests/logging_utils.py` with sanitize/dir helpers.
2. Add an autouse `per_test_logger` fixture as described.
3. Add timeout guardrails: prefer pytest-timeout and add a `pytest_runtest_call`
   fallback that runs tests in a daemon thread.
4. Add `tests/helpers/setup_questionary_mocks` equivalent to guard runtime
   dependencies for your project.
5. Add a `tests/helpers/path_utils.ensure_path_exists()` and call it in any
   test helper that loads modules from paths.
6. Document environment variables and CI steps in repository README.

Appendix: example fixture (high level)
-------------------------------------
- See `tests/conftest.py` in this repository for a ready-to-copy implementation
  of the logging fixture, timeout fallback, and test start printing.

Change control
--------------
- This architecture is intentionally conservative. If a project demands
  extremely high-performance CI (millions of tests), adapt the file-per-test
  strategy to batched logging and log rotation. For most projects the per-test
  file approach is easy to adopt and yields clear diagnostics.

Contact
-------
If you want, I can produce a small standalone package (pip-installable) that
implements the above fixtures and helpers so you can reuse them across
projects with a one-line `pytest_plugins = ['tui_test_helpers']` import.

*** End of document
Testing Architecture — Import resolution, timeouts, and per-test logging
===========================================================================

Purpose
-------
This document describes the testing architecture used by the project. It is
intended as a complete, reusable strategy you can copy into other projects.
It covers:

- Import-resolution contract for runtime dependencies (questionary/runtime)
- How tests avoid import-time side-effects (prompt_toolkit PromptSession etc.)
- Per-test timeouts and fallback strategies
- Per-test logging (buffered files, optional real-time echoing, replay on failure)
- Path validation for file-based test loading
- Practical guidance for CI and cross-platform (Windows PowerShell) usage

Design Goals
-----------
- Tests must be hermetic: importing modules should not create real console
  sessions, open network connections, or produce non-deterministic side effects.
- Tests should fail fast and provide clear diagnostics: missing test assets,
  long-running or hanging tests, and unexpected imports should yield readable
  error messages.
- Per-test logs should be available for debugging and attached to CI artifacts
  when failures happen. Developers should be able to see logs in real time
  during local runs when desired.
- The architecture should be portable across platforms and working directories
  (Windows PowerShell included), and be easy to copy into other projects.

Contracts and Conventions
-------------------------
1. Centralized runtime accessor
   - The package exposes a small runtime accessor module (e.g.
     `package._runtime`) with simple functions:
       - `get_questionary()` -> returns active questionary object or None
       - `set_questionary_for_tests(obj)` -> install a test runtime mock
       - `clear_questionary_for_tests()` -> clear the test runtime mock
   - Modules use a thin module-level proxy or call the runtime accessor at
     call time rather than creating expensive runtime objects at import time.
   - Tests should either insert a stub into `sys.modules['questionary']` or
     call `set_questionary_for_tests()` early (fixtures) to control runtime
     behavior.

2. Avoid import-time effects
   - Tests must not cause real `prompt_toolkit` `PromptSession` creation while
     importing code. To guarantee this:
     - Real prompt factories are resolved at call-time (lazy factories), and
       any code that may touch `prompt_toolkit` is executed inside functions
       that can be stubbed in tests.
     - Tests use `tests.helpers.setup_questionary_mocks()` which installs a
       lightweight fake `questionary` object in `sys.modules` and sets the
       runtime accessor accordingly.

3. Path validation
   - Tests that load modules directly from file paths must validate those
     paths early using `tests.helpers.path_utils.ensure_path_exists(path,
     required=True)` to fail fast when local files are missing or when the
     repository layout differs.

Timeouts and Hanging Tests
--------------------------
- Default timeout: configurable via `TEST_TIMEOUT_SECONDS` env var (default
  conservative value: 5 seconds for unit tests).
- Preferred mechanism: `pytest-timeout` plugin added to test dependencies and
  configured globally in `pytest.ini` when available.
- Fallback mechanism: a `pytest_runtest_call` hook that runs tests in a daemon
  thread and fails with a clear timeout message if the test doesn't complete
  within the timeout. This avoids hanging the entire runner when the plugin is
  not available.
- When a timeout occurs, the test harness should print a helpful message and
  — when possible — a stacktrace for where the test got stuck (pytest-timeout
  can provide a stack snapshot; the thread-based fallback will report the
  timeout and the test's output).

Per-test logging
----------------
- Goals:
  - Always capture logs to a per-test file (`test-logs/{worker}/{safe-nodeid}.log`).
  - Optionally stream logs to stdout in real time (controlled by
    `TEST_LOG_ECHO=1`).
  - When a test fails, replay the per-test log to the terminal so developers
    immediately see the context that led to the failure.
  - Keep logs structured enough to be ingested by CI systems (JSON option)
    while remaining human-friendly by default.

- Mechanics:
  - An autouse pytest fixture configures a `logging.FileHandler` with a
    formatter and attaches it to the root logger for the duration of the test.
  - Filenames are sanitized versions of the pytest nodeid. Worker id (xdist)
    is appended as a directory component to avoid collisions.
  - Environment toggles:
      - `TEST_LOG_DIR` — base output folder for logs (default: repo-root/test-logs)
      - `TEST_LOG_LEVEL` — default logging level (INFO)
      - `TEST_LOG_ECHO` — if '1', also attach a `StreamHandler` to stdout for
        real-time visibility.
      - `TEST_LOG_JSON` — if '1', emit JSON entries (optional/advanced).
  - On teardown, if the test failed (the pytest report object shows failure
    in `rep_call.failed`), the fixture emits the log file contents to stdout
    surrounded by clear header/footer markers. CI can collect these files as
    artifacts automatically.

- XDist and concurrency:
  - Per-worker subdirectories avoid inter-process contention.
  - File-by-file writing is simple and robust; no central logging queue is
    required for the common case.

Diagnostic helpers
------------------
- `tests/logging_utils.py` exposes helpers to sanitize nodeids, compute worker
  ids, and compute default log dirs. These are intentionally tiny and copyable
  into other projects.

Developer UX
------------
- Before each test runs, the runner prints a concise line:

    RUNNING <nodeid> (timeout=<n>s)

  This makes it easy to spot the currently running test in long output.
- If `TEST_LOG_ECHO=1` is set, logs stream to the terminal in real time.
- When a test fails, the test runner prints the per-test log file contents so
  developers can immediately read diagnostics without opening separate files.

CI Integration
--------------
- CI job should:
  - Set `TEST_TIMEOUT_SECONDS` to a stricter default for the entire suite
    (e.g., 10s for unit tests) or rely on pytest-timeout plugin configuration.
  - On test failure, upload the `test-logs/` directory as job artifacts so
    maintainers can inspect logs offline.
  - Optionally enable `TEST_LOG_JSON=1` to have logs ingested by structured
    log analysis systems.

Portability and PowerShell
--------------------------
- `dev.ps1` contains PowerShell-friendly helpers to run the moderate test
  subset. Scripts avoid brittle relative `Set-Location` commands and resolve
  the repository root using the script's path. The per-test logging and
  timeout facilities work on Windows and POSIX.

Copying this architecture to another project
-------------------------------------------
1. Add a `tests/logging_utils.py` with sanitize/dir helpers.
2. Add an autouse `per_test_logger` fixture as described.
3. Add timeout guardrails: prefer pytest-timeout and add a `pytest_runtest_call`
   fallback that runs tests in a daemon thread.
4. Add `tests/helpers/setup_questionary_mocks` equivalent to guard runtime
   dependencies for your project.
5. Add a `tests/helpers/path_utils.ensure_path_exists()` and call it in any
   test helper that loads modules from paths.
6. Document environment variables and CI steps in repository README.

Appendix: example fixture (high level)
-------------------------------------
- See `tests/conftest.py` in this repository for a ready-to-copy implementation
  of the logging fixture, timeout fallback, and test start printing.

Change control
--------------
- This architecture is intentionally conservative. If a project demands
  extremely high-performance CI (millions of tests), adapt the file-per-test
  strategy to batched logging and log rotation. For most projects the per-test
  file approach is easy to adopt and yields clear diagnostics.

Contact
-------
If you want, I can produce a small standalone package (pip-installable) that
implements the above fixtures and helpers so you can reuse them across
projects with a one-line `pytest_plugins = ['tui_test_helpers']` import.

*** End of document
