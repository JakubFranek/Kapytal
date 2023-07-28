from collections.abc import Collection
from datetime import timedelta

from src.models.base_classes.account import Account
from src.models.base_classes.transaction import Transaction
from src.models.model_objects.cash_objects import (
    CashAccount,
    CashTransaction,
    CashTransactionType,
    CashTransfer,
    RefundTransaction,
)
from src.models.model_objects.currency_objects import Currency
from src.models.model_objects.security_objects import (
    SecurityAccount,
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
        "initial_balances",
        "delta_total",
        "delta_neutral",
        "delta_performance",
        "delta_performance_securities",
        "delta_performance_currencies",
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
        self.initial_balances = base_currency.zero_amount

        self.delta_total = base_currency.zero_amount
        self.delta_neutral = base_currency.zero_amount
        self.delta_performance = base_currency.zero_amount
        self.delta_performance_securities = base_currency.zero_amount
        self.delta_performance_currencies = base_currency.zero_amount

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
    start_date = transactions[0].datetime_.date() - timedelta(days=1)
    final_date = transactions[-1].datetime_.date()

    start_balance = base_currency.zero_amount
    final_balance = base_currency.zero_amount
    for account in accounts:
        start_balance += account.get_balance(base_currency, start_date)
        final_balance += account.get_balance(base_currency, final_date)
        if isinstance(account, CashAccount):
            initial_balance_date = account.balance_history[0][0].date()
            if start_date <= initial_balance_date <= final_date:
                stats.initial_balances += account.initial_balance.convert(
                    base_currency, initial_balance_date
                )

    delta_security = base_currency.zero_amount
    security_accounts = [
        account for account in accounts if isinstance(account, SecurityAccount)
    ]
    for account in security_accounts:
        delta_security -= account.get_balance(base_currency, start_date)
        delta_security += account.get_balance(base_currency, final_date)

    for transaction in transactions:
        date_ = transaction.datetime_.date()
        if isinstance(transaction, CashTransaction):
            if transaction.type_ == CashTransactionType.INCOME:
                stats.incomes += transaction.amount.convert(base_currency, date_)
            else:
                stats.expenses += transaction.amount.convert(base_currency, date_)
        elif isinstance(transaction, RefundTransaction):
            stats.refunds += transaction.amount.convert(base_currency, date_)
        elif isinstance(transaction, CashTransfer):
            if transaction.sender in accounts and transaction.recipient in accounts:
                continue
            if transaction.sender in accounts:
                stats.outward_transfers += transaction.amount_sent.convert(
                    base_currency, date_
                )
            if transaction.recipient in accounts:
                stats.inward_transfers += transaction.amount_received.convert(
                    base_currency, date_
                )
        elif isinstance(transaction, SecurityTransaction):
            if (
                transaction.cash_account in accounts
                and transaction.security_account in accounts
            ):
                if transaction.type_ == SecurityTransactionType.BUY:
                    delta_security -= transaction.amount.convert(base_currency, date_)
                else:
                    delta_security += transaction.amount.convert(base_currency, date_)
                continue
            if transaction.cash_account in accounts:
                if transaction.type_ == SecurityTransactionType.BUY:
                    stats.outward_transfers += transaction.amount.convert(
                        base_currency, date_
                    )
                else:
                    stats.inward_transfers += transaction.amount.convert(
                        base_currency, date_
                    )
            elif transaction.type_ == SecurityTransactionType.BUY:
                stats.inward_transfers += transaction.amount.convert(
                    base_currency, date_
                )
            else:
                stats.outward_transfers += transaction.amount.convert(
                    base_currency, date_
                )

    stats.inflows = (
        stats.incomes + stats.inward_transfers + stats.refunds + stats.initial_balances
    )
    stats.outflows = stats.expenses + stats.outward_transfers

    stats.delta_total = final_balance - start_balance
    stats.delta_neutral = stats.inflows - stats.outflows
    stats.delta_performance = stats.delta_total - stats.delta_neutral
    stats.delta_performance_securities = delta_security
    stats.delta_performance_currencies = (
        stats.delta_performance - stats.delta_performance_securities
    )

    return stats


def calculate_periodic_cash_flow(
    transactions: Collection[Transaction],
    accounts: Collection[Account],
    base_currency: Currency,
    period_format: str,
) -> tuple[CashFlowStats]:
    transactions = sorted(transactions, key=lambda x: x.timestamp)

    # separate transactions into bins by period
    transactions_by_period: dict[str, list[Transaction]] = {}
    for transaction in transactions:
        key = transaction.datetime_.strftime(period_format)
        if key not in transactions_by_period:
            transactions_by_period[key] = []
        transactions_by_period[key].append(transaction)

    stats_list: list[CashFlowStats] = []
    for period in transactions_by_period:
        stats = calculate_cash_flow(
            transactions_by_period[period],
            accounts,
            base_currency,
        )
        stats.period = period
        stats_list.append(stats)

    _stats_list = stats_list.copy()
    _stats_list.append(calculate_average_cash_flow(stats_list, base_currency))
    _stats_list.append(calculate_total_cash_flow(stats_list, base_currency))

    return tuple(_stats_list)


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
        average.initial_balances += stats.initial_balances
        average.inflows += stats.inflows
        average.expenses += stats.expenses
        average.outward_transfers += stats.outward_transfers
        average.outflows += stats.outflows
        average.delta_neutral += stats.delta_neutral
        average.delta_total += stats.delta_total
        average.delta_performance += stats.delta_performance
        average.delta_performance_securities += stats.delta_performance_securities
        average.delta_performance_currencies += stats.delta_performance_currencies

    average.incomes /= periods
    average.inward_transfers /= periods
    average.refunds /= periods
    average.initial_balances /= periods
    average.inflows /= periods
    average.expenses /= periods
    average.outward_transfers /= periods
    average.outflows /= periods
    average.delta_neutral /= periods
    average.delta_total /= periods
    average.delta_performance /= periods
    average.delta_performance_securities /= periods
    average.delta_performance_currencies /= periods

    return average


def calculate_total_cash_flow(
    stats_list: Collection[CashFlowStats], base_currency: Currency
) -> CashFlowStats:
    total = CashFlowStats(base_currency)
    total.period = "Total"
    for stats in stats_list:
        total.incomes += stats.incomes
        total.inward_transfers += stats.inward_transfers
        total.refunds += stats.refunds
        total.initial_balances += stats.initial_balances
        total.inflows += stats.inflows
        total.expenses += stats.expenses
        total.outward_transfers += stats.outward_transfers
        total.outflows += stats.outflows
        total.delta_neutral += stats.delta_neutral
        total.delta_total += stats.delta_total
        total.delta_performance += stats.delta_performance
        total.delta_performance_securities += stats.delta_performance_securities
        total.delta_performance_currencies += stats.delta_performance_currencies

    return total
