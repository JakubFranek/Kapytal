from collections import defaultdict
from collections.abc import Collection
from dataclasses import dataclass, field

from src.models.base_classes.transaction import Transaction
from src.models.model_objects.attributes import Attribute, AttributeType
from src.models.model_objects.cash_objects import (
    CashTransaction,
    RefundTransaction,
)
from src.models.model_objects.currency_objects import CashAmount, Currency
from src.models.model_objects.security_objects import (
    SecurityTransaction,
    SecurityTransactionType,
)
from src.models.statistics.common_classes import TransactionBalance


@dataclass
class AttributeStats:
    attribute: Attribute
    no_of_transactions: int
    balance: CashAmount | None
    transactions: set[CashTransaction | RefundTransaction | SecurityTransaction] = (
        field(default_factory=set)
    )


def calculate_periodic_totals_and_averages(
    periodic_stats: dict[str, tuple[AttributeStats]], currency: Currency
) -> tuple[
    dict[str, TransactionBalance],
    dict[Attribute, TransactionBalance],
    dict[Attribute, TransactionBalance],
    dict[Attribute, TransactionBalance],
    dict[Attribute, TransactionBalance],
    dict[Attribute, TransactionBalance],
    dict[Attribute, TransactionBalance],
]:
    """Returns a tuple of (period_totals, attribute_averages, attribute_totals,
    income_attribute_averages, expense_attribute_averages, income_attribute_totals,
    expense_attribute_totals)"""

    def make_dict() -> defaultdict[Attribute, TransactionBalance]:
        return defaultdict(lambda: TransactionBalance(currency.zero_amount))

    def add_balance(
        target: dict[Attribute, TransactionBalance],
        attribute: Attribute,
        transactions: set[Transaction],
        balance: CashAmount,
    ) -> None:
        target[attribute].add_transaction_balance(transactions, balance)

    def split_income_expense(
        transactions: set[Transaction],
    ) -> tuple[
        set[CashTransaction | RefundTransaction | SecurityTransaction],
        set[CashTransaction | RefundTransaction | SecurityTransaction],
    ]:
        income = {
            transaction
            for transaction in transactions
            if (
                isinstance(transaction, (CashTransaction, RefundTransaction))
                and transaction.get_amount().value_normalized > 0
            )
            or (
                isinstance(transaction, SecurityTransaction)
                and transaction.type_ == SecurityTransactionType.DIVIDEND
            )
        }
        return income, transactions - income

    def average_dict(
        source: dict[Attribute, TransactionBalance],
    ) -> dict[Attribute, TransactionBalance]:
        return {
            attr: TransactionBalance(
                src.balance / len(periodic_stats), src.transactions
            )
            for attr, src in source.items()
        }

    def get_transaction_amount(
        transaction: CashTransaction | RefundTransaction | SecurityTransaction,
        attribute: Attribute,
        currency: Currency,
    ) -> CashAmount:
        return (
            transaction.get_amount_for_tag(attribute).convert(
                currency, transaction.date_
            )
            if attribute.type_ == AttributeType.TAG
            else transaction.get_amount().convert(currency, transaction.date_)
        )

    period_totals: dict[str, TransactionBalance] = {}
    attribute_totals = make_dict()
    income_attribute_totals = make_dict()
    expense_attribute_totals = make_dict()

    for period, stats in periodic_stats.items():
        total_period_balance = TransactionBalance(currency.zero_amount)

        for stat in stats:
            total_period_balance.transactions |= stat.transactions
            total_period_balance.balance += stat.balance

            add_balance(
                attribute_totals, stat.attribute, stat.transactions, stat.balance
            )

            # split income/expense and update respective totals
            income_tx, expense_tx = split_income_expense(stat.transactions)
            add_balance(
                income_attribute_totals,
                stat.attribute,
                income_tx,
                sum(
                    (
                        get_transaction_amount(transaction, stat.attribute, currency)
                        for transaction in income_tx
                    ),
                    start=currency.zero_amount,
                ),
            )
            add_balance(
                expense_attribute_totals,
                stat.attribute,
                expense_tx,
                sum(
                    (
                        get_transaction_amount(transaction, stat.attribute, currency)
                        for transaction in expense_tx
                    ),
                    start=currency.zero_amount,
                ),
            )

        period_totals[period] = total_period_balance

    attribute_averages = average_dict(attribute_totals)
    income_attribute_averages = average_dict(income_attribute_totals)
    expense_attribute_averages = average_dict(expense_attribute_totals)

    return (
        period_totals,
        attribute_averages,
        dict(attribute_totals),
        income_attribute_averages,
        expense_attribute_averages,
        dict(income_attribute_totals),
        dict(expense_attribute_totals),
    )


