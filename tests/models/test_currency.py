import string
from datetime import datetime, timedelta, timezone
from typing import Any

import pytest
from hypothesis import assume, given
from hypothesis import strategies as st

from src.models.currency import Currency

timezone_offset = +1.0  # Central European Time (CET = UTC+01:00)
tzinfo = timezone(timedelta(hours=timezone_offset))


@given(code=st.text(alphabet=string.ascii_letters, min_size=3, max_size=3))
def test_code_pass(code: str) -> None:
    dt_start = datetime.now(tzinfo)
    currency = Currency(code)

    dt_created_diff = currency.date_created - dt_start

    assert currency.code == code.upper()
    assert dt_created_diff.seconds < 1


@given(code=st.text(max_size=2))
def test_code_too_short(code: str) -> None:
    with pytest.raises(
        ValueError, match="Currency code must be a three letter ISO-4217 code."
    ):
        Currency(code)


@given(code=st.text(min_size=4))
def test_code_too_long(code: str) -> None:
    with pytest.raises(
        ValueError, match="Currency code must be a three letter ISO-4217 code."
    ):
        Currency(code)


@given(code=st.text(min_size=3, max_size=3))
def test_code_not_alpha(code: str) -> None:
    assume(any(char.isdigit() for char in code))
    with pytest.raises(
        ValueError, match="Currency code must be a three letter ISO-4217 code."
    ):
        Currency(code)


@given(
    code=st.integers()
    | st.floats()
    | st.none()
    | st.datetimes()
    | st.booleans()
    | st.sampled_from([[], (), {}, set()])
)
def test_code_not_string(code: Any) -> None:
    with pytest.raises(TypeError, match="Currency code must be a string."):
        Currency(code)
