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


def test_format_number_variants():
    m = load_standalone_utils()
    # decimals
    assert m.format_number(1234.567, decimal_places=2) == "1234.57"
    assert m.format_number(1000, thousands_sep=True) in ("1,000", "1,000.0", "1,000.0")
    assert m.format_number(0.5, percentage=True).endswith("%")
    assert m.format_number(9.5, currency="$").startswith("$")


def test_parse_color_cases():
    m = load_standalone_utils()
    c1 = m.parse_color("#ff0000")
    assert c1.hex.lower() == "#ff0000"

    c2 = m.parse_color("rgb(0,255,0)")
    assert c2.rgb == (0, 255, 0)

    c3 = m.parse_color("blue")
    assert c3.hex.lower() == "#0000ff"

    # invalid input should raise ValueError
    import pytest

    with pytest.raises(ValueError):
        m.parse_color("not-a-color")
