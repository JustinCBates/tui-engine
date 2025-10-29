"""DI-driven test verifying ApplicationWrapper.register_ctrlc using injected
key_bindings (no monkeypatching).
"""
from tui_engine.ptk_adapter import ApplicationWrapper


class FakeKeyBindings:
    def __init__(self):
        # store handlers by key
        self.handlers = {}

    def add(self, key, filter=None):
        # returns a decorator that captures handler
        def _decor(fn):
            self.handlers[key] = fn
            return fn

        return _decor


def test_register_ctrlc_records_handler_via_injection():
    fake_kb = FakeKeyBindings()
    wrapper = ApplicationWrapper()
    # Inject the fake key_bindings object
    wrapper.set_key_bindings(fake_kb)

    # Register a ctrl-c handler
    called = {}

    def handler(ev=None):
        called['ok'] = True

    ok = wrapper.register_ctrlc(handler)
    assert ok is True
    # Ensure the fake keybindings recorded the handler under 'c-c'
    assert 'c-c' in fake_kb.handlers
    # Call the recorded handler to simulate key press
    fake_kb.handlers['c-c']()
    assert called.get('ok') is True
