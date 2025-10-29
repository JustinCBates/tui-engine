from src.tui_engine.page import Page
from src.tui_engine.ptk_adapter import PTKAdapter


def test_ptk_adapter_build_layout():
    p = Page("Adapter Smoke")
    p.container('header','header').text('title','Adapter Title')
    body = p.container('body','section')
    body.text('intro','Adapter intro')

    adapter = PTKAdapter(page=p, page_state=p.page_state, events=p.events)
    summary = adapter.build_layout(p.root)

    assert isinstance(summary, dict)
    assert summary['type'] == 'container'
    # find header child
    names = [c['name'] for c in summary.get('children', [])]
    assert 'header' in names
    assert 'body' in names
