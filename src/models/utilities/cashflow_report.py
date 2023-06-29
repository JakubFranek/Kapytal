from collections.abc import Collection

from src.models.base_classes.account import Account
from src.models.model_objects.cash_objects import (
    CashTransaction,
    CashTransactionType,
    CashTransfer,
    RefundTransaction,
)
from src.models.model_objects.currency_objects import Currency


class CashFlowStats:
    __slots__ = (
        "incomes",
        "expenses",
        "refunds",
        "inward_transfers",
        "outward_transfers",
        "delta_total",
        "delta_neutral",
        "delta_performance",
        "inflows",
        "outflows",
    )

    def __init__(self, base_currency: Currency) -> None:
        self.incomes = base_currency.zero_amount
        self.expenses = base_currency.zero_amount
        self.refunds = base_currency.zero_amount
        self.inward_transfers = base_currency.zero_amount
        self.outward_transfers = base_currency.zero_amount

        self.delta_total = base_currency.zero_amount
        self.delta_neutral = base_currency.zero_amount
        self.delta_performance = base_currency.zero_amount

        self.inflows = base_currency.zero_amount
        self.outflows = base_currency.zero_amount

    def __repr__(self) -> str:
        return "CashFlowStats"


def calculate_cash_flow(
    transactions: Collection[CashTransaction | RefundTransaction],
    accounts: Collection[Account],
    base_currency: Currency,
) -> CashFlowStats:
    stats = CashFlowStats(base_currency)

    transactions = sorted(transactions, key=lambda x: x.timestamp)
    earliest_date = transactions[0].datetime_.date()
    latest_date = transactions[-1].datetime_.date()

    initial_balance = base_currency.zero_amount
    final_balance = base_currency.zero_amount
    for account in accounts:
        initial_balance += account.get_balance(base_currency, earliest_date)
        final_balance += account.get_balance(base_currency, latest_date)

    for transaction in transactions:
        if isinstance(transaction, CashTransaction):
            if transaction.type_ == CashTransactionType.INCOME:
                stats.incomes += transaction.amount.convert(base_currency)
            else:
                stats.expenses -= transaction.amount.convert(base_currency)
        if isinstance(transaction, RefundTransaction):
            stats.refunds += transaction.amount.convert(base_currency)
        if isinstance(transaction, CashTransfer):
            if transaction.sender in accounts and transaction.recipient in accounts:
                continue
            if transaction.sender in accounts:
                stats.outward_transfers -= transaction.amount.convert(base_currency)
            if transaction.recipient in accounts:
                stats.inward_transfers += transaction.amount.convert(base_currency)

    stats.delta_total = final_balance - initial_balance
    stats.delta_neutral = (
        stats.incomes
        + stats.refunds
        + stats.inward_transfers
        + stats.expenses
        + stats.outward_transfers
    )
    stats.delta_performance = stats.delta_total - stats.delta_neutral

    stats.inflows = stats.incomes + stats.inward_transfers + stats.refunds
    stats.outflows = stats.expenses + stats.outward_transfers

    return stats
