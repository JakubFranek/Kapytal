from types import NoneType

import pytest

from src.models.model_objects.cash_objects import _validate_collection_of_tuple_pairs


def test_validate_collection_of_tuple_pairs_invalid_length() -> None:
    with pytest.raises(ValueError, match="Length of 'collection' must be at least 1."):
        _validate_collection_of_tuple_pairs([], NoneType, NoneType, 1)
