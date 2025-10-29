import pytest

from tui_engine.widgets.text_input_adapter import TextInputAdapter


class FakeWidget:
    def __init__(self, text=""):
        self.text = text


def test_text_input_adapter_with_fake_widget():
    fake = FakeWidget(text="hello")
    adapter = TextInputAdapter(element=None, widget=fake)

    # adapter should read initial text via _tui_sync
    assert adapter._tui_sync() == "hello"
    assert adapter.get_value() == "hello"

    # set value should update underlying widget and get_value
    adapter.set_value('world')
    assert fake.text == 'world'
    assert adapter.get_value() == 'world'


@pytest.mark.skipif(not hasattr(__import__('builtins'), '__name__') and True, reason="PTK optional test")
def test_text_input_adapter_with_real_textarea_if_available():
    # If prompt-toolkit is available this should construct a TextArea and operate
    try:
        from tui_engine.widgets.text_input_adapter import _PTK_AVAILABLE
    except Exception:
        pytest.skip("adapter module missing")

    if not _PTK_AVAILABLE:
        pytest.skip("prompt-toolkit not installed")

    # construct adapter without a widget; it will create a real TextArea
    adapter = TextInputAdapter(element=None, widget=None)
    # set a value and ensure reading it back works
    adapter.set_value('real')
    val = adapter.get_value()
    assert val is not None
    assert 'real' in str(val)
