import itertools
from collections.abc import Collection, Sequence
from dataclasses import dataclass, field

from src.models.model_objects.attributes import Category, CategoryType
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
    balance: CashAmount
    transactions: set[CashTransaction | RefundTransaction] = field(default_factory=set)


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
                if stats.category.type_ == CategoryType.INCOME or (
                    stats.category.type_ == CategoryType.INCOME_AND_EXPENSE
                    and stats.balance.value_rounded > 0
                ):
                    transactions = {
                        transaction
                        for transaction in stats.transactions
                        if (
                            isinstance(transaction, CashTransaction)
                            and transaction.type_ == CashTransactionType.INCOME
                        )
                    }
                    income_balance.add_transaction_balance(transactions, stats.balance)
                elif stats.category.type_ == CategoryType.EXPENSE or (
                    stats.category.type_ == CategoryType.INCOME_AND_EXPENSE
                    and stats.balance.value_rounded < 0
                ):
                    transactions = {
                        transaction
                        for transaction in stats.transactions
                        if (
                            isinstance(transaction, RefundTransaction)
                            or transaction.type_ == CashTransactionType.EXPENSE
                        )
                    }
                    expense_balance.add_transaction_balance(transactions, stats.balance)

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


def calculate_average_per_period_category_stats(
    periodic_stats: dict[str, tuple[CategoryStats]],
) -> dict[Category, CategoryStats]:
    base_currency = next(iter(periodic_stats.values()))[0].balance.currency
    all_stats = list(itertools.chain(*periodic_stats.values()))
    periods = len(periodic_stats)

    average_stats: dict[Category, CategoryStats] = {}
    for stats in all_stats:
        if stats.category in average_stats:
            _average_stats = average_stats[stats.category]
            _average_stats.balance += stats.balance
            _average_stats.transactions_self += stats.transactions_self
            _average_stats.transactions_total += stats.transactions_total
            _average_stats.transactions.add(*stats.transactions)
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
        date_ = transaction.datetime_.date()
        for category in transaction.categories:
            stats = stats_dict[category]
            stats.transactions.add(transaction)

            stats.balance += transaction.get_amount_for_category(
                category, total=False
            ).convert(base_currency)
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
