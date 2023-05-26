from datetime import datetime
from decimal import Decimal
from typing import Any

import pytest
from hypothesis import assume, given
from hypothesis import strategies as st
from src.models.base_classes.account import UnrelatedAccountError
from src.models.model_objects.account_group import AccountGroup
from src.models.model_objects.currency_objects import CashAmount, Currency, ExchangeRate
from src.models.model_objects.security_objects import (
    Security,
    SecurityAccount,
    SecurityRelatedTransaction,
)
from src.models.user_settings import user_settings
from tests.models.test_assets.composites import (
    account_groups,
    currencies,
    everything_except,
    names,
    security_accounts,
    security_transactions,
    security_transfers,
    valid_decimals,
)


@given(name=names(), parent=st.none() | account_groups())
def test_creation(name: str, parent: AccountGroup | None) -> None:
    security_account = SecurityAccount(name, parent)
    expected_path = parent.path + "/" + name if parent is not None else name
    assert security_account.name == name
    assert security_account.parent == parent
    assert security_account.securities == {}
    assert security_account.transactions == ()
    assert security_account.__repr__() == f"SecurityAccount({expected_path})"


@given(
    security_account=security_accounts(),
    transaction=everything_except(SecurityRelatedTransaction),
)
def test_validate_transaction_invalid_type(
    security_account: SecurityAccount, transaction: Any
) -> None:
    with pytest.raises(
        TypeError, match="Parameter 'transaction' must be a SecurityRelatedTransaction."
    ):
        security_account._validate_transaction(transaction)


@given(
    security_account=security_accounts(),
    transaction=security_transactions() | security_transfers(),
)
def test_validate_transaction_unrelated(
    security_account: SecurityAccount, transaction: SecurityRelatedTransaction
) -> None:
    assume(not transaction.is_account_related(security_account))
    with pytest.raises(UnrelatedAccountError):
        security_account._validate_transaction(transaction)


@given(
    currency_a=currencies(),
    currency_b=currencies(),
    price_a=valid_decimals(min_value=0, max_value=1e6),
    price_b=valid_decimals(min_value=0, max_value=1e6),
    shares_a=st.integers(min_value=1, max_value=1e6),
    shares_b=st.integers(min_value=1, max_value=1e6),
    exchange_rate=valid_decimals(min_value=0.01, max_value=1e6, places=4),
)
def test_get_balance(  # noqa: PLR0913
    currency_a: Currency,
    currency_b: Currency,
    price_a: Decimal,
    price_b: Decimal,
    shares_a: int,
    shares_b: int,
    exchange_rate: Decimal,
) -> None:
    assume(currency_a != currency_b)
    date_ = datetime.now(user_settings.settings.time_zone).date()
    exchange_rate_obj = ExchangeRate(currency_a, currency_b)
    exchange_rate_obj.set_rate(date_, exchange_rate)
    account = SecurityAccount("Test")
    security_a = Security("A", "A", "ETF", currency_a, 1)
    security_b = Security("B", "B", "ETF", currency_b, 1)
    security_a.set_price(date_, CashAmount(price_a, currency_a))
    security_b.set_price(date_, CashAmount(price_b, currency_b))
    account._securities[security_a] += shares_a
    account._securities[security_b] += shares_b
    account._update_balances()
    balance_a = account.get_balance(currency_a)
    balance_b = account.get_balance(currency_b)
    expected_a = shares_a * security_a.price + shares_b * security_b.price.convert(
        currency_a
    )
    expected_b = (
        shares_a * security_a.price.convert(currency_b) + shares_b * security_b.price
    )
    assert round(balance_a.value_normalized, 10) == round(
        expected_a.value_normalized, 10
    )
    assert round(balance_b.value_normalized, 10) == round(
        expected_b.value_normalized, 10
    )
