from collections.abc import Collection
from dataclasses import dataclass
from datetime import date, timedelta
from decimal import Decimal
from enum import Enum, auto

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
    SecurityTransaction,
    SecurityTransactionType,
)
from src.models.statistics.common_classes import TransactionBalance


class PeriodType(Enum):
    MONTH = auto()
    YEAR = auto()


@dataclass
class Period:
    name: str
    start: date
    end: date

    def __eq__(self, __value: object) -> bool:
        if not isinstance(__value, Period):
            return NotImplemented
        return (
            self.name == __value.name
            and self.start == __value.start
            and self.end == __value.end
        )

    def __hash__(self) -> int:
        return hash((self.name, self.start, self.end))

    def __repr__(self) -> str:
        return f"Period({self.name})"


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
        "savings_rate",
        "period",
    )

    def __init__(self, base_currency: Currency) -> None:
        self.incomes = TransactionBalance(base_currency.zero_amount)
        self.expenses = TransactionBalance(base_currency.zero_amount)
        self.refunds = TransactionBalance(base_currency.zero_amount)
        self.inward_transfers = TransactionBalance(base_currency.zero_amount)
        self.outward_transfers = TransactionBalance(base_currency.zero_amount)
        self.initial_balances = base_currency.zero_amount

        self.delta_total = base_currency.zero_amount
        self.delta_neutral = TransactionBalance(base_currency.zero_amount)
        self.delta_performance = base_currency.zero_amount
        self.delta_performance_securities = base_currency.zero_amount
        self.delta_performance_currencies = base_currency.zero_amount

        self.inflows = TransactionBalance(base_currency.zero_amount)
        self.outflows = TransactionBalance(base_currency.zero_amount)

        self.savings_rate = Decimal(0)

        self.period = ""

    def __repr__(self) -> str:
        return f"CashFlowStats({self.period})"


def calculate_cash_flow(
    transactions: Collection[Transaction],
    accounts: Collection[Account],
    base_currency: Currency,
    start_date: date | None = None,
    end_date: date | None = None,
) -> CashFlowStats:
    stats = CashFlowStats(base_currency)

    transactions = sorted(transactions, key=lambda x: x.timestamp)
    if start_date is None:
        start_date = transactions[0].datetime_.date()
    if end_date is None:
        end_date = transactions[-1].datetime_.date()

    start_balance = base_currency.zero_amount
    end_balance = base_currency.zero_amount
    delta_security = base_currency.zero_amount
    for account in accounts:
        # start balance is the ending balance of previous day
        _start_balance = account.get_balance(
            base_currency, start_date - timedelta(days=1)
        )
        _end_balance = account.get_balance(base_currency, end_date)
        start_balance += _start_balance
        end_balance += _end_balance
        if isinstance(account, CashAccount):
            initial_balance_date = account.balance_history[0][0].date()
            if start_date <= initial_balance_date <= end_date:
                stats.initial_balances += account.initial_balance.convert(
                    base_currency, initial_balance_date
                )
        else:
            delta_security -= _start_balance
            delta_security += _end_balance

    for transaction in transactions:
        date_ = transaction.datetime_.date()
        if date_ < start_date or date_ > end_date:
            raise ValueError(f"Unexpected Transaction date: {date_}")
        if isinstance(transaction, CashTransaction):
            if transaction.type_ == CashTransactionType.INCOME:
                stats.incomes.balance += transaction.amount.convert(
                    base_currency, date_
                )
                stats.incomes.transactions.add(transaction)
            else:
                stats.expenses.balance += transaction.amount.convert(
                    base_currency, date_
                )
                stats.expenses.transactions.add(transaction)
        elif isinstance(transaction, RefundTransaction):
            stats.refunds.balance += transaction.amount.convert(base_currency, date_)
            stats.refunds.transactions.add(transaction)
        elif isinstance(transaction, CashTransfer):
            if transaction.sender in accounts and transaction.recipient in accounts:
                continue
            if transaction.sender in accounts:
                stats.outward_transfers.balance += transaction.amount_sent.convert(
                    base_currency, date_
                )
                stats.outward_transfers.transactions.add(transaction)
            if transaction.recipient in accounts:
                stats.inward_transfers.balance += transaction.amount_received.convert(
                    base_currency, date_
                )
                stats.inward_transfers.transactions.add(transaction)
        elif isinstance(transaction, SecurityTransaction):
            if (
                transaction.cash_account in accounts
                and transaction.security_account in accounts
            ):
                if transaction.type_ == SecurityTransactionType.BUY:
                    delta_security -= transaction.amount.convert(base_currency, date_)
                else:
                    delta_security += transaction.amount.convert(base_currency, date_)
            elif transaction.cash_account in accounts:
                if transaction.type_ == SecurityTransactionType.BUY:
                    stats.outward_transfers.balance += transaction.amount.convert(
                        base_currency, date_
                    )
                    stats.outward_transfers.transactions.add(transaction)
                else:
                    stats.inward_transfers.balance += transaction.amount.convert(
                        base_currency, date_
                    )
                    stats.inward_transfers.transactions.add(transaction)
            elif transaction.type_ == SecurityTransactionType.BUY:
                stats.inward_transfers.balance += transaction.amount.convert(
                    base_currency, date_
                )
                stats.inward_transfers.transactions.add(transaction)
            else:
                stats.outward_transfers.balance += transaction.amount.convert(
                    base_currency, date_
                )
                stats.outward_transfers.transactions.add(transaction)
            # TODO: handle SecurityTransfers

    stats.inflows = stats.incomes + stats.inward_transfers + stats.refunds
    stats.inflows.balance += stats.initial_balances
    stats.outflows = stats.expenses + stats.outward_transfers

    stats.delta_total = end_balance - start_balance  # net growth
    stats.delta_neutral = stats.inflows - stats.outflows  # cash flow
    stats.delta_performance = (  # gain/loss
        stats.delta_total - stats.delta_neutral.balance
    )
    stats.delta_performance_securities = delta_security
    stats.delta_performance_currencies = (
        stats.delta_performance - stats.delta_performance_securities
    )

    savings_rate_eligible_inflow = (
        stats.incomes.balance + stats.inward_transfers.balance + stats.initial_balances
    )
    if savings_rate_eligible_inflow.value_normalized != 0:
        stats.savings_rate = stats.delta_neutral.balance / savings_rate_eligible_inflow
    else:
        stats.savings_rate = Decimal("NaN")

    return stats


