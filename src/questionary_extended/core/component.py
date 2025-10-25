"""
Component wrappers for questionary-extended.

This module provides enhanced wrappers around questionary components,
maintaining full API compatibility while adding new capabilities.
"""

import importlib
import sys
from types import SimpleNamespace
from typing import Any, Callable, Dict, List, Optional

# Backwards-compatible module-level attribute for tests that monkeypatch
# the `questionary` module on this module.
# Use the shared proxy so tests can monkeypatch attributes on the module-level
try:
    from .._questionary_proxy import questionary_proxy as questionary
except Exception:
    # Fallback: provide a SimpleNamespace so tests can monkeypatch attributes
    # on the module-level `questionary` even in early import scenarios.
    def _questionary_placeholder(*a: object, **kw: object) -> object:  # type: ignore
        raise NotImplementedError("questionary is not configured in this environment")

    questionary = SimpleNamespace(
        text=_questionary_placeholder,
        select=_questionary_placeholder,
        confirm=_questionary_placeholder,
        password=_questionary_placeholder,
        checkbox=_questionary_placeholder,
        autocomplete=_questionary_placeholder,
        path=_questionary_placeholder,
    )
    # Sentinel to detect the module-level placeholder so runtime or
    # environment-installed `questionary` can be preferred when tests
    # patch the top-level module (sys.modules['questionary']).
    _default_questionary_placeholder = questionary


class Component:
    """
    Base wrapper class for questionary components.

    Provides enhanced functionality while maintaining questionary compatibility:
    from types import SimpleNamespace
    - Enhanced validation with multiple validators
    - State integration and event hooks
    """

    def __init__(self, name: str, component_type: str, **kwargs: Any) -> None:
        """
        Initialize a component wrapper.

        Args:
            name: Component name for state management
            component_type: Type of questionary component (text, select, etc.)
            **kwargs: Component configuration options
        """
        self.name = name
        self.component_type = component_type
        self.config = kwargs
        self.when_condition: Optional[str] = kwargs.get("when")
        self.validators: List[Callable[..., Any]] = []

        # Extract questionary-compatible config
        self.questionary_config = {
            k: v for k, v in kwargs.items() if k not in ["when", "enhanced_validation"]
        }

    def add_validator(self, validator: Callable[..., Any]) -> None:
        """Add a validator function."""
        self.validators.append(validator)

    def is_visible(self, state: Dict[str, Any]) -> bool:
        """Check if component should be visible based on 'when' condition."""
        # Explicit visibility override (show/hide from assemblies)
        if hasattr(self, "visible"):
            return bool(self.visible)

        if not self.when_condition:
            return True

        # TODO: implement expression evaluation of `when` conditions safely
        # For now, default to visible to avoid accidental hiding while the
        # expression evaluator is implemented.
        return True

    def create_questionary_component(self) -> Any:
        """Create the underlying questionary component."""
        from typing import Callable as _Callable
        # Resolution strategy (single-source-first): prefer the centralized
        # runtime accessor so behavior is consistent with the repository-wide
        # contract. The runtime accessor itself should consult sys.modules or
        # an explicit test-installed object. If the accessor returns None,
        # fall back to sys.modules/module-level/import as a last resort.
        q = None
        try:
            _rt = importlib.import_module("questionary_extended._runtime")
            q = _rt.get_questionary()
        except Exception:
            q = None

        # If runtime accessor didn't supply a usable object, try sys.modules
        # next (covers direct monkeypatch.setattr("questionary.x", ...)).
        try:
            if q is None:
                q_sys = sys.modules.get("questionary")
                if q_sys is not None:
                    q = q_sys
        except Exception:
            pass

        # Next prefer a module-level `questionary` attribute if present
        # (covers tests that patch the module directly).
        try:
            if q is None:
                m_q = globals().get("questionary", None)
                if m_q is not None:
                    q = m_q
        except Exception:
            pass

        # Last resort: import top-level module directly.
        if q is None:
            try:
                q = importlib.import_module("questionary")
            except Exception:
                raise ImportError(
                    "`questionary` is not available. In tests call setup_questionary_mocks() or set the runtime mock via questionary_extended._runtime.set_questionary_for_tests(mock)."
                )

        # Prefer the first candidate that provides a callable factory for the
        # requested component type. We search multiple candidates because
        # tests may patch different module objects (module-level attr, the
        # importable 'questionary' module, or the runtime accessor).
        # Validate supported component types early so callers get a clear
        # ValueError for unsupported types (matches existing tests).
        supported = {"text", "select", "confirm", "password", "checkbox", "autocomplete", "path"}
        if self.component_type not in supported:
            raise ValueError(f"Unsupported component type: {self.component_type}")
        candidates = []
        # 1) runtime accessor (single source of truth)
        try:
            _rt = importlib.import_module("questionary_extended._runtime")
            candidates.append(_rt.get_questionary())
        except Exception:
            candidates.append(None)

        # 2) explicit top-level/importable module (sys.modules or import)
        try:
            import importlib as _il

            q_imported = None
            try:
                q_imported = _il.import_module("questionary")
            except Exception:
                q_imported = sys.modules.get("questionary")
            candidates.append(q_imported)
        except Exception:
            candidates.append(sys.modules.get("questionary"))

        # 3) module-level attribute (may be placeholder or patched)
        candidates.append(globals().get("questionary", None))

        # Prefer module-level patches when present (tests often patch
        # `src.questionary_extended.core.component.questionary.<name>`).
        component_func = None
        mod_q = globals().get("questionary", None)
        try:
            attr_mod = getattr(mod_q, self.component_type, None) if mod_q is not None else None
        except Exception:
            attr_mod = None

        # Runtime accessor candidate (already at candidates[0])
        try:
            rt_candidate = candidates[0]
        except Exception:
            rt_candidate = None
        try:
            attr_rt = getattr(rt_candidate, self.component_type, None) if rt_candidate is not None else None
        except Exception:
            attr_rt = None

        # Imported/top-level candidate (candidates[1])
        try:
            imp_candidate = candidates[1]
        except Exception:
            imp_candidate = None
        try:
            attr_imp = getattr(imp_candidate, self.component_type, None) if imp_candidate is not None else None
        except Exception:
            attr_imp = None

        def _is_valid_factory(f):
            if not callable(f):
                return False
            if f is globals().get("_questionary_placeholder"):
                return False
            try:
                modname = getattr(f, "__module__", "")
                if modname.startswith("questionary_extended._questionary_proxy"):
                    return False
            except Exception:
                pass
            return True

        # Selection priority: runtime accessor (single source) -> imported/top-level -> module-level
        # Enforce the repository contract by preferring the runtime accessor when
        # it is set. Fall back to the importable `questionary` module and then
        # to any module-level patched attribute. This keeps a single canonical
        # source while still allowing reasonable fallbacks for tests that patch
        # other places.
        if _is_valid_factory(attr_rt):
            component_func = attr_rt
        elif _is_valid_factory(attr_imp):
            component_func = attr_imp
        elif _is_valid_factory(attr_mod):
            component_func = attr_mod

        if component_func is None:
            raise ValueError(f"Unsupported component type or missing factory: {self.component_type}")

        try:
            return component_func(**self.questionary_config)
        except Exception as exc:
            # Some environments (CI, headless Windows) raise a
            # NoConsoleScreenBufferError from prompt_toolkit when a real
            # console is not available. Tests that intend to invoke
            # questionary should either monkeypatch the functions or use
            # the mocking helper. If a console error occurs, re-raise with
            # a clearer message to help debugging.
            if (
                hasattr(exc, "__class__")
                and exc.__class__.__name__ == "NoConsoleScreenBufferError"
            ):
                raise RuntimeError(
                    "No console available for prompt_toolkit/questionary"
                ) from exc
            raise


