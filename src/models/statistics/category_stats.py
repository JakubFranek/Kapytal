import itertools
from collections.abc import Collection
from dataclasses import dataclass

from src.models.model_objects.attributes import Category
from src.models.model_objects.cash_objects import (
    CashTransaction,
    RefundTransaction,
)
from src.models.model_objects.currency_objects import CashAmount, Currency


@dataclass
class CategoryStats:
    category: Category
    transactions_self: int | float
    transactions_total: int | float
    balance: CashAmount


def calculate_monthly_totals_and_averages(
    monthly_stats: dict[str, tuple[CategoryStats]]
) -> tuple[
    dict[str, CashAmount], dict[Category, CashAmount], dict[Category, CashAmount]
]:
    """Returns a tuple of (month_totals, category_averages, category_totals)"""
    category_totals: dict[Category, CashAmount] = {}
    month_totals: dict[str, CashAmount] = {}
    category_averages: dict[Category, CashAmount] = {}

    currency = None
    for month in monthly_stats:
        if len(monthly_stats[month]) == 0:
            continue
        currency = monthly_stats[month][0].balance.currency
    if currency is None:
        raise ValueError("No data found within 'monthly_stats'.")

    for month in monthly_stats:
        month_totals[month] = sum(
            (stats.balance for stats in monthly_stats[month]),
            start=currency.zero_amount,
        )
        for stats in monthly_stats[month]:
            category_totals[stats.category] = (
                category_totals.get(stats.category, currency.zero_amount)
                + stats.balance
            )
    category_averages = {
        category: category_totals[category] / len(monthly_stats)
        for category in category_totals
    }
    return month_totals, category_averages, category_totals


def calculate_monthly_category_stats(
    transactions: Collection[CashTransaction | RefundTransaction],
    base_currency: Currency,
    all_categories: Collection[Category],
    period_format: str = "%B %Y",
) -> dict[str, tuple[CategoryStats]]:
    transactions = sorted(transactions, key=lambda x: x.timestamp)

    # separate transactions into bins by month/year
    transactions_by_month: dict[str, list[CashTransaction | RefundTransaction]] = {}
    for transaction in transactions:
        key = transaction.datetime_.strftime(period_format)
        if key not in transactions_by_month:
            transactions_by_month[key] = []
        transactions_by_month[key].append(transaction)

    stats_dict: dict[str, tuple[CategoryStats]] = {}
    for month in transactions_by_month:
        monthly_stats = calculate_category_stats(
            transactions_by_month[month], base_currency, all_categories
        )
        stats_dict[month] = tuple(monthly_stats.values())

    return stats_dict


def calculate_average_per_month_category_stats(
    stats_per_month: dict[str, tuple[CategoryStats]],
) -> dict[Category, CategoryStats]:
    base_currency = list(stats_per_month.values())[0][0].balance.currency
    all_stats = list(itertools.chain(*stats_per_month.values()))
    periods = len(stats_per_month)

    average_stats: dict[Category, CategoryStats] = {}
    for stats in all_stats:
        if stats.category in average_stats:
            average_stats[stats.category].balance += stats.balance
            average_stats[stats.category].transactions_self += stats.transactions_self
            average_stats[stats.category].transactions_total += stats.transactions_total
        else:
            average_stats[stats.category] = CategoryStats(
                stats.category, 0, 0, base_currency.zero_amount
            )

    for stats in average_stats.values():
        stats.balance = stats.balance / periods
        stats.transactions_self = round(stats.transactions_self / periods, 2)
        stats.transactions_total = round(stats.transactions_total / periods, 2)

    return average_stats


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
        already_counted_ancestors = set()
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
                if (
                    ancestor not in transaction.categories
                    and ancestor not in already_counted_ancestors
                ):
                    ancestor_stats.transactions_total += 1
                    ancestor_stats.balance += transaction.get_amount_for_category(
                        ancestor, total=True
                    ).convert(base_currency)
                    already_counted_ancestors.add(ancestor)
                else:  # prevent double counting if both parent and child are present
                    ancestor_stats.balance += transaction.get_amount_for_category(
                        ancestor, total=False
                    ).convert(base_currency)

    return stats_dict
