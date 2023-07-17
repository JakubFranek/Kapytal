from types import NoneType

import pytest
from src.models.model_objects.attributes import Category, CategoryType
from src.models.model_objects.cash_objects import (
    _is_category_related,
    _validate_collection_of_tuple_pairs,
)


def test_validate_collection_of_tuple_pairs_invalid_length() -> None:
    with pytest.raises(ValueError, match="Length of 'collection' must be at least 1."):
        _validate_collection_of_tuple_pairs([], NoneType, NoneType, 1)


def test_is_category_related() -> None:
    c1 = Category("1", CategoryType.EXPENSE)
    c2 = Category("2", CategoryType.EXPENSE, c1)
    c3 = Category("3", CategoryType.EXPENSE, c2)
    cx = Category("x", CategoryType.EXPENSE)
    categories = [c1, c2, c3, cx]
    assert _is_category_related(c1, categories)
    assert not _is_category_related(cx, [c1, c2, c3])
    assert _is_category_related(c2, [c1, c3])
