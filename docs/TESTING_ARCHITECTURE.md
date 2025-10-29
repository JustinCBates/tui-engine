# Testing architecture and DI examples

This document shows recommended patterns for testing PTK integration using
dependency injection only (no monkeypatching of module-level symbols).

## DI hooks recap

- `ApplicationWrapper.set_real_app(app)` — inject a fake or real prompt-toolkit
  application instance used by adapters.
- `ApplicationWrapper.set_key_bindings(kb)` — inject a `key_bindings` object
  (or fake) so tests can assert registration of key handlers.
- `PTKAdapter.register_widget_mapping(path, widget)` — register a mapping
  between a domain `element.path` and a widget test double (any object). The
  adapter uses this mapping to transfer focus into a real app when present.

## Simple DI example: focus transfer

This example shows how to inject a fake application and a fake widget, then
assert that `PTKAdapter._apply_focus_to_ptk()` focuses the widget by calling
`app.layout.focus(widget)`.

```py
from tui_engine.container import ContainerElement
from tui_engine.ptk_adapter import PTKAdapter, ApplicationWrapper

class FakeLayout:
    def __init__(self):
        self.focus_called_with = None
    def focus(self, widget):
        self.focus_called_with = widget

class FakeApp:
    def __init__(self):
        self.layout = FakeLayout()

root = ContainerElement('root')
btn = root.child('body').button('ok')

fake_app = FakeApp()
wrapper = ApplicationWrapper()
wrapper.set_real_app(fake_app)
adapter = PTKAdapter(root, None, None, app=wrapper)

fake_widget = object()
adapter.register_widget_mapping(btn.path, fake_widget)
adapter.focus_registry.register(btn)
adapter.focus_registry.set_focused(btn.path)

adapter._apply_focus_to_ptk()
assert fake_app.layout.focus_called_with is fake_widget
```

## Keybinding DI example: Ctrl-C

Inject a fake `key_bindings` object that records handlers. Use
`ApplicationWrapper.set_key_bindings(fake_kb)` and then call
`ApplicationWrapper.register_ctrlc(handler)`; finally assert the fake key
bindings hold the handler under `'c-c'` and invoke it.

```py
from tui_engine.ptk_adapter import ApplicationWrapper

class FakeKeyBindings:
    def __init__(self):
        self.handlers = {}
    def add(self, key, filter=None):
        def _decor(fn):
            self.handlers[key] = fn
            return fn
        return _decor

called = {}

def handler(ev=None):
    called['ok'] = True

wrapper = ApplicationWrapper()
fake_kb = FakeKeyBindings()
wrapper.set_key_bindings(fake_kb)
wrapper.register_ctrlc(handler)
assert 'c-c' in fake_kb.handlers
fake_kb.handlers['c-c']()
assert called.get('ok') is True
```

## Tips

- Prefer asserting on the stable descriptors returned by
  `ptk_widget_factory.map_element_to_widget(...)` for headless tests.
- Use injected fakes for prompt-toolkit-specific behavior; do not patch
  `prompt_toolkit` modules in tests.
- For end-to-end interactive tests that require a terminal, keep them separate
  and clearly marked; CI runners should skip them by default.
