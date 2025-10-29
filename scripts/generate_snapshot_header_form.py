import os
import sys

# Ensure project root is on sys.path so 'src' is importable when running this
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from src.tui_engine.page import Page


p = Page("Snapshot Demo")
p.container('header','header').text('title','Adapter Title')
body = p.container('body','section')
body.text('intro','Snapshot intro')

lines = p.root.get_render_lines()
for l in lines:
    print(l)
