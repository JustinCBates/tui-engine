"""
DEPRECATED: Complex questionary mocking system.

This file contains 669 lines of complex questionary mocking logic that is
largely superfluous due to the new dependency injection system.

For NEW tests, use the clean helpers from tests.helpers.questionary_helpers:
- mock_questionary() for simple mocking  
- mock_questionary_with_types() for multiple component types
- QuestionaryTestHelper for advanced scenarios

This file is maintained for backward compatibility with existing tests that
haven't been migrated to the DI system yet. Eventually most of this can be
removed as tests are migrated to the cleaner DI patterns.

The DI system eliminates the need for complex fallback resolution and 
provides clean, maintainable test patterns.
"""

import sys
import types
from typing import Any, Callable, Dict, Optional


class ValidationError(Exception):
    def __init__(self, message: str = "", cursor_position: int = 0):
        super().__init__(message)
        self.message = message
        self.cursor_position = cursor_position


class Separator:
    """Lightweight stand-in for questionary.Separator used in tests.

    Implemented so isinstance(..., questionary.Separator) checks succeed
    when tests import Separator from the mocked `questionary` module.
    """

    def __init__(self, title: str):
        self.title = title

    def __repr__(self) -> str:  # keep representation similar to real Separator
        return f"--- {self.title} ---"


def _make_prompt_factory(
    responses: Optional[Dict[str, Any]], kind: str, default: Any = None
) -> Callable:
    responses = responses or {}

    def factory(message: str = "", **kwargs) -> types.SimpleNamespace:
        # Order of resolution: exact kind mapping -> message-keyed mapping -> default
        val = None
        if kind in responses:
            candidate = responses[kind]
            if callable(candidate):
                try:
                    val = candidate(message, **kwargs)
                except TypeError:
                    val = candidate()
            else:
                val = candidate

        # message-keyed mapping support
        if val is None and message in responses:
            candidate = responses[message]
            if callable(candidate):
                try:
                    val = candidate(message, **kwargs)
                except TypeError:
                    val = candidate()
            else:
                val = candidate

        if val is None:
            val = default

        # Return an object with .ask() to mimic questionary prompt objects
        return types.SimpleNamespace(ask=lambda: val)

    return factory


def setup_questionary_mocks(
    monkeypatch: Optional[object],
    responses: Optional[Dict[str, Any]] = None,
    *,
    default_text: Any = "default_text",
) -> types.ModuleType:
    """Install a lightweight questionary mock into sys.modules and the runtime accessor.

    - monkeypatch: pytest monkeypatch fixture (may be None in ad-hoc debug runs)
    - responses: mapping of prompt-kind or message -> response value or callable(message, **kwargs)
    - default_text: fallback value for text prompts

    Returns the mock object installed as the `questionary` module.
    """

    # Use a real module object so "from questionary import X" works
    mock_q = types.ModuleType("questionary")

    # factories for common prompt kinds
    mock_q.text = _make_prompt_factory(responses, "text", default_text)
    mock_q.select = _make_prompt_factory(responses, "select", "default_option")
    mock_q.confirm = _make_prompt_factory(responses, "confirm", True)
    mock_q.password = _make_prompt_factory(responses, "password", "default_password")
    mock_q.checkbox = _make_prompt_factory(responses, "checkbox", ["default_checkbox"])
    mock_q.autocomplete = _make_prompt_factory(
        responses, "autocomplete", "default_autocomplete"
    )
    mock_q.path = _make_prompt_factory(responses, "path", "/default/path")

    # compatibility attributes expected by validators and prompt helpers
    mock_q.ValidationError = ValidationError
    mock_q.Separator = Separator

    # Install into sys.modules so "from questionary import X" works
    if monkeypatch is None:
        sys.modules["questionary"] = mock_q
    else:
        # pytest.MonkeyPatch supports setitem on sys.modules
        try:
            monkeypatch.setitem(sys.modules, "questionary", mock_q)
        except Exception:
            # fallback: set attribute path used by some tests
            try:
                monkeypatch.setattr("questionary", mock_q, raising=False)
            except Exception:
                # last resort: write directly
                sys.modules["questionary"] = mock_q

    # Also set the runtime accessor if available
    try:
        from questionary_extended import _runtime as _rt

        if hasattr(_rt, "set_questionary_for_tests"):
            try:
                _rt.set_questionary_for_tests(mock_q)
            except Exception:
                # best-effort: ignore if runtime helper not present or errors
                pass
    except Exception:
        # If the package isn't importable yet, ignore; tests that need it will
        # call setup_questionary_mocks() before importing modules that access it.
        pass

    return mock_q


