import time
from datetime import datetime

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from src.models.constants import tzinfo
from src.models.transactions.transaction import Transaction
from tests.models.composites import transactions


@given(description=st.text(min_size=0, max_size=256), datetime_=st.datetimes())
def test_creation_pass(description: str, datetime_: datetime) -> None:
    dt_start = datetime.now(tzinfo)
    transaction = Transaction(description, datetime_)

    dt_created_diff = transaction.datetime_created - dt_start
    dt_edited_diff = transaction.datetime_edited - dt_start

    assert transaction.description == description
    assert transaction.datetime_ == datetime_
    assert dt_created_diff.seconds < 1
    assert dt_edited_diff.seconds < 1


@given(
    description=st.integers()
    | st.floats()
    | st.none()
    | st.datetimes()
    | st.booleans()
    | st.sampled_from([[], (), {}, set()]),
    datetime_=st.datetimes(),
)
def test_invalid_description_type(description: str, datetime_: datetime) -> None:
    with pytest.raises(TypeError, match="Transaction description must be a string."):
        Transaction(description, datetime_)


@given(
    description=st.text(min_size=257),
    datetime_=st.datetimes(),
)
@settings(max_examples=10)
def test_invalid_description_value(description: str, datetime_: datetime) -> None:
    with pytest.raises(ValueError, match="description length must be between"):
        Transaction(description, datetime_)


@given(
    description=st.text(min_size=0, max_size=256),
    datetime_=st.integers()
    | st.floats()
    | st.none()
    | st.text()
    | st.booleans()
    | st.sampled_from([[], (), {}, set()]),
)
def test_invalid_datetime_type(description: str, datetime_: datetime) -> None:
    with pytest.raises(TypeError, match="Transaction datetime_ must be a datetime."):
        Transaction(description, datetime_)


@given(transaction=transactions(), new_description=st.text(min_size=0, max_size=256))
def test_description_setter(transaction: Transaction, new_description: str) -> None:
    dt_edited_previous = transaction.datetime_edited
    time.sleep(1 / 1_000_000)
    transaction.description = new_description
    dt_edited_new = transaction.datetime_edited

    dt_edited_diff = dt_edited_new - dt_edited_previous

    assert dt_edited_diff.microseconds < 10_000


@given(transaction=transactions(), new_datetime=st.datetimes())
def test_datetime_setter(transaction: Transaction, new_datetime: datetime) -> None:
    dt_edited_previous = transaction.datetime_edited
    time.sleep(1 / 1_000_000)
    transaction.datetime_ = new_datetime
    dt_edited_new = transaction.datetime_edited

    dt_edited_diff = dt_edited_new - dt_edited_previous

    assert dt_edited_diff.microseconds < 10_000
