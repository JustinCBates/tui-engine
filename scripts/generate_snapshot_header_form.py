import os
import sys

# Ensure project root is on sys.path so 'src' is importable when running this
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
for l in lines:
    print(l)
