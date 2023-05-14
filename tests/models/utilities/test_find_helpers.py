import uuid

import pytest
from src.models.custom_exceptions import NotFoundError
from src.models.utilities.find_helpers import (
    find_transaction_by_uuid,
)


def test_find_transaction_by_uuid_not_found() -> None:
    with pytest.raises(NotFoundError):
        find_transaction_by_uuid(uuid.uuid4(), [])
