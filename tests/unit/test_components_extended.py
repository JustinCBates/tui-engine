from pathlib import Path
from tests.helpers.test_helpers import load_module_from_path

comp = load_module_from_path(
    "questionary_extended.components", Path("src/questionary_extended/components.py").resolve()
)


def test_choice_post_init_defaults():
    c = comp.Choice("title")
    assert c.value == "title"
    assert c.disabled is False


def test_tree_node_from_dict_and_methods():
    data = {"a": {"b": [1, 2], "c": {"d": []}}, "z": []}
    root = comp.TreeNode.from_dict(data, name="root")
    # root should have children
    assert any(child.name == "a/" or child.name == "a" or child.name == "z/" for child in root.children)
    # add_child and is_leaf
    node = comp.TreeNode("leaf")
    assert node.is_leaf()
    node.add_child(comp.TreeNode("child"))
    assert not node.is_leaf()


def test_colorinfo_from_hex_branches():
    # grayscale where diff == 0
    ci = comp.ColorInfo.from_hex("#808080")
    assert isinstance(ci.hsl, tuple)

    # red is max == r
    cir = comp.ColorInfo.from_hex("#ff0000")
    assert cir.rgb[0] == 255 and cir.hsl[0] == 0

    # green max == g
    cig = comp.ColorInfo.from_hex("#00ff00")
    assert cig.rgb[1] == 255

    # blue max == b
    cib = comp.ColorInfo.from_hex("#0000ff")
    assert cib.rgb[2] == 255


def test_progressstep_to_question_dict():
    ps1 = comp.ProgressStep(name="s1", description="desc")
    qd = ps1.to_question_dict()
    assert qd["name"] == "s1"

    ps2 = comp.ProgressStep(name="s2", description="desc", question={"type": "input", "message": "m"})
    qd2 = ps2.to_question_dict()
    assert qd2.get("type") == "input"
