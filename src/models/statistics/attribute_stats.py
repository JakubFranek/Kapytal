import itertools
from collections.abc import Collection
from dataclasses import dataclass, field

from src.models.model_objects.attributes import Attribute, AttributeType
from src.models.model_objects.cash_objects import (
    CashTransaction,
    RefundTransaction,
)
from src.models.model_objects.currency_objects import CashAmount, Currency
from src.models.statistics.common_classes import TransactionBalance


@dataclass
class AttributeStats:
    attribute: Attribute
    no_of_transactions: int
    balance: CashAmount
    transactions: set[CashTransaction | RefundTransaction] = field(default_factory=set)


def calculate_periodic_totals_and_averages(
    periodic_stats: dict[str, tuple[AttributeStats]], currency: Currency
) -> tuple[
    dict[str, TransactionBalance],
    dict[Attribute, TransactionBalance],
    dict[Attribute, TransactionBalance],
]:
    """Returns a tuple of (period_totals, attribute_averages, attribute_totals)"""
    period_totals: dict[str, TransactionBalance] = {}
    attribute_averages: dict[Attribute, TransactionBalance] = {}
    attribute_totals: dict[Attribute, TransactionBalance] = {
        stat.attribute: TransactionBalance(currency.zero_amount)
        for stats in periodic_stats.values()
        for stat in stats
    }

    for period in periodic_stats:
        total_period_balance = TransactionBalance(currency.zero_amount)

        for stats in periodic_stats[period]:
            total_period_balance.transactions = total_period_balance.transactions.union(
                stats.transactions
            )
            total_period_balance.balance += stats.balance

            attribute_totals[stats.attribute].add_transaction_balance(
                stats.transactions, stats.balance
            )
        period_totals[period] = total_period_balance

    attribute_averages = {
        attribute: TransactionBalance(
            attribute_totals[attribute].balance / len(periodic_stats),
            attribute_totals[attribute].transactions,
        )
        for attribute in attribute_totals
    }
    return period_totals, attribute_averages, attribute_totals


def calculate_periodic_attribute_stats(
    transactions: Collection[CashTransaction | RefundTransaction],
    base_currency: Currency,
    all_attributes: Collection[Attribute],
    period_format: str = "%B %Y",
) -> dict[str, tuple[AttributeStats]]:
    transactions = sorted(transactions, key=lambda x: x.timestamp)

    # separate transactions into bins by period
    transactions_by_period: dict[str, list[CashTransaction | RefundTransaction]] = {}
    for transaction in transactions:
        key = transaction.datetime_.strftime(period_format)
        if key not in transactions_by_period:
            transactions_by_period[key] = []
        transactions_by_period[key].append(transaction)

    stats_dict: dict[str, tuple[AttributeStats]] = {}
    for period in transactions_by_period:
        period_stats = calculate_attribute_stats(
            transactions_by_period[period], base_currency, all_attributes
        )
        stats_dict[period] = tuple(period_stats.values())

    return stats_dict


def calculate_attribute_stats(
    transactions: Collection[CashTransaction | RefundTransaction],
    base_currency: Currency,
    all_attributes: Collection[Attribute],
) -> dict[Attribute, AttributeStats]:
    attribute_types = {attribute.type_ for attribute in all_attributes}
    if len(attribute_types) > 1:
        raise ValueError("All Attributes must be of the same type_.")
    attribute_type = attribute_types.pop() if len(attribute_types) == 1 else None

    stats_dict: dict[Attribute, AttributeStats] = {}
    for attribute in all_attributes:
        stats = AttributeStats(attribute, 0, base_currency.zero_amount)
        stats_dict[attribute] = stats
    for transaction in transactions:
        date_ = transaction.datetime_.date()
        if attribute_type == AttributeType.TAG:
            for tag in transaction.tags:
                stats = stats_dict[tag]
                stats.transactions.add(transaction)
                stats.no_of_transactions += 1
                stats.balance += transaction.get_amount_for_tag(tag).convert(
                    base_currency, date_
                )
        elif attribute_type == AttributeType.PAYEE:
            stats = stats_dict[transaction.payee]
            stats.transactions.add(transaction)
            stats.no_of_transactions += 1
            stats.balance += transaction.get_amount(transaction.account).convert(
                base_currency
            )
    return stats_dict
