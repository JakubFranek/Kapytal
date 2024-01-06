from datetime import datetime, timedelta
from decimal import Decimal
from typing import Any

import pytest
from hypothesis import assume, given
from hypothesis import strategies as st
from src.models.custom_exceptions import AlreadyExistsError
from src.models.model_objects.account_group import AccountGroup
from src.models.model_objects.cash_objects import (
    CashAccount,
    CashRelatedTransaction,
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
from src.models.user_settings import user_settings
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
    assert cash_account.__repr__() == f"CashAccount({name})"
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
    name=st.just("Valid Name"),
    currency=currencies(),
    data=st.data(),
)
def test_initial_balance_invalid_value(
    name: str,
    currency: Currency,
    data: st.DataObject,
) -> None:
    initial_balance = data.draw(cash_amounts(currency, max_value=-1))
    with pytest.raises(
        ValueError, match="CashAccount.initial_balance must not be negative."
    ):
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
    assume(account not in transfer.accounts)

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
    datetime_balance_list: list[
        tuple[datetime, CashAmount, CashRelatedTransaction | None]
    ] = [(oldest_datetime - timedelta(days=1), account.initial_balance, None)]
    transactions.sort(key=lambda transaction: transaction.datetime_)
    for transaction in transactions:
        if transaction.type_ == CashTransactionType.INCOME:
            next_balance = datetime_balance_list[-1][1] + transaction.amount
        else:
            next_balance = datetime_balance_list[-1][1] - transaction.amount
        datetime_balance_list.append((transaction.datetime_, next_balance, transaction))

    assert datetime_balance_list[-1][1] == account.get_balance(currency)
    assert set(datetime_balance_list) == set(account.balance_history)


@given(currency=currencies(), data=st.data())
def test_get_balance_after_transaction(currency: Currency, data: st.DataObject) -> None:
    account = data.draw(cash_accounts(currency=currency))
    transaction_1 = data.draw(cash_transactions(currency=currency, account=account))

    balance_after_1 = account.get_balance_after_transaction(currency, transaction_1)

    assert balance_after_1 == account.get_balance(currency)

    transaction_2 = data.draw(cash_transactions(currency=currency, account=account))

    assume(transaction_2.datetime_ > transaction_1.datetime_)

    balance_after_1_new = account.get_balance_after_transaction(currency, transaction_1)
    balance_after_2 = account.get_balance_after_transaction(currency, transaction_2)

    assert balance_after_1 == balance_after_1_new
    assert balance_after_2 == account.get_balance(currency)


@given(transaction=cash_transactions())
def test_add_transaction_already_exists(transaction: CashTransaction) -> None:
    account = transaction.account
    with pytest.raises(AlreadyExistsError):
        account.add_transaction(transaction)


@given(currency=currencies(), data=st.data())
def test_get_balance_with_date(
    currency: Currency,
    data: st.DataObject,
) -> None:
    account = data.draw(cash_accounts(currency=currency))
    t1 = data.draw(cash_transactions(currency=currency, account=account))
    t2 = data.draw(cash_transactions(currency=currency, account=account))
    t3 = data.draw(cash_transactions(currency=currency, account=account))
    t1._datetime = datetime.now(user_settings.settings.time_zone) - timedelta(days=2)
    t2._datetime = datetime.now(user_settings.settings.time_zone) - timedelta(days=1)
    t3._datetime = datetime.now(user_settings.settings.time_zone)
    t1._timestamp = t1._datetime.timestamp()
    t2._timestamp = t2._datetime.timestamp()
    t3._timestamp = t3._datetime.timestamp()
    transactions = [t1, t2, t3]
    account.update_balance()
    transaction_sum_3 = sum(
        (t.get_amount(account) for t in transactions), start=currency.zero_amount
    )
    transaction_sum_2 = sum(
        (t.get_amount(account) for t in transactions[:-1]), start=currency.zero_amount
    )
    transaction_sum_1 = sum(
        (t.get_amount(account) for t in transactions[:-2]), start=currency.zero_amount
    )

    latest_balance = account.get_balance(currency)
    balance_3 = account.get_balance(currency, t3.date_)
    balance_2 = account.get_balance(currency, t2.date_)
    balance_1 = account.get_balance(currency, t1.date_)
    balance_0 = account.get_balance(currency, t1.date_ - timedelta(days=1))
    balance_m1 = account.get_balance(currency, t1.date_ - timedelta(days=2))
    assert latest_balance == account.initial_balance + transaction_sum_3
    assert balance_3 == latest_balance
    assert balance_2 == account.initial_balance + transaction_sum_2
    assert balance_1 == account.initial_balance + transaction_sum_1
    assert balance_0 == account.initial_balance
    assert balance_m1 == currency.zero_amount


def test_parent_change_balance_update() -> None:
    amount = 100
    currency = Currency("USD", 2)
    parent_1 = AccountGroup("Parent 1")
    parent_2 = AccountGroup("Parent 2")
    cash_account = CashAccount(
        "Cash Account",
        currency,
        parent=parent_1,
        initial_balance=CashAmount(amount, currency),
    )
    CashAccount(
        "Dummy",
        currency,
        parent=parent_2,
        initial_balance=currency.zero_amount,
    )

    assert cash_account.get_balance(currency).value_normalized == amount
    assert parent_1.get_balance(currency).value_normalized == amount
    assert parent_2.get_balance(currency).value_normalized == 0

    cash_account.parent = parent_2
    parent_2.set_child_index(cash_account, 0)

    assert cash_account.get_balance(currency).value_normalized == amount
    assert parent_1.get_balance(currency).value_normalized == 0
    assert parent_2.get_balance(currency).value_normalized == amount
