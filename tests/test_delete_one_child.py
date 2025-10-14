from bst.binary_search import BinarySearchTree


def test_delete_root_with_right_only_child():
    bst = BinarySearchTree()
    for key in [10, 20]:
        bst.insert(key)
    bst.delete(10)
    assert bst.inorder() == [20]


def test_delete_root_with_left_only_child():
    bst = BinarySearchTree()
    for key in [10, 5]:
        bst.insert(key)
    bst.delete(10)
    assert bst.inorder() == [5]
