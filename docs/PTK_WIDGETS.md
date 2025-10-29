PTK widget adapters and testing
================================

This document explains the wrapper Protocols, adapter responsibilities, and example test patterns for prompt-toolkit adapters in this repository.

Overview
--------

We follow a headless-first design: domain elements produce stable headless descriptors suitable for unit tests. When prompt-toolkit is available at runtime we create real widgets and, where beneficial, wrap them in thin adapter objects that implement the `TuiWidgetProtocol` family. Wrappers give us a stable surface for adapters, focus/sync logic, and easier unit testing.

Core Protocols
--------------

The Protocols are defined in `src/tui_engine/widgets/protocols.py` and include:

- `TuiWidgetProtocol` — minimal runtime contract: `_tui_path: Optional[str]`, `_tui_focusable: bool`, `focus()` and `_tui_sync()`.
- `ValueWidgetProtocol` — for single-value widgets (text inputs): `get_value()` and `set_value()`.
- `ChoiceWidgetProtocol` — for option lists (radio/checkbox): `options` and `get_selected()`/`set_selected()`.
- `ActionWidgetProtocol` — for action-like widgets (buttons): `click()`.

Adapter responsibilities
------------------------

Adapters (wrappers) should:

- Expose the minimal Protocol surface above so `PTKAdapter` and other runtime helpers can call `focus()` and `_tui_sync()` without probing raw widget internals.
- Offer a `.ptk_widget` property (or return the raw widget from the adapter) so the prompt-toolkit layout gets the raw widget for mounting and focusing.
- Keep `_tui_sync()` cheap and idempotent — it should push widget state back into the domain element or return the current value for the adapter to persist.
- Avoid complex side-effects; prefer to call domain handlers (e.g., `element.on_change`) rather than mutating global state.

Factory and runtime contracts
-----------------------------

When creating real widgets the factory (`ptk_widget_factory.map_element_to_widget`) will set runtime tags when possible:

- `_tui_path` — path to the domain element (useful for diagnostics and testing)
- `_tui_focusable` — whether the widget should be focused
- `_tui_sync` — a callable that, when called, will synchronize the real widget state back to the domain element. For adapters this is often implemented on the adapter and/or the underlying raw widget.

Testing patterns
----------------

1) Headless unit tests (preferred)

   - Call the headless `map_element_to_widget()` with a synthetic element and assert the returned descriptor shape (type, options, value, selected).
   - Use the headless `Page.render()` and `ContainerElement.get_render_lines()` to snapshot rendered output.

2) Adapter unit tests (fast, deterministic)

   - Create a small fake raw widget implementing the few attributes used by the adapter (e.g., a fake `TextArea` with `.text` and `.focus()`).
   - Instantiate the adapter with the fake widget and assert `get_value()`, `set_value()`, `focus()`, and `_tui_sync()` behaviors.

   Example (text input):

   ```python
   fake = type('F', (), {'text': 'x', 'focus': lambda self: setattr(self, '_f', True)})()
   adapter = TextInputAdapter(fake)
   assert adapter.get_value() == 'x'
   adapter.set_value('y')
   assert fake.text == 'y'
   adapter._tui_sync()
   assert adapter._last_synced.startswith('y')
   ```

3) Guarded integration tests (optional in CI)

   - These tests run only when prompt-toolkit is installed.
   - They create real widgets via `map_element_to_widget()` and verify that calling the real widget's handler or `_tui_sync()` updates the domain element.

   Example guard in pytest:

   ```python
   try:
       from prompt_toolkit.widgets import TextArea
   except Exception:
       pytest.skip('prompt-toolkit not available')
   ```

Adapter examples
----------------

- TextInputAdapter (in `src/tui_engine/widgets/text_input_adapter.py`): wraps a `TextArea` or fallback and implements `get_value()`/`set_value()` and `_tui_sync()` that updates `_last_synced`.
- RadioListAdapter / CheckboxListAdapter: wrap RadioList/CheckboxList variants and normalize selected values to lists or scalars.
- ButtonAdapter: exposes `click()` that triggers the raw widget handler and/or `element.on_click`.

Migration notes and compat
-------------------------

- Some prompt-toolkit distributions differ in available widgets (`CheckboxList` may be missing). Factory code attempts to detect availability and fall back to textual `Window` representations.
- To keep consumer code stable prefer using the wrapper Protocol surface instead of probing raw widget attributes.

FAQ / Troubleshooting
---------------------

- Q: My guarded integration tests fail in CI but pass locally.
  - A: Ensure the CI job installs prompt-toolkit or mark the job to skip when it's missing. Consider running the guarded tests in a separate CI matrix entry.

