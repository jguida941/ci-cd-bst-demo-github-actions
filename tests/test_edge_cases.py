from bst.binary_search import BinarySearchTree


def test_search_on_empty_tree_returns_none():
    bst = BinarySearchTree()
    assert bst.search(123) is None


def test_delete_on_empty_tree_no_crash_and_stays_empty():
    bst = BinarySearchTree()
    bst.delete(999)
    assert bst.inorder() == []


def test_insert_duplicate_is_ignored_order_unchanged():
    bst = BinarySearchTree()
    for key in [2, 1, 3]:
        bst.insert(key)
    bst.insert(2)
    assert bst.inorder() == [1, 2, 3]
