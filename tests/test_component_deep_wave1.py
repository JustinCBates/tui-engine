import questionary
from questionary_extended.core.component import Component


def test_component_various_types_and_config(monkeypatch):
    called = {}

    def fake_password(**kwargs):
        called['password'] = kwargs
        return 'PWD'

    def fake_autocomplete(**kwargs):
        called['autocomplete'] = kwargs
        return 'AC'

    def fake_path(**kwargs):
        called['path'] = kwargs
        return 'PATH'

    monkeypatch.setattr(questionary, 'password', fake_password)
    monkeypatch.setattr(questionary, 'autocomplete', fake_autocomplete)
    monkeypatch.setattr(questionary, 'path', fake_path)

    c_pwd = Component('p', 'password', message='m', when='cond', enhanced_validation=True)
    res1 = c_pwd.create_questionary_component()
    assert res1 == 'PWD'
    # ensure internal questionary_config filtered out control keys
    assert 'when' not in c_pwd.questionary_config and 'enhanced_validation' not in c_pwd.questionary_config
    assert 'message' in called['password']

    c_ac = Component('a', 'autocomplete', message='m', choices=['x'])
    res2 = c_ac.create_questionary_component()
    assert res2 == 'AC'
    assert 'choices' in called['autocomplete']

    c_path = Component('pth', 'path', message='m')
    res3 = c_path.create_questionary_component()
    assert res3 == 'PATH'
