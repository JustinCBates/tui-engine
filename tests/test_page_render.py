from src.tui_engine.page import Page


def test_page_render_headless():
    p = Page("Smoke Test")
    p.container('header','header').text('title','Smoke Title')
    body = p.container('body','section')
    body.text('intro','Hello from smoke')
    output = "\n".join(p.render(80))
    assert "Smoke Test" in output
    assert "Smoke Title" in output
    assert "Hello from smoke" in output
