from datetime import datetime, timedelta
from decimal import Decimal
from typing import Any

import pytest
from hypothesis import assume, given

from src.models.constants import tzinfo
from src.models.model_objects.attributes import (
    Attribute,
    AttributeType,
    Category,
    CategoryType,
    InvalidAttributeError,
    InvalidCategoryError,
)
from src.models.model_objects.cash_objects import (
    CashAccount,
    CashTransaction,
    CashTransactionType,
    InvalidCashTransactionTypeError,
    RefundPrecedesTransactionError,
    RefundTransaction,
    UnrelatedAccountError,
    UnrelatedTransactionError,
)
from src.models.model_objects.currency import CashAmount, Currency, CurrencyError
from tests.models.test_assets.composites import (
    cash_accounts,
    cash_transactions,
    everything_except,
)

currency = Currency("CZK", 2)

cat_1 = Category("Groceries", CategoryType.EXPENSE)
cat_2 = Category("Electronics", CategoryType.EXPENSE)
cat_3 = Category("Hygiene", CategoryType.EXPENSE)

tag_1 = Attribute("Split half", AttributeType.TAG)
tag_2 = Attribute("Fun stuff", AttributeType.TAG)
tag_3 = Attribute("Everything Tag", AttributeType.TAG)
tag_4 = Attribute("Personal Hygiene", AttributeType.TAG)


def test_creation() -> None:
    refunded_transaction = get_preloaded_expense()
    refunded_account = get_refunded_account()

    description = "The Refund"
    datetime_ = datetime.strptime("07-01-2022 00:00:00", "%m-%d-%Y %H:%M:%S").replace(
        tzinfo=tzinfo
    )
    category_amount_pairs = get_valid_category_amount_pairs()
    tag_amount_pairs = get_valid_tag_amount_pairs()

    refund = RefundTransaction(
        description,
        datetime_,
        refunded_account,
        refunded_transaction,
        category_amount_pairs,
        tag_amount_pairs,
    )

    assert refund.amount == CashAmount(50, currency)
    assert (
        refunded_account.get_balance(currency)
        == refunded_account.initial_balance + refund.amount
    )
    assert (
        refunded_transaction.account.get_balance(currency)
        == refunded_transaction.account.initial_balance - refunded_transaction.amount
    )
    assert refund.currency == refunded_transaction.currency
    assert refund.category_names == ", ".join((cat_1.path, cat_2.path, cat_3.path))
    assert refund.category_amount_pairs == category_amount_pairs
    assert refund.tag_amount_pairs == tag_amount_pairs
    assert refund in refunded_transaction.refunds
    assert refund.__repr__() == (
        f"RefundTransaction(account='{refund.account.name}', "
        f"amount={refund.amount} {refund.account.currency.code}, "
        f"category={{{refund.category_names}}}, "
        f"{refund.datetime_.strftime('%Y-%m-%d')})"
    )


def test_unrelated_refund_transaction() -> None:
    transaction = get_preloaded_expense()
    refund = get_preloaded_refund()
    with pytest.raises(UnrelatedTransactionError):
        transaction.add_refund(refund)


@given(transaction=everything_except(CashTransaction), account=cash_accounts())
def test_invalid_refunded_transaction_type(
    transaction: Any, account: CashAccount
) -> None:
    with pytest.raises(
        TypeError, match="Refunded transaction must be a CashTransaction."
    ):
        RefundTransaction("", datetime.now(tzinfo), account, transaction, [], [])


@given(transaction=cash_transactions(), account=cash_accounts())
def test_invalid_refunded_transaction_type_enum(
    transaction: CashTransaction, account: CashAccount
) -> None:
    assume(transaction.type_ != CashTransactionType.EXPENSE)
    with pytest.raises(InvalidCashTransactionTypeError):
        RefundTransaction("", datetime.now(tzinfo), account, transaction, [], [])


def test_invalid_datetime_value() -> None:
    refunded_transaction = get_preloaded_expense()
    datetime_ = refunded_transaction.datetime_ - timedelta(days=1)
    with pytest.raises(RefundPrecedesTransactionError):
        RefundTransaction(
            "", datetime_, refunded_transaction.account, refunded_transaction, [], []
        )


@given(account=everything_except(CashAccount))
def test_invalid_account_type(account: Any) -> None:
    refunded_transaction = get_preloaded_expense()
    datetime_ = refunded_transaction.datetime_ + timedelta(days=1)
    category_amount_pairs = get_valid_category_amount_pairs()
    tag_amount_pairs = get_valid_tag_amount_pairs()
    with pytest.raises(
        TypeError, match="RefundTransaction.account must be a CashAccount."
    ):
        RefundTransaction(
            "",
            datetime_,
            account,
            refunded_transaction,
            category_amount_pairs,
            tag_amount_pairs,
        )


