from datetime import datetime
from decimal import Decimal, InvalidOperation
from types import NoneType
from typing import Any

import pytest
from hypothesis import assume, given
from hypothesis import strategies as st
from src.models.base_classes.account import UnrelatedAccountError
from src.models.model_objects.cash_objects import CashAccount
from src.models.model_objects.currency_objects import (
    CashAmount,
    Currency,
    CurrencyError,
)
from src.models.model_objects.security_objects import (
    Security,
    SecurityAccount,
    SecurityTransaction,
    SecurityTransactionType,
)
from src.models.user_settings import user_settings
from tests.models.test_assets.composites import (
    cash_accounts,
    cash_amounts,
    everything_except,
    securities,
    security_accounts,
    share_decimals,
)


@given(
    description=st.text(min_size=1, max_size=256),
    type_=st.just(SecurityTransactionType.BUY),
    security_account=security_accounts(),
    cash_account=cash_accounts(),
    data=st.data(),
)
def test_buy(
    description: str,
    type_: SecurityTransactionType,
    security_account: SecurityAccount,
    cash_account: CashAccount,
    data: st.DataObject,
) -> None:
    currency = cash_account.currency
    price_per_share = data.draw(
        cash_amounts(currency=currency, min_value=0, max_value=1e6)
    )
    security = data.draw(securities(cash_account.currency))
    shares = data.draw(share_decimals(decimals=security.shares_decimals))
    datetime_ = data.draw(
        st.datetimes(
            timezones=st.just(user_settings.settings.time_zone),
        )
    )
    transaction = SecurityTransaction(
        description,
        datetime_,
        type_,
        security,
        shares,
        price_per_share,
        security_account,
        cash_account,
    )
    assert transaction.price_per_share == price_per_share
    assert transaction.shares == shares
    assert transaction.security == security
    assert transaction.security_account == security_account
    assert transaction.cash_account == cash_account
    assert transaction.currency == cash_account.currency
    assert transaction.currencies == (cash_account.currency,)
    assert (
        cash_account.get_balance(currency)
        == cash_account.initial_balance - shares * price_per_share
    )
    assert security_account.securities[security] == shares
    assert transaction.__repr__() == (
        f"SecurityTransaction({transaction.type_.name}, "
        f"security='{transaction.security.symbol}', "
        f"shares={transaction.shares}, "
        f"{transaction.datetime_.strftime('%Y-%m-%d')})"
    )


@given(
    data=st.data(),
)
def test_sell(data: st.DataObject) -> None:
    buy = get_buy()
    security = buy.security
    shares = data.draw(share_decimals(decimals=security.shares_decimals))
    currency = security.currency
    price_per_share = data.draw(cash_amounts(currency=currency, min_value=0))
    security_account = buy.security_account
    cash_account = buy.cash_account

    sell = SecurityTransaction(
        "A Sell transaction",
        datetime.now(user_settings.settings.time_zone),
        SecurityTransactionType.SELL,
        security,
        shares,
        price_per_share,
        security_account,
        cash_account,
    )
    assert security_account.securities[security] == buy.shares - sell.shares
    assert cash_account.get_balance(
        currency
    ) == cash_account.initial_balance + buy.get_amount(cash_account) + sell.get_amount(
        cash_account
    )


@given(
    type_=everything_except((SecurityTransactionType, NoneType)),
    security=securities(),
    security_account=security_accounts(),
    cash_account=cash_accounts(),
    datetime_=st.datetimes(timezones=st.just(user_settings.settings.time_zone)),
    data=st.data(),
)
def test_invalid_type_type(  # noqa: PLR0913
    type_: SecurityTransactionType,
    security: Security,
    security_account: SecurityAccount,
    cash_account: CashAccount,
    datetime_: datetime,
    data: st.DataObject,
) -> None:
    shares = data.draw(share_decimals(decimals=security.shares_decimals))

    with pytest.raises(
        TypeError, match="SecurityTransaction.type_ must be a SecurityTransactionType."
    ):
        SecurityTransaction(
            "Test description",
            datetime_,
            type_,
            security,
            shares,
            Decimal("100"),
            security_account,
            cash_account,
        )


