from typing import Any

import pytest
from hypothesis import given
from hypothesis import strategies as st
from src.models.custom_exceptions import InvalidCharacterError
from src.models.mixins.name_mixin import NameLengthError
from src.models.model_objects.account_group import AccountGroup
from tests.models.test_assets.composites import account_groups, everything_except, names
from tests.models.test_assets.concrete_abcs import ConcreteAccount


@given(name=names())
def test_creation(name: str) -> None:
    account = ConcreteAccount(name)
    assert account.name == name
    assert account.path == name


def test_eq() -> None:
    account1 = ConcreteAccount("test")
    account2 = ConcreteAccount("test")
    assert account1.__eq__(account2) == (account1.uuid == account2.uuid)
    assert account1.__hash__() != account2.__hash__()
    account2._uuid = account1.uuid
    assert account1.__eq__(account2) == (account1.uuid == account2.uuid)
    assert account1.__hash__() == account2.__hash__()
    assert account1.__eq__("anything else") is NotImplemented


@given(name=st.just(""))
def test_name_too_short(name: str) -> None:
    with pytest.raises(NameLengthError):
        ConcreteAccount(name)


@given(name=names(min_size=65))
def test_name_too_long(name: str) -> None:
    with pytest.raises(NameLengthError):
        ConcreteAccount(name)


def test_name_invalid_character() -> None:
    with pytest.raises(InvalidCharacterError):
        ConcreteAccount("Invalid/name/with/slashes")


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


@given(parent=account_groups())
def test_set_same_parent(parent: AccountGroup) -> None:
    account = get_concrete_account()
    account.parent = parent
    account.parent = parent
    assert account.parent == parent


@given(
    parent=everything_except((AccountGroup, type(None))),
)
def test_invalid_parent_type(parent: Any) -> None:
    account = get_concrete_account()
    with pytest.raises(
        TypeError, match="Account.parent must be an AccountGroup or a None."
    ):
        account.parent = parent


def get_concrete_account() -> ConcreteAccount:
    return ConcreteAccount("Valid Name")
