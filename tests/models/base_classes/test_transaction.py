from collections.abc import Collection
from datetime import datetime
from types import NoneType
from typing import Any
from uuid import UUID

import pytest
from hypothesis import given
from hypothesis import strategies as st
from src.models.custom_exceptions import NotFoundError
from src.models.model_objects.attributes import (
    Attribute,
    AttributeType,
    InvalidAttributeError,
)
from src.models.user_settings import user_settings
from tests.models.test_assets.composites import attributes, everything_except
from tests.models.test_assets.concrete_abcs import ConcreteTransaction


@given(
    description=st.text(min_size=0, max_size=256),
    datetime_=st.datetimes(
        min_value=datetime(1971, 1, 1),  # noqa: DTZ001
        timezones=st.just(user_settings.settings.time_zone),
    ),
)
def test_creation(description: str, datetime_: datetime) -> None:
    dt_start = datetime.now(user_settings.settings.time_zone).replace(microsecond=0)
    transaction = ConcreteTransaction(description, datetime_)

    dt_created_diff = transaction.datetime_created - dt_start

    assert transaction.description == description.strip()
    assert transaction.datetime_ == datetime_
    assert isinstance(transaction.uuid, UUID)
    assert dt_created_diff.seconds < 1


@given(
    description=everything_except((str, NoneType)),
    datetime_=st.datetimes(),
)
def test_invalid_description_type(description: str, datetime_: datetime) -> None:
    with pytest.raises(TypeError, match="Transaction.description must be a string."):
        ConcreteTransaction(description, datetime_)


@given(
    description=st.text(min_size=257, max_size=500),
    datetime_=st.datetimes(),
)
def test_invalid_description_value(description: str, datetime_: datetime) -> None:
    with pytest.raises(ValueError, match="description length must be between"):
        ConcreteTransaction(description, datetime_)


@given(
    description=st.text(min_size=0, max_size=256),
    datetime_=everything_except((datetime, NoneType)),
)
def test_invalid_datetime_type(description: str, datetime_: datetime) -> None:
    with pytest.raises(TypeError, match="Transaction.datetime_ must be a datetime."):
        ConcreteTransaction(description, datetime_)


@given(
    description=st.text(min_size=0, max_size=256),
    datetime_=st.datetimes(
        min_value=datetime(year=1971, month=1, day=1),  # noqa: DTZ001
        timezones=st.just(user_settings.settings.time_zone),
    ),
)
def test_set_attributes_same_values(description: str, datetime_: datetime) -> None:
    transaction = ConcreteTransaction(description, datetime_)
    transaction.set_attributes()
    assert transaction.description == description.strip()
    assert transaction.datetime_ == datetime_


@given(tags=st.lists(attributes(AttributeType.TAG), min_size=1, max_size=5))
def test_add_remove_tags(tags: list[Attribute]) -> None:
    transaction = ConcreteTransaction(
        "test", datetime.now(user_settings.settings.time_zone)
    )
    transaction.add_tags(tags)
    for tag in tags:
        assert tag in transaction.tags
        transaction.remove_tags([tag])
        assert tag not in transaction.tags


@given(tags=everything_except(Collection))
def test_validate_tags_invalid_type(tags: Any) -> None:
    transaction = ConcreteTransaction(
        "test", datetime.now(user_settings.settings.time_zone)
    )
    with pytest.raises(TypeError, match="Parameter 'tags' must be a Collection."):
        transaction._validate_tags(tags)


@given(tags=st.lists(everything_except(Attribute), min_size=1, max_size=5))
def test_validate_tags_invalid_member_types(tags: Any) -> None:
    transaction = ConcreteTransaction(
        "test", datetime.now(user_settings.settings.time_zone)
    )
    with pytest.raises(
        TypeError, match="Parameter 'tags' must be a Collection of Attributes."
    ):
        transaction._validate_tags(tags)


@given(tags=st.lists(attributes(AttributeType.PAYEE), min_size=1, max_size=5))
def test_validate_tags_invalid_attribute_type(tags: Any) -> None:
    transaction = ConcreteTransaction(
        "test", datetime.now(user_settings.settings.time_zone)
    )
    with pytest.raises(InvalidAttributeError):
        transaction._validate_tags(tags)


def test_clear_tags() -> None:
    transaction = ConcreteTransaction(
        "test", datetime.now(user_settings.settings.time_zone)
    )
    tag = Attribute("TEST TAG", AttributeType.TAG)
    transaction._tags = frozenset((tag,))
    assert transaction.tags == frozenset((tag,))
    transaction.clear_tags()
    assert transaction.tags == frozenset()


def test_replace_tag() -> None:
    transaction = ConcreteTransaction(
        "test", datetime.now(user_settings.settings.time_zone)
    )
    tag_1 = Attribute("TAG1", AttributeType.TAG)
    tag_2 = Attribute("TAG2", AttributeType.TAG)
    transaction._tags = frozenset((tag_1,))
    assert transaction.tags == frozenset((tag_1,))
    transaction.replace_tag(tag_1, tag_2)
    assert transaction.tags == frozenset((tag_2,))


def test_replace_tag_not_found() -> None:
    transaction = ConcreteTransaction(
        "test", datetime.now(user_settings.settings.time_zone)
    )
    tag_1 = Attribute("TAG1", AttributeType.TAG)
    tag_2 = Attribute("TAG2", AttributeType.TAG)
    tag_3 = Attribute("TAG3", AttributeType.TAG)
    transaction._tags = frozenset((tag_1,))
    assert transaction.tags == frozenset((tag_1,))
    with pytest.raises(NotFoundError):
        transaction.replace_tag(tag_2, tag_3)
