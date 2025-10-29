from tui_engine.focus import FocusRegistry
from tui_engine.container import ContainerElement, Element


def make_sample_tree():
    root = ContainerElement("root")
    header = root.child("header")
    b1 = header.button("ok")
    b2 = header.button("cancel")
    body = root.child("body")
    i1 = body.input("name", value="x")
    i2 = body.input("email", value="y")
    return root, [b1, b2, i1, i2]


def test_focus_registry_basic_traversal():
    root, elems = make_sample_tree()
    reg = FocusRegistry()
    for e in elems:
        reg.register(e)

    assert reg.get_focused() == elems[0].path
    assert reg.focus_next() == elems[1].path
    assert reg.focus_next() == elems[2].path
    assert reg.focus_prev() == elems[1].path


def test_modal_trap_limits_traversal():
    root, elems = make_sample_tree()
    reg = FocusRegistry()
    for e in elems:
        reg.register(e)

    # trap to only header buttons
    header_paths = [elems[0].path, elems[1].path]
    with reg.modal_trap(header_paths):
        assert reg.get_focused() in header_paths
        # cycle within trap
        first = reg.get_focused()
        nxt = reg.focus_next()
        assert nxt in header_paths
        # prev cycles within trap as well
        prev = reg.focus_prev()
        assert prev in header_paths