@given(account=cash_accounts())
def test_invalid_account_currency(account: CashAccount) -> None:
    refunded_transaction = get_preloaded_expense()
    assume(account.currency != refunded_transaction.currency)
    datetime_ = refunded_transaction.datetime_ + timedelta(days=1)
    category_amount_pairs = get_valid_category_amount_pairs()
    tag_amount_pairs = get_valid_tag_amount_pairs()
    with pytest.raises(CurrencyError):
        RefundTransaction(
            "",
            datetime_,
            account,
            refunded_transaction,
            category_amount_pairs,
            tag_amount_pairs,
        )


def test_invalid_category_pair_categories() -> None:
    refunded_transaction = get_preloaded_expense()
    refunded_account = get_refunded_account()

    datetime_ = refunded_transaction.datetime_ + timedelta(days=1)
    c1 = Category("Wrong Category 1", CategoryType.EXPENSE)
    c2 = Category("Wrong Category 2", CategoryType.EXPENSE)
    c3 = Category("Wrong Category 3", CategoryType.EXPENSE)
    category_amount_pairs = (
        (c1, CashAmount(0, currency)),
        (c2, CashAmount(50, currency)),
        (c3, CashAmount(0, currency)),
    )
    tag_amount_pairs = get_valid_tag_amount_pairs()
    with pytest.raises(InvalidCategoryError):
        RefundTransaction(
            "",
            datetime_,
            refunded_account,
            refunded_transaction,
            category_amount_pairs,
            tag_amount_pairs,
        )


def test_invalid_category_pair_decimal_values() -> None:
    refunded_transaction = get_preloaded_expense()
    refunded_account = get_refunded_account()

    datetime_ = refunded_transaction.datetime_ + timedelta(days=1)
    category_amount_pairs = (
        (cat_1, CashAmount(-1, currency)),
        (cat_2, CashAmount(-10, currency)),
        (cat_3, CashAmount(-100, currency)),
    )
    tag_amount_pairs = get_valid_tag_amount_pairs()
    with pytest.raises(
        ValueError, match="Second member of RefundTransaction.category_amount_pairs"
    ):
        RefundTransaction(
            "",
            datetime_,
            refunded_account,
            refunded_transaction,
            category_amount_pairs,
            tag_amount_pairs,
        )


def test_invalid_refund_amount() -> None:
    refunded_transaction = get_preloaded_expense()
    refunded_account = get_refunded_account()

    datetime_ = refunded_transaction.datetime_ + timedelta(days=1)
    category_amount_pairs = (
        (cat_1, CashAmount(0, currency)),
        (cat_2, CashAmount(0, currency)),
        (cat_3, CashAmount(0, currency)),
    )
    tag_amount_pairs = get_valid_tag_amount_pairs()
    with pytest.raises(ValueError, match="Total refunded amount must be positive."):
        RefundTransaction(
            "",
            datetime_,
            refunded_account,
            refunded_transaction,
            category_amount_pairs,
            tag_amount_pairs,
        )


def test_invalid_category_refund_amount() -> None:
    refunded_transaction = get_preloaded_expense()
    refunded_account = get_refunded_account()

    datetime_ = refunded_transaction.datetime_ + timedelta(days=1)
    category_amount_pairs = (
        (cat_1, CashAmount(200, currency)),
        (cat_2, CashAmount(0, currency)),
        (cat_3, CashAmount(0, currency)),
    )
    tag_amount_pairs = get_valid_tag_amount_pairs()
    with pytest.raises(ValueError, match="Refunded amount for category "):
        RefundTransaction(
            "",
            datetime_,
            refunded_account,
            refunded_transaction,
            category_amount_pairs,
            tag_amount_pairs,
        )


def test_invalid_tag_type() -> None:
    refunded_transaction = get_preloaded_expense()
    refunded_account = get_refunded_account()

    datetime_ = refunded_transaction.datetime_ + timedelta(days=1)
    category_amount_pairs = get_valid_category_amount_pairs()
    t1 = Attribute("Wrong Attribute", AttributeType.PAYEE)
    tag_amount_pairs = (
        (t1, CashAmount(50, currency)),
        (tag_2, CashAmount(50, currency)),
        (tag_3, CashAmount(50, currency)),
        (tag_4, CashAmount(0, currency)),
    )
    with pytest.raises(InvalidAttributeError):
        RefundTransaction(
            "",
            datetime_,
            refunded_account,
            refunded_transaction,
            category_amount_pairs,
            tag_amount_pairs,
        )


