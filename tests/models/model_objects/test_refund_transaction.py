from datetime import datetime, timedelta
from decimal import Decimal
from types import NoneType
from typing import Any

import pytest
from hypothesis import assume, given
from hypothesis import strategies as st

import src.models.user_settings.user_settings as user_settings
from src.models.custom_exceptions import InvalidOperationError
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
from src.models.model_objects.currency_objects import (
    CashAmount,
    Currency,
    CurrencyError,
)
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
        tzinfo=user_settings.settings.time_zone
    )
    category_amount_pairs = get_valid_category_amount_pairs()
    tag_amount_pairs = get_valid_tag_amount_pairs()
    tags = tuple(tag for tag, _ in tag_amount_pairs)
    payee = refunded_transaction.payee

    refund = RefundTransaction(
        description,
        datetime_,
        refunded_account,
        refunded_transaction,
        payee,
        category_amount_pairs,
        tag_amount_pairs,
    )
    categories = tuple(category for category, _ in category_amount_pairs)

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
    assert refund.currencies == (refunded_transaction.currency,)
    assert refund.category_names == ", ".join((cat_1.path, cat_2.path, cat_3.path))
    assert refund.category_amount_pairs == category_amount_pairs
    assert refund.categories == categories
    assert refund.tag_amount_pairs == tag_amount_pairs
    assert refund in refunded_transaction.refunds
    assert refund.payee == payee
    assert refund.tags == tags
    assert refund.__repr__() == (
        f"RefundTransaction(account='{refund.account.name}', "
        f"amount={refund.amount}, "
        f"category={{{refund.category_names}}}, "
        f"{refund.datetime_.strftime('%Y-%m-%d')})"
    )


def test_unrelated_refund_transaction() -> None:
    transaction = get_preloaded_expense()
    refund = get_preloaded_refund()
    with pytest.raises(UnrelatedTransactionError):
        transaction.add_refund(refund)


@given(
    transaction=everything_except((CashTransaction, NoneType)), account=cash_accounts()
)
def test_invalid_refunded_transaction_type(
    transaction: Any, account: CashAccount
) -> None:
    with pytest.raises(
        TypeError, match="Refunded transaction must be a CashTransaction."
    ):
        RefundTransaction(
            "",
            datetime.now(user_settings.settings.time_zone),
            account,
            transaction,
            [],
            [],
            None,
        )


@given(transaction=cash_transactions(), account=cash_accounts())
def test_invalid_refunded_transaction_type_enum(
    transaction: CashTransaction, account: CashAccount
) -> None:
    assume(transaction.type_ != CashTransactionType.EXPENSE)
    with pytest.raises(InvalidCashTransactionTypeError):
        RefundTransaction(
            "",
            datetime.now(user_settings.settings.time_zone),
            account,
            transaction,
            [],
            [],
            None,
        )


def test_invalid_datetime_value() -> None:
    refunded_transaction = get_preloaded_expense()
    datetime_ = refunded_transaction.datetime_ - timedelta(days=1)
    payee = refunded_transaction.payee
    with pytest.raises(RefundPrecedesTransactionError):
        RefundTransaction(
            "",
            datetime_,
            refunded_transaction.account,
            refunded_transaction,
            [],
            [],
            payee,
        )


@given(account=everything_except((CashAccount, NoneType)))
def test_invalid_account_type(account: Any) -> None:
    refunded_transaction = get_preloaded_expense()
    datetime_ = refunded_transaction.datetime_ + timedelta(days=1)
    category_amount_pairs = get_valid_category_amount_pairs()
    tag_amount_pairs = get_valid_tag_amount_pairs()
    payee = refunded_transaction.payee
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
            payee,
        )


