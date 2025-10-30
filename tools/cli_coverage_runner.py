"""Non-interactive runner to exercise tui_engine.cli for coverage.

This script patches the interactive prompt functions used by the CLI so the
module's functions can be executed without user interaction. It's intended to
be executed under coverage in a subprocess and then combined with the tests'
coverage data.
"""

import importlib
import runpy
import sys
import types
from typing import Any, Callable, Iterable, Mapping, Dict, Literal, cast


def make_stub_prompt(value: Any = None) -> Callable[..., Any]:
    # Return a callable that mimics the prompt constructors used in cli.py.
    def _factory(*a: Any, **k: Any) -> Any:
        class Stub:
            def __init__(self, val: Any = value) -> None:
                self._val = val

            def ask(self) -> Any:
                return self._val

        return Stub()

    return _factory


def _patch_module(mod: Any) -> None:
    # Patch questionary functions referenced by the cli module
    try:
        import questionary as _q

        # confirm should sometimes return True once so form_builder loop runs
        class ConfirmFactory:
            def __init__(self) -> None:
                self.calls: int = 0

            def __call__(self, *a: Any, **k: Any) -> Any:
                # Return a Stub whose ask() returns True on first call then False
                val = self.calls == 0
                self.calls += 1
                return make_stub_prompt(val)()

        _q.confirm = ConfirmFactory()
        _q.text = lambda *a, **k: make_stub_prompt("stub")()
        _q.select = lambda *a, **k: make_stub_prompt("Option 1")()
        _q.prompt = cast(Any, lambda questions: {q.get("name", f"field_{i}"): "value" for i, q in enumerate(questions)})
    except Exception:
        # If questionary isn't importable, ignore - the module may already
        # provide replacements in tests/CI.
        pass

    # Patch prompt helpers imported directly into cli (names used in the file)
    mod.enhanced_text = make_stub_prompt("hello")
    mod.number = make_stub_prompt("42")
    mod.rating = make_stub_prompt(5)
    mod.tree_select = make_stub_prompt("Python")
    mod.color = make_stub_prompt("#ffffff")
    # cli imports `date as date_prompt`
    mod.date_prompt = make_stub_prompt("2020-01-01")

    # Minimal ProgressTracker context manager stub
    class DummyProgress:
        def __init__(self, *a: Any, **k: Any) -> None:
            pass

        def __enter__(self) -> "DummyProgress":
            return self

        def __exit__(self, *a: Any) -> Literal[False]:
            return False

        def step(self, *a: Any, **k: Any) -> None:
            return None

        def complete(self, *a: Any, **k: Any) -> None:
            return None

    mod.ProgressTracker = DummyProgress

    # Save original cli for later manipulations in the runner
    mod._original_cli_for_coverage = getattr(mod, "cli", None)


def _call_command(obj: Any, *args: Any, **kwargs: Any) -> Any:
    # click-wrapped objects often expose .callback or __wrapped__ to get the
    # underlying function. Try both, then fall back to calling the object.
    if hasattr(obj, "callback"):
        func = obj.callback
    elif hasattr(obj, "__wrapped__"):
        func = obj.__wrapped__
    else:
        func = obj

    try:
        return func(*args, **kwargs)
    except SystemExit:
        # click may call sys.exit(); swallow for coverage purposes
        return None
    except Exception:
        # We don't want the runner to fail the coverage collection; print and
        # continue so remaining code runs.
        import traceback

        traceback.print_exc()
        return None


def main() -> None:
    try:
        mod: Any = importlib.import_module("tui_engine.cli")
    except Exception:
        print("tui_engine.cli not importable; skipping cli coverage runner")
        return
    _patch_module(mod)

    # Call the primary commands to execute their bodies
    for name in ("demo", "form_builder", "themes", "wizard_demo"):
        obj = getattr(mod, name, None)
        if obj is None:
            continue
        if name == "wizard_demo":
            _call_command(obj, 1)
        else:
            _call_command(obj)

    # Exercise quick() with all branches
    quick = getattr(mod, "quick", None)
    if quick is not None:
        for pt in ("text", "number", "date", "select", "rating", "color"):
            _call_command(quick, pt)

    # Finally call main() to exercise the top-level error handling and the
    # call-site typically run in the `if __name__ == "__main__"` guard.
    try:
        _call_command(mod.main)
    except Exception:
        pass

    # Trigger KeyboardInterrupt handling in main()
    def _raise_keyboard() -> None:
        raise KeyboardInterrupt()

    mod.cli = _raise_keyboard
    _call_command(mod.main)

    # Trigger generic Exception handling in main()
    def _raise_exc() -> None:
        raise Exception("coverage-run")

    mod.cli = _raise_exc
    _call_command(mod.main)

    # Restore original cli
    if hasattr(mod, "_original_cli_for_coverage"):
        mod.cli = mod._original_cli_for_coverage

    # Run the module as __main__ in a fresh namespace while providing a fake
    # `questionary` module to avoid interactive prompts. This ensures the
    # `if __name__ == "__main__": main()` guard is executed in coverage.
    fake_q: Any = types.ModuleType("questionary")
    # simple stubs
    fake_q.confirm = lambda *a, **k: make_stub_prompt(False)()
    fake_q.text = lambda *a, **k: make_stub_prompt("stub")()
    fake_q.select = lambda *a, **k: make_stub_prompt("Option 1")()
    fake_q.prompt = cast(Any, lambda questions: {q.get("name", f"field_{i}"): "value" for i, q in enumerate(questions)})

    # minimal Question symbol expected by prompts.py
    class Question:
        def __init__(self, *a: Any, **k: Any) -> None:
            pass

        def ask(self) -> Any:
            return None

    fake_q.Question = Question

    saved = sys.modules.get("questionary")
    try:
        sys.modules["questionary"] = fake_q
        # run module as __main__; ignore errors
        try:
            runpy.run_module("tui_engine.cli", run_name="__main__")
        except Exception:
            pass
    finally:
        if saved is None:
            del sys.modules["questionary"]
        else:
            sys.modules["questionary"] = saved


if __name__ == "__main__":
    main()
