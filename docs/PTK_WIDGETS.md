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
