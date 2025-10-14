import pytest

from bst.binary_search import BinarySearchTree

DEFAULT_KEYS = [50, 30, 20, 40, 70, 60, 80]


@pytest.fixture
def bst_tree():
    tree = BinarySearchTree()
    for key in DEFAULT_KEYS:
        tree.insert(key)
    return tree


@pytest.fixture
def initial_bst():
    tree = BinarySearchTree()
    for key in DEFAULT_KEYS:
        tree.insert(key)
    return tree
