from collections.abc import Collection, Sequence
from dataclasses import dataclass, field

from src.models.model_objects.attributes import Category
from src.models.model_objects.cash_objects import (
    CashTransaction,
    CashTransactionType,
    RefundTransaction,
)
from src.models.model_objects.currency_objects import CashAmount, Currency
from src.models.statistics.common_classes import TransactionBalance


@dataclass
class CategoryStats:
    category: Category
    transactions_self: int | float
    transactions_total: int | float
    balance: CashAmount | None
    transactions: set[CashTransaction | RefundTransaction] = field(default_factory=set)


# TODO: add all-encompassing class which would store all stats, averages,
# totals etc. and would cleanly interface with the view model


def calculate_periodic_totals_and_averages(
    periodic_stats: dict[str, Sequence[CategoryStats]], currency: Currency
) -> tuple[
    dict[str, TransactionBalance],
    dict[str, TransactionBalance],
    dict[str, TransactionBalance],
    dict[Category, TransactionBalance],
    dict[Category, TransactionBalance],
]:
    """Returns a tuple of (period_totals, period_income_totals, period_expense_totals,
    category_averages, category_totals)"""

    period_totals: dict[str, TransactionBalance] = {}
    period_income_totals: dict[str, TransactionBalance] = {}
    period_expense_totals: dict[str, TransactionBalance] = {}
    category_averages: dict[Category, TransactionBalance] = {}
    category_totals: dict[Category, TransactionBalance] = {
        stat.category: TransactionBalance(currency.zero_amount)
        for stats in periodic_stats.values()
        for stat in stats
    }

    for period in periodic_stats:
        income_balance = TransactionBalance(currency.zero_amount)
        expense_balance = TransactionBalance(currency.zero_amount)
        total_balance = TransactionBalance(currency.zero_amount)

        for stats in periodic_stats[period]:
            total_balance.transactions = total_balance.transactions.union(
                stats.transactions
            )

            if stats.category.parent is None:
                total_balance.balance += stats.balance
                income_data = TransactionBalance(currency.zero_amount)
                expense_data = TransactionBalance(currency.zero_amount)

                for transaction in stats.transactions:
                    date_ = transaction.date_
                    amount = transaction.get_amount_for_category(
                        stats.category, total=True
                    ).convert(currency, date_)
                    if (
                        isinstance(transaction, CashTransaction)
                        and transaction.type_ == CashTransactionType.INCOME
                    ):
                        income_data.add_transaction_balance({transaction}, amount)
                    else:
                        expense_data.add_transaction_balance({transaction}, amount)

                income_balance += income_data
                expense_balance += expense_data

            category_totals[stats.category].add_transaction_balance(
                stats.transactions, stats.balance
            )

        period_income_totals[period] = income_balance
        period_expense_totals[period] = expense_balance
        period_totals[period] = total_balance

    category_averages = {
        category: TransactionBalance(
            category_totals[category].balance / len(periodic_stats),
            category_totals[category].transactions,
        )
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


def calculate_category_stats(
    transactions: Collection[CashTransaction | RefundTransaction],
    base_currency: Currency | None,
    categories: Collection[Category],
) -> dict[Category, CategoryStats]:
    stats_dict: dict[Category, CategoryStats] = {}
    for category in categories:
        if base_currency is None:
            stats = CategoryStats(category, 0, 0, None)
        else:
            stats = CategoryStats(category, 0, 0, base_currency.zero_amount)
        stats_dict[category] = stats

    if base_currency is None:
        return stats_dict

    for transaction in transactions:
        already_counted_ancestors = set()
        date_ = transaction.date_
        for category in transaction.categories:
            stats = stats_dict[category]
            stats.transactions.add(transaction)

            stats.balance += transaction.get_amount_for_category(
                category, total=False
            ).convert(base_currency, date_)
            stats.transactions_self += 1
            stats.transactions_total += 1

            ancestors = category.ancestors
            for ancestor in ancestors:
                ancestor_stats = stats_dict[ancestor]
                ancestor_stats.transactions.add(transaction)
                if (
                    ancestor not in transaction.categories
                    and ancestor not in already_counted_ancestors
                ):
                    ancestor_stats.transactions_total += 1
                    ancestor_stats.balance += transaction.get_amount_for_category(
                        ancestor, total=True
                    ).convert(base_currency, date_)
                    already_counted_ancestors.add(ancestor)
                else:  # prevent double counting if both parent and child are present
                    ancestor_stats.balance += transaction.get_amount_for_category(
                        ancestor, total=False
                    ).convert(base_currency, date_)

    return stats_dict
