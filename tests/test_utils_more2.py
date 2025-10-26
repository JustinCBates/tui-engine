import importlib
import importlib.util
import sys
from pathlib import Path


def load_standalone_utils():
    repo_root = Path(__file__).resolve().parents[1]
    module_path = repo_root / "src" / "questionary_extended" / "utils.py"
    spec = importlib.util.spec_from_file_location(
        "questionary_extended._utils_file", str(module_path)
    )
    module = importlib.util.module_from_spec(spec)
    if "questionary_extended" not in sys.modules:
        importlib.import_module("questionary_extended")
    module.__package__ = "questionary_extended"
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_render_markdown_and_wrap():
    m = load_standalone_utils()
    s = m.render_markdown("**bold** and *italic* and `code`")
    assert "\033[1m" in s and "\033[3m" in s and "\033[2m" in s

    wrapped = m.wrap_text("a b c d e f g h", 3)
    assert all(len(line) <= 3 for line in wrapped)


def test_table_and_tree_and_sanitize():
    m = load_standalone_utils()
    row = m.create_table_row(["longtext"], [5])
    assert isinstance(row, str) and "|" in row

    line = m.create_tree_line(
        "x", level=2, is_last=False, has_children=True, expanded=True
    )
    assert "└──" in line or "▶" in line or "▼" in line

    assert m.sanitize_input("abc\x00\x01") == "abc"


def test_generate_choices_from_range_and_email_url():
    m = load_standalone_utils()
    choices = m.generate_choices_from_range(1, 3)
    assert choices == ["1", "2", "3"] or choices == ["1.0", "2.0", "3.0"]

    assert m.validate_email("x@y.com")
    assert not m.validate_url("not-a-url")