"""Test helpers for mocking questionary in headless environments.

This module exposes `setup_questionary_mocks(monkeypatch, responses)` which
installs a lightweight fake `questionary` module in `sys.modules` and
patches common internal import locations so tests won't attempt to open a
real console. `responses` may be either a mapping (message/name/prompt_type ->
value) or a callable factory with signature
`factory(kind=<str>, name=<opt>, message=<opt>, choices=<opt>, kwargs=<dict>)`.
"""

import typing

# Singleton factories per-kind so identity checks (``is``) and
# monkeypatch.setattr("questionary.X", ...) are reliable across
# multiple setup calls. Factories should consult the current responder
# so their behavior can change when tests call setup_questionary_mocks
# repeatedly, but the callable identity remains stable.
_factory_singletons: dict = {}
_current_responder = None


def _make_responder(responses: typing.Union[typing.Mapping, typing.Callable]):
    if callable(responses):
        return responses

    mapping = dict(responses or {})

    def responder(kind=None, name=None, message=None, choices=None, kwargs=None):
        # Prefer exact message matches, then name, then kind, then sensible defaults
        if message is not None:
            key = str(message)
            if key in mapping:
                return mapping[key]
            # allow fuzzy substring matches to be tolerant in tests
            for k in mapping:
                try:
                    if isinstance(k, str) and (k == key or k in key or key in k):
                        return mapping[k]
                except Exception:
                    continue

        if name and name in mapping:
            return mapping[name]

        if kind and kind in mapping:
            return mapping[kind]

        # sensible defaults
        if kind == "checkbox":
            return []
        if kind == "confirm":
            return True
        return "default_text"

    return responder


