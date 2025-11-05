import pytest

from tui_engine.widgets.checkbox_list_adapter import CheckboxListAdapter


class _FakeCheckboxList:
    def __init__(self, checked: list[str] | None = None) -> None:
        self.checked_values = list(checked) if checked is not None else []

    def focus(self) -> None:
        self._focused = True


def test_fake_checkbox_get_set_and_sync() -> None:
    fake = _FakeCheckboxList(checked=['a'])
    adapter = CheckboxListAdapter(fake)

    assert adapter.get_selected() == ['a']

    adapter.set_selected(['b', 'c'])
    assert set(fake.checked_values) == {'b', 'c'}

    synced = adapter._tui_sync()
    assert isinstance(synced, list)


def test_prompt_toolkit_checkbox_if_available() -> None:
    try:
        from prompt_toolkit.widgets import CheckboxList
    except Exception:
        pytest.skip("prompt_toolkit CheckboxList not available")

    opts = [('a', 'A'), ('b', 'B')]
    cl = CheckboxList(opts)
    adapter = CheckboxListAdapter(cl)

    # adapter should return a list
    sel = adapter.get_selected()
    assert isinstance(sel, list)

    adapter.set_selected(['a'])
    assert 'a' in adapter.get_selected()
