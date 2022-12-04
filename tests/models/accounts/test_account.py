from datetime import datetime, timedelta, timezone
from typing import Any

import pytest
from hypothesis import given
from hypothesis import strategies as st

from src.models.accounts.account import Account

timezone_offset = +1.0  # Central European Time (CET = UTC+01:00)
tzinfo = timezone(timedelta(hours=timezone_offset))


@given(name=st.text(min_size=1, max_size=32))
def test_creation_pass(name: str) -> None:
    dt_start = datetime.now(tzinfo)
    account = Account(name)

    dt_created_diff = account.datetime_created - dt_start

    assert account.name == name
    assert dt_created_diff.seconds < 1


@given(name=st.just(""))
def test_name_too_short(name: str) -> None:
    with pytest.raises(ValueError, match="Account name length must be*"):
        Account(name)


@given(name=st.text(min_size=33))
def test_name_too_long(name: str) -> None:
    with pytest.raises(ValueError, match="Account name length must be*"):
        Account(name)


@given(
    name=st.integers()
    | st.floats()
    | st.none()
    | st.datetimes()
    | st.booleans()
    | st.sampled_from([[], (), {}, set()])
)
def test_name_not_string(name: Any) -> None:
    with pytest.raises(TypeError, match="Account name must be a string."):
        Account(name)