def setup_questionary_mocks(monkeypatch, responses=None):
    """Install test-friendly questionary mocks.

    Args:
        monkeypatch: pytest monkeypatch fixture
        responses: mapping or callable used to compute prompt responses
    Returns:
        The mock questionary object installed into `sys.modules`.
    """
    # Provide sensible defaults when none supplied (keeps older tests working
    # when they call setup_questionary_mocks(monkeypatch) with no args).
    if responses is None:
        responses = {
            "text": "default_text",
            "select": "default_option",
            "confirm": True,
            "checkbox": ["default_choice"],
            "password": "default_password",
            "autocomplete": "default_auto",
            "path": "/default/path",
        }

    responder = _make_responder(responses)
    # Update the module-level responder so existing singleton factories
    # created in previous setup calls will consult the new responder and
    # return updated values without recreating factory callables.
    global _current_responder
    _current_responder = responder

    # Create stable factory functions and prompt objects so tests that check
    # identity (e.g. `c._factory is questionary.confirm`) and attribute access
    # (e.g. returned_object.name) behave consistently.
    def _make_prompt_object(name, kwargs, value):
        """Return an object that mimics a real questionary prompt: has `.ask()`
        and exposes `.name` and `.kwargs` for tests that inspect them.

        Additionally, provide a small mapping-like surface so older tests that
        call `.get()` or treat the returned prompt as a mapping succeed.
        """

        class PromptObj:
            def __init__(self, name, kwargs, value):
                self.name = name
                self.kwargs = dict(kwargs or {})
                self._value = value

            def ask(self):
                return self._value

            # Minimal mapping-like accessors so tests that call `.get()` or
            # index into the returned object behave as if it's a dict when the
            # underlying value is a mapping.
            def get(self, key, default=None):
                try:
                    if isinstance(self._value, dict):
                        if key in self._value:
                            return self._value.get(key, default)
                    # Fallback to expose commonly-requested keys from kwargs
                    if key in self.kwargs:
                        return self.kwargs.get(key, default)
                except Exception:
                    pass
                return default

            def __getitem__(self, key):
                if isinstance(self._value, dict):
                    return self._value[key]
                raise TypeError("PromptObj value is not subscriptable")

            def keys(self):
                if isinstance(self._value, dict):
                    return self._value.keys()
                return []

            def items(self):
                if isinstance(self._value, dict):
                    return self._value.items()
                return []

            def __iter__(self):
                if isinstance(self._value, dict):
                    return iter(self._value)
                return iter(())

            def __repr__(self):
                return f"<Prompt name={self.name!r} value={self._value!r}>"

        return PromptObj(name, kwargs, value)

    def make_factory(kind):
        # Return a singleton callable per kind. The callable consults the
        # module-level _current_responder to compute its return value so
        # repeated calls to setup_questionary_mocks can update responses
        # without creating new callables (preserving identity checks).
        if kind in _factory_singletons:
            return _factory_singletons[kind]

        def factory(*args, **kwargs):
            # use the live responder (may be updated by subsequent setups)
            val = None
            try:
                val = _current_responder(
                    kind=kind,
                    name=kwargs.get("name"),
                    message=kwargs.get("message"),
                    choices=kwargs.get("choices"),
                    kwargs=kwargs,
                )
            except Exception:
                # Fallback to local responder captured at setup time
                try:
                    val = responder(
                        kind=kind,
                        name=kwargs.get("name"),
                        message=kwargs.get("message"),
                        choices=kwargs.get("choices"),
                        kwargs=kwargs,
                    )
                except Exception:
                    val = None
            # If the caller passed a `name` or positional name, expose it
            name = None
            if kwargs.get("name"):
                name = kwargs.get("name")
            elif len(args) >= 1:
                name = args[0]
            # Default to the kind when no explicit name is provided so callers
            # that expect a named prompt (e.g., Component.create_questionary_component)
            # get a sensible identifier.
            if not name:
                name = kind
            # If the caller passed through structured kwargs (default, choices,
            # validate) surface them in the returned prompt mapping only when
            # the responder produced a mapping. If the responder returned a
            # scalar, return it directly from .ask() to match tests that
            # expect a raw value.
            out_val = None
            try:
                if isinstance(val, dict):
                    out_val = dict(val)
                else:
                    out_val = val
            except Exception:
                out_val = val

            # Merge common keys from kwargs into the returned mapping only if
            # the output is a mapping/dict so tests that expect mapping-like
            # behavior can observe them.
            if isinstance(out_val, dict):
                if "default" in kwargs:
                    out_val.setdefault("default", kwargs.get("default"))
                if "choices" in kwargs:
                    out_val.setdefault("choices", kwargs.get("choices"))
                if "validate" in kwargs:
                    out_val.setdefault("validate", kwargs.get("validate"))

            return _make_prompt_object(name, kwargs, out_val)

        # give a helpful __name__ for debugging
        factory.__name__ = f"mock_questionary_{kind}"
        _factory_singletons[kind] = factory
        return factory

    # Use a real module object so ``from questionary import X`` works
    mock_q = types.ModuleType("questionary")
    mock_q.text = make_factory("text")
    mock_q.select = make_factory("select")
    mock_q.confirm = make_factory("confirm")
    mock_q.password = make_factory("password")
    mock_q.checkbox = make_factory("checkbox")
    mock_q.autocomplete = make_factory("autocomplete")
    mock_q.path = make_factory("path")
    # expose a ValidationError compatible with prompt_toolkit so validators
    # that raise prompt_toolkit.validation.ValidationError compare equal to
    # the exception type tests expect (questionary.ValidationError).
    try:
        from prompt_toolkit.validation import ValidationError as PTValidationError

        mock_q.ValidationError = PTValidationError
    except Exception:
        # Fallback to our lightweight ValidationError class defined earlier
        try:
            mock_q.ValidationError = ValidationError
        except NameError:
            mock_q.ValidationError = Exception
    # Provide a minimal Validator base class so modules that subclass it
    # (e.g. `class NumberValidator(Validator)`) can import it during module
    # import time.
    mock_q.Validator = object

    # Use the module-level Separator class for consistency
    mock_q.Separator = Separator

    def _prompt(questions, **kwargs):
        # Default behavior: return a dict with a 'prompted' key so tests that
        # expect the original question list are able to assert identity.
        # Tests that monkeypatch `questionary.prompt` will replace this.
        return {"prompted": questions}

    # attach helpers to the mock object
    mock_q.Separator = Separator
    mock_q.prompt = _prompt

    # Minimal Style implementation so `from questionary import Style` works
    class Style:
        def __init__(self, rules=None):
            # rules is often a list of (token, style) tuples
            self._style_rules = list(rules or [])

        def __repr__(self):
            return f"<Style rules={len(self._style_rules)}>"

    mock_q.Style = Style

    # Capture previous 'questionary' module (if any) so we can update
    # existing module-level references later.
    prev_q = sys.modules.get("questionary")

    # ensure sys.modules has our fake module so imports pick it up
    sys.modules["questionary"] = mock_q

    # Also set the package-level runtime cache so modules that use the
    # centralized resolver will immediately see the mock. This makes the
    # testing contract explicit and avoids stale-reference problems.
    try:
        import importlib as _il

        _rt = _il.import_module("questionary_extended._runtime")
        _rt.set_questionary_for_tests(mock_q)
    except Exception:
        # If the runtime helper isn't importable in the test environment
        # (very early import scenarios), it's okay—sys.modules entry will
        # still be used when the package resolves questionary lazily.
        pass

    # Also push the same factory callables into the module-level proxy
    # (`questionary_extended._questionary_proxy.questionary_proxy`) so
    # modules that import that proxy and then call `proxy.text` will
    # observe the same callable instances. This synchronizes the proxy
    # overrides with the sys.modules entry and the runtime accessor.
    try:
        import importlib as _il

        _qp = _il.import_module("questionary_extended._questionary_proxy")
        qp = getattr(_qp, "questionary_proxy", None)
        if qp is not None:
            for _n in (
                "text",
                "select",
                "confirm",
                "password",
                "checkbox",
                "autocomplete",
                "path",
                "prompt",
                "Separator",
            ):
                try:
                    if hasattr(mock_q, _n):
                        setattr(qp, _n, getattr(mock_q, _n))
                except Exception:
                    continue
    except Exception:
        pass

    # Attempt to patch known package internals that may have imported
    # `questionary` already so their local references point at our mock.
    # This avoids identity mismatches for tests that import a module and
    # then expect `module.questionary` to be the same object as the one
    # installed into sys.modules.
    try:
        import importlib as _il

        for modname in (
            "questionary_extended.core.prompts_base",
            "questionary_extended.prompts_extended",
            # NOTE: avoid injecting proxies into core.component_wrappers here. The
            # component_wrappers module defines its own convenience factory
            # functions (text/select/...) which should remain as the
            # canonical Component factories during tests. Injecting
            # proxies here can accidentally replace those factory
            # functions with direct proxies to the runtime `questionary`
            # mock (causing convenience wrappers to return prompt
            # instances instead of Component objects). The core.component_wrappers
            # module will still receive a `questionary` attribute so
            # runtime resolution works; we only avoid replacing its
            # factory symbols.
            # "questionary_extended.core.component",
            "questionary_extended.cli",
        ):
            try:
                m = _il.import_module(modname)
                try:
                    m.questionary = mock_q

                    # For common symbol names, install thin proxy callables on
                    # the module that forward to the live `sys.modules['questionary']`
                    # entry. This ensures tests that monkeypatch `questionary.<name>`
                    # will be observed by modules that captured the symbol at
                    # import-time (they'll call the proxy which looks up the
                    # current value on each invocation).
                    def _make_proxy(attr_name):
                        def _proxy(*args, **kwargs):
                            q = sys.modules.get("questionary")
                            if q is None:
                                raise RuntimeError("questionary mock not installed")
                            fn = getattr(q, attr_name)
                            return fn(*args, **kwargs)

                        _proxy.__name__ = f"proxy_questionary_{attr_name}"
                        return _proxy

                    for _n in (
                        "text",
                        "select",
                        "confirm",
                        "password",
                        "checkbox",
                        "autocomplete",
                        "path",
                        "prompt",
                        "Separator",
                    ):
                        try:
                            if hasattr(m, _n):
                                existing = getattr(m, _n)
                                # Only replace if the existing attr appears to be
                                # a reference to the external `questionary` module
                                # (e.g., imported via `from questionary import select`).
                                mod_of_existing = getattr(existing, "__module__", "")
                                if (
                                    mod_of_existing.startswith("questionary")
                                    or mod_of_existing == "questionary"
                                ):
                                    setattr(m, _n, _make_proxy(_n))
                                else:
                                    # Skip replacing module-defined functions to avoid
                                    # clobbering our package's own API.
                                    continue
                            else:
                                # Do NOT inject proxies into modules that didn't
                                # originally define the symbol. Previously we
                                # created attributes unconditionally which could
                                # overwrite legitimate functions (eg. component.text).
                                continue
                        except Exception:
                            continue
                except Exception:
                    pass
            except Exception:
                # If module isn't importable yet, skip it — the calling test
                # will import after setup_questionary_mocks and pick up our
                # sys.modules entry instead.
                continue
    except Exception:
        pass

    # Ensure any already-imported modules that kept a reference to the
    # previous 'questionary' object now point at our mock. This addresses
    # the common test pattern where tests `import questionary` at module
    # scope during collection; replacing the sys.modules entry alone is
    # insufficient to update those module-level variables. We iterate the
    # modules list defensively and replace attributes named 'questionary'
    # that still reference the prior object.
    try:
        if prev_q is not None:
            for mod in list(sys.modules.values()):
                try:
                    if not hasattr(mod, "__dict__"):
                        continue
                    if mod.__dict__.get("questionary") is prev_q:
                        mod.__dict__["questionary"] = mock_q
                except Exception:
                    continue
    except Exception:
        pass

    # Ensure parent package attributes for already-loaded submodules are
    # exposed as attributes on their parent package/module objects. Tests
    # commonly use monkeypatch.setattr with dotted import paths which rely
    # on attribute traversal (eg. "questionary_extended.core.component.questionary").
    # If a submodule exists in sys.modules but the parent package object
    # doesn't have a corresponding attribute, monkeypatch.resolve will raise
    # an AttributeError. We perform a best-effort synchronization of the
    # existing sys.modules entries without importing new modules (to avoid
    # executing prompt-toolkit code during collection).
    try:
        import importlib as _il

        pkg = sys.modules.get("questionary_extended")
        if pkg is None:
            try:
                pkg = _il.import_module("questionary_extended")
            except Exception:
                pkg = None

        if pkg is not None:
            for modname in list(sys.modules.keys()):
                if not modname.startswith("questionary_extended."):
                    continue
                parts = modname.split(".")
                # Walk the parts and ensure parent attributes point at the
                # corresponding child modules when they're already loaded.
                for i in range(1, len(parts)):
                    parent_name = ".".join(parts[:i])
                    child_name = parts[i]
                    parent_mod = sys.modules.get(parent_name)
                    child_mod = sys.modules.get(".".join(parts[: i + 1]))
                    if parent_mod is None or child_mod is None:
                        continue
                    try:
                        setattr(parent_mod, child_name, child_mod)
                    except Exception:
                        # Ignore failures — this is a non-critical best-effort
                        # synchronization step used only for monkeypatch resolution.
                        continue
    except Exception:
        pass

    # Do NOT import package internals here: importing modules can execute
    # top-level code (including prompt-toolkit creation) and block test
    # collection on headless CI/Windows. Rely on inserting into sys.modules
    # and setting the runtime accessor instead. Tests that need to monkeypatch
    # already-imported modules should set attributes themselves.

    return mock_q


