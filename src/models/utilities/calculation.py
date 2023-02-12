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
    _transactions = transactions
    if date_start is not None:
        _transactions = [
            transaction
            for transaction in _transactions
            if transaction.datetime_.date() >= date_start
        ]
    if date_end is not None:
        _transactions = [
            transaction
            for transaction in _transactions
            if transaction.datetime_.date() <= date_end
        ]
    if attribute.type_ == AttributeType.PAYEE:
        filtered_transactions = [
            transaction
            for transaction in _transactions
            if isinstance(transaction, (CashTransaction, RefundTransaction))
            and transaction.payee == attribute
        ]
    else:
        filtered_transactions = [
            transaction
            for transaction in _transactions
            if isinstance(transaction, (CashTransaction, RefundTransaction))
            and attribute in transaction.tags
        ]

    no_of_transactions = len(filtered_transactions)
    balance = sum(
        (
            transaction.get_amount(transaction.account)
            for transaction in filtered_transactions
        ),
        start=CashAmount(0, currency),
    )
    return AttributeStats(attribute, no_of_transactions, balance)
