from datetime import datetime
from decimal import Decimal
from typing import Any

import pytest
from hypothesis import assume, given
from hypothesis import strategies as st

from src.models.constants import tzinfo
from src.models.model_objects.attributes import Attribute, Category
from src.models.model_objects.cash_objects import (
    CashAccount,
    CashTransaction,
    CashTransactionType,
)
from tests.models.composites import (
    attributes,
    cash_accounts,
    cash_transactions,
    categories,
)
from tests.models.testing_constants import min_datetime


@given(
    description=st.text(min_size=0, max_size=256),
    datetime_=st.datetimes(min_value=min_datetime),
    type_=st.sampled_from(CashTransactionType),
    account=cash_accounts(),
    amount=st.decimals(min_value=0.01, allow_infinity=False, allow_nan=False),
    payee=attributes(),
    category=categories(),
    tags=st.lists(attributes()),
)
def test_creation(  # noqa: CFQ002,TMN001
    description: str,
    datetime_: datetime,
    type_: CashTransactionType,
    account: CashAccount,
    amount: Decimal,
    payee: Attribute,
    category: Category,
    tags: list[Attribute],
) -> None:
    account_currency = account.currency
    dt_start = datetime.now(tzinfo)
    cash_transaction = CashTransaction(
        description, datetime_, type_, account, amount, payee, category, tags
    )

    dt_created_diff = cash_transaction.datetime_created - dt_start
    dt_edited_diff = cash_transaction.datetime_edited - dt_start

    assert cash_transaction.description == description
    assert cash_transaction.datetime_ == datetime_
    assert cash_transaction.type_ == type_
    assert cash_transaction.account == account
    assert cash_transaction.amount == amount
    assert cash_transaction.currency == account_currency
    assert cash_transaction.category == category
    assert cash_transaction.payee == payee
    assert cash_transaction.tags == tuple(tags)
    assert cash_transaction in account.transactions
    assert dt_created_diff.seconds < 1
    assert dt_edited_diff.seconds < 1


@given(
    transaction=cash_transactions(),
    new_type=st.integers()
    | st.floats()
    | st.text()
    | st.none()
    | st.datetimes()
    | st.booleans()
    | st.sampled_from([[], (), {}, set()]),
)
def test_type_invalid_type(transaction: CashTransaction, new_type: Any) -> None:
    with pytest.raises(
        TypeError, match="CashTransaction.type_ must be a CashTransactionType."
    ):
        transaction.type_ = new_type


@given(
    transaction=cash_transactions(),
    new_account=st.integers()
    | st.floats()
    | st.text()
    | st.none()
    | st.datetimes()
    | st.booleans()
    | st.sampled_from([[], (), {}, set()]),
)
def test_account_invalid_type(transaction: CashTransaction, new_account: Any) -> None:
    with pytest.raises(
        TypeError, match="CashTransaction.account must be a CashAccount."
    ):
        transaction.account = new_account


@given(
    transaction=cash_transactions(),
    new_amount=st.integers()
    | st.floats()
    | st.text()
    | st.none()
    | st.datetimes()
    | st.booleans()
    | st.sampled_from([[], (), {}, set()]),
)
def test_amount_invalid_type(transaction: CashTransaction, new_amount: Any) -> None:
    with pytest.raises(TypeError, match="CashTransaction.amount must be a Decimal."):
        transaction.amount = new_amount


@given(
    transaction=cash_transactions(),
    new_amount=st.decimals(max_value=-0.01),
)
def test_amount_invalid_value(
    transaction: CashTransaction, new_amount: Decimal
) -> None:
    with pytest.raises(
        ValueError,
        match="CashTransaction.amount must be a finite and positive Decimal.",
    ):
        transaction.amount = new_amount


@given(
    transaction=cash_transactions(),
    new_payee=st.integers()
    | st.floats()
    | st.text()
    | st.none()
    | st.datetimes()
    | st.booleans()
    | st.sampled_from([[], (), {}, set()]),
)
def test_payee_invalid_type(transaction: CashTransaction, new_payee: Any) -> None:
    with pytest.raises(TypeError, match="CashTransaction.payee must be an Attribute."):
        transaction.payee = new_payee


@given(
    transaction=cash_transactions(),
    new_category=st.integers()
    | st.floats()
    | st.text()
    | st.none()
    | st.datetimes()
    | st.booleans()
    | st.sampled_from([[], (), {}, set()]),
)
def test_category_invalid_type(transaction: CashTransaction, new_category: Any) -> None:
    with pytest.raises(TypeError, match="CashTransaction.category must be a Category."):
        transaction.category = new_category


@given(
    transaction=cash_transactions(),
    new_tags=st.integers()
    | st.floats()
    | st.text(min_size=1)
    | st.none()
    | st.datetimes()
    | st.booleans(),
)
def test_tags_invalid_type(transaction: CashTransaction, new_tags: Any) -> None:
    with pytest.raises(
        TypeError, match="CashTransaction.tags must be a collection of Attributes."
    ):
        transaction.tags = new_tags


@given(
    transaction=cash_transactions(),
    new_account=cash_accounts(),
)
def test_change_account(transaction: CashTransaction, new_account: CashAccount) -> None:
    previous_account = transaction.account
    assert transaction in previous_account.transactions
    assert transaction not in new_account.transactions
    transaction.account = new_account
    assert transaction in new_account.transactions
    assert transaction not in previous_account.transactions


@given(transaction=cash_transactions())
def test_get_amount_for_account(transaction: CashTransaction) -> None:
    account = transaction.account
    amount = transaction.amount
    if transaction.type_ == CashTransactionType.INCOME:
        expected_amount = amount
    else:
        expected_amount = -amount

    result = transaction.get_amount_for_account(account)
    assert result == expected_amount


@given(
    transaction=cash_transactions(),
    account=cash_accounts(),
)
def test_get_amount_for_account_invalid_account_value(
    transaction: CashTransaction, account: CashAccount
) -> None:
    assume(transaction.account != account)
    with pytest.raises(
        ValueError,
        match='The argument "account" is not related to this CashTransaction.',
    ):
        transaction.get_amount_for_account(account)
