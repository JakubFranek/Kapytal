from datetime import datetime, timedelta
from decimal import Decimal

import pytest
from hypothesis import given
from hypothesis import strategies as st

from src.models.constants import tzinfo
from src.models.model_objects.cash_objects import CashAccount
from src.models.model_objects.currency import Currency
from src.models.model_objects.security_objects import (
    Security,
    SecurityAccount,
    SecurityTransaction,
    SecurityTransactionType,
)
from tests.models.test_assets.composites import (
    cash_accounts,
    everything_except,
    securities,
    security_accounts,
)
from tests.models.test_assets.get_valid_objects import get_security


@given(
    description=st.text(min_size=1, max_size=256),
    type_=st.just(SecurityTransactionType.BUY),
    security=securities(),
    shares=st.integers(min_value=1),
    price_per_share=st.decimals(
        min_value=0, max_value=1e10, allow_infinity=False, allow_nan=False, places=3
    ),
    fees=st.decimals(
        min_value=0, max_value=1e10, allow_infinity=False, allow_nan=False, places=3
    ),
    security_account=security_accounts(),
    cash_account=cash_accounts(),
    data=st.data(),
)
def test_buy(
    description: str,
    type_: SecurityTransactionType,
    security: Security,
    shares: int,
    price_per_share: Decimal,
    fees: Decimal,
    security_account: SecurityAccount,
    cash_account: CashAccount,
    data: st.DataObject,
) -> None:
    datetime_ = data.draw(
        st.datetimes(
            min_value=cash_account.initial_datetime.replace(tzinfo=None)
            + timedelta(days=1),
            timezones=st.just(tzinfo),
        )
    )
    transaction = SecurityTransaction(
        description,
        datetime_,
        type_,
        security,
        shares,
        price_per_share,
        fees,
        security_account,
        cash_account,
    )
    assert transaction.price_per_share == price_per_share
    assert transaction.shares == shares
    assert transaction.security == security
    assert transaction.security_account == security_account
    assert transaction.cash_account == cash_account
    assert (
        cash_account.balance
        == cash_account.initial_balance - shares * price_per_share - fees
    )
    assert security_account.securities[security] == shares
    assert transaction.__repr__() == (
        f"SecurityTransaction({transaction.type_.name}, "
        f"security='{transaction.security.symbol}', "
        f"shares={transaction.shares}, "
        f"{transaction.datetime_.strftime('%Y-%m-%d')})"
    )


@given(
    shares=st.integers(min_value=1, max_value=10),
    price_per_share=st.decimals(
        min_value=0, max_value=1e10, allow_infinity=False, allow_nan=False, places=3
    ),
    fees=st.decimals(
        min_value=0, max_value=1e10, allow_infinity=False, allow_nan=False, places=3
    ),
)
def test_sell(shares: int, price_per_share: Decimal, fees: Decimal) -> None:
    buy = get_buy()
    security_account = buy.security_account
    cash_account = buy.cash_account
    security = buy.security
    sell = SecurityTransaction(
        "A Sell transaction",
        datetime.now(tzinfo),
        SecurityTransactionType.SELL,
        security,
        shares,
        price_per_share,
        fees,
        security_account,
        cash_account,
    )
    assert security_account.securities[security] == buy.shares - sell.shares
    assert cash_account.balance == cash_account.initial_balance + buy.get_amount(
        cash_account
    ) + sell.get_amount(cash_account)


@given(
    type_=everything_except(SecurityTransactionType),
    security=securities(),
    security_account=security_accounts(),
    cash_account=cash_accounts(),
    data=st.data(),
)
def test_invalid_type_type(
    type_: SecurityTransactionType,
    security: Security,
    security_account: SecurityAccount,
    cash_account: CashAccount,
    data: st.DataObject,
) -> None:
    datetime_ = data.draw(
        st.datetimes(
            min_value=cash_account.initial_datetime.replace(tzinfo=None)
            + timedelta(days=1)
        )
    )
    with pytest.raises(
        TypeError, match="SecurityTransaction.type_ must be a SecurityTransactionType."
    ):
        SecurityTransaction(
            "Test description",
            datetime_,
            type_,
            security,
            1,
            Decimal("100"),
            Decimal("1"),
            security_account,
            cash_account,
        )


@given(
    type_=st.sampled_from(SecurityTransactionType),
    security=everything_except(Security),
    security_account=security_accounts(),
    cash_account=cash_accounts(),
    data=st.data(),
)
def test_invalid_security_type(
    type_: SecurityTransactionType,
    security: Security,
    security_account: SecurityAccount,
    cash_account: CashAccount,
    data: st.DataObject,
) -> None:
    datetime_ = data.draw(
        st.datetimes(
            min_value=cash_account.initial_datetime.replace(tzinfo=None)
            + timedelta(days=1)
        )
    )
    with pytest.raises(
        TypeError, match="SecurityTransaction.security must be a Security."
    ):
        SecurityTransaction(
            "Test description",
            datetime_,
            type_,
            security,
            1,
            Decimal("100"),
            Decimal("1"),
            security_account,
            cash_account,
        )


