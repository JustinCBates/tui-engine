# TUI Engine — Architecture Overview

This document consolidates the current design decisions, reconciles prior design documents, and lays out a concrete implementation plan for the new TUI Engine core.

This file intentionally replaces the earlier multi-class model (Card, Section, Assembly, Spatial engine) with a single, recursive container primitive (ContainerElement) and a prompt-toolkit driven rendering/input pipeline.

## Goals

- Provide a small, consistent core API for composing UI trees.
- Use prompt-toolkit as the canonical rendering and input backbone.
- Remove the legacy spatial layout engine and all adapter indirection.
- Keep domain logic (state, validation, business rules) separate from rendering.
- Ship an explicit migration/refactor plan that is destructive by design (no adapters).

## High-level decisions

1. Single container primitive
   - Replace `Card`, `Section`, and `Assembly` with `ContainerElement`.
   - `ContainerElement` is recursive and can contain other `ContainerElement`s and leaf elements.
   - A `variant`/`style` property controls presentation (e.g. `section`, `card`, `header`, `footer`), not behavior.

2. Prompt-toolkit as renderer and input system
   - All rendering, layout, keyboard handling, and widget behavior will be implemented using `prompt_toolkit` primitives (HSplit, VSplit, Frame, Window, Controls, Widgets, KeyBindings, Application).
   - Use `PromptSession` for blocking prompts and `Application` for continuous UIs.

3. Event and state model
   - Implement a thin domain-level pub/sub event bus for business events (state changes, validation results, navigation events).
   - Map domain events to prompt-toolkit redraws via `app.invalidate()` and prompt-toolkit scheduling (`create_background_task`, asyncio).

4. Dependency Injection
   - Adopt a module-level factory/provider pattern for external dependencies (questionary replacements, prompt-toolkit factories, etc.). See the DI design notes.

5. Destructive refactor policy
   - The legacy core will be removed entirely (no adapters). We will keep a safety branch/tag prior to deletion for archival.

## Why these choices

- Simplicity: One container type avoids conceptual duplication and simplifies the public API.
- Predictability: Mapping directly to prompt-toolkit reduces the amount of custom layout code we must maintain and leverages a mature layout/event system.
- Separation of concerns: Domain model and UI rendering are cleanly separated. The UI layer is an adapter over the domain tree.

## Public API contract (sketch)

- ContainerElement(name: str, variant: str = "container", style: Optional[dict] = None)
  - add_child(child)
  - remove_child(child)
  - get_render_lines(width: int = 80) -> List[str]
  - to_ptk_container() -> prompt_toolkit.container (adapter function)
  - visible: bool; mark_dirty(); clear_dirty(); metadata/state dict

- Page(title: str = "")
  - add_element(elem)
  - render()  # for non-interactive or debug flows
  - run_application() -> starts a prompt-toolkit Application using an adapter

Note: `to_ptk_container()` is an internal adapter used to transform a ContainerElement tree into a prompt-toolkit layout (HSplit/VSplit/Frame). It is not intended for library consumers.

## Event system

- Use prompt-toolkit's built-in primitives for input events (KeyBindings, Buffer callbacks, widget handlers).
- Implement a small domain-level pub/sub for cross-component events:
  - publish(topic: str, payload: Any)
  - subscribe(topic: str, handler: Callable)
  - Example topics: `container.changed`, `navigation.request`, `validation.result`.
- Adapter will translate domain events into prompt-toolkit redraws (call `app.invalidate()`), and may run callbacks on the prompt-toolkit event loop.

## Prompt-toolkit responsibilities

- Layout & sizing: HSplit/VSplit, Window, Frame, FloatContainer
- Widget rendering: TextArea, RadioList, CheckboxList, Buttons
- Input handling: KeyBindings, Buffer events, widget callbacks
- Styling & theming: Style strings and per-widget style selectors
- Async tasks & background work: `create_background_task`, `app.invalidate()`

## Dependency injection

- Use a module-level provider (e.g., `questionary_provider` or `prompt_provider`) for external modules so tests can inject stub implementations.
- Public API: `set_x_factory(factory)`, `get_x()`, `clear_x_factory()` per provider.