def test_invalid_tag() -> None:
    refunded_transaction = get_preloaded_expense()
    refunded_account = get_refunded_account()

    datetime_ = refunded_transaction.datetime_ + timedelta(days=1)
    category_amount_pairs = get_valid_category_amount_pairs()
    t1 = Attribute("Wrong Attribute", AttributeType.TAG)
    tag_amount_pairs = (
        (t1, CashAmount(50, currency)),
        (tag_2, CashAmount(50, currency)),
        (tag_3, CashAmount(50, currency)),
        (tag_4, CashAmount(0, currency)),
    )
    with pytest.raises(InvalidAttributeError):
        RefundTransaction(
            "",
            datetime_,
            refunded_account,
            refunded_transaction,
            category_amount_pairs,
            tag_amount_pairs,
        )


def test_invalid_tag_decimal() -> None:
    refunded_transaction = get_preloaded_expense()
    refunded_account = get_refunded_account()

    datetime_ = refunded_transaction.datetime_ + timedelta(days=1)
    category_amount_pairs = get_valid_category_amount_pairs()
    tag_amount_pairs = (
        (tag_1, CashAmount(-1, currency)),
        (tag_2, CashAmount(-10, currency)),
        (tag_3, CashAmount("-0.1", currency)),
        (tag_4, CashAmount("-100.0", currency)),
    )
    with pytest.raises(ValueError, match="must be a non-negative CashAmount."):
        RefundTransaction(
            "",
            datetime_,
            refunded_account,
            refunded_transaction,
            category_amount_pairs,
            tag_amount_pairs,
        )


def test_invalid_tag_amount() -> None:
    refunded_transaction = get_preloaded_expense()
    refunded_account = get_refunded_account()

    datetime_ = refunded_transaction.datetime_ + timedelta(days=1)
    category_amount_pairs = get_valid_category_amount_pairs()
    tag_amount_pairs = (
        (tag_1, CashAmount(500, currency)),
        (tag_2, CashAmount(50, currency)),
        (tag_3, CashAmount(50, currency)),
        (tag_4, CashAmount(0, currency)),
    )
    with pytest.raises(ValueError, match="Refunded amount for tag "):
        RefundTransaction(
            "",
            datetime_,
            refunded_account,
            refunded_transaction,
            category_amount_pairs,
            tag_amount_pairs,
        )


def test_invalid_pair_type() -> None:
    refunded_transaction = get_preloaded_expense()
    refunded_account = get_refunded_account()

    datetime_ = refunded_transaction.datetime_ + timedelta(days=1)
    category_amount_pairs = (
        [cat_1, CashAmount(0, currency)],
        (cat_2, CashAmount(50, currency)),
        (cat_3, CashAmount(0, currency)),
    )
    tag_amount_pairs = get_valid_tag_amount_pairs()
    with pytest.raises(TypeError, match="Elements of 'collection' must be tuples."):
        RefundTransaction(
            "",
            datetime_,
            refunded_account,
            refunded_transaction,
            category_amount_pairs,  # type: ignore
            tag_amount_pairs,
        )


def test_multi_refund() -> None:
    refunded_transaction = get_preloaded_expense()
    refunded_account = get_refunded_account()

    description = "The Refund"
    datetime_ = datetime.strptime("07-01-2022 00:00:00", "%m-%d-%Y %H:%M:%S").replace(
        tzinfo=tzinfo
    )
    category_amount_pairs = get_valid_category_amount_pairs()
    tag_amount_pairs = get_valid_tag_amount_pairs()

    refund_1 = RefundTransaction(
        description,
        datetime_,
        refunded_account,
        refunded_transaction,
        category_amount_pairs,
        tag_amount_pairs,
    )

    category_amount_pairs = (
        (cat_1, CashAmount(0, currency)),
        (cat_2, CashAmount(0, currency)),
        (cat_3, CashAmount(20, currency)),
    )
    tag_amount_pairs = (
        (tag_1, CashAmount(0, currency)),
        (tag_2, CashAmount(0, currency)),
        (tag_3, CashAmount(20, currency)),
        (tag_4, CashAmount(20, currency)),
    )

    refund_2 = RefundTransaction(
        description,
        datetime_,
        refunded_account,
        refunded_transaction,
        category_amount_pairs,
        tag_amount_pairs,
    )

    assert refund_1.amount == CashAmount(50, currency)
    assert refund_2.amount == CashAmount(20, currency)
    assert (
        refunded_account.get_balance(currency)
        == refunded_account.initial_balance + refund_1.amount + refund_2.amount
    )
    assert (
        refunded_transaction.account.get_balance(currency)
        == refunded_transaction.account.initial_balance - refunded_transaction.amount
    )
    assert refund_1 in refunded_transaction.refunds
    assert refund_2 in refunded_transaction.refunds


