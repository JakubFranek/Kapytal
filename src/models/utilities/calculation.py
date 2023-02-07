from collections.abc import Collection
from datetime import date
from typing import NamedTuple

from src.models.base_classes.transaction import Transaction
from src.models.model_objects.attributes import Attribute, AttributeType
from src.models.model_objects.cash_objects import CashTransaction, RefundTransaction
from src.models.model_objects.currency_objects import CashAmount, Currency

AttributeStats = NamedTuple(
    "AttributeStats",
    [("attribute", Attribute), ("no_of_transactions", int), ("balance", CashAmount)],
)


def get_attribute_stats(
    attribute: Attribute,
    transactions: Collection[Transaction],
    currency: Currency,
    date_start: date | None = None,
    date_end: date | None = None,
) -> AttributeStats:
    if date_start is not None:
        transactions = [
            transaction
            for transaction in transactions
            if transaction.datetime_.date() >= date_start
        ]
    if date_end is not None:
        transactions = [
            transaction
            for transaction in transactions
            if transaction.datetime_.date() <= date_end
        ]
    if attribute.type_ == AttributeType.PAYEE:
        transactions = [
            transaction
            for transaction in transactions
            if isinstance(transaction, (CashTransaction, RefundTransaction))
            and transaction.payee == attribute
        ]
    else:
        transactions = [
            transaction
            for transaction in transactions
            if isinstance(transaction, (CashTransaction, RefundTransaction))
            and attribute in transaction.tags
        ]

    no_of_transactions = len(transactions)
    balance = sum(
        (transaction.get_amount(transaction.account) for transaction in transactions),
        start=CashAmount(0, currency),
    )
    return AttributeStats(attribute, no_of_transactions, balance)