# Convenience wrapper functions matching questionary API
def text(name: str, message: Optional[str] = None, **kwargs: Any) -> Component:
    """Create a text input component."""
    if message is None:
        message = f"{name.replace('_', ' ').title()}:"
    return Component(name, "text", message=message, **kwargs)


def select(
    name: str,
    message: Optional[str] = None,
    choices: Optional[List[str]] = None,
    **kwargs: Any,
) -> Component:
    """Create a selection component."""
    if message is None:
        message = f"Choose {name.replace('_', ' ')}:"
    if choices is None:
        choices = []
    return Component(name, "select", message=message, choices=choices, **kwargs)


def confirm(name: str, message: Optional[str] = None, **kwargs: Any) -> Component:
    """Create a confirmation component."""
    if message is None:
        message = f"Confirm {name.replace('_', ' ')}?"
    return Component(name, "confirm", message=message, **kwargs)


def password(name: str, message: Optional[str] = None, **kwargs: Any) -> Component:
    """Create a password input component."""
    if message is None:
        message = f"{name.replace('_', ' ').title()}:"
    return Component(name, "password", message=message, **kwargs)


def checkbox(
    name: str,
    message: Optional[str] = None,
    choices: Optional[List[str]] = None,
    **kwargs: Any,
) -> Component:
    """Create a checkbox component."""
    if message is None:
        message = f"Select {name.replace('_', ' ')}:"
    if choices is None:
        choices = []
    return Component(name, "checkbox", message=message, choices=choices, **kwargs)


def autocomplete(
    name: str,
    message: Optional[str] = None,
    choices: Optional[List[str]] = None,
    **kwargs: Any,
) -> Component:
    """Create an autocomplete component."""
    if message is None:
        message = f"Choose {name.replace('_', ' ')}:"
    if choices is None:
        choices = []
    return Component(name, "autocomplete", message=message, choices=choices, **kwargs)


def path(name: str, message: Optional[str] = None, **kwargs: Any) -> Component:
    """Create a path selection component."""
    if message is None:
        message = f"{name.replace('_', ' ').title()}:"
    return Component(name, "path", message=message, **kwargs)


__all__ = [
    "Component",
    "text",
    "select",
    "confirm",
    "password",
    "checkbox",
    "autocomplete",
    "path",
]