@given(
    account=everything_except(CashAccount),
)
def test_get_amount_invalid_account_type(account: Any) -> None:
    refund = get_preloaded_refund()
    with pytest.raises(TypeError, match="Argument 'account' must be a CashAccount."):
        refund.get_amount(account)


@given(account=cash_accounts())
def test_get_amount_unrelated_account(account: CashAccount) -> None:
    refund = get_preloaded_refund()
    with pytest.raises(UnrelatedAccountError):
        refund.get_amount(account)


def test_remove_refund() -> None:
    refunded_transaction = get_preloaded_expense()
    refunded_account = get_refunded_account()

    description = "The Refund"
    datetime_ = datetime.strptime("07-01-2022 00:00:00", "%m-%d-%Y %H:%M:%S").replace(
        tzinfo=tzinfo
    )
    category_amount_pairs = get_valid_category_amount_pairs()
    tag_amount_pairs = get_valid_tag_amount_pairs()

    refund = RefundTransaction(
        description,
        datetime_,
        refunded_account,
        refunded_transaction,
        category_amount_pairs,
        tag_amount_pairs,
    )

    assert refund in refunded_transaction.refunds

    refunded_transaction.remove_refund(refund)

    assert refund not in refunded_transaction.refunds


def get_preloaded_refund() -> RefundTransaction:
    refunded_transaction = get_preloaded_expense()
    refunded_account = get_refunded_account()

    description = "The Refund"
    datetime_ = datetime.strptime("07-01-2022 00:00:00", "%m-%d-%Y %H:%M:%S").replace(
        tzinfo=tzinfo
    )
    category_amount_pairs = get_valid_category_amount_pairs()
    tag_amount_pairs = (
        (tag_1, CashAmount(50, currency)),
        (tag_2, CashAmount(50, currency)),
        (tag_3, CashAmount(50, currency)),
        (tag_4, CashAmount(0, currency)),
    )

    return RefundTransaction(
        description,
        datetime_,
        refunded_account,
        refunded_transaction,
        category_amount_pairs,
        tag_amount_pairs,
    )


def get_preloaded_expense() -> CashTransaction:
    initial_datetime = datetime.strptime(
        "01-01-2021 00:00:00", "%m-%d-%Y %H:%M:%S"
    ).replace(tzinfo=tzinfo)
    account = CashAccount(
        "Test Account", currency, CashAmount(Decimal(1000), currency), initial_datetime
    )

    description = "A transaction to be refunded."
    datetime_ = datetime.strptime("01-01-2022 00:00:00", "%m-%d-%Y %H:%M:%S").replace(
        tzinfo=tzinfo
    )
    payee = Attribute("Some payee", AttributeType.PAYEE)
    category_amount_pairs = (
        (cat_1, CashAmount(100, currency)),
        (cat_2, CashAmount(50, currency)),
        (cat_3, CashAmount(20, currency)),
    )
    tag_amount_pairs = (
        (tag_1, CashAmount(150, currency)),
        (tag_2, CashAmount(50, currency)),
        (tag_3, CashAmount(170, currency)),
        (tag_4, CashAmount(20, currency)),
    )

    return CashTransaction(
        description,
        datetime_,
        CashTransactionType.EXPENSE,
        account,
        category_amount_pairs,
        payee,
        tag_amount_pairs,
    )


def get_refunded_account() -> CashAccount:
    initial_datetime = datetime.strptime(
        "01-01-2021 00:00:00", "%m-%d-%Y %H:%M:%S"
    ).replace(tzinfo=tzinfo)
    return CashAccount(
        "Refunded Account",
        currency,
        CashAmount(0, currency),
        initial_datetime,
    )


def get_valid_category_amount_pairs() -> tuple[tuple[Category, Decimal], ...]:
    return (
        (cat_1, CashAmount(0, currency)),
        (cat_2, CashAmount(50, currency)),
        (cat_3, CashAmount(0, currency)),
    )


def get_valid_tag_amount_pairs() -> tuple[tuple[Attribute, Decimal], ...]:
    return (
        (tag_1, CashAmount(50, currency)),
        (tag_2, CashAmount(50, currency)),
        (tag_3, CashAmount(50, currency)),
        (tag_4, CashAmount(0, currency)),
    )
