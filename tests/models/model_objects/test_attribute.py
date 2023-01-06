from datetime import datetime
from typing import Any

import pytest
from hypothesis import given
from hypothesis import strategies as st

from src.models.constants import tzinfo
from src.models.mixins.name_mixin import NameLengthError
from src.models.model_objects.attributes import Attribute, AttributeType
from tests.models.test_assets.composites import everything_except


@given(name=st.text(min_size=1, max_size=32), type_=st.sampled_from(AttributeType))
def test_creation(name: str, type_: AttributeType) -> None:
    dt_start = datetime.now(tzinfo)
    attribute = Attribute(name, type_)

    dt_created_diff = attribute.datetime_created - dt_start

    assert attribute.name == name
    assert attribute.__repr__() == f"Attribute('{name}', {type_.name})"
    assert dt_created_diff.seconds < 1


@given(
    name=everything_except(str),
    type_=st.sampled_from(AttributeType),
)
def test_name_invalid_type(name: Any, type_: AttributeType) -> None:
    with pytest.raises(TypeError, match="Attribute.name must be a string."):
        Attribute(name, type_)


@given(
    name=st.just(""),
    type_=st.sampled_from(AttributeType),
)
def test_name_too_short(name: str, type_: AttributeType) -> None:
    with pytest.raises(NameLengthError):
        Attribute(name, type_)


@given(
    name=st.text(min_size=33),
    type_=st.sampled_from(AttributeType),
)
def test_name_too_long(name: str, type_: AttributeType) -> None:
    with pytest.raises(NameLengthError):
        Attribute(name, type_)


@given(
    name=st.just("Valid Name"),
    type_=everything_except(AttributeType),
)
def test_type_invalid_type(name: str, type_: Any) -> None:
    with pytest.raises(TypeError, match="Attribute.type_ must be an AttributeType."):
        Attribute(name, type_)
