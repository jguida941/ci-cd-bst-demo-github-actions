from bst.binary_search import BinarySearchTree


def test_delete_node_with_two_children_deep_successor():
    bst = BinarySearchTree()
    for key in [50, 30, 70, 60, 80, 55, 65]:
        bst.insert(key)
    bst.delete(50)
    assert bst.inorder() == [30, 55, 60, 65, 70, 80]
