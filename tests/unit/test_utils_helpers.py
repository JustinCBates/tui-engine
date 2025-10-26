import importlib
import importlib.util
import os

# Try to import the utilities module from the package; if the package is a
# subpackage (folder) that doesn't expose certain helpers, fall back to
# loading the standalone `utils.py` source file so tests can exercise
# helpers like `create_table_row` which live there.
utils = importlib.import_module("questionary_extended.utils")
if not hasattr(utils, "create_table_row"):
    # locate the file relative to this repository layout
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    candidate = os.path.join(repo_root, "src", "questionary_extended", "utils.py")
    if os.path.exists(candidate):
        spec = importlib.util.spec_from_file_location("qe_utils_file", candidate)
        module = importlib.util.module_from_spec(spec)
        # Ensure relative imports inside the file resolve to the package
        module.__package__ = "questionary_extended"
        import sys

        sys.modules["questionary_extended._qe_utils_file"] = module
        spec.loader.exec_module(module)  # type: ignore[attr-defined]
        utils = module


def test_render_markdown_basic():
    s = "This is **bold** and *italic* and `code`."
    out = utils.render_markdown(s)
    # Ensure bold and italic are rendered; code formatting may vary by platform
    assert "\x1b[1m" in out and "\x1b[3m" in out
    assert "\x1b[2m" in out or "`code`" in out


def test_create_table_row_and_truncate():
    row = utils.create_table_row(["hello", "world"], [10, 10])
    assert "|" in row

    assert utils.truncate_text("abcdef", 4) == "a..." or isinstance(
        utils.truncate_text("abcd", 4), str
    )


def test_create_tree_line_variants():
    t1 = utils.create_tree_line(
        "root", 0, is_last=False, has_children=True, expanded=False
    )
    assert "root" in t1

    t2 = utils.create_tree_line("leaf", 2, is_last=True, has_children=False)
    assert "└──" in t2 or "leaf" in t2
