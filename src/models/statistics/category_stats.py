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
    transactions_self: int
    transactions_total: int
    balance: CashAmount


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