@given(
    type_=st.sampled_from(SecurityTransactionType),
    security=everything_except((Security, NoneType)),
    security_account=security_accounts(),
    cash_account=cash_accounts(),
    datetime_=st.datetimes(timezones=st.just(user_settings.settings.time_zone)),
)
def test_invalid_security_type(
    type_: SecurityTransactionType,
    security: Security,
    security_account: SecurityAccount,
    cash_account: CashAccount,
    datetime_: datetime,
) -> None:
    with pytest.raises(
        TypeError, match="SecurityTransaction.security must be a Security."
    ):
        SecurityTransaction(
            "Test description",
            datetime_,
            type_,
            security,
            Decimal("1"),
            Decimal("100"),
            security_account,
            cash_account,
        )


@given(
    type_=st.sampled_from(SecurityTransactionType),
    security=securities(),
    shares=everything_except((Decimal, str, int, NoneType)),
    security_account=security_accounts(),
    cash_account=cash_accounts(),
    datetime_=st.datetimes(timezones=st.just(user_settings.settings.time_zone)),
)
def test_invalid_shares_type(  # noqa: PLR0913
    type_: SecurityTransactionType,
    security: Security,
    shares: Decimal,
    security_account: SecurityAccount,
    cash_account: CashAccount,
    datetime_: datetime,
) -> None:
    with pytest.raises(
        TypeError, match="SecurityTransaction.shares must be a Decimal."
    ):
        SecurityTransaction(
            "Test description",
            datetime_,
            type_,
            security,
            shares,
            Decimal("100"),
            security_account,
            cash_account,
        )


@given(
    type_=st.sampled_from(SecurityTransactionType),
    security=securities(),
    shares=st.text(),
    security_account=security_accounts(),
    cash_account=cash_accounts(),
    datetime_=st.datetimes(timezones=st.just(user_settings.settings.time_zone)),
)
def test_invalid_shares_str_value(  # noqa: PLR0913
    type_: SecurityTransactionType,
    security: Security,
    shares: str,
    security_account: SecurityAccount,
    cash_account: CashAccount,
    datetime_: datetime,
) -> None:
    try:
        Decimal(shares)
    except InvalidOperation:
        with pytest.raises(InvalidOperation):
            SecurityTransaction(
                "Test description",
                datetime_,
                type_,
                security,
                shares,
                Decimal("100"),
                security_account,
                cash_account,
            )


@given(
    type_=st.sampled_from(SecurityTransactionType),
    security=securities(),
    shares=st.decimals(max_value=0),
    security_account=security_accounts(),
    cash_account=cash_accounts(),
    datetime_=st.datetimes(timezones=st.just(user_settings.settings.time_zone)),
)
def test_invalid_shares_value(  # noqa: PLR0913
    type_: SecurityTransactionType,
    security: Security,
    shares: int,
    security_account: SecurityAccount,
    cash_account: CashAccount,
    datetime_: datetime,
) -> None:
    with pytest.raises(
        ValueError,
        match="must be a finite positive number.",
    ):
        SecurityTransaction(
            "Test description",
            datetime_,
            type_,
            security,
            shares,
            CashAmount("1000", security.currency),
            security_account,
            cash_account,
        )


@given(
    type_=st.sampled_from(SecurityTransactionType),
    security=securities(),
    security_account=security_accounts(),
    cash_account=cash_accounts(),
    datetime_=st.datetimes(timezones=st.just(user_settings.settings.time_zone)),
    data=st.data(),
)
def test_invalid_shares_decimals(  # noqa: PLR0913
    type_: SecurityTransactionType,
    security: Security,
    security_account: SecurityAccount,
    cash_account: CashAccount,
    datetime_: datetime,
    data: st.DataObject,
) -> None:
    shares = data.draw(st.integers(min_value=1)) * Decimal(
        10 ** (-security.shares_decimals - 1)
    )

    with pytest.raises(
        ValueError,
        match=".shares must have maximum",
    ):
        SecurityTransaction(
            "Test description",
            datetime_,
            type_,
            security,
            shares,
            CashAmount("1000", security.currency),
            security_account,
            cash_account,
        )


