import uuid

import pytest
from src.models.custom_exceptions import NotFoundError
from src.models.utilities.find_helpers import (
    find_account_by_path,
    find_account_group_by_path,
    find_attribute_by_name,
    find_category_by_path,
    find_currency_by_code,
    find_security_by_name,
    find_transaction_by_uuid,
)


def test_find_account_group_by_path_not_found() -> None:
    with pytest.raises(NotFoundError):
        find_account_group_by_path("invalid path", [])


def test_find_account_by_path_not_found() -> None:
    with pytest.raises(NotFoundError):
        find_account_by_path("test", [])


def test_find_attribute_by_name_not_found() -> None:
    with pytest.raises(NotFoundError):
        find_attribute_by_name("invalid name", [])


def test_find_category_by_path_not_found() -> None:
    with pytest.raises(NotFoundError):
        find_category_by_path("invalid path", [])


def test_find_currency_by_code_not_found() -> None:
    with pytest.raises(NotFoundError):
        find_currency_by_code("invalid code", [])


def test_find_security_by_name_not_found() -> None:
    with pytest.raises(NotFoundError):
        find_security_by_name("test", [])


def test_find_transaction_by_uuid_not_found() -> None:
    with pytest.raises(NotFoundError):
        find_transaction_by_uuid(uuid.uuid4(), [])
