import importlib
import importlib.util
import sys
from pathlib import Path


def load_utils_module():
    # Load module from src/questionary_extended/utils.py by filesystem path
    # tests are located at <repo>/tests, so project root is parents[1]
    repo_root = Path(__file__).resolve().parents[1]
    module_path = repo_root / "src" / "questionary_extended" / "utils.py"
    # Load as a submodule of the package so relative imports (from .components) work
    spec = importlib.util.spec_from_file_location("questionary_extended._utils_file", str(module_path))
    module = importlib.util.module_from_spec(spec)
    # Ensure package is present
    if "questionary_extended" not in sys.modules:
        importlib.import_module("questionary_extended")
    # set package so relative imports succeed
    module.__package__ = "questionary_extended"
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_utils_module_functions():
    m = load_utils_module()

    # format_date / parse_date
    from datetime import datetime

    assert m.format_date(datetime(2021, 3, 4), "%Y-%m-%d") == "2021-03-04"
    assert m.parse_date("2021-03-04").year == 2021

    # format_number / parse_number
    assert "1,234" in m.format_number(1234, thousands_sep=True)
    assert m.parse_number("1,234") == 1234.0

    # truncate_text
    assert m.truncate_text("hello world", 5).endswith("...")

    # create_progress_bar
    bar = m.create_progress_bar(2, 4, width=8)
    assert "2/4" in bar

    # fuzzy_match
    matches = m.fuzzy_match("al", ["Alpha", "Beta"])
    assert any("Alpha" == name for name, _ in matches)
