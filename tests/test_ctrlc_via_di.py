"""DI-driven test verifying ApplicationWrapper.register_ctrlc using injected
key_bindings (no monkeypatching).
"""
from typing import Any, Callable

from tui_engine.ptk_adapter import ApplicationWrapper


class FakeKeyBindings:
    def __init__(self) -> None:
        # store handlers by key
        self.handlers: dict[str, Callable[..., Any]] = {}

    def add(self, key: str, filter: Any = None) -> Callable[[Any], Any]:
        # returns a decorator that captures handler
        def _decor(fn: Callable[[Any], Any]) -> Callable[[Any], Any]:
            self.handlers[key] = fn
            return fn

        return _decor


def test_register_ctrlc_records_handler_via_injection() -> None:
    fake_kb = FakeKeyBindings()
    wrapper = ApplicationWrapper()
    # Inject the fake key_bindings object
    wrapper.set_key_bindings(fake_kb)

    # Register a ctrl-c handler
    called = {}

    def handler(ev: Any = None) -> None:
        called['ok'] = True

    ok = wrapper.register_ctrlc(handler)
    assert ok is True
    # Ensure the fake keybindings recorded the handler under 'c-c'
    assert 'c-c' in fake_kb.handlers
    # Call the recorded handler to simulate key press
    fake_kb.handlers['c-c']()
    assert called.get('ok') is True
