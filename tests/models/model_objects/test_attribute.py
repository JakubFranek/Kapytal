from datetime import datetime
from typing import Any

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from src.models.constants import tzinfo
from src.models.model_objects.attributes import Attribute, AttributeType


@given(name=st.text(min_size=1, max_size=32), type_=st.sampled_from(AttributeType))
def test_creation(name: str, type_: AttributeType) -> None:
    dt_start = datetime.now(tzinfo)
    attribute = Attribute(name, type_)

    dt_created_diff = attribute.datetime_created - dt_start

    assert attribute.name == name
    assert dt_created_diff.seconds < 1


@given(
    name=st.integers()
    | st.floats()
    | st.none()
    | st.datetimes()
    | st.booleans()
    | st.sampled_from([[], (), {}, set()]),
    type_=st.sampled_from(AttributeType),
)
def test_name_not_string(name: Any, type_: AttributeType) -> None:
    with pytest.raises(TypeError, match="Attribute.name must be a string."):
        Attribute(name, type_)


@given(
    name=st.just(""),
    type_=st.sampled_from(AttributeType),
)
def test_name_too_short(name: str, type_: AttributeType) -> None:
    with pytest.raises(ValueError, match="Attribute.name length must be*"):
        Attribute(name, type_)


@given(
    name=st.text(min_size=33),
    type_=st.sampled_from(AttributeType),
)
@settings(max_examples=15)
def test_name_too_long(name: str, type_: AttributeType) -> None:
    with pytest.raises(ValueError, match="Attribute.name length must be*"):
        Attribute(name, type_)


@given(
    name=st.text(min_size=1, max_size=32),
    type_=st.integers()
    | st.floats()
    | st.none()
    | st.datetimes()
    | st.booleans()
    | st.sampled_from([[], (), {}, set()]),
)
def test_type_invalid_type(name: str, type_: Any) -> None:
    with pytest.raises(TypeError, match="Attribute.type_ must be an AttributeType."):
        Attribute(name, type_)