def calculate_periodic_cash_flow(
    transactions: Collection[Transaction],
    accounts: Collection[Account],
    base_currency: Currency,
    period_type: PeriodType,
    start_date: date | None,
    end_date: date | None,
) -> tuple[CashFlowStats]:
    transactions = sorted(transactions, key=lambda x: x.timestamp)
    start_date = transactions[0].datetime_.date() if start_date is None else start_date
    end_date = transactions[-1].datetime_.date() if end_date is None else end_date

    periods = get_periods(start_date, end_date, period_type)
    period_format = "%Y" if period_type == PeriodType.YEAR else "%b %Y"

    # separate transactions into bins by period
    transactions_by_period: dict[Period, list[Transaction]] = {}
    for transaction in transactions:
        key = transaction.datetime_.strftime(period_format)
        period = periods[key]
        if period not in transactions_by_period:
            transactions_by_period[period] = []
        transactions_by_period[period].append(transaction)

    stats_list: list[CashFlowStats] = []
    for period, transactions in transactions_by_period.items():
        stats = calculate_cash_flow(
            transactions,
            accounts,
            base_currency,
            start_date=period.start,
            end_date=period.end,
        )
        stats.period = period.name
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
        if not stats.savings_rate.is_nan():
            average.savings_rate += stats.savings_rate

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
    average.savings_rate /= periods

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

    total.savings_rate = Decimal("NaN")
    return total


def get_periods(
    start_date: date, end_date: date, type_: PeriodType
) -> dict[str, Period]:
    periods: list[Period] = []
    if type_ == PeriodType.MONTH:
        earliest_period_name = start_date.strftime("%b %Y")
        earliest_period_start = start_date
        earliest_period_end = get_last_day_of_month(earliest_period_start)
        if earliest_period_end > end_date:
            earliest_period_end = end_date
        earliest_period = Period(
            name=earliest_period_name,
            start=earliest_period_start,
            end=earliest_period_end,
        )
        periods.append(earliest_period)
        while end_date > periods[-1].end:
            period_start = periods[-1].end + timedelta(days=1)
            period_end = get_last_day_of_month(period_start)
            if period_end > end_date:
                period_end = end_date
            period_name = period_start.strftime("%b %Y")
            period = Period(
                name=period_name,
                start=period_start,
                end=period_end,
            )
            periods.append(period)
    elif type_ == PeriodType.YEAR:
        earliest_period_name = start_date.strftime("%Y")
        earliest_period_start = start_date
        earliest_period_end = start_date.replace(month=12, day=31)
        if earliest_period_end > end_date:
            earliest_period_end = end_date
        earliest_period = Period(
            name=earliest_period_name,
            start=earliest_period_start,
            end=earliest_period_end,
        )
        periods.append(earliest_period)
        while end_date > periods[-1].end:
            period_start = periods[-1].end + timedelta(days=1)
            period_end = period_start.replace(year=period_start.year + 1) - timedelta(
                days=1
            )
            if period_end > end_date:
                period_end = end_date
            period_name = period_start.strftime("%Y")
            period = Period(
                name=period_name,
                start=period_start,
                end=period_end,
            )
            periods.append(period)
    return {period.name: period for period in periods}


def get_last_day_of_month(any_day: date) -> date:
    # The day 28 exists in every month. 4 days later, it's always next month
    next_month = any_day.replace(day=28) + timedelta(days=4)
    # subtracting the number of the current day brings us back one month
    return next_month - timedelta(days=next_month.day)
