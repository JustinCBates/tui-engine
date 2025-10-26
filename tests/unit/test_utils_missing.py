from types import SimpleNamespace

import pytest

from tests.helpers.test_helpers import _find_repo_root, load_module_from_path


def _load_utils_module():
    # Load the specific source file module (avoid colliding with the utils package)
    repo_root = _find_repo_root()
    file_path = str(repo_root / "src" / "questionary_extended" / "utils.py")
    return load_module_from_path("questionary_extended._file_utils", file_path)


def test_parse_color_hex_fallback_to_from_hex_again(monkeypatch):
    mod = _load_utils_module()
    original = mod.ColorInfo.from_hex
    call = {"n": 0}

    def fake_from_hex(arg):
        call["n"] += 1
        if call["n"] == 1:
            return SimpleNamespace(hex="#112233")
        return original(arg)

    monkeypatch.setattr(mod.ColorInfo, "from_hex", fake_from_hex)

    res = mod.parse_color("#abc123")
    assert hasattr(res, "hex")
    assert res.hex.startswith("#")


def test_parse_color_named_color_fallback(monkeypatch):
    mod = _load_utils_module()
    original = mod.ColorInfo.from_hex
    call = {"n": 0}

    def fake_from_hex(arg):
        call["n"] += 1
        if call["n"] == 1:
            return SimpleNamespace(hex="#445566")
        return original(arg)

    monkeypatch.setattr(mod.ColorInfo, "from_hex", fake_from_hex)

    res = mod.parse_color("red")
    assert hasattr(res, "hex")


def test_parse_color_hex_without_hash_raises(monkeypatch):
    mod = _load_utils_module()

    def raising(arg):
        raise ValueError("bad hex")

    monkeypatch.setattr(mod.ColorInfo, "from_hex", raising)

    with pytest.raises(ValueError):
        mod.parse_color("abcdef")


def test_fuzzy_match_word_starts_and_threshold():
    mod = _load_utils_module()
    choices = ["alpha beta", "beginning", "substringmatch", "exact"]

    # 'be' will match 'beginning' (substring) -> score 0.8
    res = mod.fuzzy_match("be", choices)
    assert ("beginning", 0.8) in res

    # 'al' will match 'alpha beta' via substring -> score 0.8 and included by default
    res2 = mod.fuzzy_match("al", choices)
    assert ("alpha beta", 0.8) in res2

    # If threshold > 0.6, the 0.6 match should be excluded
    res3 = mod.fuzzy_match("al", choices, threshold=0.7)
    assert all(score >= 0.7 for _, score in res3)


def test_parse_color_returns_result_when_missing_attrs(monkeypatch):
    mod = _load_utils_module()

    # from_hex returns an object missing rgb and hex -> should return that object
    def blank(arg):
        return SimpleNamespace()

    monkeypatch.setattr(mod.ColorInfo, "from_hex", blank)
    out = mod.parse_color("#123456")
    assert out.__class__.__name__ == "SimpleNamespace"


def test_parse_color_rgb_missing_attrs_returns(monkeypatch):
    mod = _load_utils_module()

    def blank(arg):
        return SimpleNamespace()

    monkeypatch.setattr(mod.ColorInfo, "from_hex", blank)
    out = mod.parse_color("rgb(1,2,3)")
    assert out.__class__.__name__ == "SimpleNamespace"


def test_parse_color_unrecognized_raises():
    mod = _load_utils_module()
    with pytest.raises(ValueError):
        mod.parse_color("not-a-color-format-xyz")


def test_parse_color_rgb_success_attrs(monkeypatch):
    mod = _load_utils_module()

    def success(arg):
        return SimpleNamespace(rgb=(1, 2, 3), hex="#010203")

    monkeypatch.setattr(mod.ColorInfo, "from_hex", success)
    out = mod.parse_color("rgb(1,2,3)")
    assert getattr(out, "rgb", None) == (1, 2, 3)


def test_parse_color_hex_without_hash_success(monkeypatch):
    mod = _load_utils_module()

    def success(arg):
        return SimpleNamespace(rgb=(17, 34, 51), hex="#112233")

    monkeypatch.setattr(mod.ColorInfo, "from_hex", success)
    out = mod.parse_color("112233")
    assert getattr(out, "hex", "").startswith("#")


def test_named_color_missing_hex_returns(monkeypatch):
    mod = _load_utils_module()

    def blank(arg):
        return SimpleNamespace()

    monkeypatch.setattr(mod.ColorInfo, "from_hex", blank)
    out = mod.parse_color("red")
    assert isinstance(out, SimpleNamespace)


def test_fullmatch_hex_val_calls_from_hex(monkeypatch):
    mod = _load_utils_module()
    call = {"n": 0}

    def fake(arg):
        call["n"] += 1
        if call["n"] == 1:
            return SimpleNamespace(hex="#112233")
        return SimpleNamespace(rgb=(17, 34, 51), hex="#112233")

    monkeypatch.setattr(mod.ColorInfo, "from_hex", fake)
    out = mod.parse_color("112233")
    assert getattr(out, "hex", "").startswith("#")


def test_fullmatch_hex_val_returns_result_when_no_hex(monkeypatch):
    mod = _load_utils_module()

    def blank(arg):
        return SimpleNamespace()

    monkeypatch.setattr(mod.ColorInfo, "from_hex", blank)
    out = mod.parse_color("a1b2c3")
    assert isinstance(out, SimpleNamespace)


def test_fuzzy_match_startswith_and_wordstartswith_via_custom_lower():
    mod = _load_utils_module()

    class CLow:
        def __init__(self, text, contains=False, starts=False, split_parts=None):
            self._text = text
            self._contains = contains
            self._starts = starts
            self._split = split_parts or []

        def __contains__(self, item):
            # Force 'in' to return False unless explicitly allowed
            return self._contains

        def startswith(self, prefix):
            return self._starts

        def split(self):
            return self._split

    class ChoiceObj:
        def __init__(self, text, clower):
            self.text = text
            self._clower = clower

        def lower(self):
            return self._clower

        def __repr__(self):
            return f"ChoiceObj({self.text})"

    # startswith branch: make __contains__ False, startswith True
    cl = CLow("beginning", contains=False, starts=True, split_parts=["beginning"])
    choice = ChoiceObj("beginning", cl)
    res = mod.fuzzy_match("be", [choice])
    assert any(score == 0.7 for _, score in res)

    # any(word.startswith) branch: __contains__ False, startswith False, but split words start with query
    cl2 = CLow(
        "alpha beta", contains=False, starts=False, split_parts=["alpha", "beta"]
    )
    choice2 = ChoiceObj("alpha beta", cl2)
    res2 = mod.fuzzy_match("be", [choice2])
    assert any(score == 0.6 for _, score in res2)
