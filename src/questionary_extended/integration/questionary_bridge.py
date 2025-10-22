"""
Questionary bridge for questionary-extended.

Provides a small compatibility layer that can turn our core Component wrappers
into runnable questionary prompts and collect their results into PageState.

This is a minimal, incremental implementation intended to be expanded as the
core Page/Card/Assembly APIs are completed.
"""
from typing import Any, Iterable

try:
    import questionary
except Exception:  # pragma: no cover - runtime environment dependent
    questionary = None  # type: ignore

from ..core import Component, PageState, Card, Assembly


class QuestionaryBridge:
    """Lightweight bridge to run questionary prompts from core components."""

    def __init__(self, state: PageState):
        self.state = state

    def ask_component(self, component: Component) -> Any:
        """
        Render a single Component using questionary and return the answer.

        The Component wrapper exposes `create_questionary_component()` which
        returns a questionary prompt object (for supported component types).
        """
        if questionary is None:
            raise RuntimeError(
                "questionary is not available in the current environment."
            )

        prompt = component.create_questionary_component()
        # The object returned by questionary functions normally implements `.ask()`
        answer = prompt.ask()

        # Persist into state using the component name (global key)
        # Callers may prefer to namespace the key (assembly.field) themselves
        self.state.set(component.name, answer)
        return answer

    def _walk_components(self, items: Iterable[Any]) -> Iterable[Component]:
        """Yield Component instances from nested Card/Assembly/component containers."""
        for item in items:
            if isinstance(item, Component):
                yield item
            elif isinstance(item, Card):
                # Yield components inside the Card
                for c in getattr(item, "components", []):
                    if isinstance(c, Component):
                        yield c
                    else:
                        # Nested containers (Assembly) handled below
                        for c2 in self._walk_components(getattr(item, "components", [])):
                            yield c2
            elif isinstance(item, Assembly):
                for c in getattr(item, "components", []):
                    if isinstance(c, Component):
                        yield c
                    else:
                        for c2 in self._walk_components(getattr(item, "components", [])):
                            yield c2
            else:
                # Unknown item types are ignored for now
                continue

    def run(self, root_items: Iterable[Any]) -> None:
        """
        Run all components found under `root_items` (typically a Page.components list).

        Results are written into the provided PageState instance.
        """
        for component in self._walk_components(root_items):
            # Basic visibility check: Component.is_visible may consult state
            try:
                visible = component.is_visible(self.state.get_all_state())
            except Exception:
                visible = True

            if not visible:
                continue

            self.ask_component(component)


__all__ = ["QuestionaryBridge"]
