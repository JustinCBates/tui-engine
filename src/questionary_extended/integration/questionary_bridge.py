"""
Questionary bridge for questionary-extended.

Provides a small compatibility layer that can turn our core Component wrappers
into runnable questionary prompts and collect their results into PageState.

This is a minimal, incremental implementation intended to be expanded as the
core Page/Card/Assembly APIs are completed.
"""

import importlib
from types import SimpleNamespace
from typing import Any, Iterable

from src.tui_engine.questionary_factory import get_questionary
from ..core.component_wrappers import Component
from ..core.state import PageState


# Backwards-compatible module-level placeholder for tests that monkeypatch
def _questionary_placeholder(*a: object, **kw: object) -> object:
    raise NotImplementedError("questionary is not configured in this environment")


# A lightweight fallback questionary object used when no runtime or proxy is
# available. Tests that inject a real questionary should replace this by
# either installing a module in sys.modules or using the runtime setter.
_FALLBACK_QUESTIONARY = SimpleNamespace(
    text=_questionary_placeholder,
    select=_questionary_placeholder,
    confirm=_questionary_placeholder,
    password=_questionary_placeholder,
    checkbox=_questionary_placeholder,
    autocomplete=_questionary_placeholder,
    path=_questionary_placeholder,
    prompt=_questionary_placeholder,
)

# Expose a module-level `questionary` attribute so tests that use
# `monkeypatch.setattr('questionary_extended.integration.questionary_bridge.questionary', ...)`
# can reliably replace it. Tests sometimes expect this attribute to exist
# even if the real runtime resolver isn't configured.
questionary = _FALLBACK_QUESTIONARY


class QuestionaryBridge:
    """Lightweight bridge to run questionary prompts from core components."""

    def __init__(self, state: PageState) -> None:
        self.state = state

    def _resolve_questionary(self) -> Any:
        """Resolve the active questionary object using the DI system with fallbacks.

        Resolution order:
        1. Module-level `questionary` override (for test monkeypatching)
        2. DI system questionary module
        3. Fallback placeholder object
        """
        # Honor a module-level `questionary` when present (tests may set this
        # explicitly to None to simulate absence). This preserves monkeypatch support.
        if "questionary" in globals():
            return globals().get("questionary")

        # Use the DI system as primary resolution
        try:
            q = get_questionary()
            if q is not None:
                return q
        except Exception:
            # DI system failed; fall back to placeholder
            pass

        return _FALLBACK_QUESTIONARY

    def ask_component(self, component: Component) -> Any:
        """
        Render a single Component using questionary and return the answer.

        The Component wrapper exposes `create_questionary_component()` which
        returns a questionary prompt object (for supported component types).
        """
        questionary = self._resolve_questionary()

        # If the resolved questionary is explicitly absent (tests may set
        # the module-level attribute to None), surface a clear RuntimeError
        # so callers/tests can detect that prompts are not available.
        if questionary is None:
            raise RuntimeError(
                "questionary is not available in the current environment"
            )

        # Creating the prompt object may itself access prompt_toolkit's
        # console output and raise NoConsoleScreenBufferError on Windows
        # in headless environments. Wrap creation to normalize those
        # errors into RuntimeError for callers/tests, but allow errors
        # raised during `.ask()` to propagate so calling code can handle
        # specific exceptions like KeyboardInterrupt.
        try:
            prompt = component.create_questionary_component()
        except Exception as e:
            try:
                from prompt_toolkit.output.win32 import (  # type: ignore
                    NoConsoleScreenBufferError,  # type: ignore
                )

                if isinstance(e, NoConsoleScreenBufferError):
                    raise RuntimeError(
                        "questionary not usable in this environment"
                    ) from e
            except Exception:
                pass

            raise RuntimeError(f"questionary prompt creation failed: {e}") from e

        # Wrap `.ask()` exceptions into a normalized RuntimeError message so
        # tests that assert on the bridge's error text remain stable. Preserve
        # the original exception as the __cause__.
        try:
            answer = prompt.ask()
        except Exception as e:
            raise RuntimeError("questionary prompt failed") from e

        # Persist into state using the component name (global key)
        # Callers may prefer to namespace the key (assembly.field) themselves
        self.state.set(component.name, answer)
        return answer

    def _walk_components(self, items: Iterable[Any]) -> Iterable[Component]:
        """Yield Component instances from nested Card/Assembly/component containers."""
        for item in items:
            # Prefer duck-typing over strict isinstance checks so tests that
            # load modules in isolation (file-based imports) still work when
            # objects implement the expected interface.
            if hasattr(item, "create_questionary_component") and hasattr(item, "name"):
                # Component-like object
                yield item
                continue

            # Container-like: object that exposes a `components` attribute
            comps = getattr(item, "components", None)
            if comps is None:
                # Unknown/unsupported item: ignore
                continue

            # Iterate the child components and recurse where necessary
            for c in comps:
                # If child looks like a Component, yield it; otherwise recurse
                if hasattr(c, "create_questionary_component") and hasattr(c, "name"):
                    yield c
                else:
                    yield from self._walk_components(getattr(c, "components", []))

    def run(self, root_items: Iterable[Any]) -> None:
        """
        Run all components found under `root_items` (typically a Page.components list).

        Results are written into the provided PageState instance.
        """
        for component in self._walk_components(root_items):
            # Determine visibility; visibility code may raise, so default to
            # visible on error to avoid hiding components unexpectedly.
            try:
                visible = component.is_visible(self.state.get_all_state())
            except Exception:
                visible = True

            if not visible:
                continue

            self.ask_component(component)


__all__ = ["QuestionaryBridge"]
