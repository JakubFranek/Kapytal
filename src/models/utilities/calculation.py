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
