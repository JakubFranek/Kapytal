import uuid
from datetime import datetime

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from src.models.constants import tzinfo
from tests.models.test_assets.composites import everything_except
from tests.models.test_assets.concrete_abcs import ConcreteTransaction


@given(description=st.text(min_size=0, max_size=256), datetime_=st.datetimes())
def test_creation(description: str, datetime_: datetime) -> None:
    dt_start = datetime.now(tzinfo)
    transaction = ConcreteTransaction(description, datetime_)

    dt_created_diff = transaction.datetime_created - dt_start

    assert transaction.description == description
    assert transaction.datetime_ == datetime_
    assert isinstance(transaction.uuid, uuid.UUID)
    assert dt_created_diff.seconds < 1


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
@settings(max_examples=10)
def test_invalid_description_value(description: str, datetime_: datetime) -> None:
    with pytest.raises(ValueError, match="description length must be between"):
        ConcreteTransaction(description, datetime_)


@given(
    description=st.text(min_size=0, max_size=256), datetime_=everything_except(datetime)
)
def test_invalid_datetime_type(description: str, datetime_: datetime) -> None:
    with pytest.raises(TypeError, match="Transaction.datetime_ must be a datetime."):
        ConcreteTransaction(description, datetime_)
