from datetime import datetime
from typing import Any

import pytest
from hypothesis import given
from hypothesis import strategies as st

from src.models.constants import tzinfo
from src.models.mixins.name_mixin import NameLengthError
from src.models.model_objects.account_group import AccountGroup
from tests.models.test_assets.composites import account_groups, everything_except
from tests.models.test_assets.concrete_abcs import ConcreteAccount
from tests.models.test_assets.get_valid_objects import get_concrete_account


@given(name=st.text(min_size=1, max_size=32))
def test_creation(name: str) -> None:
    dt_start = datetime.now(tzinfo)
    account = ConcreteAccount(name)

    dt_created_diff = account.datetime_created - dt_start

    assert account.name == name
    assert account.path == name
    assert dt_created_diff.seconds < 1


@given(name=st.just(""))
def test_name_too_short(name: str) -> None:
    with pytest.raises(NameLengthError):
        ConcreteAccount(name)


@given(name=st.text(min_size=33))
def test_name_too_long(name: str) -> None:
    with pytest.raises(NameLengthError):
        ConcreteAccount(name)


@given(name=everything_except(str))
def test_name_invalid_type(name: Any) -> None:
    with pytest.raises(TypeError, match="Account.name must be a string."):
        ConcreteAccount(name)


@given(parent=account_groups())
def test_add_and_remove_parent(parent: AccountGroup) -> None:
    account = get_concrete_account()
    assert account.parent is None
    assert account.path == account.name
    account.parent = parent
    assert account.parent == parent
    assert account in parent.children
    assert account.path == f"{parent.name}/{account.name}"
    account.parent = None
    assert account.parent is None
    assert account not in parent.children
    assert account.path == account.name


@given(
    parent=everything_except((AccountGroup, type(None))),
)
def test_invalid_parent_type(parent: Any) -> None:
    account = get_concrete_account()
    with pytest.raises(
        TypeError, match="Account.parent must be an AccountGroup or a None."
    ):
        account.parent = parent


def test_abstract_get_balance() -> None:
    account = get_concrete_account()
    with pytest.raises(NotImplementedError):
        account.get_balance(None)


def test_abstract_transactions() -> None:
    account = get_concrete_account()
    with pytest.raises(NotImplementedError):
        account.transactions
