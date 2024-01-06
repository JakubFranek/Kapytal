from collections import defaultdict
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Any

import pytest
from hypothesis import assume, given
from hypothesis import strategies as st
from src.models.base_classes.account import UnrelatedAccountError
from src.models.model_objects.account_group import AccountGroup
from src.models.model_objects.cash_objects import CashAccount
from src.models.model_objects.currency_objects import CashAmount, Currency, ExchangeRate
from src.models.model_objects.security_objects import (
    Security,
    SecurityAccount,
    SecurityRelatedTransaction,
    SecurityTransaction,
    SecurityTransactionType,
    SecurityTransfer,
)
from src.models.user_settings import user_settings
from tests.models.test_assets.composites import (
    account_groups,
    cash_accounts,
    currencies,
    everything_except,
    names,
    securities,
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
    assert security_account.related_securities == set()
    assert security_account.currency is None
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
    datetime_ = datetime.now(user_settings.settings.time_zone)
    date_ = datetime_.date()
    exchange_rate_obj = ExchangeRate(currency_a, currency_b)
    exchange_rate_obj.set_rate(date_, exchange_rate)
    account = SecurityAccount("Test")
    security_a = Security("A", "A", "ETF", currency_a, 1)
    security_b = Security("B", "B", "ETF", currency_b, 1)
    security_a.set_price(date_, CashAmount(price_a, currency_a))
    security_b.set_price(date_, CashAmount(price_b, currency_b))
    d = defaultdict(lambda: Decimal(0))
    d[security_a] += shares_a
    d[security_b] += shares_b
    account._securities_history = [(datetime_, d)]
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


@given(currency=currencies(), data=st.data())
def test_get_balance_with_date(
    currency: Currency,
    data: st.DataObject,
) -> None:
    security = Security("NAME", "SYMB", "TYPE", currency, 1)

    account: SecurityAccount = data.draw(security_accounts())
    cash_account: CashAccount = data.draw(cash_accounts(currency=currency))
    t1: SecurityTransaction = data.draw(
        security_transactions(
            security_account=account, cash_account=cash_account, security=security
        )
    )
    t2: SecurityTransaction = data.draw(
        security_transactions(
            security_account=account, cash_account=cash_account, security=security
        )
    )
    t3: SecurityTransaction = data.draw(
        security_transactions(
            security_account=account, cash_account=cash_account, security=security
        )
    )

    t1._datetime = datetime.now(user_settings.settings.time_zone) - timedelta(days=5)
    t2._datetime = datetime.now(user_settings.settings.time_zone) - timedelta(days=3)
    t3._datetime = datetime.now(user_settings.settings.time_zone)
    t1._timestamp = t1._datetime.timestamp()
    t2._timestamp = t2._datetime.timestamp()
    t3._timestamp = t3._datetime.timestamp()
    transactions = [t1, t2, t3]
    security.set_price(t1.date_ - timedelta(days=10), CashAmount(1, currency))
    account.update_securities()
    transaction_sum_3 = sum(
        (
            (t.security.price * t.get_shares(account)).convert(currency)
            for t in transactions
        ),
        start=currency.zero_amount,
    )
    transaction_sum_2 = sum(
        (
            (t.security.price * t.get_shares(account)).convert(currency)
            for t in transactions[:-1]
        ),
        start=currency.zero_amount,
    )
    transaction_sum_1 = sum(
        (
            (t.security.price * t.get_shares(account)).convert(currency)
            for t in transactions[:-2]
        ),
        start=currency.zero_amount,
    )

    latest_balance = account.get_balance(currency)
    balance_3 = account.get_balance(currency, t3.date_)
    balance_2 = account.get_balance(currency, t2.date_)
    balance_1 = account.get_balance(currency, t1.date_)
    balance_0 = account.get_balance(currency, t1.date_ - timedelta(days=10))
    balance_1x = account.get_balance(currency, t1.date_ + timedelta(days=1))

    assert latest_balance == transaction_sum_3
    assert balance_3 == latest_balance
    assert balance_2 == transaction_sum_2
    assert balance_1 == transaction_sum_1
    assert balance_0 == currency.zero_amount
    assert balance_1x == transaction_sum_1

    assert account.currency == currency
    assert account.related_securities == {security}


@given(
    currency=currencies(),
    price_a=valid_decimals(min_value=0, max_value=1e6),
    price_b=valid_decimals(min_value=0, max_value=1e6),
    shares_a=st.integers(min_value=1, max_value=1e6),
    shares_b=st.integers(min_value=1, max_value=1e6),
)
def test_get_balance_same_currency_securities(
    currency: Currency,
    price_a: Decimal,
    price_b: Decimal,
    shares_a: int,
    shares_b: int,
) -> None:
    datetime_ = datetime.now(user_settings.settings.time_zone)
    date_ = datetime_.date()
    account = SecurityAccount("Test")
    security_a = Security("A", "A", "ETF", currency, 1)
    security_b = Security("B", "B", "ETF", currency, 1)
    security_a.set_price(date_, CashAmount(price_a, currency))
    security_b.set_price(date_, CashAmount(price_b, currency))
    d = defaultdict(lambda: Decimal(0))
    d[security_a] += shares_a
    d[security_b] += shares_b
    account._securities_history = [(datetime_, d)]
    account._update_balances()
    balance_a = account.get_balance(currency)
    balance_b = account.get_balance(currency)
    expected_a = shares_a * security_a.price + shares_b * security_b.price.convert(
        currency
    )
    expected_b = (
        shares_a * security_a.price.convert(currency) + shares_b * security_b.price
    )
    assert round(balance_a.value_normalized, 10) == round(
        expected_a.value_normalized, 10
    )
    assert round(balance_b.value_normalized, 10) == round(
        expected_b.value_normalized, 10
    )


def test_get_average_price_with_transfers() -> None:
    account = SecurityAccount("Test")
    account_2 = SecurityAccount("Original Buyer")
    usd = Currency("USD", 2)
    cash_account = CashAccount("Test", usd, CashAmount(0, usd))
    security = Security("Alphabet", "ABC", "Stock", usd, 1)

    SecurityTransaction(
        "test",
        datetime.now(user_settings.settings.time_zone),
        SecurityTransactionType.BUY,
        security,
        5,
        CashAmount(5, usd),
        account_2,
        cash_account,
    )
    SecurityTransaction(
        "test",
        datetime.now(user_settings.settings.time_zone),
        SecurityTransactionType.BUY,
        security,
        5,
        CashAmount(3, usd),
        account_2,
        cash_account,
    )
    SecurityTransfer(
        "transfer",
        datetime.now(user_settings.settings.time_zone),
        security,
        5,
        account_2,
        account,
    )
    SecurityTransaction(
        "test",
        datetime.now(user_settings.settings.time_zone),
        SecurityTransactionType.BUY,
        security,
        5,
        CashAmount(6, usd),
        account,
        cash_account,
    )

    avg_price = account.get_average_price(security)
    assert avg_price == CashAmount(5, usd)


@given(security=everything_except(Security))
def test_get_average_price_invalid_type(security: Any) -> None:
    account = SecurityAccount("Test")
    with pytest.raises(TypeError, match="Parameter 'security' must be a Security."):
        account.get_average_price(security)


@given(security=securities())
def test_get_average_price_invalid_security(security: Security) -> None:
    account = SecurityAccount("Test")
    with pytest.raises(ValueError, match="not in this SecurityAccount."):
        account.get_average_price(security)


def test_get_average_price_specific_date() -> None:
    account = SecurityAccount("Test")
    account_2 = SecurityAccount("Original Buyer")
    usd = Currency("USD", 2)
    cash_account = CashAccount("Test", usd, CashAmount(0, usd))
    security = Security("Alphabet", "ABC", "Stock", usd, 1)
    security_dummy = Security("Dummy", "DUMMY", "Stock", usd, 1)
    today = datetime.now(user_settings.settings.time_zone)

    SecurityTransaction(
        "test",
        today - timedelta(days=5),
        SecurityTransactionType.BUY,
        security,
        5,
        CashAmount(5, usd),
        account_2,
        cash_account,
    )
    SecurityTransaction(
        "test",
        today - timedelta(days=4),
        SecurityTransactionType.BUY,
        security,
        5,
        CashAmount(3, usd),
        account_2,
        cash_account,
    )
    SecurityTransfer(
        "transfer",
        today - timedelta(days=3),
        security_dummy,
        5,
        account_2,
        account,
    )
    SecurityTransfer(
        "transfer",
        today - timedelta(days=3),
        security,
        5,
        account_2,
        account,
    )
    SecurityTransaction(
        "test",
        today - timedelta(days=2),
        SecurityTransactionType.BUY,
        security,
        5,
        CashAmount(6, usd),
        account,
        cash_account,
    )
    SecurityTransaction(
        "test",
        today - timedelta(days=1),
        SecurityTransactionType.BUY,
        security_dummy,
        5,
        CashAmount(6, usd),
        account,
        cash_account,
    )
    SecurityTransaction(
        "test",
        today,
        SecurityTransactionType.BUY,
        security,
        5,
        CashAmount(6, usd),
        account,
        cash_account,
    )

    avg_price = account.get_average_price(security, today.date() - timedelta(days=2))
    assert avg_price == CashAmount(5, usd)


def test_get_average_price_invalid_date() -> None:
    account = SecurityAccount("Test")
    usd = Currency("USD", 2)
    security = Security("Alphabet", "ABC", "Stock", usd, 1)
    today = datetime.now(user_settings.settings.time_zone)

    with pytest.raises(ValueError, match="not in this SecurityAccount"):
        account.get_average_price(security, today.date() - timedelta(days=7))
