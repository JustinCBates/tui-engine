from questionary_extended.components import ColorInfo, ProgressStep, TreeNode


def test_colorinfo_from_hex():
    c = ColorInfo.from_hex("#ff0000")
    assert c.hex.lower() == "#ff0000"
    assert c.rgb == (255, 0, 0)
    assert isinstance(c.hsl[0], int)


def test_treenode_from_dict_and_leaf():
    data = {"a": {"b": [1, 2], "c": "d"}, "e": "f"}
    root = TreeNode.from_dict(data, name="root")
    assert not root.is_leaf()
    # find child 'a'
    a_children = [ch for ch in root.children if ch.name == "a"]
    assert a_children
    a_node = a_children[0]
    # The list under 'b' produces children named by the list items ('1', '2')
    assert any(child.name == "c" for child in a_node.children)
    assert any(child.name in ("1", "2") for child in a_node.children)


def test_progressstep_to_question_dict():
    ps = ProgressStep(name="step1", description="Do thing")
    q = ps.to_question_dict()
    assert isinstance(q, dict)
    assert q.get("name") == "step1"
