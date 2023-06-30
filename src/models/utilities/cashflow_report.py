from collections.abc import Collection

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
    average.incomes = sum(
        (stats.incomes for stats in stats_list), start=base_currency.zero_amount
    ) / len(stats_list)
    average.inward_transfers = sum(
        (stats.inward_transfers for stats in stats_list),
        start=base_currency.zero_amount,
    ) / len(stats_list)
    average.refunds = sum(
        (stats.refunds for stats in stats_list), start=base_currency.zero_amount
    ) / len(stats_list)
    average.inflows = sum(
        (stats.inflows for stats in stats_list), start=base_currency.zero_amount
    ) / len(stats_list)
    average.expenses = sum(
        (stats.expenses for stats in stats_list), start=base_currency.zero_amount
    ) / len(stats_list)
    average.outward_transfers = sum(
        (stats.outward_transfers for stats in stats_list),
        start=base_currency.zero_amount,
    ) / len(stats_list)
    average.outflows = sum(
        (stats.outflows for stats in stats_list), start=base_currency.zero_amount
    ) / len(stats_list)
    average.delta_total = sum(
        (stats.delta_total for stats in stats_list), start=base_currency.zero_amount
    ) / len(stats_list)
    average.delta_neutral = sum(
        (stats.delta_neutral for stats in stats_list), start=base_currency.zero_amount
    ) / len(stats_list)
    average.delta_performance = sum(
        (stats.delta_performance for stats in stats_list),
        start=base_currency.zero_amount,
    ) / len(stats_list)

    return average
