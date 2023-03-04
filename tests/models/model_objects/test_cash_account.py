from datetime import datetime, timedelta
from decimal import Decimal
from typing import Any

import pytest
from hypothesis import assume, given
from hypothesis import strategies as st

from src.models.custom_exceptions import AlreadyExistsError
from src.models.model_objects.cash_objects import (
    CashAccount,
    CashTransaction,
    CashTransactionType,
    CashTransfer,
    UnrelatedAccountError,
)
from src.models.model_objects.currency_objects import (
    CashAmount,
    Currency,
    CurrencyError,
)
from tests.models.test_assets.composites import (
    cash_accounts,
    cash_amounts,
    cash_transactions,
    cash_transfers,
    currencies,
    everything_except,
    names,
    valid_decimals,
)


@given(
    name=names(),
    currency=currencies(),
    initial_balance=valid_decimals(min_value=0),
)
def test_creation(
    name: str,
    currency: Currency,
    initial_balance: Decimal,
) -> None:
    initial_amount = CashAmount(initial_balance, currency)
    cash_account = CashAccount(name, currency, initial_amount)
    assert cash_account.name == name
    assert cash_account.path == name
    assert cash_account.__repr__() == f"CashAccount('{name}')"
    assert cash_account.currency == currency
    assert cash_account.get_balance(currency) == initial_amount
    assert cash_account.initial_balance == initial_amount


@given(
    name=st.just("Valid Name"),
    currency=everything_except(Currency),
    initial_balance=st.just(None),
)
def test_currency_incorrect_type(
    name: str,
    currency: Any,
    initial_balance: Decimal,
) -> None:
    with pytest.raises(TypeError, match="CashAccount.currency must be a Currency."):
        CashAccount(name, currency, initial_balance)


@given(cash_account=cash_accounts())
def test_initial_balance_same_value(cash_account: CashAccount) -> None:
    prev_balance = cash_account.initial_balance
    cash_account.initial_balance = prev_balance
    assert cash_account.initial_balance == prev_balance


@given(
    name=st.just("Valid Name"),
    currency=currencies(),
    initial_balance=everything_except(CashAmount),
)
def test_initial_balance_invalid_type(
    name: str,
    currency: Currency,
    initial_balance: Any,
) -> None:
    with pytest.raises(
        TypeError, match="CashAccount.initial_balance must be a CashAmount."
    ):
        CashAccount(name, currency, initial_balance)


@given(
    name=st.just("Valid Name"),
    currency=currencies(),
    invalid_currency=currencies(),
    data=st.data(),
)
def test_initial_balance_invalid_currency(
    name: str,
    currency: Currency,
    invalid_currency: Currency,
    data: st.DataObject,
) -> None:
    assume(currency != invalid_currency)
    initial_balance = data.draw(cash_amounts(invalid_currency))
    with pytest.raises(CurrencyError):
        CashAccount(name, currency, initial_balance)


@given(
    account=cash_accounts(),
    transaction=everything_except((CashTransaction, CashTransfer)),
)
def test_validate_transaction_invalid_type(
    account: CashAccount, transaction: Any
) -> None:
    with pytest.raises(
        TypeError,
        match="Parameter 'transaction' must be a",
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
    assume(transfer.recipient != account and transfer.sender != account)

    with pytest.raises(UnrelatedAccountError):
        account._validate_transaction(transaction)
    with pytest.raises(UnrelatedAccountError):
        account._validate_transaction(transfer)


@given(currency=currencies(), data=st.data())
def test_get_balance(currency: Currency, data: st.DataObject) -> None:
    account = data.draw(cash_accounts(currency=currency))
    transactions = data.draw(
        st.lists(
            cash_transactions(currency=currency, account=account),
            min_size=1,
            max_size=5,
        )
    )
    oldest_datetime = min(transaction.datetime_ for transaction in transactions)
    datetime_balance_list: list[tuple[datetime, CashAmount]] = [
        (oldest_datetime - timedelta(days=1), account.initial_balance)
    ]
    transactions.sort(key=lambda transaction: transaction.datetime_)
    for transaction in transactions:
        if transaction.type_ == CashTransactionType.INCOME:
            next_balance = datetime_balance_list[-1][1] + transaction.amount
        else:
            next_balance = datetime_balance_list[-1][1] - transaction.amount
        datetime_balance_list.append((transaction.datetime_, next_balance))

    assert datetime_balance_list[-1][1] == account.get_balance(currency)
    assert set(datetime_balance_list) == set(account.balance_history)


@given(transaction=cash_transactions())
def test_add_transaction_already_exists(transaction: CashTransaction) -> None:
    account = transaction.account
    with pytest.raises(AlreadyExistsError):
        account.add_transaction(transaction)
