from datetime import datetime
from decimal import Decimal

from src.models.constants import tzinfo
from src.models.model_objects.attributes import (
    Attribute,
    AttributeType,
    Category,
    CategoryType,
)
from src.models.model_objects.cash_objects import (
    CashAccount,
    CashTransaction,
    CashTransactionType,
    RefundTransaction,
)
from src.models.model_objects.currency import Currency


def test_creation() -> None:
    refunded_transaction = get_preloaded_expense()

    initial_datetime = datetime.strptime(
        "01-01-2021 00:00:00", "%m-%d-%Y %H:%M:%S"
    ).replace(tzinfo=tzinfo)
    refunded_account = CashAccount(
        "Refunded Account",
        refunded_transaction.currency,
        Decimal("0"),
        initial_datetime,
    )
    tags: list[Category] = []
    for tag, _ in refunded_transaction.category_amount_pairs:
        tags.append(tag)
    cat_1, cat_2, cat_3 = tags

    tags: list[Attribute] = []
    for tag, _ in refunded_transaction.tag_amount_pairs:
        tags.append(tag)
    tag_1, tag_2, tag_3, tag_4 = tags

    description = "The Refund"
    datetime_ = datetime.strptime("07-01-2022 00:00:00", "%m-%d-%Y %H:%M:%S").replace(
        tzinfo=tzinfo
    )
    category_amount_pairs = ((cat_2, Decimal("50")),)
    tag_amount_pairs = (
        (tag_1, Decimal("50")),
        (tag_2, Decimal("50")),
        (tag_3, Decimal("50")),
    )

    refund = RefundTransaction(
        description,
        datetime_,
        refunded_account,
        refunded_transaction,
        category_amount_pairs,
        tag_amount_pairs,
    )

    assert refund.amount == Decimal("50")
    assert refunded_account.balance == refunded_account.initial_balance + refund.amount
    assert (
        refunded_transaction.account.balance
        == refunded_transaction.account.initial_balance - refunded_transaction.amount
    )


def get_preloaded_expense() -> CashTransaction:
    currency = Currency("CZK")
    initial_datetime = datetime.strptime(
        "01-01-2021 00:00:00", "%m-%d-%Y %H:%M:%S"
    ).replace(tzinfo=tzinfo)
    account = CashAccount("Test Account", currency, Decimal(1000), initial_datetime)

    description = "A transaction to be refunded."
    datetime_ = datetime.strptime("01-01-2022 00:00:00", "%m-%d-%Y %H:%M:%S").replace(
        tzinfo=tzinfo
    )
    payee = Attribute("Some payee", AttributeType.PAYEE)

    cat_1 = Category("Groceries", CategoryType.EXPENSE)
    cat_2 = Category("Electronics", CategoryType.EXPENSE)
    cat_3 = Category("Hygiene", CategoryType.EXPENSE)
    category_amount_pairs = (
        (cat_1, Decimal("100")),
        (cat_2, Decimal("50")),
        (cat_3, Decimal("20")),
    )

    tag_1 = Attribute("Split half", AttributeType.TAG)
    tag_2 = Attribute("Fun stuff", AttributeType.TAG)
    tag_3 = Attribute("Everything Tag", AttributeType.TAG)
    tag_4 = Attribute("Personal Hygiene", AttributeType.TAG)
    tag_amount_pairs = (
        (tag_1, Decimal("150")),
        (tag_2, Decimal("50")),
        (tag_3, Decimal("170")),
        (tag_3, Decimal("20")),
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
