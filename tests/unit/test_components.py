from pathlib import Path
from tests.helpers.test_helpers import load_module_from_path

# Load components via centralized loader to ensure __package__ and relative imports
components = load_module_from_path(
    "questionary_extended.components", Path("src/questionary_extended/components.py").resolve()
)


def test_choice_post_init_defaults_value():
    c = components.Choice(title="Test")
    # value should default to title when not provided
    assert c.value == "Test"


def test_tree_node_add_and_is_leaf_and_from_dict():
    # add_child and is_leaf
    root = components.TreeNode(name="root")
    assert root.is_leaf()
    child = components.TreeNode(name="child")
    root.add_child(child)
    assert not root.is_leaf()
    assert root.children[0].name == "child"

    # from_dict with nested dict and list
    data = {"a": {"b": 1}, "c": [2, 3], "d": 4}
    tree = components.TreeNode.from_dict(data, name="root")
    # should have children for keys a and d, and list items from 'c' become children named '2' and '3'
    names = [n.name for n in tree.children]
    assert "a" in names and "d" in names
    assert "2" in names and "3" in names


def test_colorinfo_from_hex_and_hsl_branches():
    # Pure gray (diff == 0) should exercise the diff==0 branch
    gray = components.ColorInfo.from_hex("#808080")
    assert gray.hex.lower() == "#808080"
    assert isinstance(gray.rgb, tuple) and len(gray.rgb) == 3

    # A bright color to exercise other hue branches
    red = components.ColorInfo.from_hex("#ff0000")
    assert red.rgb == (255, 0, 0)
    # hsl values should be sensible integers
    assert all(isinstance(x, int) for x in red.hsl)

    # Also exercise green and blue branches (max == g and max == b)
    green = components.ColorInfo.from_hex("#00ff00")
    assert green.rgb == (0, 255, 0)
    blue = components.ColorInfo.from_hex("#0000ff")
    assert blue.rgb == (0, 0, 255)


def test_progressstep_to_question_dict_branches():
    # Branch when question is provided
    q = {"type": "input", "message": "Enter"}
    step = components.ProgressStep(name="s1", description="desc", question=q)
    d = step.to_question_dict()
    # question dict should be merged into the returned dict; message should come from the question
    assert d["name"] == "s1" and d["message"] == "Enter" and d["type"] == "input"

    # Branch when question is None
    step2 = components.ProgressStep(name="s2", description="desc2")
    d2 = step2.to_question_dict()
    assert d2["type"] == "confirm" and "Complete step" in d2["message"]
