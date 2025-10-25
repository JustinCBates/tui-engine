from types import SimpleNamespace
from questionary_extended.core.component import Component
# Simulate top-level questionary module
import sys
# Ensure there's a top-level questionary module
q = SimpleNamespace()
# initial stubs
q.text = lambda **kwargs: SimpleNamespace(name='text', kwargs=kwargs)
q.select = lambda **kwargs: SimpleNamespace(name='select', kwargs=kwargs)
q.confirm = lambda **kwargs: SimpleNamespace(name='confirm', kwargs=kwargs)
q.password = lambda **kwargs: SimpleNamespace(name='password', kwargs=kwargs)
q.checkbox = lambda **kwargs: SimpleNamespace(name='checkbox', kwargs=kwargs)
q.autocomplete = lambda **kwargs: SimpleNamespace(name='autocomplete', kwargs=kwargs)
q.path = lambda **kwargs: SimpleNamespace(name='path', kwargs=kwargs)
sys.modules['questionary'] = q

called = {}

def mk(name):
    def _fake(**kwargs):
        called[name] = kwargs
        return SimpleNamespace(name=name, kwargs=kwargs)
    return _fake

# Simulate monkeypatch.setattr("questionary.text", mk('text')) etc.
sys.modules['questionary'].text = mk('text')
sys.modules['questionary'].select = mk('select')
sys.modules['questionary'].confirm = mk('confirm')
sys.modules['questionary'].password = mk('password')
sys.modules['questionary'].checkbox = mk('checkbox')
sys.modules['questionary'].autocomplete = mk('autocomplete')
sys.modules['questionary'].path = mk('path')

c = Component('u','text', message='Hello')
res = c.create_questionary_component()
print('res for text:', res, 'called keys:', called.keys())

c2 = Component('p','select', choices=['a','b'], message='Pick')
r2 = c2.create_questionary_component()
print('res for select:', r2, 'called keys:', called.keys())
print('called dict:', called)
