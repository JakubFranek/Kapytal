import itertools
from collections.abc import Collection
from dataclasses import dataclass

from src.models.model_objects.attributes import Attribute, AttributeType
from src.models.model_objects.cash_objects import (
    CashTransaction,
    RefundTransaction,
)
from src.models.model_objects.currency_objects import CashAmount, Currency


@dataclass
class AttributeStats:
    attribute: Attribute
    no_of_transactions: int
    balance: CashAmount


def calculate_periodic_totals_and_averages(
    periodic_stats: dict[str, tuple[AttributeStats]]
) -> tuple[
    dict[str, CashAmount], dict[Attribute, CashAmount], dict[Attribute, CashAmount]
]:
    """Returns a tuple of (period_totals, attribute_averages, attribute_totals)"""
    attribute_totals: dict[AttributeStats, CashAmount] = {}
    period_totals: dict[str, CashAmount] = {}
    attribute_averages: dict[AttributeStats, CashAmount] = {}

    currency = None
    for period in periodic_stats:
        if len(periodic_stats[period]) == 0:
            continue
        currency = periodic_stats[period][0].balance.currency
    if currency is None:
        raise ValueError("No data found within 'periodic_stats'.")

    for period in periodic_stats:
        period_totals[period] = sum(
            (stats.balance for stats in periodic_stats[period]),
            start=currency.zero_amount,
        )
        for stats in periodic_stats[period]:
            attribute_totals[stats.attribute] = (
                attribute_totals.get(stats.attribute, currency.zero_amount)
                + stats.balance
            )
    attribute_averages = {
        attribute: attribute_totals[attribute] / len(periodic_stats)
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


def calculate_average_per_period_attribute_stats(
    transactions: Collection[CashTransaction | RefundTransaction],
    base_currency: Currency,
    all_attributes: Collection[Attribute],
) -> tuple[AttributeStats]:
    periodic_stats = calculate_periodic_attribute_stats(
        transactions, base_currency, all_attributes
    )
    all_stats = list(itertools.chain(*periodic_stats.values()))
    periods = len(periodic_stats)

    average_stats: dict[Attribute, AttributeStats] = {}
    for stats in all_stats:
        if stats.attribute in average_stats:
            average_stats[stats.attribute].balance += stats.balance
            average_stats[
                stats.attribute
            ].no_of_transactions += stats.no_of_transactions
        else:
            average_stats[stats.attribute] = AttributeStats(
                stats.attribute, 0, base_currency.zero_amount
            )

    for stats in average_stats.values():
        stats.balance = stats.balance / periods
        stats.no_of_transactions = stats.no_of_transactions / periods

    return tuple(average_stats.values())


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
        if attribute_type == AttributeType.TAG:
            for attribute in transaction.tags:
                stats = stats_dict[attribute]
                stats.no_of_transactions += 1
                stats.balance += transaction.get_amount_for_tag(attribute).convert(
                    base_currency
                )
        else:
            stats = stats_dict[transaction.payee]
            stats.no_of_transactions += 1
            stats.balance += transaction.get_amount(transaction.account).convert(
                base_currency
            )
    return stats_dict
