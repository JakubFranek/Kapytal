import string
from datetime import datetime
from typing import Any

import pytest
from hypothesis import assume, given
from hypothesis import strategies as st

from src.models.constants import tzinfo
from src.models.model_objects.currency import Currency
from tests.models.test_assets.composites import everything_except


@given(
    code=st.text(alphabet=string.ascii_letters, min_size=3, max_size=3),
    places=st.integers(min_value=0, max_value=8),
)
def test_creation(code: str, places: int) -> None:
    dt_start = datetime.now(tzinfo)
    currency = Currency(code, places)

    dt_created_diff = currency.datetime_created - dt_start

    assert currency.code == code.upper()
    assert currency.places == places
    assert currency.convertible_to == set()
    assert currency.exchange_rates == {}
    assert dt_created_diff.seconds < 1


@given(code=st.text(max_size=2), places=st.integers(min_value=0, max_value=8))
def test_code_too_short(code: str, places: int) -> None:
    with pytest.raises(
        ValueError, match="Currency.code must be a three letter ISO-4217 code."
    ):
        Currency(code, places)


@given(code=st.text(min_size=4), places=st.integers(min_value=0, max_value=8))
def test_code_too_long(code: str, places: int) -> None:
    with pytest.raises(
        ValueError, match="Currency.code must be a three letter ISO-4217 code."
    ):
        Currency(code, places)


@given(
    code=st.text(min_size=3, max_size=3), places=st.integers(min_value=0, max_value=8)
)
def test_code_not_alpha(code: str, places: int) -> None:
    assume(any(char.isdigit() for char in code))
    with pytest.raises(
        ValueError, match="Currency.code must be a three letter ISO-4217 code."
    ):
        Currency(code, places)


@given(code=everything_except(str), places=st.integers(min_value=0, max_value=8))
def test_code_not_string(code: Any, places: int) -> None:
    with pytest.raises(TypeError, match="Currency.code must be a string."):
        Currency(code, places)


@given(
    code=st.text(alphabet=string.ascii_letters, min_size=3, max_size=3),
    places=everything_except(int),
)
def test_places_invalid_type(code: Any, places: int) -> None:
    with pytest.raises(TypeError, match="Currency.places must be an integer."):
        Currency(code, places)


@given(
    code=st.text(alphabet=string.ascii_letters, min_size=3, max_size=3),
    places=st.integers(max_value=-1),
)
def test_places_invalid_value(code: Any, places: int) -> None:
    with pytest.raises(ValueError, match="Currency.places must not be negative."):
        Currency(code, places)


@given(
    code=st.text(alphabet=string.ascii_letters, min_size=3, max_size=3),
    places_1=st.integers(min_value=0, max_value=8),
    places_2=st.integers(min_value=0, max_value=8),
)
def test_hash(code: str, places_1: int, places_2: int) -> None:
    currency_1 = Currency(code, places_1)
    currency_2 = Currency(code, places_2)
    assert currency_1 == currency_2
    assert currency_1.__hash__() == currency_2.__hash__()