## Files & layout (recommended)

- `src/tui_engine/container.py` — ContainerElement, Element (leaf)
- `src/tui_engine/page.py` — Page class, run/render helpers
- `src/tui_engine/ptk_adapter.py` — ContainerElement -> prompt-toolkit adapter and Application wrapper
- `src/tui_engine/events.py` — small pub/sub wrapper used by domain objects
- `src/tui_engine/di.py` — simple provider/factory helpers
- `docs/ARCHITECTURE.md` — this file

## Implementation Plan

This section expands the earlier milestone list into a concrete implementation plan with deliverables, acceptance criteria, and rough estimates. The plan is organized into phases so we can stop at any point with a usable system.

Phase A — Scaffold & API (2–3 days)
- Deliverables:
  - `src/tui_engine/container.py` implementing `ContainerElement` and `Element` (leaf).
  - `src/tui_engine/page.py` with `Page` and a non-ptk `get_render_lines()` fallback renderer.
  - Unit tests for tree composition and `get_render_lines()` behavior.
- Acceptance criteria:
  - Library imports cleanly.
  - `run_section_demo()` can be implemented using the fallback renderer and produces readable output.

Phase B — Prompt-toolkit adapter (2–4 days)
- Deliverables:
  - `src/tui_engine/ptk_adapter.py` that converts a `ContainerElement` tree into prompt-toolkit containers (HSplit/VSplit/Frame).
  - An `Application` wrapper that supports redraws via `app.invalidate()` and integrates keybindings for navigation/exit.
  - One demo refactored to run under the adapter.
- Acceptance criteria:
  - Adapter renders header/body/footer and nested containers correctly in non-fullscreen mode.
  - Keybindings (Tab/Enter/Ctrl-C) behave predictably and trigger domain events / redraws.

Phase C — Delete legacy core & CI migration (1–2 days)
- Deliverables:
  - Archive branch `backup/legacy-core-before-refactor` containing the full old core.
  - Remove `src/questionary_extended/core` and any spatial engine modules from the main tree.
  - CI configuration updated to run new tests and lint checks.
- Acceptance criteria:
  - Test suite passes (or failures are documented and tracked) on CI with the new core.
  - No references to old core remain in imports across the repo.

Phase D — Tests, polish & docs (2–3 days)
- Deliverables:
  - Integration tests exercising the adapter in headless/non-fullscreen mode.
  - Developer docs and migration notes updated in `docs/`.
  - A small sample app demonstrating the new API and prompt-toolkit interaction.
- Acceptance criteria:
  - Tests covering at least the container rendering contract and a smoke test of the prompt-toolkit Application.
  - README/documentation for contributors describing how to extend container styles and adapter mapping.

## Backlog (prioritized)

The backlog captures work that is not in the initial phases but will be needed for a production-quality release. Items are prioritized and given rough estimates.

P0 — Must-have
- Implement module-level DI providers for external dependencies (questionary/prompt replacements). (0.5 day)
- Add unit tests for `Page.card()` / equivalent convenience helpers that users expect. (0.5 day)

P1 — High priority
- Implement domain-level pub/sub bridge that schedules callbacks on the prompt-toolkit event loop. (1 day)
- Add simple theming/style primitives and a mapping file for `variant -> prompt-toolkit style`. (1 day)
- Add snapshot tests for `get_render_lines()` outputs for common demos. (1 day)

P2 — Medium priority
- Implement keyboard focus management utilities and a small focus-trap helper for modal dialogs. (1–2 days)
- Add a small adapter for `PromptSession` to be used by blocking prompts without switching to full-screen. (0.5 day)

P3 — Low priority / Nice-to-have
- Animation utilities using `create_background_task` for animated transitions. (2 days)
- Accessibility checks and basic screen-reader hints (investigate prompt-toolkit capabilities). (2 days)

Notes about prioritization
- P0/P1 items should be delivered before deleting the legacy core. P2/P3 can be implemented iteratively after the main adapter is in place.


## Conflicts with prior design docs and resolution

- Prior: Spatial engine provided per-section reservation, clipping, and incremental buffer diffing.
  - Decision: Remove the custom spatial engine. prompt-toolkit provides robust sizing/scrolling and redraw semantics. The domain model will provide size hints only where necessary; the adapter will use prompt-toolkit sizing rules.

