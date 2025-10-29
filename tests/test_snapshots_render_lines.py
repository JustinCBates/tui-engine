def test_header_form_snapshot():
    import os
    import sys

    # make 'src' importable when running tests from repo root
    ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if ROOT not in sys.path:
        sys.path.insert(0, ROOT)

    from src.tui_engine.page import Page

    p = Page("Snapshot Demo")
    p.container('header','header').text('title','Adapter Title')
    body = p.container('body','section')
    body.text('intro','Snapshot intro')

    lines = p.root.get_render_lines()
    got = "\n".join(lines).rstrip() + "\n"

    here = os.path.dirname(os.path.abspath(__file__))
    snapshot_path = os.path.join(here, 'snapshots', 'header_form.txt')
    with open(snapshot_path, 'r') as fh:
        expected = fh.read()

    assert got == expected
