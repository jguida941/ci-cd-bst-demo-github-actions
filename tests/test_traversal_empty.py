from bst.binary_search import BinarySearchTree


def test_inorder_on_empty_tree_returns_empty_list():
    bst = BinarySearchTree()
    assert bst.inorder() == []
