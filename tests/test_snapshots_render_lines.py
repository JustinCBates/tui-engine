def test_header_form_snapshot() -> None:
    import os
    import sys

    # make 'src' importable when running tests from repo root
    ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if ROOT not in sys.path:
        sys.path.insert(0, ROOT)

    import tui_engine.factories as widgets
    from tui_engine.page import Page

    p = Page("Snapshot Demo")
    hdr = p.container('header','header')
    hdr.add(widgets.text('title','Adapter Title'))
    body = p.container('body','section')
    body.add(widgets.text('intro','Snapshot intro'))

    lines = p.root.get_render_lines()
    got = "\n".join(lines).rstrip() + "\n"

    here = os.path.dirname(os.path.abspath(__file__))
    snapshot_path = os.path.join(here, 'snapshots', 'header_form.txt')
    with open(snapshot_path) as fh:
        expected = fh.read()

    assert got == expected