@given(
    type_=st.sampled_from(SecurityTransactionType),
    security=securities(),
    shares=everything_except(int),
    security_account=security_accounts(),
    cash_account=cash_accounts(),
    data=st.data(),
)
def test_invalid_shares_type(
    type_: SecurityTransactionType,
    security: Security,
    shares: int,
    security_account: SecurityAccount,
    cash_account: CashAccount,
    data: st.DataObject,
) -> None:
    datetime_ = data.draw(
        st.datetimes(
            min_value=cash_account.initial_datetime.replace(tzinfo=None)
            + timedelta(days=1)
        )
    )
    with pytest.raises(TypeError, match="SecurityTransaction.shares must be an int."):
        SecurityTransaction(
            "Test description",
            datetime_,
            type_,
            security,
            shares,
            Decimal("100"),
            Decimal("1"),
            security_account,
            cash_account,
        )


@given(
    type_=st.sampled_from(SecurityTransactionType),
    security=securities(),
    shares=st.integers(max_value=0),
    security_account=security_accounts(),
    cash_account=cash_accounts(),
    data=st.data(),
)
def test_invalid_shares_value(
    type_: SecurityTransactionType,
    security: Security,
    shares: int,
    security_account: SecurityAccount,
    cash_account: CashAccount,
    data: st.DataObject,
) -> None:
    datetime_ = data.draw(
        st.datetimes(
            min_value=cash_account.initial_datetime.replace(tzinfo=None)
            + timedelta(days=1)
        )
    )
    with pytest.raises(
        ValueError, match="SecurityTransaction.shares must be at least 1."
    ):
        SecurityTransaction(
            "Test description",
            datetime_,
            type_,
            security,
            shares,
            Decimal("100"),
            Decimal("1"),
            security_account,
            cash_account,
        )


@given(
    type_=st.sampled_from(SecurityTransactionType),
    security=securities(),
    security_account=everything_except(SecurityAccount),
    cash_account=cash_accounts(),
    data=st.data(),
)
def test_invalid_security_account_type(
    type_: SecurityTransactionType,
    security: Security,
    security_account: SecurityAccount,
    cash_account: CashAccount,
    data: st.DataObject,
) -> None:
    datetime_ = data.draw(
        st.datetimes(
            min_value=cash_account.initial_datetime.replace(tzinfo=None)
            + timedelta(days=1),
            timezones=st.just(tzinfo),
        )
    )
    with pytest.raises(
        TypeError,
        match="SecurityTransaction.security_account must be a SecurityAccount.",
    ):
        SecurityTransaction(
            "Test description",
            datetime_,
            type_,
            security,
            1,
            Decimal("100"),
            Decimal("1"),
            security_account,
            cash_account,
        )


@given(
    datetime_=st.datetimes(),
    type_=st.sampled_from(SecurityTransactionType),
    security=securities(),
    security_account=security_accounts(),
    cash_account=everything_except(CashAccount),
)
def test_invalid_cash_account_type(
    datetime_: datetime,
    type_: SecurityTransactionType,
    security: Security,
    security_account: SecurityAccount,
    cash_account: CashAccount,
) -> None:
    with pytest.raises(
        TypeError,
        match="SecurityTransaction.cash_account must be a CashAccount.",
    ):
        SecurityTransaction(
            "Test description",
            datetime_,
            type_,
            security,
            1,
            Decimal("100"),
            Decimal("1"),
            security_account,
            cash_account,
        )


@given(security_account=security_accounts())
def test_buy_change_security_account(security_account: SecurityAccount) -> None:
    buy = get_buy()
    security = buy.security
    old_security_account = buy.security_account
    assert buy in old_security_account.transactions
    assert old_security_account.securities[security] == buy.shares

    buy.security_account = security_account
    assert buy in security_account.transactions
    assert buy not in old_security_account.transactions
    assert old_security_account.securities[security] == 0
    assert security_account.securities[security] == buy.shares


@given(security_account=security_accounts())
def test_sell_change_security_account(security_account: SecurityAccount) -> None:
    sell = get_sell()
    security = sell.security
    old_security_account = sell.security_account
    assert sell in old_security_account.transactions
    assert old_security_account.securities[security] == -sell.shares

    sell.security_account = security_account
    assert sell in security_account.transactions
    assert sell not in old_security_account.transactions
    assert old_security_account.securities[security] == 0
    assert security_account.securities[security] == -sell.shares


@given(cash_account=cash_accounts())
def test_change_cash_account(cash_account: CashAccount) -> None:
    buy = get_buy()
    old_cash_account = buy.cash_account
    assert buy in old_cash_account.transactions

    buy.cash_account = cash_account
    assert buy in cash_account.transactions
    assert buy not in old_cash_account.transactions


def get_sell() -> SecurityTransaction:
    buy = get_buy()
    description = "A Sell transaction"
    datetime_ = datetime.now(tzinfo)
    type_ = SecurityTransactionType.SELL
    security = get_security()
    shares = 10
    price_per_share = Decimal("105.49")
    fees = Decimal("1.25")
    return SecurityTransaction(
        description,
        datetime_,
        type_,
        security,
        shares,
        price_per_share,
        fees,
        buy.security_account,
        buy.cash_account,
    )


def get_buy() -> SecurityTransaction:
    description = "A Buy transaction"
    datetime_ = datetime.now(tzinfo)
    type_ = SecurityTransactionType.BUY
    security = get_security()
    shares = 10
    price_per_share = Decimal("99.77")
    fees = Decimal("1.25")
    security_account = SecurityAccount("Interactive Brokers")
    cash_account = CashAccount(
        "Interactive Brokers EUR",
        Currency("EUR"),
        Decimal("1000"),
        datetime.now(tzinfo) - timedelta(days=7),
    )
    return SecurityTransaction(
        description,
        datetime_,
        type_,
        security,
        shares,
        price_per_share,
        fees,
        security_account,
        cash_account,
    )
