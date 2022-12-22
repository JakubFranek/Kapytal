import time
import uuid
from datetime import datetime

import pytest
from hypothesis import given
from hypothesis import strategies as st

from src.models.constants import tzinfo
from tests.models.test_assets.composites import everything_except
from tests.models.test_assets.concrete_abcs import ConcreteTransaction
from tests.models.test_assets.get_valid_objects import get_concrete_transaction


@given(description=st.text(min_size=0, max_size=256), datetime_=st.datetimes())
def test_creation(description: str, datetime_: datetime) -> None:
    dt_start = datetime.now(tzinfo)
    transaction = ConcreteTransaction(description, datetime_)

    dt_created_diff = transaction.datetime_created - dt_start
    dt_edited_diff = transaction.datetime_edited - dt_start

    assert transaction.description == description
    assert transaction.datetime_ == datetime_
    assert isinstance(transaction.uuid, uuid.UUID)
    assert dt_created_diff.seconds < 1
    assert dt_edited_diff.seconds < 1


@given(
    description=everything_except(str),
    datetime_=st.datetimes(),
)
def test_invalid_description_type(description: str, datetime_: datetime) -> None:
    with pytest.raises(TypeError, match="Transaction.description must be a string."):
        ConcreteTransaction(description, datetime_)


@given(
    description=st.text(min_size=257),
    datetime_=st.datetimes(),
)
def test_invalid_description_value(description: str, datetime_: datetime) -> None:
    with pytest.raises(ValueError, match="description length must be between"):
        ConcreteTransaction(description, datetime_)


@given(
    description=st.text(min_size=0, max_size=256), datetime_=everything_except(datetime)
)
def test_invalid_datetime_type(description: str, datetime_: datetime) -> None:
    with pytest.raises(TypeError, match="Transaction.datetime_ must be a datetime."):
        ConcreteTransaction(description, datetime_)


@given(new_description=st.text(min_size=0, max_size=256))
def test_description_setter(new_description: str) -> None:
    transaction = get_concrete_transaction()
    dt_edited_previous = transaction.datetime_edited
    time.sleep(1 / 1_000_000)
    transaction.description = new_description
    dt_edited_new = transaction.datetime_edited

    dt_edited_diff = dt_edited_new - dt_edited_previous

    assert dt_edited_diff.microseconds < 100_000


@given(new_datetime=st.datetimes())
def test_datetime_setter(new_datetime: datetime) -> None:
    transaction = get_concrete_transaction()
    dt_edited_previous = transaction.datetime_edited
    time.sleep(1 / 1_000_000)
    transaction.datetime_ = new_datetime
    dt_edited_new = transaction.datetime_edited

    dt_edited_diff = dt_edited_new - dt_edited_previous

    assert dt_edited_diff.microseconds < 100_000


def test_abstract_get_amount_for_account() -> None:
    transaction = get_concrete_transaction()
    with pytest.raises(NotImplementedError):
        transaction.get_amount_for_account(None)


def test_abstract_is_account_related() -> None:
    transaction = get_concrete_transaction()
    with pytest.raises(NotImplementedError):
        transaction.is_account_related(None)
