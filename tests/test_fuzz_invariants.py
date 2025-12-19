from hypothesis import given, settings
from hypothesis import strategies as st

from bst.binary_search import BinarySearchTree


@settings(deadline=None, max_examples=200, derandomize=True)
@given(st.lists(st.integers(min_value=-1000, max_value=1000), unique=True))
def test_invariants_random_ops(keys):
    tree = BinarySearchTree()

    for key in keys:
        tree.insert(key)

    inorder = tree.inorder()
    assert inorder == sorted(keys)
    assert set(inorder) == set(keys)

    to_delete = keys[::2]
    for key in to_delete:
        tree.delete(key)

    remaining = set(keys) - set(to_delete)
    inorder_after_delete = tree.inorder()
    assert inorder_after_delete == sorted(remaining)

    for key in remaining:
        assert tree.search(key) is not None
    for key in to_delete:
        assert tree.search(key) is None
