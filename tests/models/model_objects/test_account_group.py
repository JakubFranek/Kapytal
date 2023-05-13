from datetime import datetime
from decimal import Decimal
from typing import Any

import pytest
from hypothesis import assume, given
from hypothesis import strategies as st
from src.models.custom_exceptions import NotFoundError
from src.models.model_objects.account_group import AccountGroup
from src.models.model_objects.currency_objects import CashAmount, Currency, ExchangeRate
from src.models.user_settings import user_settings
from tests.models.test_assets.composites import (
    account_groups,
    cash_accounts,
    currencies,
    everything_except,
    names,
    valid_decimals,
)


@given(name=names(), currency=currencies())
def test_creation(name: str, currency: Currency) -> None:
    account_group = AccountGroup(name)

    assert account_group.name == name
    assert account_group.parent is None
    assert account_group.get_balance(currency) == CashAmount(Decimal(0), currency)
    assert account_group.__repr__() == f"AccountGroup('{name}')"
    assert account_group.path == name


@given(parent=account_groups())
def test_add_and_remove_parent(parent: AccountGroup) -> None:
    account_group = get_account_group()
    expected_repr = f"AccountGroup('{account_group.name}')"
    assert account_group.parent is None
    assert account_group.children == ()
    assert account_group.__repr__() == expected_repr
    assert account_group.path == account_group.name

    account_group.parent = parent
    expected_path = parent.path + "/" + account_group.name
    expected_repr = f"AccountGroup('{expected_path}')"
    assert account_group.parent == parent
    assert account_group in parent.children
    assert account_group.__repr__() == expected_repr
    assert account_group.path == f"{account_group.parent.name}/{account_group.name}"

    account_group.parent = None
    expected_repr = f"AccountGroup('{account_group.name}')"
    assert account_group.parent is None
    assert account_group not in parent.children
    assert account_group.__repr__() == expected_repr
    assert account_group.path == account_group.name


@given(parent=account_groups())
def test_set_same_parent(parent: AccountGroup) -> None:
    account_group = get_account_group()
    account_group.parent = parent
    account_group.parent = parent
    assert account_group.parent == parent


@given(parent=everything_except((AccountGroup, type(None))))
def test_invalid_parent_type(parent: Any) -> None:
    account_group = get_account_group()
    with pytest.raises(
        TypeError, match="AccountGroup.parent must be an AccountGroup or a None."
    ):
        account_group.parent = parent


@given(currency=currencies(), data=st.data())
def test_get_balance_single_currency(currency: Currency, data: st.DataObject) -> None:
    accounts = data.draw(
        st.lists(cash_accounts(currency=currency), min_size=0, max_size=5)
    )

    account_group = get_account_group()
    for account in accounts:
        account.parent = account_group

    expected_sum = sum(
        (account.get_balance(currency) for account in accounts),
        start=currency.zero_amount,
    )
    account_group._update_balances()
    assert account_group.get_balance(currency) == expected_sum


@given(
    currency_a=currencies(),
    currency_b=currencies(),
    rate=valid_decimals(min_value=0.01, max_value=1e10),
    data=st.data(),
)
def test_get_balance_multiple_currency(
    currency_a: Currency, currency_b: Currency, rate: Decimal, data: st.DataObject
) -> None:
    assume(currency_a != currency_b)
    exchange_rate = ExchangeRate(currency_a, currency_b)
    exchange_rate.set_rate(datetime.now(user_settings.settings.time_zone).date(), rate)

    account_a = data.draw(cash_accounts(currency=currency_a))
    account_b = data.draw(cash_accounts(currency=currency_b))

    account_group = get_account_group()
    account_a.parent = account_group
    account_b.parent = account_group

    expected_sum_a = account_a.get_balance(currency_a) + account_b.get_balance(
        currency_a
    )
    expected_sum_b = account_a.get_balance(currency_b) + account_b.get_balance(
        currency_b
    )
    account_group._update_balances()
    assert account_group.get_balance(currency_a) == expected_sum_a
    assert account_group.get_balance(currency_b) == expected_sum_b


@given(data=st.data())
def test_set_child_index(data: st.DataObject) -> None:
    parent = get_account_group()
    children = data.draw(st.lists(account_groups(), min_size=5, max_size=5))
    for child in children:
        child.parent = parent

    selected_child = children[0]
    parent.set_child_index(selected_child, 2)
    assert parent.children[2] == selected_child


def test_set_child_index_child_does_not_exist() -> None:
    parent = get_account_group()
    with pytest.raises(NotFoundError):
        parent.set_child_index(None, 0)


def test_set_child_index_negative() -> None:
    parent = get_account_group()
    with pytest.raises(ValueError, match="negative"):
        parent.set_child_index(None, -1)


def get_account_group() -> AccountGroup:
    return AccountGroup("Valid Name", None)
