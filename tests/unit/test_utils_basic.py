from questionary_extended import utils


def test_format_number_percent_and_currency():
    pct = utils.format_number(0.1567, percentage=True, decimal_places=1)
    assert pct.endswith("%")
    # ensure numeric part parses
    num_part = pct.rstrip("%")
    float(num_part)
    formatted = utils.format_number(1234.5, thousands_sep=True)
    assert "," in formatted or formatted.replace(" ", "").replace(".", "").isdigit()


def test_parse_number_basic():
    assert utils.parse_number("1,234") == 1234
    assert abs(utils.parse_number("12.34") - 12.34) < 1e-9
    assert utils.parse_number("50%") == 50.0


def test_fuzzy_match_basic():
    res = utils.fuzzy_match("py", ["python", "java", "cpython"], threshold=0.2)
    assert any(r[0] == "python" for r in res)
