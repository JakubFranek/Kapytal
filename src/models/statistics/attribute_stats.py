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


def calculate_monthly_attribute_stats(
    transactions: Collection[CashTransaction | RefundTransaction],
    base_currency: Currency,
    all_attributes: Collection[Attribute],
) -> dict[str, tuple[AttributeStats]]:
    transactions = sorted(transactions, key=lambda x: x.timestamp)

    # separate transactions into bins by month/year
    transactions_by_month: dict[str, list[CashTransaction | RefundTransaction]] = {}
    for transaction in transactions:
        key = transaction.datetime_.strftime("%B %Y")
        if key not in transactions_by_month:
            transactions_by_month[key] = []
        transactions_by_month[key].append(transaction)

    stats_dict: dict[str, tuple[AttributeStats]] = {}
    for month in transactions_by_month:
        monthly_stats = calculate_attribute_stats(
            transactions_by_month[month], base_currency, all_attributes
        )
        stats_dict[month] = tuple(monthly_stats.values())

    return stats_dict


def calculate_average_per_month_attribute_stats(
    transactions: Collection[CashTransaction | RefundTransaction],
    base_currency: Currency,
    all_attributes: Collection[Attribute],
) -> tuple[AttributeStats]:
    stats_per_month = calculate_monthly_attribute_stats(
        transactions, base_currency, all_attributes
    )
    all_stats = list(itertools.chain(*stats_per_month.values()))
    periods = len(stats_per_month)

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
    if len(attribute_types) != 1:
        raise ValueError("All Attributes must be of the same type_.")
    attribute_type = attribute_types.pop()

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
