import string
from datetime import datetime
from typing import Any

import pytest
from hypothesis import assume, given
from hypothesis import strategies as st

from src.models.constants import tzinfo
from src.models.model_objects.currency import Currency
from tests.models.test_assets.composites import everything_except


@given(code=st.text(alphabet=string.ascii_letters, min_size=3, max_size=3))
def test_creation(code: str) -> None:
    dt_start = datetime.now(tzinfo)
    currency = Currency(code)

    dt_created_diff = currency.datetime_created - dt_start

    assert currency.code == code.upper()
    assert dt_created_diff.seconds < 1


@given(code=st.text(max_size=2))
def test_code_too_short(code: str) -> None:
    with pytest.raises(
        ValueError, match="Currency.code must be a three letter ISO-4217 code."
    ):
        Currency(code)


@given(code=st.text(min_size=4))
def test_code_too_long(code: str) -> None:
    with pytest.raises(
        ValueError, match="Currency.code must be a three letter ISO-4217 code."
    ):
        Currency(code)


@given(code=st.text(min_size=3, max_size=3))
def test_code_not_alpha(code: str) -> None:
    assume(any(char.isdigit() for char in code))
    with pytest.raises(
        ValueError, match="Currency.code must be a three letter ISO-4217 code."
    ):
        Currency(code)


@given(code=everything_except(str))
def test_code_not_string(code: Any) -> None:
    with pytest.raises(TypeError, match="Currency.code must be a string."):
        Currency(code)
