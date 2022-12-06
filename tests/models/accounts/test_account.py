from datetime import datetime
from typing import Any

import pytest
from hypothesis import assume, given, settings
from hypothesis import strategies as st

from src.models.accounts.account import Account
from src.models.accounts.account_group import AccountGroup
from src.models.constants import tzinfo
from tests.models.composites import account_groups


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
@settings(max_examples=15)
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


@given(name=st.text(min_size=1, max_size=32), parent=account_groups())
def test_add_and_remove_parent(name: str, parent: AccountGroup) -> None:
    account = Account(name)
    assert account.parent is None
    account.parent = parent
    assert account.parent == parent
    assert account in parent.children
    account.parent = None
    assert account.parent is None
    assert account not in parent.children


@given(
    name=st.text(min_size=1, max_size=32),
    parent=st.integers()
    | st.floats()
    | st.none()
    | st.datetimes()
    | st.booleans()
    | st.sampled_from([[], (), {}, set()]),
)
def test_invalid_parent_type(name: str, parent: Any) -> None:
    assume(parent is not None)
    account = Account(name)
    with pytest.raises(
        TypeError, match="Account parent can only be an AccountGroup or a None."
    ):
        account.parent = parent
