def test_delete_leaf(bst_tree):
    bst_tree.delete(20)
    assert bst_tree.inorder() == [30, 40, 50, 60, 70, 80]


def test_delete_with_children(bst_tree):
    bst_tree.delete(30)
    assert bst_tree.inorder() == [20, 40, 50, 60, 70, 80]


def test_delete_root_with_two_children(initial_bst):
    initial_bst.delete(50)
    traversal = initial_bst.inorder()
    assert traversal == [20, 30, 40, 60, 70, 80]
    assert 50 not in traversal
