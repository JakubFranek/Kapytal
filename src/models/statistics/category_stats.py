import itertools
from collections.abc import Collection, Sequence
from dataclasses import dataclass

from src.models.model_objects.attributes import Category, CategoryType
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


def calculate_periodic_totals_and_averages(
    periodic_stats: dict[str, Sequence[CategoryStats]], currency: Currency
) -> tuple[
    dict[str, CashAmount],
    dict[str, CashAmount],
    dict[str, CashAmount],
    dict[Category, CashAmount],
    dict[Category, CashAmount],
]:
    """Returns a tuple of (period_totals, period_income_totals, period_expense_totals,
    category_averages, category_totals)"""

    category_totals: dict[Category, CashAmount] = {}
    period_totals: dict[str, CashAmount] = {}
    period_income_totals: dict[str, CashAmount] = {}
    period_expense_totals: dict[str, CashAmount] = {}
    category_averages: dict[Category, CashAmount] = {}

    for period in periodic_stats:
        period_income_totals[period] = sum(
            (
                stats.balance
                for stats in periodic_stats[period]
                if (
                    stats.category.type_ == CategoryType.INCOME
                    or (
                        stats.category.type_ == CategoryType.INCOME_AND_EXPENSE
                        and stats.balance.value_rounded > 0
                    )
                )
                and stats.category.parent is None
            ),
            start=currency.zero_amount,
        )
        period_expense_totals[period] = sum(
            (
                stats.balance
                for stats in periodic_stats[period]
                if (
                    stats.category.type_ == CategoryType.EXPENSE
                    or (
                        stats.category.type_ == CategoryType.INCOME_AND_EXPENSE
                        and stats.balance.value_rounded < 0
                    )
                )
                and stats.category.parent is None
            ),
            start=currency.zero_amount,
        )
        period_totals[period] = (
            period_income_totals[period] + period_expense_totals[period]
        )
        for stats in periodic_stats[period]:
            category_totals[stats.category] = (
                category_totals.get(stats.category, currency.zero_amount)
                + stats.balance
            )
    category_averages = {
        category: category_totals[category] / len(periodic_stats)
        for category in category_totals
    }
    return (
        period_totals,
        period_income_totals,
        period_expense_totals,
        category_averages,
        category_totals,
    )


def calculate_periodic_category_stats(
    transactions: Collection[CashTransaction | RefundTransaction],
    base_currency: Currency,
    all_categories: Collection[Category],
    period_format: str = "%B %Y",
) -> dict[str, tuple[CategoryStats]]:
    transactions = sorted(transactions, key=lambda x: x.timestamp)

    # separate transactions into bins by period
    transactions_by_period: dict[str, list[CashTransaction | RefundTransaction]] = {}
    for transaction in transactions:
        key = transaction.datetime_.strftime(period_format)
        if key not in transactions_by_period:
            transactions_by_period[key] = []
        transactions_by_period[key].append(transaction)

    stats_dict: dict[str, tuple[CategoryStats]] = {}
    for period in transactions_by_period:
        period_stats = calculate_category_stats(
            transactions_by_period[period], base_currency, all_categories
        )
        stats_dict[period] = tuple(period_stats.values())

    return stats_dict


def calculate_average_per_period_category_stats(
    periodic_stats: dict[str, tuple[CategoryStats]],
) -> dict[Category, CategoryStats]:
    base_currency = list(periodic_stats.values())[0][0].balance.currency
    all_stats = list(itertools.chain(*periodic_stats.values()))
    periods = len(periodic_stats)

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
