#!/usr/bin/env python3
"""Dump the prompt-toolkit container tree for demos/demo_alignment.build_app().

Run with: python3 tools/dump_demo_alignment.py
"""
from typing import Any

import sys
from importlib import import_module

# Ensure project root is on sys.path
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

try:
    mod = import_module('demos.demo_alignment')
except Exception as e:
    print('Failed to import demo:', e)
    raise

app = mod.build_app()
layout = getattr(app, 'layout', None)
root = None
if layout is not None:
    try:
        root = layout.container
    except Exception:
        root = None

from prompt_toolkit.layout.containers import (
    FloatContainer, ConditionalContainer, HSplit, VSplit, Window, Float, DynamicContainer
)
from prompt_toolkit.widgets import Frame, Box


def dump(node: Any, indent: int = 0) -> None:
    prefix = ' ' * indent
    t = type(node).__name__
    print(f"{prefix}{t}: {repr(node)[:200]}")
    # Show some useful attrs
    if isinstance(node, Frame):
        print(prefix + '  Frame.title=' + repr(getattr(node, 'title', None)))
        print(prefix + '  Frame.style=' + repr(getattr(node, 'container').style if hasattr(node, 'container') else None))
        dump(node.body if hasattr(node, 'body') else node.container, indent + 2)
    elif isinstance(node, Box):
        # Box has .body attribute
        dump(node.body, indent + 2)
    elif isinstance(node, FloatContainer):
        print(prefix + '  FloatContainer.content:')
        dump(node.content, indent + 2)
        for f in getattr(node, 'floats', []):
            print(prefix + f"  Float(top={getattr(f,'top',None)}, left={getattr(f,'left',None)}, right={getattr(f,'right',None)})")
            dump(f.content, indent + 4)
    elif isinstance(node, ConditionalContainer):
        print(prefix + '  ConditionalContainer.content:')
        dump(node.content, indent + 2)
    elif isinstance(node, DynamicContainer):
        try:
            real = node._get_container()
        except Exception:
            real = None
        print(prefix + '  DynamicContainer -> ' + repr(type(real)))
        if real is not None:
            dump(real, indent + 2)
    elif isinstance(node, (HSplit, VSplit)):
        for i, child in enumerate(node.children):
            print(prefix + f'  child[{i}] ->')
            dump(child, indent + 4)
    else:
        # leaf
        pass

if root is None:
    print('No root container found on app.layout; cannot dump')
else:
    dump(root)

print('\nDone.')
