Release notes (draft) — feature/demos

Summary
-------
This release consolidates legacy UI primitives and introduces a headless-first
adapter model with a prompt-toolkit renderer.

Highlights
- Replaced Card/Section/Assembly with `ContainerElement` and `Element`.
- Added a prompt-toolkit adapter (`PTKAdapter`) with headless descriptors for
  deterministic unit testing.
- Implemented a FocusRegistry and DI-friendly ApplicationWrapper with keybinding
  support and Ctrl-C handling.
- Added `ptk_widget_factory` to map domain elements to prompt-toolkit widgets
  (best-effort) and headless descriptors for tests.
- Introduced `_tui_sync` contract to synchronize widget state back to domain
  elements; adapter invokes sync on accept and focus changes.

Breaking changes
- Public API: `Card`/`Section`/`Assembly` removed in favor of
  `ContainerElement`. See `docs/MIGRATION.md` for automated transformations.

Upgrade notes
- Update imports and usages to `from tui_engine.container import ContainerElement`
  and adjust code to use `container.text(...)`, `container.input(...)` and
  `container.button(..., on_click=...)`.

Tests & CI
- Added unit and integration tests for widget mapping and sync behavior. The
  integration test is guarded and only runs when prompt-toolkit is available to
  avoid CI flakiness.

Known issues & next steps
- Consider wrapping prompt-toolkit widgets in a small `TuiWidgetAdapter` to
  remove fragile attribute probing across PTK versions.
- Add snapshot tests for render lines.
- Plan removal of legacy core modules in a subsequent PR after final
  validation.

Acknowledgements
- Thanks to contributors for early design feedback and test cases.