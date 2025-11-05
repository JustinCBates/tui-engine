import pytest

from tui_engine.widgets.radio_list_adapter import RadioListAdapter


class _FakeRadio:
    def __init__(self, current: str | None = None) -> None:
        self.current_value = current

    def focus(self) -> None:
        self._focused = True


def test_fake_radio_adapter_get_set_and_sync() -> None:
    fake = _FakeRadio(current='opt1')
    adapter = RadioListAdapter(fake)

    assert adapter.get_selected() == ['opt1']

    adapter.set_selected(['opt2'])
    assert fake.current_value == 'opt2'

    # sync returns the raw selected value
    assert adapter._tui_sync() == 'opt2'


def test_prompt_toolkit_radiolist_if_available() -> None:
    try:
        from prompt_toolkit.widgets import RadioList
    except Exception:
        pytest.skip("prompt_toolkit RadioList not available")

    opts = [('a', 'A'), ('b', 'B')]
    rl = RadioList(opts)
    adapter = RadioListAdapter(rl)

    # default selection may be None
    sel = adapter.get_selected()
    assert isinstance(sel, list)

    # set and read back
    adapter.set_selected(['b'])
    assert adapter.get_selected() == ['b']
