from src.tui_engine.container import ContainerElement, Element


def test_container_add_and_render():
    c = ContainerElement("root", variant="page")
    c.text("t1", "hello")
    sub = c.child("sub", variant="section")
    sub.text("s1", "child text")

    lines = c.get_render_lines(80)
    assert any("hello" in l for l in lines)
    assert any("child text" in l for l in lines)
