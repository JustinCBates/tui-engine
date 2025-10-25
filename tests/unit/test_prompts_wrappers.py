import importlib
import sys
import types
import pathlib
from tests.helpers.test_helpers import load_module_from_path


class DummyPrompt:
    def __init__(self, result=None):
        self._result = result

    def ask(self):
        return self._result


class LazyQuestionStub:
    def __init__(self, factory, message, **kwargs):
        self._factory = factory
        self._message = message
        self._kwargs = kwargs

    def ask(self):
        # Call the factory (expected to return a DummyPrompt)
        obj = self._factory(self._message, **self._kwargs)
        if hasattr(obj, "ask"):
            return obj.ask()
        return obj


def _load_prompts_with_stubs(monkeypatch):
    """Inject lightweight stubs for questionary and internal modules and
    load prompts.py from file so tests don't create real prompt sessions.
    """
    root = pathlib.Path(__file__).resolve().parents[2] / "src" / "questionary_extended"
    prompts_path = str(root / "prompts.py")

    # Minimal questionary stub
    q = types.ModuleType("questionary")
    q.text = lambda *a, **k: DummyPrompt(k.get("default", ""))
    q.select = lambda *a, **k: DummyPrompt((k.get("choices") or [])[0] if k.get("choices") else None)
    q.autocomplete = lambda *a, **k: DummyPrompt(None)
    q.checkbox = lambda *a, **k: DummyPrompt([])
    q.confirm = lambda *a, **k: DummyPrompt(True)
    q.Separator = lambda title: f"SEP:{title}"
    q.password = lambda *a, **k: DummyPrompt(None)
    q.path = lambda *a, **k: DummyPrompt(None)
    q.Question = type("Question", (), {})
    q.ValidationError = Exception
    q.Validator = type("Validator", (), {})

    # Minimal components stub
    comp = types.ModuleType("questionary_extended.components")
    class Column:
        def __init__(self, name, type=None, width=20, **k):
            self.name = name
            self.width = width

    class ProgressStep:
        pass

    comp.Column = Column
    comp.ProgressStep = ProgressStep
    comp.ColorInfo = types.SimpleNamespace(from_hex=lambda x: types.SimpleNamespace(hex=x))

    # Minimal Choice and others to satisfy package __init__ imports
    class Choice:
        def __init__(self, title, value=None, **k):
            self.title = title
            self.value = value or title

    comp.Choice = Choice
    comp.Separator = lambda *a, **k: types.SimpleNamespace(title="-")

    # Provide a fake package module to prevent executing real __init__.py
    pkg = types.ModuleType("questionary_extended")
    pkg.__path__ = [str(root)]
    sys.modules["questionary_extended"] = pkg

    # Minimal prompts_core stub
    pc = types.ModuleType("questionary_extended.prompts_core")
    pc.LazyQuestion = LazyQuestionStub
    pc.ProgressTracker = object

    # Insert into sys.modules so relative imports work
    sys.modules["questionary"] = q
    sys.modules["questionary_extended.components"] = comp
    sys.modules["questionary_extended.prompts_core"] = pc

    # Minimal styles stub to satisfy `from .styles import Theme`
    styles = types.ModuleType("questionary_extended.styles")
    class Theme:
        def __init__(self, name):
            self.name = name
            self.palette = types.SimpleNamespace(primary="#000000")

    styles.Theme = Theme
    styles.THEMES = {"dark": Theme("Dark")}
    styles.get_theme_names = lambda: ["dark"]
    sys.modules["questionary_extended.styles"] = styles

    # Load prompts.py by path using centralized helper to avoid DeprecationWarnings
    module = load_module_from_path("questionary_extended.prompts", prompts_path)
    return module


def test_grouped_select_and_tree(monkeypatch):
    prompts = _load_prompts_with_stubs(monkeypatch)

    groups = {"G1": ["a", "b"], "G2": [{"x": "y"}, "c"]}
    q = prompts.grouped_select("msg", groups)
    # q is a LazyQuestionStub; ensure factory callable exists
    assert callable(q._factory)

    # tree_select should flatten nested dicts
    tree = {"Root": {"Child": ["one", "two"]}}
    tq = prompts.tree_select("pick", tree)
    assert callable(tq._factory)
    # ensure the flattened choices were passed to the factory via kwargs
    assert "choices" in tq._kwargs
    assert any("Root/Child/one" in str(c) for c in tq._kwargs["choices"])


def test_rating_and_slider_and_table(monkeypatch):
    prompts = _load_prompts_with_stubs(monkeypatch)

    r = prompts.rating("rate", max_rating=4, icon="*")
    # rating returns LazyQuestionStub with choices in kwargs
    assert isinstance(r._kwargs.get("choices"), list)
    assert len(r._kwargs["choices"]) == 4

    s = prompts.slider("slide", min_value=0, max_value=10, step=2, default=4)
    assert callable(s._factory)

    tbl = prompts.table("tab", columns=[prompts.Column("c1"), prompts.Column("c2")])
    assert callable(tbl._factory)
    assert "Table input" in tbl._message
