from datetime import datetime
from decimal import Decimal
from typing import Any

import pytest
from hypothesis import assume, given
from hypothesis import strategies as st

from src.models.base_classes.account import UnrelatedAccountError
from src.models.constants import tzinfo
from src.models.model_objects.account_group import AccountGroup
from src.models.model_objects.currency import CashAmount, Currency, ExchangeRate
from src.models.model_objects.security_objects import (
    Security,
    SecurityAccount,
    SecurityRelatedTransaction,
    SecurityType,
)
from tests.models.test_assets.composites import (
    account_groups,
    currencies,
    everything_except,
    security_accounts,
    security_transactions,
    security_transfers,
    valid_decimals,
)


@given(name=st.text(min_size=1, max_size=32), parent=st.none() | account_groups())
def test_creation(name: str, parent: AccountGroup | None) -> None:
    security_account = SecurityAccount(name, parent)
    assert security_account.name == name
    assert security_account.parent == parent
    assert security_account.securities == {}
    assert security_account.transactions == ()
    assert security_account.__repr__() == f"SecurityAccount('{name}')"


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
    currency_A=currencies(),
    currency_B=currencies(),
    price_A=valid_decimals(min_value=0, max_value=1e6),
    price_B=valid_decimals(min_value=0, max_value=1e6),
    shares_A=st.integers(min_value=1, max_value=1e6),
    shares_B=st.integers(min_value=1, max_value=1e6),
    exchange_rate=valid_decimals(min_value=0.01, max_value=1e6),
)
def test_get_balance(
    currency_A: Currency,
    currency_B: Currency,
    price_A: Decimal,
    price_B: Decimal,
    shares_A: int,
    shares_B: int,
    exchange_rate: Decimal,
) -> None:
    assume(currency_A != currency_B)
    date_ = datetime.now(tzinfo).date()
    exchange_rate_obj = ExchangeRate(currency_A, currency_B)
    exchange_rate_obj.set_rate(date_, exchange_rate)
    account = SecurityAccount("Test")
    security_A = Security("A", "A", SecurityType.ETF, currency_A, 1)
    security_B = Security("B", "B", SecurityType.ETF, currency_B, 1)
    security_A.set_price(date_, CashAmount(price_A, currency_A))
    security_B.set_price(date_, CashAmount(price_B, currency_B))
    account._securities[security_A] += shares_A
    account._securities[security_B] += shares_B
    balance_A = account.get_balance(currency_A)
    balance_B = account.get_balance(currency_B)
    expected_A = shares_A * security_A.price + shares_B * security_B.price.convert(
        currency_A
    )
    expected_B = (
        shares_A * security_A.price.convert(currency_B) + shares_B * security_B.price
    )
    assert balance_A == expected_A
    assert balance_B == expected_B
