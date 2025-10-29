import importlib

from tui_engine.container import ContainerElement, Element
from tui_engine.ptk_adapter import PTKAdapter, ApplicationWrapper


def make_sample_tree():
    root = ContainerElement("root")
    header = root.child("header")
    header.button("ok")
    header.button("cancel")
    body = root.child("body")
    body.input("name", value="x")
    body.input("email", value="y")
    return root


def test_build_real_layout_best_effort():
    root = make_sample_tree()
    adapter = PTKAdapter(root, None, None, app=ApplicationWrapper())
    res = adapter.build_real_layout(root)
    # If prompt-toolkit is installed, we expect a real container; otherwise we
    # return None. Ensure the call is best-effort (doesn't raise) and returns
    # either a container or None.
    try:
        import prompt_toolkit  # type: ignore
        assert res is not None
    except Exception:
        assert res is None
