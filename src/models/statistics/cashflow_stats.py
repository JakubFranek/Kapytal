from collections.abc import Collection
from datetime import timedelta

from src.models.base_classes.account import Account
from src.models.base_classes.transaction import Transaction
from src.models.model_objects.cash_objects import (
    CashTransaction,
    CashTransactionType,
    CashTransfer,
    RefundTransaction,
)
from src.models.model_objects.currency_objects import Currency
from src.models.model_objects.security_objects import (
    SecurityTransaction,
    SecurityTransactionType,
)


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
        "period",
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

        self.period = ""

    def __repr__(self) -> str:
        return "CashFlowStats"


def calculate_cash_flow(
    transactions: Collection[Transaction],
    accounts: Collection[Account],
    base_currency: Currency,
) -> CashFlowStats:
    stats = CashFlowStats(base_currency)

    transactions = sorted(transactions, key=lambda x: x.timestamp)
    earliest_date = transactions[0].datetime_.date() - timedelta(days=1)
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
                stats.expenses += transaction.amount.convert(base_currency)
        elif isinstance(transaction, RefundTransaction):
            stats.refunds += transaction.amount.convert(base_currency)
        elif isinstance(transaction, CashTransfer):
            if transaction.sender in accounts and transaction.recipient in accounts:
                continue
            if transaction.sender in accounts:
                stats.outward_transfers += transaction.amount_sent.convert(
                    base_currency
                )
            if transaction.recipient in accounts:
                stats.inward_transfers += transaction.amount_received.convert(
                    base_currency
                )
        elif isinstance(transaction, SecurityTransaction):
            if (
                transaction.cash_account in accounts
                and transaction.security_account in accounts
            ):
                continue
            if transaction.cash_account in accounts:
                if transaction.type_ == SecurityTransactionType.BUY:
                    stats.outward_transfers += transaction.amount.convert(base_currency)
                else:
                    stats.inward_transfers += transaction.amount.convert(base_currency)
            elif transaction.type_ == SecurityTransactionType.BUY:
                stats.inward_transfers += transaction.amount.convert(base_currency)
            else:
                stats.outward_transfers += transaction.amount.convert(base_currency)

    stats.inflows = stats.incomes + stats.inward_transfers + stats.refunds
    stats.outflows = stats.expenses + stats.outward_transfers

    stats.delta_total = final_balance - initial_balance
    stats.delta_neutral = stats.inflows - stats.outflows
    stats.delta_performance = stats.delta_total - stats.delta_neutral

    return stats


def calculate_monthly_cash_flow(
    transactions: Collection[Transaction],
    accounts: Collection[Account],
    base_currency: Currency,
) -> tuple[CashFlowStats]:
    transactions = sorted(transactions, key=lambda x: x.timestamp)

    # separate transactions into bins by month/year
    transactions_by_month: dict[str, list[Transaction]] = {}
    for transaction in transactions:
        key = transaction.datetime_.strftime("%B %Y")
        if key not in transactions_by_month:
            transactions_by_month[key] = []
        transactions_by_month[key].append(transaction)

    stats_list: list[CashFlowStats] = []
    for month in transactions_by_month:
        stats = calculate_cash_flow(
            transactions_by_month[month],
            accounts,
            base_currency,
        )
        stats.period = month
        stats_list.append(stats)

    stats_list.append(calculate_average_cash_flow(stats_list, base_currency))

    return tuple(stats_list)


def calculate_annual_cash_flow(
    transactions: Collection[Transaction],
    accounts: Collection[Account],
    base_currency: Currency,
) -> tuple[CashFlowStats]:
    transactions = sorted(transactions, key=lambda x: x.timestamp)

    # separate transactions into bins by month/year
    transactions_by_year: dict[str, list[Transaction]] = {}
    for transaction in transactions:
        key = transaction.datetime_.strftime("%Y")
        if key not in transactions_by_year:
            transactions_by_year[key] = []
        transactions_by_year[key].append(transaction)

    stats_list: list[CashFlowStats] = []
    for year in transactions_by_year:
        stats = calculate_cash_flow(
            transactions_by_year[year],
            accounts,
            base_currency,
        )
        stats.period = year
        stats_list.append(stats)

    stats_list.append(calculate_average_cash_flow(stats_list, base_currency))

    return tuple(stats_list)


def calculate_average_cash_flow(
    stats_list: Collection[CashFlowStats], base_currency: Currency
) -> CashFlowStats:
    average = CashFlowStats(base_currency)
    average.period = "Average"
    periods = len(stats_list)
    for stats in stats_list:
        average.incomes += stats.incomes
        average.inward_transfers += stats.inward_transfers
        average.refunds += stats.refunds
        average.inflows += stats.inflows
        average.expenses += stats.expenses
        average.outward_transfers += stats.outward_transfers
        average.outflows += stats.outflows
        average.delta_neutral += stats.delta_neutral
        average.delta_total += stats.delta_total
        average.delta_performance += stats.delta_performance

    average.incomes /= periods
    average.inward_transfers /= periods
    average.refunds /= periods
    average.inflows /= periods
    average.expenses /= periods
    average.outward_transfers /= periods
    average.outflows /= periods
    average.delta_neutral /= periods
    average.delta_total /= periods
    average.delta_performance /= periods

    return average