def calculate_periodic_attribute_stats(
    transactions: Collection[CashTransaction | RefundTransaction | SecurityTransaction],
    base_currency: Currency,
    all_attributes: Collection[Attribute],
    period_format: str = "%B %Y",
) -> dict[str, tuple[AttributeStats, ...]]:
    transactions = sorted(transactions, key=lambda x: x.timestamp)

    # separate transactions into bins by period
    transactions_by_period: dict[
        str, list[CashTransaction | RefundTransaction | SecurityTransaction]
    ] = {}
    for transaction in transactions:
        key = transaction.datetime_.strftime(period_format)
        if key not in transactions_by_period:
            transactions_by_period[key] = []
        transactions_by_period[key].append(transaction)

    stats_dict: dict[str, tuple[AttributeStats, ...]] = {}
    for period, stats in transactions_by_period.items():
        period_stats = calculate_attribute_stats(stats, base_currency, all_attributes)
        stats_dict[period] = tuple(period_stats.values())

    return stats_dict


def calculate_attribute_stats(
    transactions: Collection[Transaction],
    base_currency: Currency | None,
    all_attributes: Collection[Attribute],
) -> dict[Attribute, AttributeStats]:
    """Build AttributeStats for each attribute in all_attributes."""

    attribute_types = {attr.type_ for attr in all_attributes}
    if len(attribute_types) > 1:
        raise ValueError("All Attributes must be of the same type_.")

    attribute_type = attribute_types.pop() if attribute_types else None

    # Initialize stats dict with zero balances
    stats_dict: dict[Attribute, AttributeStats] = {
        attr: AttributeStats(
            attr, 0, base_currency.zero_amount if base_currency else None
        )
        for attr in all_attributes
    }

    if base_currency is None:
        return stats_dict

    for transaction in transactions:
        if not isinstance(
            transaction, (CashTransaction, RefundTransaction, SecurityTransaction)
        ) or (
            isinstance(transaction, SecurityTransaction)
            and transaction.type_ != SecurityTransactionType.DIVIDEND
        ):
            continue

        if attribute_type == AttributeType.TAG:
            for tag in transaction.tags:
                add_to_stats(stats_dict[tag], transaction)
        elif hasattr(transaction, "payee"):
            add_to_stats(stats_dict[transaction.payee], transaction)

    return stats_dict


def split_attribute_stats(
    stats: AttributeStats, base_currency: Currency
) -> tuple[AttributeStats, AttributeStats]:
    """Return (income_stats, expense_stats)."""

    income_stats = AttributeStats(stats.attribute, 0, base_currency.zero_amount)
    expense_stats = AttributeStats(stats.attribute, 0, base_currency.zero_amount)

    for transaction in stats.transactions:
        target = (
            income_stats
            if (
                (
                    isinstance(transaction, (CashTransaction, RefundTransaction))
                    and transaction.get_amount().value_normalized > 0
                )
                or (
                    isinstance(transaction, SecurityTransaction)
                    and transaction.type_ == SecurityTransactionType.DIVIDEND
                )
            )
            else expense_stats
        )
        add_to_stats(target, transaction)

    return income_stats, expense_stats


def add_to_stats(
    target: AttributeStats,
    transaction: CashTransaction | RefundTransaction | SecurityTransaction,
) -> None:
    if target.attribute.type_ == AttributeType.TAG:
        amount = transaction.get_amount_for_tag(target.attribute)
        if amount.value_normalized != 0:
            target.balance += amount.convert(target.balance.currency, transaction.date_)
            target.transactions.add(transaction)
            target.no_of_transactions += 1
    else:
        target.balance += transaction.get_amount().convert(
            target.balance.currency, transaction.date_
        )
        target.transactions.add(transaction)
        target.no_of_transactions += 1
