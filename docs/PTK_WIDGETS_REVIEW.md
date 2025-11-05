PTK widget factory and adapter review

Summary
-------
This short review records the decisions made in the `feature/demos` branch
regarding mapping domain elements to prompt-toolkit widgets and the minimal
runtime contract used to keep domain state and widget state synchronized.

Decisions implemented
- Headless descriptors: `map_element_to_widget` returns a stable dict used by
  unit tests and CI (keys: `path`, `name`, `variant`, `type`, `options`,
  `selected`, `ptk_widget`).
- Best-effort real widgets: when prompt-toolkit is importable, the factory
  creates real widgets and attaches small adapter-friendly attributes:
  - `_tui_path` : element path
  - `_tui_focusable` : boolean
  - `_tui_sync` : callable to push widget state back to the domain element
- Adapter wiring: `PTKAdapter.build_real_layout()` registers widget mappings
  and records `_tui_sync` callables; adapter invokes sync on Enter and before
  focus changes (Tab/Shift-Tab). The adapter also calls `_tui_sync()` once at
  mount time to populate initial state.

Open questions & version concerns
- prompt-toolkit API differences: `CheckboxList` and attribute names vary by
  version. The current approach probes common attribute names at runtime. This
  is pragmatic but brittle; we should consider a small wrapper interface
  (e.g. `TuiWidgetAdapter`) to normalize accessors across versions.
- Event wiring: wrapping widget handlers (`handler`, `accept`) may not be
  robust across all widget types; tests cover common cases but edge cases may
  require adapter-level event routing.
- Integration testing: running real prompt-toolkit Applications in CI can be
  flaky (terminal / tty requirements). The current approach uses guarded
  integration tests (skip when PTK unavailable) and keeps most behavior
  covered by headless tests.

Suggested next steps
- Add a small `TuiWidgetAdapter` class to standardize `focus(), sync(), get_value()`
  semantics and delegate to different prompt-toolkit widget types.
- Expand tests to include a fake widget adapter to validate all sync/wrapping
  code paths without requiring a real terminal.
- If we intend to support multiple PTK versions widely, add compatibility
  shims for CheckboxList/RadioList attribute names.

Conclusion
----------
The current implementation is pragmatic and keeps headless tests deterministic
while enabling richer integration when prompt-toolkit is present. The small
runtime contract (`_tui_sync`, `_tui_path`, `_tui_focusable`) is readable and
DI-friendly; wrapping PTK internals with a thin adapter would reduce runtime
probing and make the code easier to evolve.