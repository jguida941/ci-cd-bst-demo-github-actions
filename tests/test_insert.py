def test_insert_duplicate_is_ignored(bst_tree):
    bst_tree.insert(70)
    traversal = bst_tree.inorder()
    assert traversal.count(70) == 1
    assert traversal == [20, 30, 40, 50, 60, 70, 80]


def test_insert_new_value(bst_tree):
    bst_tree.insert(65)
    assert bst_tree.inorder() == [20, 30, 40, 50, 60, 65, 70, 80]
