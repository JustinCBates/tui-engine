import tui_engine.factories as widgets
from tui_engine.page import Page


def test_page_render_headless() -> None:
    p = Page("Smoke Test")
    hdr = p.container('header','header')
    hdr.add(widgets.text('title','Smoke Title'))
    body = p.container('body','section')
    body.add(widgets.text('intro','Hello from smoke'))
    output = "\n".join(p.render(80))
    assert "Smoke Test" in output
    assert "Smoke Title" in output
    assert "Hello from smoke" in output
