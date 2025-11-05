import tui_engine.factories as widgets
from tui_engine.container import Container


def test_container_add_and_render() -> None:
    c = Container("root", variant="page")
    c.add(widgets.text("t1", "hello"))
    sub = c.child("sub", variant="section")
    sub.add(widgets.text("s1", "child text"))

    lines = c.get_render_lines(80)
    assert any("hello" in l for l in lines)
    assert any("child text" in l for l in lines)