@given(
    type_=st.sampled_from(SecurityTransactionType),
    security=securities(),
    security_account=security_accounts(),
    datetime_=st.datetimes(
        min_value=datetime(1900, 1, 1),  # noqa: DTZ001
        timezones=st.just(user_settings.settings.time_zone),
    ),
    data=st.data(),
)
def test_valid_shares_unit_str(
    type_: SecurityTransactionType,
    security: Security,
    security_account: SecurityAccount,
    datetime_: datetime,
    data: st.DataObject,
) -> None:
    cash_account = data.draw(cash_accounts(currency=security.currency))
    shares = data.draw(share_decimals(decimals=security.shares_decimals))
    SecurityTransaction(
        "Test description",
        datetime_,
        type_,
        security,
        shares,
        CashAmount("1000", security.currency),
        security_account,
        cash_account,
    )


@given(
    type_=st.sampled_from(SecurityTransactionType),
    security_account=everything_except((SecurityAccount, NoneType)),
    cash_account=cash_accounts(),
    datetime_=st.datetimes(timezones=st.just(user_settings.settings.time_zone)),
    data=st.data(),
)
def test_invalid_security_account_type(
    type_: SecurityTransactionType,
    security_account: SecurityAccount,
    cash_account: CashAccount,
    datetime_: datetime,
    data: st.DataObject,
) -> None:
    currency = cash_account.currency
    security = data.draw(securities(currency=currency))
    shares = data.draw(share_decimals(decimals=security.shares_decimals))
    with pytest.raises(
        TypeError,
        match="SecurityTransaction.security_account must be a SecurityAccount.",
    ):
        SecurityTransaction(
            "Test description",
            datetime_,
            type_,
            security,
            shares,
            CashAmount("100", currency),
            security_account,
            cash_account,
        )


@given(
    datetime_=st.datetimes(),
    type_=st.sampled_from(SecurityTransactionType),
    security=securities(),
    security_account=security_accounts(),
    cash_account=everything_except((CashAccount, NoneType)),
    data=st.data(),
)
def test_invalid_cash_account_type(  # noqa: PLR0913
    datetime_: datetime,
    type_: SecurityTransactionType,
    security: Security,
    security_account: SecurityAccount,
    cash_account: CashAccount,
    data: st.DataObject,
) -> None:
    currency = security.currency
    shares = data.draw(share_decimals(decimals=security.shares_decimals))
    with pytest.raises(
        TypeError,
        match="SecurityTransaction.cash_account must be a CashAccount.",
    ):
        SecurityTransaction(
            "Test description",
            datetime_,
            type_,
            security,
            shares,
            CashAmount("100", currency),
            security_account,
            cash_account,
        )


@given(
    datetime_=st.datetimes(),
    type_=st.sampled_from(SecurityTransactionType),
    security=securities(),
    security_account=security_accounts(),
    price_per_share=everything_except((CashAmount, NoneType)),
    data=st.data(),
)
def test_invalid_price_per_share_type(  # noqa: PLR0913
    datetime_: datetime,
    type_: SecurityTransactionType,
    security: Security,
    security_account: SecurityAccount,
    price_per_share: Any,
    data: st.DataObject,
) -> None:
    currency = security.currency
    cash_account = data.draw(cash_accounts(currency=currency))
    shares = data.draw(share_decimals(decimals=security.shares_decimals))
    with pytest.raises(
        TypeError,
        match="SecurityTransaction amounts must be CashAmounts.",
    ):
        SecurityTransaction(
            "Test description",
            datetime_,
            type_,
            security,
            shares,
            price_per_share,
            security_account,
            cash_account,
        )


