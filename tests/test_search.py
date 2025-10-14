def test_search_found(bst_tree):
    node = bst_tree.search(60)
    assert node is not None
    assert node.key == 60


def test_search_not_found(bst_tree):
    assert bst_tree.search(999) is None


def test_search_node_string_representation(bst_tree):
    node = bst_tree.search(50)
    assert node is not None
    assert str(node) == "50"