@given(account=cash_accounts())
def test_invalid_account_currency(account: CashAccount) -> None:
    refunded_transaction = get_preloaded_expense()
    assume(account.currency != refunded_transaction.currency)
    datetime_ = refunded_transaction.datetime_ + timedelta(days=1)
    category_amount_pairs = get_valid_category_amount_pairs()
    tag_amount_pairs = get_valid_tag_amount_pairs()
    payee = refunded_transaction.payee
    with pytest.raises(CurrencyError):
        RefundTransaction(
            "",
            datetime_,
            account,
            refunded_transaction,
            category_amount_pairs,
            tag_amount_pairs,
            payee,
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
    payee = refunded_transaction.payee

    with pytest.raises(InvalidCategoryError):
        RefundTransaction(
            "",
            datetime_,
            refunded_account,
            refunded_transaction,
            payee,
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
    payee = refunded_transaction.payee

    with pytest.raises(
        ValueError, match="Second member of RefundTransaction.category_amount_pairs"
    ):
        RefundTransaction(
            "",
            datetime_,
            refunded_account,
            refunded_transaction,
            payee,
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
    payee = refunded_transaction.payee

    with pytest.raises(ValueError, match="Total refunded amount must be positive."):
        RefundTransaction(
            "",
            datetime_,
            refunded_account,
            refunded_transaction,
            payee,
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
    payee = refunded_transaction.payee

    with pytest.raises(ValueError, match="Refunded amount for category "):
        RefundTransaction(
            "",
            datetime_,
            refunded_account,
            refunded_transaction,
            payee,
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
    payee = refunded_transaction.payee

    with pytest.raises(InvalidAttributeError):
        RefundTransaction(
            "",
            datetime_,
            refunded_account,
            refunded_transaction,
            payee,
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
    payee = refunded_transaction.payee

    with pytest.raises(InvalidAttributeError):
        RefundTransaction(
            "",
            datetime_,
            refunded_account,
            refunded_transaction,
            payee,
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
    payee = refunded_transaction.payee

    with pytest.raises(ValueError, match="must be a non-negative CashAmount."):
        RefundTransaction(
            "",
            datetime_,
            refunded_account,
            refunded_transaction,
            payee,
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
    payee = refunded_transaction.payee

    with pytest.raises(ValueError, match="Refunded amount for tag "):
        RefundTransaction(
            "",
            datetime_,
            refunded_account,
            refunded_transaction,
            payee,
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
    payee = refunded_transaction.payee

    with pytest.raises(TypeError, match="Elements of 'collection' must be tuples."):
        RefundTransaction(
            "",
            datetime_,
            refunded_account,
            refunded_transaction,
            payee,
            category_amount_pairs,  # type: ignore
            tag_amount_pairs,
        )


@given(payee=everything_except((Attribute, NoneType)))
def test_invalid_payee_type(payee: Any) -> None:
    refunded_transaction = get_preloaded_expense()
    account = refunded_transaction.account
    datetime_ = refunded_transaction.datetime_ + timedelta(days=1)
    category_amount_pairs = get_valid_category_amount_pairs()
    tag_amount_pairs = get_valid_tag_amount_pairs()
    with pytest.raises(TypeError, match="Payee must be an Attribute."):
        RefundTransaction(
            "",
            datetime_,
            account,
            refunded_transaction,
            payee,
            category_amount_pairs,
            tag_amount_pairs,
        )


def test_invalid_type_of_payee() -> None:
    payee = Attribute("test", AttributeType.TAG)
    refunded_transaction = get_preloaded_expense()
    account = refunded_transaction.account
    datetime_ = refunded_transaction.datetime_ + timedelta(days=1)
    category_amount_pairs = get_valid_category_amount_pairs()
    tag_amount_pairs = get_valid_tag_amount_pairs()
    with pytest.raises(
        ValueError,
        match="The type_ of payee Attribute must be PAYEE.",
    ):
        RefundTransaction(
            "",
            datetime_,
            account,
            refunded_transaction,
            payee,
            category_amount_pairs,
            tag_amount_pairs,
        )


def test_multi_refund() -> None:
    refunded_transaction = get_preloaded_expense()
    refunded_account = get_refunded_account()

    description = "The Refund"
    datetime_ = datetime.strptime("07-01-2022 00:00:00", "%m-%d-%Y %H:%M:%S").replace(
        tzinfo=user_settings.settings.time_zone
    )
    category_amount_pairs = get_valid_category_amount_pairs()
    tag_amount_pairs = get_valid_tag_amount_pairs()
    payee = refunded_transaction.payee

    refund_1 = RefundTransaction(
        description,
        datetime_,
        refunded_account,
        refunded_transaction,
        payee,
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
        payee,
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
    with pytest.raises(TypeError, match="Parameter 'account' must be a CashAccount."):
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
        tzinfo=user_settings.settings.time_zone
    )
    category_amount_pairs = get_valid_category_amount_pairs()
    tag_amount_pairs = get_valid_tag_amount_pairs()
    payee = refunded_transaction.payee

    refund = RefundTransaction(
        description,
        datetime_,
        refunded_account,
        refunded_transaction,
        payee,
        category_amount_pairs,
        tag_amount_pairs,
    )

    assert refund in refunded_transaction.refunds

    refunded_transaction.remove_refund(refund)

    assert refund not in refunded_transaction.refunds


def test_validate_attributes_same_values() -> None:
    refund = get_preloaded_refund()
    refund.validate_attributes()


def test_set_attributes_same_values() -> None:
    refund = get_preloaded_refund()
    prev_description = refund.description
    prev_datetime = refund.datetime_
    prev_account = refund.account
    prev_refunded_transaction = refund.refunded_transaction
    prev_category_amount_pairs = refund.category_amount_pairs
    prev_tag_amount_pairs = refund.tag_amount_pairs
    refund.set_attributes()
    assert prev_description == refund.description
    assert prev_datetime == refund.datetime_
    assert prev_account == refund.account
    assert prev_refunded_transaction == refund.refunded_transaction
    assert prev_category_amount_pairs == refund.category_amount_pairs
    assert prev_tag_amount_pairs == refund.tag_amount_pairs


@given(data=st.data())
def test_change_account(data: st.DataObject) -> None:
    refund = get_preloaded_refund()
    old_account = refund.account
    new_account = data.draw(cash_accounts(currency=refund.currency))

    assert refund in old_account.transactions
    assert refund not in new_account.transactions

    refund.set_attributes(account=new_account)

    assert refund in new_account.transactions
    assert refund not in old_account.transactions


def test_add_remove_tags() -> None:
    refund = get_preloaded_refund()
    with pytest.raises(InvalidOperationError):
        refund.add_tags(None)
    with pytest.raises(InvalidOperationError):
        refund.remove_tags(None)


def test_edit_refunded_transaction_fail() -> None:
    refund = get_preloaded_refund()
    refunded_transaction = refund.refunded_transaction
    with pytest.raises(InvalidOperationError):
        refunded_transaction.set_attributes()


def get_preloaded_refund() -> RefundTransaction:
    refunded_transaction = get_preloaded_expense()
    refunded_account = get_refunded_account()

    description = "The Refund"
    datetime_ = datetime.strptime("07-01-2022 00:00:00", "%m-%d-%Y %H:%M:%S").replace(
        tzinfo=user_settings.settings.time_zone
    )
    category_amount_pairs = get_valid_category_amount_pairs()
    tag_amount_pairs = (
        (tag_1, CashAmount(50, currency)),
        (tag_2, CashAmount(50, currency)),
        (tag_3, CashAmount(50, currency)),
        (tag_4, CashAmount(0, currency)),
    )
    payee = refunded_transaction.payee

    return RefundTransaction(
        description,
        datetime_,
        refunded_account,
        refunded_transaction,
        payee,
        category_amount_pairs,
        tag_amount_pairs,
    )


def get_preloaded_expense() -> CashTransaction:
    account = CashAccount("Test Account", currency, CashAmount(Decimal(1000), currency))

    description = "A transaction to be refunded."
    datetime_ = datetime.strptime("01-01-2022 00:00:00", "%m-%d-%Y %H:%M:%S").replace(
        tzinfo=user_settings.settings.time_zone
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
        payee,
        category_amount_pairs,
        tag_amount_pairs,
    )


def get_refunded_account() -> CashAccount:
    return CashAccount("Refunded Account", currency, CashAmount(0, currency))


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
