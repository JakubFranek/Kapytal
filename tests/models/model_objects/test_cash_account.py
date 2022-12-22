from datetime import datetime, timedelta
from decimal import Decimal
from typing import Any

import pytest
from hypothesis import assume, given
from hypothesis import strategies as st

from src.models.constants import tzinfo
from src.models.model_objects.cash_objects import (
    CashAccount,
    CashTransaction,
    CashTransactionType,
    CashTransfer,
    TransactionPrecedesAccountError,
    UnrelatedAccountError,
)
from src.models.model_objects.currency import Currency
from tests.models.test_assets.composites import (
    cash_accounts,
    cash_transactions,
    cash_transfers,
    currencies,
    everything_except,
)


@given(
    name=st.text(min_size=1, max_size=32),
    currency=currencies(),
    initial_balance=st.decimals(min_value=0, allow_nan=False, allow_infinity=False),
    initial_datetime=st.datetimes(),
)
def test_creation(
    name: str,
    currency: Currency,
    initial_balance: Decimal,
    initial_datetime: datetime,
) -> None:
    cash_account = CashAccount(name, currency, initial_balance, initial_datetime)
    assert cash_account.name == name
    assert cash_account.path == name
    assert (
        cash_account.__repr__()
        == f"CashAccount('{name}', currency='{cash_account.currency.code}')"
    )
    assert cash_account.currency == currency
    assert cash_account.balance == initial_balance
    assert cash_account.initial_balance == initial_balance
    assert cash_account.initial_datetime == initial_datetime


@given(
    name=st.just("Valid Name"),
    currency=everything_except(Currency),
    initial_balance=st.just(Decimal(0)),
    initial_datetime=st.just(datetime.now(tzinfo)),
)
def test_currency_incorrect_type(
    name: str,
    currency: Any,
    initial_balance: Decimal,
    initial_datetime: datetime,
) -> None:
    with pytest.raises(TypeError, match="CashAccount.currency must be a Currency."):
        CashAccount(name, currency, initial_balance, initial_datetime)


@given(
    name=st.just("Valid Name"),
    currency=currencies(),
    initial_balance=everything_except(Decimal),
    initial_datetime=st.just(datetime.now(tzinfo)),
)
def test_initial_balance_invalid_type(
    name: str,
    currency: Currency,
    initial_balance: Any,
    initial_datetime: datetime,
) -> None:
    with pytest.raises(
        TypeError, match="CashAccount.initial_balance must be a Decimal."
    ):
        CashAccount(name, currency, initial_balance, initial_datetime)


@given(
    name=st.just("Valid Name"),
    currency=currencies(),
    initial_balance=st.decimals(max_value="-0.01", allow_nan=True, allow_infinity=True),
    initial_datetime=st.datetimes(),
)
def test_initial_balance_invalid_values(
    name: str,
    currency: Currency,
    initial_balance: Decimal,
    initial_datetime: datetime,
) -> None:
    with pytest.raises(
        ValueError, match="CashAccount.initial_balance must be positive and finite."
    ):
        CashAccount(name, currency, initial_balance, initial_datetime)


@given(
    name=st.text(min_size=1, max_size=32),
    currency=currencies(),
    initial_balance=st.decimals(min_value=0, allow_nan=False, allow_infinity=False),
    initial_datetime=everything_except(datetime),
)
def test_initial_datetime_invalid_type(
    name: str, currency: Currency, initial_balance: Decimal, initial_datetime: Any
) -> None:
    with pytest.raises(
        TypeError, match="CashAccount.initial_datetime must be a datetime."
    ):
        CashAccount(name, currency, initial_balance, initial_datetime)


@given(
    account=cash_accounts(),
    transaction=everything_except((CashTransaction, CashTransfer)),
)
def test_validate_transaction_invalid_type(
    account: CashAccount, transaction: Any
) -> None:
    with pytest.raises(
        TypeError,
        match="Argument 'transaction' must be a",
    ):
        account._validate_transaction(transaction)


@given(
    account=cash_accounts(),
    transaction=cash_transactions(),
    transfer=cash_transfers(),
)
def test_validate_transaction_invalid_account(
    account: CashAccount, transaction: CashTransaction, transfer: CashTransfer
) -> None:
    assume(transaction.account != account)
    assume(transfer.account_recipient != account and transfer.account_sender != account)

    with pytest.raises(UnrelatedAccountError):
        account._validate_transaction(transaction)
    with pytest.raises(UnrelatedAccountError):
        account._validate_transaction(transfer)


@given(
    account=cash_accounts(),
    transaction=cash_transactions(),
    transfer=cash_transfers(),
    data=st.data(),
    switch=st.booleans(),
)
def test_validate_transaction_invalid_datetime(
    account: CashAccount,
    transaction: CashTransaction,
    transfer: CashTransfer,
    data: st.DataObject,
    switch: bool,
) -> None:
    transaction._account = account
    if switch:
        transfer._account_recipient = account
    else:
        transfer._account_sender = account
    invalid_datetime = data.draw(
        st.datetimes(
            max_value=account.initial_datetime.replace(tzinfo=None)
            - timedelta(seconds=1),
            timezones=st.just(tzinfo),
        )
    )
    transaction._datetime = invalid_datetime
    transfer._datetime = invalid_datetime

    with pytest.raises(TransactionPrecedesAccountError):
        account._validate_transaction(transaction)
    with pytest.raises(TransactionPrecedesAccountError):
        account._validate_transaction(transfer)


@given(
    account=cash_accounts(),
    transactions=st.lists(cash_transactions(), min_size=1, max_size=5),
)
def test_balance(account: CashAccount, transactions: list[CashTransaction]) -> None:
    datetime_balance_list = [(account.initial_datetime, account.initial_balance)]
    transactions.sort(key=lambda transaction: transaction.datetime_)
    for transaction in transactions:
        transaction.account = account
        if transaction.type_ == CashTransactionType.INCOME:
            next_balance = datetime_balance_list[-1][1] + transaction.amount
        else:
            next_balance = datetime_balance_list[-1][1] - transaction.amount
        datetime_balance_list.append((transaction.datetime_, next_balance))

    assert datetime_balance_list[-1][1] == account.balance
    assert set(datetime_balance_list) == set(account.balance_history)
