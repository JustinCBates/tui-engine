import importlib.util, sys
from pathlib import Path
# Call setup_questionary_mocks
from tests.conftest_questionary import setup_questionary_mocks
setup_questionary_mocks(None)
# load component module via loader
p = Path('src/questionary_extended/core/component.py').resolve()
spec = importlib.util.spec_from_file_location('questionary_extended.core.component', str(p))
mod = importlib.util.module_from_spec(spec)
mod.__package__ = spec.parent or ''
sys.modules[spec.name] = mod
spec.loader.exec_module(mod)
print('module text attr:', mod.text)
print('module.questionary:', getattr(mod,'questionary', None))
print('type(text):', type(mod.text))
print('text repr:', repr(mod.text))
# Call mod.text('x') and show result
res = mod.text('x')
print('result of mod.text("x"):', res)
print('result type:', type(res))