- Prior: Adapters around `questionary` and multiple fallback factories.
  - Decision: Replace complex fallback with a module-level provider/factory for external prompt modules. Use prompt-toolkit primitives directly for interactive UIs; keep `PromptSession` wrappers for simple backward-compatible prompts.

- Prior: Multiple container classes (Card/Section/Assembly).
  - Decision: Remove them. Implement a single `ContainerElement` with `variant` and `style` to differentiate visual treatment only.

## Quality gates

- All new code must have unit tests covering the container tree (compositions, visibility, render lines).
- Integration tests must exercise the adapter with a non-fullscreen prompt-toolkit Application and call `app.invalidate()` in response to domain events.
- CI must run the test suite in headless mode where possible; for prompt-toolkit UI tests we will use non-fullscreen TextArea-based rendering or snapshot tests of `get_render_lines()`.

## Backups & rollback

- Before any destructive deletion of the legacy core, create a backup branch:

```
git branch backup/legacy-core-before-refactor
git push origin backup/legacy-core-before-refactor
```

This preserves history and allows safe rollback if the refactor needs to be reversed.

## Short-term next steps (this sprint)

1. Create `ContainerElement` scaffold and `Page` with `get_render_lines()` fallback. (todo assigned)
2. Implement `ptk_adapter` and a single demo replacement. (todo assigned)
3. Create backup branch and delete legacy core once the adapter is validated.

-----

If you'd like, I can now implement Phase A (scaffold the ContainerElement and Page) on `feature/refactor`, push the changes, and add a demo that uses the fallback renderer. Confirm and I will proceed.

## Additional consolidated notes from design documents

Below are two non-conflicting design summaries pulled from the repository's design docs. These are included here so implementation work has a single reference for DI and demo expectations.

### Dependency Injection (DI) — Module-level Provider

Rationale:
- Replace ad-hoc import fallback logic with a single, testable provider.
- Keep default behavior (direct import) while enabling easy injection for tests.

Recommended minimal provider API (sketch):

```python
# src/tui_engine/questionary_factory.py
from typing import Optional, Callable, Any

QuestionaryFactory = Callable[[], Any]

class QuestionaryProvider:
  def __init__(self):
    self._factory: Optional[QuestionaryFactory] = None
    self._cached = None

  def set_factory(self, factory: QuestionaryFactory) -> None:
    self._factory = factory
    self._cached = None

  def get_questionary(self):
    if self._factory is not None:
      if self._cached is None:
        self._cached = self._factory()
      return self._cached
    import questionary
    return questionary

_provider = QuestionaryProvider()

def set_questionary_factory(factory: QuestionaryFactory) -> None:
  _provider.set_factory(factory)

def get_questionary():
  return _provider.get_questionary()

def clear_questionary_factory():
  _provider.set_factory(None)
```

Usage:
- Library code calls `get_questionary()` to obtain the module (or injected mock) and invokes components from it.
- Tests call `set_questionary_factory(lambda: mock)` to inject mocks and `clear_questionary_factory()` to restore default behavior.

Benefit: greatly simplifies testing and removes brittle import fallback logic while preserving backward compatibility.

### Enhanced Demo Summary (what demos should provide)

Key expectations for the demo system (consolidated):
- Each UI component should have a runnable basic demo and an "Explore Features" deeper demo.
- Demos should include copy-ready code samples for users to reuse.
- Navigation should be simple: Run Basic Demo, Explore Features, Copy Code, Back.
- Coverage target: provide demos for all top-level container features and for common leaf components.

Integration notes for the new architecture:
- Implement demo rendering using the `ptk_adapter` (non-fullscreen Application) or the fallback `get_render_lines()` for headless tests.
- Provide a helper `get_code_sample(component_key)` that returns a verified snippet for the demo UI.
- Keep demo logic orthogonal to the core library: demos live in `examples/` and call the public `ContainerElement`/`Page` API.

These consolidated notes are intentionally brief; they are here to ensure the implementation plan and backlog account for DI, demo coverage, and testing approaches described in the existing design documents.