class FakePrompt:
    """Compatibility fake prompt used by some older tests."""

    def __init__(self, answer=None):
        self._answer = answer

    def ask(self):
        return self._answer


class DummyState:
    """Simple in-memory state used by tests that expect a state-like object."""

    def __init__(self):
        self._data = {}

    def set(self, key, value):
        self._data[key] = value

    def get(self, key, default=None):
        return self._data.get(key, default)

    def get_all_state(self):
        return dict(self._data)


def setup_questionary_with_custom_responses(monkeypatch, factory):
    """Backward-compatible alias to install a callable responder."""
    return setup_questionary_mocks(monkeypatch, factory)


# Ensure the core.component module exposes a `questionary` attribute so tests
# that monkeypatch that symbol using a string target can succeed even when
# the real package isn't present or has been dynamically imported. This
# assignment is safe (idempotent) and will be a no-op if the module isn't
# importable in the running environment.
try:
    import importlib

    try:
        _comp = importlib.import_module("questionary_extended.core.component")
        if not hasattr(_comp, "questionary"):
            _comp.questionary = None
    except Exception:
        pass

    try:
        _comp2 = importlib.import_module("src.questionary_extended.core.component")
        if not hasattr(_comp2, "questionary"):
            _comp2.questionary = None
    except Exception:
        pass
except Exception:
    pass