@given(
    datetime_=st.datetimes(),
    type_=st.sampled_from(SecurityTransactionType),
    security_account=security_accounts(),
    cash_account=cash_accounts(),
    data=st.data(),
)
def test_invalid_cash_account_currency(
    datetime_: datetime,
    type_: SecurityTransactionType,
    security_account: SecurityAccount,
    cash_account: CashAccount,
    data: st.DataObject,
) -> None:
    security = get_security()
    assume(cash_account.currency != security.currency)
    currency = security.currency
    shares = data.draw(st.integers(min_value=1, max_value=1e10))

    with pytest.raises(CurrencyError):
        SecurityTransaction(
            "Test description",
            datetime_,
            type_,
            security,
            shares,
            CashAmount("100", currency),
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

    buy.set_attributes(security_account=security_account)
    assert buy in security_account.transactions
    assert buy not in old_security_account.transactions
    assert security not in old_security_account.securities
    assert security_account.securities[security] == buy.shares


@given(security_account=security_accounts())
def test_sell_change_security_account(security_account: SecurityAccount) -> None:
    buy = get_buy()
    sell = get_sell()
    security = sell.security
    old_security_account = sell.security_account
    assert sell in old_security_account.transactions
    expected_shares = buy.shares - sell.shares
    if expected_shares != 0:
        assert old_security_account.securities[security] == expected_shares
    else:
        assert security not in old_security_account.securities

    sell.set_attributes(security_account=security_account)
    assert sell in security_account.transactions
    assert sell not in old_security_account.transactions
    assert old_security_account.securities[security] == buy.shares
    assert security_account.securities[security] == -sell.shares


@given(data=st.data())
def test_change_cash_account(data: st.DataObject) -> None:
    buy = get_buy()
    cash_account = data.draw(cash_accounts(currency=buy.security.currency))
    old_cash_account = buy.cash_account
    assert buy in old_cash_account.transactions

    buy.set_attributes(cash_account=cash_account)
    assert buy in cash_account.transactions
    assert buy not in old_cash_account.transactions


@given(account=everything_except(SecurityAccount))
def test_get_shares_invalid_account_type(account: Any) -> None:
    transaction = get_buy()
    with pytest.raises(
        TypeError, match="Parameter 'account' must be a SecurityAccount."
    ):
        transaction.get_shares(account)


@given(account=security_accounts())
def test_get_shares_unrelated_account(account: Any) -> None:
    transaction = get_buy()
    with pytest.raises(UnrelatedAccountError):
        transaction.get_shares(account)


def test_validate_attributes_same_values() -> None:
    transaction = get_buy()
    transaction.validate_attributes()


@given(data=st.data())
def test_set_attributes_invalid_amount_value(data: st.DataObject) -> None:
    transaction = get_buy()
    amount = data.draw(
        cash_amounts(max_value=-0.01, currency=transaction.cash_account.currency)
    )
    with pytest.raises(
        ValueError, match="SecurityTransaction amounts must not be negative."
    ):
        transaction.set_attributes(price_per_share=amount)


@given(data=st.data())
def test_set_attributes_invalid_amount_currency(data: st.DataObject) -> None:
    transaction = get_buy()
    amount = data.draw(cash_amounts(min_value=0.01))
    assume(amount.currency != transaction.cash_account.currency)
    with pytest.raises(CurrencyError):
        transaction.set_attributes(price_per_share=amount)


@given(
    unrelated_cash_account=cash_accounts(),
    unrelated_security_account=security_accounts(),
)
def test_is_accounts_related(
    unrelated_cash_account: CashAccount, unrelated_security_account: SecurityAccount
) -> None:
    transaction = get_buy()
    related_accounts = (
        transaction.cash_account,
        unrelated_cash_account,
        unrelated_security_account,
    )
    assert transaction.is_accounts_related(related_accounts)
    related_accounts = (
        transaction.security_account,
        unrelated_cash_account,
        unrelated_security_account,
    )
    assert transaction.is_accounts_related(related_accounts)
    unrelated_accounts = (unrelated_cash_account, unrelated_security_account)
    assert not transaction.is_accounts_related(unrelated_accounts)


def get_sell() -> SecurityTransaction:
    buy = get_buy()
    description = "A Sell transaction"
    datetime_ = datetime.now(user_settings.settings.time_zone)
    type_ = SecurityTransactionType.SELL
    security = buy.security
    shares = Decimal("10")
    price_per_share = CashAmount("105.49", security.currency)
    return SecurityTransaction(
        description,
        datetime_,
        type_,
        security,
        shares,
        price_per_share,
        buy.security_account,
        buy.cash_account,
    )


def get_buy() -> SecurityTransaction:
    description = "A Buy transaction"
    datetime_ = datetime.now(user_settings.settings.time_zone)
    type_ = SecurityTransactionType.BUY
    security = get_security()
    shares = 10
    price_per_share = CashAmount("99.77", security.currency)
    security_account = SecurityAccount("Interactive Brokers")
    cash_account = CashAccount(
        "Interactive Brokers EUR",
        security.currency,
        CashAmount("1000", security.currency),
    )
    return SecurityTransaction(
        description,
        datetime_,
        type_,
        security,
        shares,
        price_per_share,
        security_account,
        cash_account,
    )


def get_security() -> Security:
    return Security(
        "Vanguard FTSE All-World UCITS ETF USD Acc",
        "VWCE.DE",
        "ETF",
        Currency("EUR", 2),
        1,
    )
