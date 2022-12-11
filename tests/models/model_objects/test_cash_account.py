from datetime import datetime, timedelta
from decimal import Decimal
from typing import Any

import pytest
from hypothesis import assume, given
from hypothesis import strategies as st

from src.models.model_objects.cash_objects import (
    CashAccount,
    CashTransaction,
    CashTransactionType,
    CashTransfer,
)
from src.models.model_objects.currency import Currency
from tests.models.composites import (
    cash_accounts,
    cash_transactions,
    cash_transfers,
    currencies,
)
from tests.models.testing_constants import max_datetime, min_datetime


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
    assert cash_account.currency == currency
    assert cash_account.balance == initial_balance
    assert cash_account.initial_balance == initial_balance
    assert cash_account.initial_datetime == initial_datetime


@given(
    name=st.text(min_size=1, max_size=32),
    currency=st.integers()
    | st.floats()
    | st.none()
    | st.datetimes()
    | st.booleans()
    | st.sampled_from([[], (), {}, set()]),
    initial_balance=st.decimals(min_value=0, allow_nan=False, allow_infinity=False),
    initial_datetime=st.datetimes(),
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
    name=st.text(min_size=1, max_size=32),
    currency=currencies(),
    initial_balance=st.integers()
    | st.floats()
    | st.none()
    | st.datetimes()
    | st.booleans()
    | st.sampled_from([[], (), {}, set()]),
    initial_datetime=st.datetimes(),
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
    name=st.text(min_size=1, max_size=32),
    currency=currencies(),
    initial_balance=st.decimals(max_value=-0.01, allow_nan=True, allow_infinity=True),
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
    initial_datetime=st.integers()
    | st.floats()
    | st.none()
    | st.text()
    | st.booleans()
    | st.sampled_from([[], (), {}, set()]),
)
def test_initial_datetime_invalid_type(
    name: str, currency: Currency, initial_balance: Decimal, initial_datetime: Any
) -> None:
    with pytest.raises(
        TypeError, match="CashAccount.initial_datetime must be a datetime."
    ):
        CashAccount(name, currency, initial_balance, initial_datetime)


@given(
    account=cash_accounts(max_datetime=max_datetime),
    transaction=cash_transactions(min_datetime=min_datetime),
    transfer=cash_transfers(min_datetime=min_datetime),
    sender_bool=st.booleans(),
)
def test_get_proper_list(
    account: CashAccount,
    transaction: CashTransaction,
    transfer: CashTransfer,
    sender_bool: bool,
) -> None:
    transaction.account = account
    if sender_bool:
        transfer.account_sender = account
    else:
        transfer.account_recipient = account

    expected_list_transaction = (
        account._income_list
        if transaction.type_ == CashTransactionType.INCOME
        else account._expense_list
    )
    expected_list_transfer = (
        account._transfers_received_list
        if not sender_bool
        else account._transfers_sent_list
    )
    account._validate_transaction(transaction)
    account._validate_transaction(transfer)
    result_transaction = account._get_proper_list(transaction)
    result_transfer = account._get_proper_list(transfer)

    assert result_transaction == expected_list_transaction
    assert result_transfer == expected_list_transfer


@given(
    account=cash_accounts(max_datetime=max_datetime),
    transaction=st.integers()
    | st.floats()
    | st.none()
    | st.text()
    | st.booleans()
    | st.sampled_from([[], (), {}, set()]),
)
def test_validate_transaction_invalid_type(
    account: CashAccount, transaction: Any
) -> None:
    with pytest.raises(
        TypeError,
        match="Argument transaction must be a CashTransaction or a CashTransfer.",
    ):
        account._validate_transaction(transaction)


@given(
    account=cash_accounts(max_datetime=max_datetime),
    transaction=cash_transactions(min_datetime=min_datetime),
    transfer=cash_transfers(min_datetime=min_datetime),
)
def test_validate_transaction_invalid_account(
    account: CashAccount, transaction: CashTransaction, transfer: CashTransfer
) -> None:
    assume(transaction.account != account)
    assume(transfer.account_recipient != account and transfer.account_sender != account)

    with pytest.raises(
        ValueError,
        match="This CashAccount is not related to the provided CashTransaction.",
    ):
        account._validate_transaction(transaction)
    with pytest.raises(
        ValueError,
        match="This CashAccount is not related to the provided CashTransfer.",
    ):
        account._validate_transaction(transfer)


@given(
    account=cash_accounts(max_datetime=max_datetime),
    transaction=cash_transactions(min_datetime=min_datetime),
    transfer=cash_transfers(min_datetime=min_datetime),
    data=st.data(),
)
def test_validate_transaction_invalid_datetime(
    account: CashAccount,
    transaction: CashTransaction,
    transfer: CashTransfer,
    data: st.DrawFn,
) -> None:
    transaction._account = account
    invalid_datetime = data.draw(
        st.datetimes(max_value=account.initial_datetime - timedelta(seconds=1))
    )
    transaction._datetime = invalid_datetime
    transfer._datetime = invalid_datetime

    with pytest.raises(
        ValueError,
        match="The provided CashTransaction precedes this CashAccount.initial_datetime",
    ):
        account._validate_transaction(transaction)
    with pytest.raises(
        ValueError,
        match="The provided CashTransfer precedes this CashAccount.initial_datetime.",
    ):
        account._validate_transaction(transfer)


@given(
    account=cash_accounts(max_datetime=max_datetime),
    transactions=st.lists(
        cash_transactions(min_datetime=min_datetime), min_size=1, max_size=10
    ),
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
