import pytest

from tui_engine.widgets.button_adapter import ButtonAdapter


class FakeButton:
    def __init__(self):
        self.handler = None
        self.focused = False
        self._tui_path = None
        self._tui_focusable = True

    def focus(self):
        self.focused = True


class ElementStub:
    def __init__(self):
        self.clicked = False

    def on_click(self):
        self.clicked = True


def test_button_adapter_triggers_widget_handler_and_element():
    btn = FakeButton()
    el = ElementStub()

    # Install an external handler that flips a flag
    called = {"widget": False}

    def external():
        called["widget"] = True

    btn.handler = external

    adapter = ButtonAdapter(btn, el)

    # Clicking should call the raw handler and then the element.on_click
    adapter.click()

    assert called["widget"] is True
    assert el.clicked is True


def test_button_adapter_focus_and_sync():
    btn = FakeButton()
    adapter = ButtonAdapter(btn, None)

    assert not btn.focused
    adapter.focus()
    assert btn.focused

    # _tui_sync is a no-op but should not raise
    assert adapter._tui_sync() is None
