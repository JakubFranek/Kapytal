from datetime import datetime
from decimal import Decimal
from typing import Any

import pytest
from hypothesis import assume, given
from hypothesis import strategies as st

from src.models.constants import tzinfo
from src.models.model_objects.account_group import AccountGroup
from src.models.model_objects.currency import CashAmount, Currency, ExchangeRate
from tests.models.test_assets.composites import (
    account_groups,
    cash_accounts,
    currencies,
    everything_except,
    valid_decimals,
)


@given(name=st.text(min_size=1, max_size=32), currency=currencies())
def test_creation(name: str, currency: Currency) -> None:
    dt_start = datetime.now(tzinfo)
    account_group = AccountGroup(name)

    dt_created_diff = account_group.datetime_created - dt_start

    assert account_group.name == name
    assert account_group.parent is None
    assert account_group.get_balance(currency) == CashAmount(Decimal(0), currency)
    assert dt_created_diff.seconds < 1
    assert account_group.__repr__() == f"AccountGroup('{name}', parent='None')"
    assert account_group.path == name


@given(parent=account_groups())
def test_add_and_remove_parent(parent: AccountGroup) -> None:
    account_group = get_account_group()
    expected_repr = f"AccountGroup('{account_group.name}', parent='None')"
    assert account_group.parent is None
    assert account_group.children == ()
    assert account_group.__repr__() == expected_repr
    assert account_group.path == account_group.name

    account_group.parent = parent
    expected_repr = (
        f"AccountGroup('{account_group.name}', parent='{account_group.parent}')"
    )
    assert account_group.parent == parent
    assert account_group in parent.children
    assert account_group.__repr__() == expected_repr
    assert account_group.path == f"{account_group.parent.name}/{account_group.name}"

    account_group.parent = None
    expected_repr = f"AccountGroup('{account_group.name}', parent='None')"
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


def get_account_group() -> AccountGroup:
    return AccountGroup("Valid Name", None)
