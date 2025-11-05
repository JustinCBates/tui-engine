import tui_engine.factories as widgets
from tui_engine.page import Page
from tui_engine.ptk_adapter import PTKAdapter


def test_ptk_adapter_build_layout() -> None:
    p = Page("Adapter Smoke")
    hdr = p.container('header','header')
    hdr.add(widgets.text('title','Adapter Title'))
    body = p.container('body','section')
    body.add(widgets.text('intro','Adapter intro'))

    adapter = PTKAdapter(page=p, page_state=p.page_state, events=p.events)
    summary = adapter.build_layout(p.root)

    assert isinstance(summary, dict)
    assert summary['type'] == 'container'
    # find header child
    names = [c['name'] for c in summary.get('children', [])]
    assert 'header' in names
    assert 'body' in names
