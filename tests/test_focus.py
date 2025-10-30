from typing import Any

import tui_engine.factories as widgets
from tui_engine.container import ContainerElement
from tui_engine.element import Element
from tui_engine.focus import FocusRegistry


def make_sample_tree() -> Any:
    root = ContainerElement("root")
    header = root.child("header")
    b1 = widgets.button("ok")
    header.add(b1)
    b2 = widgets.button("cancel")
    header.add(b2)
    body = root.child("body")
    i1 = widgets.input("name", value="x")
    body.add(i1)
    i2 = widgets.input("email", value="y")
    body.add(i2)
    return root, [b1, b2, i1, i2]


def test_focus_registry_basic_traversal() -> None:
    root, elems = make_sample_tree()
    reg = FocusRegistry()
    for e in elems:
        reg.register(e)

    assert reg.get_focused() == elems[0].path
    assert reg.focus_next() == elems[1].path
    assert reg.focus_next() == elems[2].path
    assert reg.focus_prev() == elems[1].path


def test_modal_trap_limits_traversal() -> None:
    root, elems = make_sample_tree()
    reg = FocusRegistry()
    for e in elems:
        reg.register(e)

    # trap to only header buttons
    header_paths = [elems[0].path, elems[1].path]
    with reg.modal_trap(header_paths):
        assert reg.get_focused() in header_paths
        # cycle within trap
        _first = reg.get_focused()
        nxt = reg.focus_next()
        assert nxt in header_paths
        # prev cycles within trap as well
        prev = reg.focus_prev()
        assert prev in header_paths
