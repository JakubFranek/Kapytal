from datetime import datetime
from decimal import Decimal
from typing import Any

import pytest
from hypothesis import assume, given
from hypothesis import strategies as st

from src.models.constants import tzinfo
from src.models.custom_exceptions import NotFoundError
from src.models.model_objects.account_group import AccountGroup
from src.models.model_objects.currency_objects import CashAmount, Currency, ExchangeRate
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
    assert account_group.__repr__() == f"AccountGroup(path='{name}')"
    assert account_group.path == name


@given(parent=account_groups())
def test_add_and_remove_parent(parent: AccountGroup) -> None:
    account_group = get_account_group()
    expected_repr = f"AccountGroup(path='{account_group.name}')"
    assert account_group.parent is None
    assert account_group.children == ()
    assert account_group.__repr__() == expected_repr
    assert account_group.path == account_group.name

    account_group.parent = parent
    expected_path = parent.path + "/" + account_group.name
    expected_repr = f"AccountGroup(path='{expected_path}')"
    assert account_group.parent == parent
    assert account_group in parent.children
    assert account_group.__repr__() == expected_repr
    assert account_group.path == f"{account_group.parent.name}/{account_group.name}"

    account_group.parent = None
    expected_repr = f"AccountGroup(path='{account_group.name}')"
    assert account_group.parent is None
    assert account_group not in parent.children
    assert account_group.__repr__() == expected_repr
    assert account_group.path == account_group.name


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
        start=CashAmount(0, currency),
    )
    assert account_group.get_balance(currency) == expected_sum


@given(
    currency_A=currencies(),
    currency_B=currencies(),
    rate=valid_decimals(min_value=0.01, max_value=1e10),
    data=st.data(),
)
def test_get_balance_multiple_currency(
    currency_A: Currency, currency_B: Currency, rate: Decimal, data: st.DataObject
) -> None:
    assume(currency_A != currency_B)
    exchange_rate = ExchangeRate(currency_A, currency_B)
    exchange_rate.set_rate(datetime.now(tzinfo).date(), rate)

    account_A = data.draw(cash_accounts(currency=currency_A))
    account_B = data.draw(cash_accounts(currency=currency_B))

    account_group = get_account_group()
    account_A.parent = account_group
    account_B.parent = account_group

    expected_sum_A = account_A.get_balance(currency_A) + account_B.get_balance(
        currency_A
    )
    expected_sum_B = account_A.get_balance(currency_B) + account_B.get_balance(
        currency_B
    )
    assert account_group.get_balance(currency_A) == expected_sum_A
    assert account_group.get_balance(currency_B) == expected_sum_B


@given(data=st.data())
def test_set_child_index(data: st.DataObject) -> None:
    parent = get_account_group()
    children = data.draw(st.lists(account_groups(), min_size=5, max_size=5))
    for child in children:
        child.parent = parent

    selected_child = children[2]
    parent.set_child_index(selected_child, 0)
    assert parent.children[0] == selected_child


def test_set_child_index_child_does_not_exist() -> None:
    parent = get_account_group()
    with pytest.raises(NotFoundError):
        parent.set_child_index(None, 0)


def get_account_group() -> AccountGroup:
    return AccountGroup("Valid Name", None)
