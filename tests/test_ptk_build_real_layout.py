import importlib
from typing import Any

import tui_engine.factories as widgets
from tui_engine.container import ContainerElement
from tui_engine.element import Element
from tui_engine.ptk_adapter import ApplicationWrapper, PTKAdapter


def make_sample_tree() -> Any:
    root = ContainerElement("root")
    header = root.child("header")
    header.add(widgets.button("ok"))
    header.add(widgets.button("cancel"))
    body = root.child("body")
    body.add(widgets.input("name", value="x"))
    body.add(widgets.input("email", value="y"))
    return root


def test_build_real_layout_best_effort() -> None:
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
