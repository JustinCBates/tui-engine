import questionary
from questionary_extended.core.component import Component, select, checkbox, confirm


def test_component_select_and_checkbox_and_confirm_monkeypatched(monkeypatch):
    called = {}

    def fake_select(**kwargs):
        called['select'] = kwargs
        return 'S'

    def fake_checkbox(**kwargs):
        called['checkbox'] = kwargs
        return 'C'

    def fake_confirm(**kwargs):
        called['confirm'] = kwargs
        return 'Q'

    monkeypatch.setattr(questionary, 'select', fake_select)
    monkeypatch.setattr(questionary, 'checkbox', fake_checkbox)
    monkeypatch.setattr(questionary, 'confirm', fake_confirm)

    s = select('choice', choices=['a', 'b'], message='pick')
    res = s.create_questionary_component()
    assert res == 'S' and 'choices' in called['select']

    cb = checkbox('many', choices=['x'], message='choose')
    res2 = cb.create_questionary_component()
    assert res2 == 'C' and 'choices' in called['checkbox']

    cf = confirm('ok')
    res3 = cf.create_questionary_component()
    assert res3 == 'Q' and 'message' in called['confirm']
