from datetime import datetime
from typing import Any

import pytest
from hypothesis import assume, given, settings
from hypothesis import strategies as st

from src.models.constants import tzinfo
from src.models.model_objects.account_group import AccountGroup
from tests.models.test_assets.composites import account_groups
from tests.models.test_assets.concrete_abcs import ConcreteAccount


@given(name=st.text(min_size=1, max_size=32))
def test_creation(name: str) -> None:
    dt_start = datetime.now(tzinfo)
    account = ConcreteAccount(name)

    dt_created_diff = account.datetime_created - dt_start

    assert account.name == name
    assert dt_created_diff.seconds < 1


@given(name=st.just(""))
def test_name_too_short(name: str) -> None:
    with pytest.raises(ValueError, match="Account.name length must be*"):
        ConcreteAccount(name)


@given(name=st.text(min_size=33))
@settings(max_examples=15)
def test_name_too_long(name: str) -> None:
    with pytest.raises(ValueError, match="Account.name length must be*"):
        ConcreteAccount(name)


@given(
    name=st.integers()
    | st.floats()
    | st.none()
    | st.datetimes()
    | st.booleans()
    | st.sampled_from([[], (), {}, set()])
)
def test_name_not_string(name: Any) -> None:
    with pytest.raises(TypeError, match="Account.name must be a string."):
        ConcreteAccount(name)


@given(name=st.text(min_size=1, max_size=32), parent=account_groups())
def test_add_and_remove_parent(name: str, parent: AccountGroup) -> None:
    account = ConcreteAccount(name)
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
    account = ConcreteAccount(name)
    with pytest.raises(
        TypeError, match="Account.parent must be an AccountGroup or a None."
    ):
        account.parent = parent


@given(name=st.text(min_size=1, max_size=32))
def test_abstract_balance(name: str) -> None:
    account = ConcreteAccount(name)
    with pytest.raises(NotImplementedError):
        account.balance


@given(name=st.text(min_size=1, max_size=32))
def test_abstract_transactions(name: str) -> None:
    account = ConcreteAccount(name)
    with pytest.raises(NotImplementedError):
        account.transactions
