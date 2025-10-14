from bst.binary_search import BinarySearchTree


def test_delete_nonexistent_key_is_noop():
    bst = BinarySearchTree()
    for key in [50, 30, 70]:
        bst.insert(key)
    bst.delete(999)
    assert bst.inorder() == [30, 50, 70]
