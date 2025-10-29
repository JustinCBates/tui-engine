import pytest

from tui_engine.widgets.text_input_adapter import TextInputAdapter


class _FakeWidget:
    def __init__(self, initial: str = ""):
        self.text = initial
        self.focused = False

    def focus(self):
        self.focused = True

    def __repr__(self):
        return f"_FakeWidget(text={self.text!r})"


def test_fake_widget_get_set_and_sync():
    w = _FakeWidget("hello")
    adapter = TextInputAdapter(w)

    assert adapter.get_value() == "hello"

    adapter.set_value("world")
    assert w.text == "world"

    # sync should copy current widget text to _last_synced
    adapter._tui_sync()
    assert adapter._last_synced == "world"

    # focus should call underlying focus
    assert not w.focused
    adapter.focus()
    assert w.focused


def test_textarea_integration_if_available():
    try:
        from prompt_toolkit.widgets import TextArea
    except Exception:
        pytest.skip("prompt_toolkit not available")

    ta = TextArea(text="ptk")
    adapter = TextInputAdapter(ta)

    assert adapter.get_value() == "ptk"

    adapter.set_value("changed")
    # Some TextArea implementations expose .text directly; buffer.text is also common
    assert adapter.get_value() in ("changed", "changed\n", "changed\r\n")

    adapter._tui_sync()
    assert adapter._last_synced != ""