- Q: `_tui_sync()` didn't update my element.
  - A: Check whether `_tui_sync()` exists on the adapter or raw widget; `PTKAdapter` prefers adapter `_tui_sync()` if provided. Also confirm the factory attached `_tui_sync` to the raw widget for non-wrapped widgets.

Appendix: quick snippets
-----------------------

- How to assert a factory returns an adapter or raw widget with `_tui_path`:

```python
desc = map_element_to_widget(elem)
w = desc['ptk_widget']
assert w is not None
assert hasattr(w, '_tui_path') or hasattr(getattr(w, 'ptk_widget', None), '_tui_path')
```

End.
PTK widget descriptors and runtime contracts

This document describes the shape of the headless descriptors returned by
`tui_engine.ptk_widget_factory.map_element_to_widget` and the small runtime
conventions used when a real prompt-toolkit widget is created.

Purpose
-------
- Provide a stable, easy-to-test descriptor shape for headless unit tests.
- Offer best-effort creation of real prompt-toolkit widgets when prompt-toolkit
  is installed.
- Expose a small set of adapter-friendly attributes on real widgets so the
  adapter and tests can map elements <-> widgets and keep state in sync.

Descriptor shape (headless)
---------------------------
The `map_element_to_widget(element)` function always returns a dict with a
stable set of keys. At minimum expect the following keys in tests and headless
runs:

- `path` (str|None): element.path (dotted path for the domain tree)
- `name` (str|None): element name
- `variant` (str|None): the domain element variant (e.g. 'button','input')
- `type` (str): descriptor type mapped from variant (e.g. 'button','input','select','radio','checkbox_list','text')
- `ptk_widget` (object|None): a real prompt-toolkit widget instance when PTK is
  available, otherwise `None`.

Variant-specific keys
- Button: `label` and optional `on_click` (callable)
- Input: `value` (string)
- Select/Radio: `options` (list of tuples [(value, label), ...]) and `selected`
- CheckboxList: `options` and `selected` (a set of selected values)
- Default text: `text`

Real-widget runtime conventions
-------------------------------
When a real prompt-toolkit widget is created, the factory tries to attach the
following attributes to make DI/tests and the adapter simpler and consistent
across PTK versions:

- `_tui_path` (str): the domain element path. Allows the adapter to map
  focused element -> prompt-toolkit widget.
- `_tui_focusable` (bool): marks that the widget can receive focus from the
  adapter.
- `_tui_sync` (callable): a best-effort function attached to the widget that,
  when called, will push the widget's current selection/value back into the
  domain element (writing `element._value` or calling `element.set_value`) and
  call `element.on_change(new_value)` if present.

Syncing behavior
- The `_tui_sync` callable is intentionally defensive: it probes common
  attribute names exposed by list widgets (e.g. `current_value`,
  `checked_values`, `current_values`, `selected`) and normalizes the result.
- For multi-select controls like `checkbox_list` the value forwarded to the
  element is a list (and headless descriptors expose `selected` as a set).
- The adapter records `_tui_sync` callables and may invoke them automatically
  when the user accepts (Enter) or when focus moves away from a widget.

Testing guidance
----------------
- Prefer headless descriptors for unit tests: assert `type`, `options`, and
  `selected` values to ensure deterministic behaviour without prompt-toolkit.
- For tests that need to exercise sync, either:
  - Use the `_tui_sync` callable on the returned `ptk_widget` to simulate
    an accept event, or
  - Inject a fake widget that exposes `current_value` / `checked_values` and
    a `_tui_sync` to validate `element._value` updates.

Adapter integration
------------------
- The `PTKAdapter.build_real_layout()` will register each created real widget
  (by `element.path`) and also record `_tui_sync` callables when present.
- The adapter exposes a mechanism to invoke the sync callable on the currently
  focused element. This occurs on common accept actions (Enter) and when focus
  moves to another element (Tab / Shift-Tab). This behavior is DI-friendly and
  can be disabled or replaced by injecting a fake `ApplicationWrapper`.

Version compatibility notes
---------------------------
Different prompt-toolkit versions expose different widget APIs (for example
`CheckboxList` may or may not be present, attribute names vary). The factory
and adapter are intentionally best-effort and will fall back to a textual
`Window` representation when a native widget isn't available.

Open questions / future improvements
- Consider standardizing a small interface wrapper around real widgets so we
  don't need to probe attributes at runtime.
- Consider adding a `tui_widget` small adapter object that exposes `focus(),
  sync(), get_value()` to decouple from prompt-toolkit internals.

Examples
--------
A simple headless assertion:

- desc = map_element_to_widget(leaf)
- assert desc['type'] == 'checkbox_list'
- assert isinstance(desc['selected'], set)

Using `_tui_sync` in an integration test:
- widget = desc['ptk_widget']
- widget._tui_sync()
- assert leaf.get_value() == expected
