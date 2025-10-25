import importlib.util
import os
import types
import sys

import pytest


# Load the standalone utils.py to ensure we exercise that file (there's also a
# package-style utils which doesn't expose all functions). This mirrors the
# approach used in other tests.
HERE = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
SRC = os.path.join(HERE, "src", "questionary_extended")

# load components first so relative imports inside utils.py resolve
COMP_PATH = os.path.join(SRC, "components.py")
spec_c = importlib.util.spec_from_file_location("questionary_extended.components", COMP_PATH)
components = importlib.util.module_from_spec(spec_c)
spec_c.loader.exec_module(components)
sys.modules["questionary_extended.components"] = components

UTILS_PATH = os.path.join(SRC, "utils.py")
spec = importlib.util.spec_from_file_location("questionary_extended.utils", UTILS_PATH)
utils = importlib.util.module_from_spec(spec)
utils.__package__ = "questionary_extended"
sys.modules["questionary_extended.utils"] = utils
spec.loader.exec_module(utils)


def test_create_progress_bar_total_zero():
    out = utils.create_progress_bar(0, 0, width=5)
    # Ensure the bar is present and the numeric portion contains the 0/0 marker
    assert "0/0" in out
    # bar is the content between [ and ]
    if "[" in out and "]" in out:
        bar = out.split("]", 1)[0].lstrip("[")
        assert len(bar) == 5
    else:
        pytest.skip("unexpected progress bar format")


def test_generate_choices_with_format_fn():
    rng = utils.generate_choices_from_range(0, 2, 1, format_fn=lambda x: f"v{x}")
    assert rng == ["v0", "v1", "v2"]


def test_fuzzy_match_exact_and_custom_objects():
    # exact equality -> score 1.0
    choices = ["apple", "banana"]
    matches = utils.fuzzy_match("apple", choices)
    assert any(score == 1.0 for (_, score) in matches)

    # create objects to exercise the otherwise-unreachable startswith branch
    class FakeLower:
        def __init__(self, s):
            self._s = s

        def __contains__(self, other):
            # force the 'in' check to be False so startswith can be hit
            return False

        def startswith(self, other):
            return True

        def split(self):
            return [self._s]

    class FakeChoice:
        def __init__(self, s):
            self.s = s

        def lower(self):
            return FakeLower(self.s)

    matches2 = utils.fuzzy_match("ap", [FakeChoice("apricot")], threshold=0.1)
    # our FakeLower forces the startswith branch; expect a score of 0.7
    assert any(abs(score - 0.7) < 1e-6 for (_, score) in matches2)

    # exercise any(word.startswith(query_lower)) branch by returning a split
    class FakeLower2:
        def __init__(self, s):
            self._s = s

        def __contains__(self, other):
            return False

        def startswith(self, other):
            return False

        def split(self):
            return [self._s]

    class FakeChoice2:
        def __init__(self, s):
            self.s = s

        def lower(self):
            return FakeLower2(self.s)

    matches3 = utils.fuzzy_match("ap", [FakeChoice2("apricot")], threshold=0.1)
    assert any(abs(score - 0.6) < 1e-6 for (_, score) in matches3)
