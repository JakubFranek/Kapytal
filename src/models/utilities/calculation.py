from collections.abc import Collection
from datetime import date
from typing import NamedTuple

from src.models.base_classes.transaction import Transaction
from src.models.model_objects.attributes import Attribute, Category
from src.models.model_objects.cash_objects import (
    CashTransaction,
    RefundTransaction,
)
from src.models.model_objects.currency_objects import CashAmount, Currency


class AttributeStats(NamedTuple):
    attribute: Attribute
    no_of_transactions: int
    balance: CashAmount


class CategoryStats(NamedTuple):
    category: Category
    transactions_self: int
    transactions_total: int
    balance: CashAmount


def get_payee_stats(
    payee: Attribute,
    transactions: Collection[Transaction],
    currency: Currency,
    date_start: date | None = None,
    date_end: date | None = None,
) -> AttributeStats:
    _transactions = _filter_date_range(transactions, date_start, date_end)

    _transactions = [
        transaction
        for transaction in _transactions
        if isinstance(transaction, CashTransaction | RefundTransaction)
        and transaction.payee == payee
    ]

    no_of_transactions = len(_transactions)
    balance = sum(
        (
            transaction.get_amount(transaction.account).convert(currency)
            for transaction in _transactions
        ),
        start=currency.zero_amount,
    )
    return AttributeStats(payee, no_of_transactions, balance)


def get_tag_stats(
    tag: Attribute,
    transactions: Collection[Transaction],
    currency: Currency,
    date_start: date | None = None,
    date_end: date | None = None,
) -> AttributeStats:
    _transactions = _filter_date_range(transactions, date_start, date_end)

    _transactions = [
        transaction for transaction in _transactions if tag in transaction.tags
    ]
    no_of_transactions = len(_transactions)

    _cash_amount_transactions = [
        transaction
        for transaction in _transactions
        if isinstance(transaction, CashTransaction | RefundTransaction)
    ]

    balance = sum(
        (
            transaction.get_amount_for_tag(tag).convert(currency)
            for transaction in _cash_amount_transactions
        ),
        start=currency.zero_amount,
    )
    return AttributeStats(tag, no_of_transactions, balance)


def get_category_stats(
    category: Category,
    transactions: Collection[Transaction],
    currency: Currency,
    date_start: date | None = None,
    date_end: date | None = None,
) -> CategoryStats:
    _transactions = _filter_date_range(transactions, date_start, date_end)

    # TODO: a lot of time is spend in this listcomp, this could be improved
    # if RecordKeeper sorted Transactions by type into several lists
    _transactions_direct: list[CashTransaction | RefundTransaction] = []
    _transactions_all: list[CashTransaction | RefundTransaction] = []
    for transaction in _transactions:
        if not isinstance(transaction, CashTransaction | RefundTransaction):
            continue
        if category in transaction.categories:
            _transactions_direct.append(transaction)
        if transaction.is_category_related(category):
            _transactions_all.append(transaction)

    transactions_self = len(_transactions_direct)
    transactions_total = len(_transactions_all)

    balance = sum(
        (
            transaction.get_amount_for_category(category, total=True).convert(currency)
            for transaction in _transactions_all
        ),
        start=currency.zero_amount,
    )
    return CategoryStats(category, transactions_self, transactions_total, balance)


def _filter_date_range(
    transactions: Collection[Transaction],
    date_start: date | None = None,
    date_end: date | None = None,
) -> tuple[Transaction, ...]:
    if date_start is None and date_end is None:
        return tuple(transactions)
    return tuple(
        transaction
        for transaction in transactions
        if (date_start is None or transaction.datetime_.date() >= date_start)
        and (date_end is None or transaction.datetime_.date() <= date_end)
    )
