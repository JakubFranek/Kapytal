import itertools
from collections.abc import Collection
from dataclasses import dataclass

from src.models.model_objects.attributes import Attribute, Category
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


@dataclass
class CategoryStats:
    category: Category
    transactions_self: int
    transactions_total: int
    balance: CashAmount


def calculate_monthly_tag_stats(
    transactions: Collection[CashTransaction | RefundTransaction],
    base_currency: Currency,
    all_tags: Collection[Attribute],
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
        monthly_tag_stats = calculate_tag_stats(
            transactions_by_month[month], base_currency, all_tags
        )
        stats_dict[month] = tuple(monthly_tag_stats.values())

    return stats_dict


def calculate_average_per_month_tag_stats(
    transactions: Collection[CashTransaction | RefundTransaction],
    base_currency: Currency,
    all_tags: Collection[Attribute],
) -> tuple[AttributeStats]:
    stats_per_month = calculate_monthly_tag_stats(transactions, base_currency, all_tags)
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


def calculate_tag_stats(
    transactions: Collection[CashTransaction | RefundTransaction],
    base_currency: Currency,
    all_tags: Collection[Attribute],
) -> dict[Attribute, AttributeStats]:
    stats_dict: dict[Attribute, AttributeStats] = {}
    for tag in all_tags:
        stats = AttributeStats(tag, 0, base_currency.zero_amount)
        stats_dict[tag] = stats
    for transaction in transactions:
        for tag in transaction.tags:
            stats = stats_dict[tag]
            stats.no_of_transactions += 1
            stats.balance += transaction.get_amount_for_tag(tag).convert(base_currency)
    return stats_dict


def calculate_payee_stats(
    transactions: Collection[CashTransaction | RefundTransaction],
    base_currency: Currency,
    all_payees: Collection[Attribute],
) -> dict[Attribute, AttributeStats]:
    stats_dict: dict[Attribute, AttributeStats] = {}
    for payee in all_payees:
        stats = AttributeStats(payee, 0, base_currency.zero_amount)
        stats_dict[payee] = stats
    for transaction in transactions:
        payee = transaction.payee
        stats = stats_dict[payee]
        stats.no_of_transactions += 1
        stats.balance += transaction.get_amount(transaction.account).convert(
            base_currency
        )
    return stats_dict


def calculate_category_stats(
    transactions: Collection[CashTransaction | RefundTransaction],
    base_currency: Currency,
    categories: Collection[Category],
) -> dict[Category, CategoryStats]:
    stats_dict: dict[Category, CategoryStats] = {}
    for category in categories:
        stats = CategoryStats(category, 0, 0, base_currency.zero_amount)
        stats_dict[category] = stats

    for transaction in transactions:
        for category in transaction.categories:
            stats = stats_dict[category]

            stats.balance += transaction.get_amount_for_category(
                category, total=False
            ).convert(base_currency)
            stats.transactions_self += 1
            stats.transactions_total += 1

            ancestors = category.ancestors
            for ancestor in ancestors:
                ancestor_stats = stats_dict[ancestor]
                if ancestor not in transaction.categories:
                    ancestor_stats.transactions_total += 1
                    ancestor_stats.balance += transaction.get_amount_for_category(
                        ancestor, total=True
                    ).convert(base_currency)
                else:  # prevent double counting if both parent and child are present
                    ancestor_stats.balance += transaction.get_amount_for_category(
                        ancestor, total=False
                    ).convert(base_currency)

    return stats_dict
