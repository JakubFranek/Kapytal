from collections.abc import Collection
from datetime import date, datetime
from decimal import Decimal
from enum import Enum, auto

from pyxirr import InvalidPaymentsError, xirr
from src.models.model_objects.currency_objects import Currency
from src.models.model_objects.security_objects import (
    Security,
    SecurityAccount,
    SecurityRelatedTransaction,
    SecurityTransaction,
    SecurityTransactionType,
    SecurityTransfer,
    SharesType,
)
from src.models.user_settings import user_settings


class SecurityStatsType(Enum):
    TOTAL = auto()
    REALIZED = auto()
    UNREALIZED = auto()


class SecurityStatsData:
    def __init__(
        self,
        securities: Collection[Security],
        accounts: Collection[SecurityAccount],
        base_currency: Currency,
    ) -> None:
        self.securities = tuple(securities)
        self.accounts = frozenset(accounts)
        self.base_currency = base_currency

        _security_stats: list[SecurityStats] = []
        for security in self.securities:
            stats = SecurityStats(security, accounts, base_currency)
            _security_stats.append(stats)
        self.security_stats = tuple(_security_stats)

        self.total_stats = TotalSecurityStats(self.security_stats, base_currency)

    def __repr__(self) -> str:
        return f"SecurityStatsData(len={len(self.security_stats)})"


class SecurityStats:
    def __init__(
        self,
        security: Security,
        accounts: Collection[SecurityAccount],
        base_currency: Currency,
    ) -> None:
        self.security = security
        self.accounts = frozenset(
            account for account in accounts if security in account.related_securities
        )
        self.base_currency = base_currency

        _account_stats: list[SecurityAccountStats] = []
        _transactions: set[SecurityRelatedTransaction] = set()
        for account in self.accounts:
            stats = SecurityAccountStats(security, account, base_currency)
            _account_stats.append(stats)
            _transactions.update(stats.transactions)
        self.account_stats = tuple(_account_stats)
        self.transactions = frozenset(_transactions)

        self.name = security.name

        self.shares_owned = sum(stats.shares_owned for stats in self.account_stats)
        self.shares_bought = sum(stats.shares_bought for stats in self.account_stats)
        self.shares_sold = sum(stats.shares_sold for stats in self.account_stats)
        self.shares_transferred = Decimal(0)

        self.price_market_native = security.price
        self.price_market_base = security.price.convert(base_currency)
        self.price_avg_buy_native = (
            sum(
                (
                    stats.price_avg_buy_native * stats.shares_bought
                    for stats in self.account_stats
                ),
                start=security.currency.zero_amount,
            )
            / self.shares_bought
        )
        self.price_avg_buy_base = (
            sum(
                (
                    stats.price_avg_buy_base * stats.shares_bought
                    for stats in self.account_stats
                ),
                start=base_currency.zero_amount,
            )
            / self.shares_bought
        )
        self.price_avg_sell_native = (
            sum(
                (
                    stats.price_avg_sell_native * stats.shares_sold
                    for stats in self.account_stats
                ),
                start=security.currency.zero_amount,
            )
            / self.shares_sold
        )
        self.price_avg_sell_base = (
            sum(
                (
                    stats.price_avg_sell_base * stats.shares_sold
                    for stats in self.account_stats
                ),
                start=base_currency.zero_amount,
            )
            / self.shares_sold
        )

        self.value_current_native = self.price_market_native * self.shares_owned
        self.value_current_base = self.price_market_base * self.shares_owned
        self.value_sold_native = self.price_avg_sell_native * self.shares_sold
        self.value_sold_base = self.price_avg_sell_base * self.shares_sold
        self.value_bought_native = self.price_avg_buy_native * self.shares_bought
        self.value_bought_base = self.price_avg_buy_base * self.shares_bought

        self.cost_basis_native_unrealized = (
            self.shares_owned * self.price_avg_buy_native
        )
        self.cost_basis_base_unrealized = self.shares_owned * self.price_avg_buy_base
        self.cost_basis_native_realized = self.shares_sold * self.price_avg_buy_native
        self.cost_basis_base_realized = self.shares_sold * self.price_avg_buy_base

        self.gain_native_unrealized = self.shares_owned * (
            self.price_market_native - self.price_avg_buy_native
        )
        self.gain_base_unrealized = self.shares_owned * (
            self.price_market_base - self.price_avg_buy_base
        )
        self.return_native_unrealized_pct = 100 * (
            self.gain_native_unrealized / self.cost_basis_native_unrealized
        )
        self.return_base_unrealized_pct = 100 * (
            self.gain_base_unrealized / self.cost_basis_base_unrealized
        )

        self.gain_native_realized = self.shares_sold * (
            self.price_avg_sell_native - self.price_avg_buy_native
        )
        self.gain_base_realized = self.shares_sold * (
            self.price_avg_sell_base - self.price_avg_buy_base
        )
        self.return_native_realized_pct = (
            100 * self.gain_native_realized / self.cost_basis_native_realized
        )
        self.return_base_realized_pct = (
            100 * self.gain_base_realized / self.cost_basis_base_realized
        )

        self.gain_native_total = self.gain_native_unrealized + self.gain_native_realized
        self.gain_base_total = self.gain_base_unrealized + self.gain_base_realized
        self.gain_currency_total = (
            self.gain_base_total - self.gain_native_total.convert(base_currency)
        )
        self.return_native_total_pct = (
            100 * self.gain_native_total / self.value_bought_native
        )
        self.return_base_total_pct = 100 * self.gain_base_total / self.value_bought_base

        self.irr_native_total_pct = 100 * calculate_irr(security, self.accounts)
        self.irr_base_total_pct = 100 * calculate_irr(
            security, self.accounts, base_currency
        )

    def __repr__(self) -> str:
        return f"SecurityStats('{self.name}')"


class SecurityAccountStats:
    def __init__(
        self, security: Security, account: SecurityAccount, base_currency: Currency
    ) -> None:
        self.security = security
        self.account = account
        self.base_currency = base_currency

        self.transactions = frozenset(
            t for t in account.transactions if t.security == security
        )

        self.name = account.path

        self.shares_owned = account.securities.get(security, Decimal(0))
        self.shares_bought = account.get_shares(security, SharesType.BOUGHT)
        self.shares_sold = account.get_shares(security, SharesType.SOLD)
        self.shares_transferred = account.get_shares(security, SharesType.TRANSFERRED)

        self.price_market_native = security.price
        self.price_market_base = security.price.convert(base_currency)
        self.price_avg_buy_native = account.get_average_price(
            security, type_=SecurityTransactionType.BUY
        )
        self.price_avg_buy_base = account.get_average_price(
            security, currency=base_currency, type_=SecurityTransactionType.BUY
        )
        self.price_avg_sell_native = account.get_average_price(
            security, type_=SecurityTransactionType.SELL
        )
        self.price_avg_sell_base = account.get_average_price(
            security, currency=base_currency, type_=SecurityTransactionType.SELL
        )

        self.value_current_native = self.shares_owned * self.price_market_native
        self.value_current_base = self.value_current_native.convert(base_currency)
        self.value_sold_native = self.shares_sold * self.price_avg_sell_native
        self.value_sold_base = self.shares_sold * self.price_avg_sell_base
        self.value_bought_native = self.shares_bought * self.price_avg_buy_native
        self.value_bought_base = self.shares_bought * self.price_avg_buy_base

        self.cost_basis_native_unrealized = (
            self.shares_owned * self.price_avg_buy_native
        )
        self.cost_basis_base_unrealized = self.shares_owned * self.price_avg_buy_base
        self.cost_basis_native_realized = self.shares_sold * self.price_avg_buy_native
        self.cost_basis_base_realized = self.shares_sold * self.price_avg_buy_base

        self.gain_native_unrealized = self.shares_owned * (
            self.price_market_native - self.price_avg_buy_native
        )
        self.gain_base_unrealized = self.shares_owned * (
            self.price_market_base - self.price_avg_buy_base
        )
        self.return_native_unrealized_pct = (
            100 * (self.gain_native_unrealized / self.cost_basis_native_unrealized)
            if self.shares_owned > 0
            else Decimal("NaN")
        )
        self.return_base_unrealized_pct = (
            100 * (self.gain_base_unrealized / self.cost_basis_base_unrealized)
            if self.shares_owned > 0
            else Decimal("NaN")
        )

        self.gain_native_realized = self.shares_sold * (
            self.price_avg_sell_native - self.price_avg_buy_native
        )
        self.gain_base_realized = self.shares_sold * (
            self.price_avg_sell_base - self.price_avg_buy_base
        )
        self.return_native_realized_pct = (
            100 * self.gain_native_realized / self.cost_basis_native_realized
        )
        self.return_base_realized_pct = (
            100 * self.gain_base_realized / self.cost_basis_base_realized
        )

        self.gain_native_total = self.gain_native_unrealized + self.gain_native_realized
        self.gain_base_total = self.gain_base_unrealized + self.gain_base_realized
        self.gain_currency_total = (
            self.gain_base_total - self.gain_native_total.convert(base_currency)
        )
        self.return_native_total_pct = (
            100 * self.gain_native_total / self.value_bought_native
        )
        self.return_base_total_pct = 100 * self.gain_base_total / self.value_bought_base

        self.irr_native_total_pct = 100 * calculate_irr(security, [account])
        self.irr_base_total_pct = 100 * calculate_irr(
            security, [account], base_currency
        )

    def __repr__(self) -> str:
        return f"SecurityAccountStats('{self.security.name}', '{self.name}')"


class TotalSecurityStats:
    def __init__(
        self, security_stats: Collection[SecurityStats], base_currency: Currency
    ) -> None:
        _accounts: set[SecurityAccount] = set()
        _transactions: set[SecurityRelatedTransaction] = set()
        for stats in security_stats:
            _accounts.update(stats.accounts)
            _transactions.update(stats.transactions)
        self.transactions = frozenset(_transactions)

        self.base_currency = base_currency

        _currencies = {stat.security.currency for stat in security_stats}
        is_single_native_currency = len(_currencies) == 2
        single_native_currency = (
            _currencies.pop() if is_single_native_currency else None
        )

        self.name = "Σ Total"

        self.value_current_native = (
            sum(
                (stats.value_current_native for stats in security_stats),
                start=single_native_currency.zero_amount,
            )
            if is_single_native_currency
            else None
        )
        self.value_current_base = sum(
            (stats.value_current_base for stats in security_stats),
            start=base_currency.zero_amount,
        )

        self.cost_basis_native_unrealized = (
            sum(
                (stats.cost_basis_native_unrealized for stats in security_stats),
                start=single_native_currency.zero_amount,
            )
            if is_single_native_currency
            else None
        )
        self.cost_basis_base_unrealized = sum(
            (stats.cost_basis_base_unrealized for stats in security_stats),
            start=base_currency.zero_amount,
        )
        self.cost_basis_native_realized = (
            sum(
                (stats.cost_basis_native_realized for stats in security_stats),
                start=single_native_currency.zero_amount,
            )
            if is_single_native_currency
            else None
        )
        self.cost_basis_base_realized = sum(
            (stats.cost_basis_base_realized for stats in security_stats),
            start=base_currency.zero_amount,
        )

        self.gain_native_unrealized = (
            sum(
                (stats.gain_native_unrealized for stats in security_stats),
                start=single_native_currency.zero_amount,
            )
            if is_single_native_currency
            else None
        )
        self.gain_base_unrealized = sum(
            (stats.gain_base_unrealized for stats in security_stats),
            start=base_currency.zero_amount,
        )
        self.return_native_unrealized_pct = (
            100 * self.gain_native_unrealized / self.cost_basis_native_unrealized
            if is_single_native_currency
            else None
        )
        self.return_base_unrealized_pct = (
            100 * self.gain_base_unrealized / self.cost_basis_base_unrealized
        )

        self.gain_native_realized = (
            sum(
                (stats.gain_native_realized for stats in security_stats),
                start=single_native_currency.zero_amount,
            )
            if is_single_native_currency
            else None
        )
        self.gain_base_realized = sum(
            (stats.gain_base_realized for stats in security_stats),
            start=base_currency.zero_amount,
        )
        self.return_native_realized_pct = (
            100 * self.gain_native_realized / self.cost_basis_native_realized
            if is_single_native_currency
            else None
        )
        self.return_base_realized_pct = (
            100 * self.gain_base_realized / self.cost_basis_base_realized
        )

        self.gain_native_total = (
            self.gain_native_unrealized + self.gain_native_realized
            if self.gain_native_unrealized is not None
            and self.gain_native_realized is not None
            else None
        )
        self.gain_base_total = self.gain_base_unrealized + self.gain_base_realized
        self.gain_currency_total = sum(
            (s.gain_currency_total for s in security_stats),
            start=base_currency.zero_amount,
        )
        self.return_native_total_pct = (
            100
            * (self.gain_native_realized - self.gain_native_unrealized)
            / (self.cost_basis_native_realized + self.cost_basis_native_unrealized)
            if self.gain_native_realized is not None
            and self.cost_basis_native_realized is not None
            else None
        )
        self.return_base_total_pct = (
            100
            * (self.gain_base_realized + self.gain_base_unrealized)
            / (self.cost_basis_base_realized + self.cost_basis_base_unrealized)
        )

        self.irr_native_total_pct = (
            100 * calculate_total_irr(_accounts, single_native_currency)
            if is_single_native_currency
            else None
        )
        self.irr_base_total_pct = 100 * calculate_total_irr(_accounts, base_currency)

    def __repr__(self) -> str:
        return "TotalSecurityStats()"


def calculate_irr(
    security: Security,
    accounts: Collection[SecurityAccount],
    currency: Currency | None = None,
) -> Decimal:
    # 'transactions' is first created as a set to remove duplicates
    # (as SecurityTransfers can relate to multiple accounts)
    _accounts = frozenset(accounts)
    transactions = {
        transaction
        for account in _accounts
        for transaction in account.transactions
        if transaction.security == security
        and isinstance(transaction, SecurityTransaction | SecurityTransfer)
    }
    transactions = sorted(transactions, key=lambda t: t.datetime_)

    if len(transactions) == 0:
        return Decimal("NaN")

    currency = currency or security.currency

    dates: list[date] = []
    cashflows: list[Decimal] = []
    for transaction in transactions:
        _date = transaction.date_

        if isinstance(transaction, SecurityTransaction):
            amount = (
                transaction.get_amount(transaction.cash_account)
                .convert(currency, _date)
                .value_normalized
            )
        else:
            if transaction.sender in _accounts and transaction.recipient in _accounts:
                continue
            if transaction.recipient in _accounts:
                avg_price = transaction.sender.get_average_price(
                    security, _date, currency
                )
                amount = -avg_price.value_normalized * transaction.shares
            else:
                avg_price = transaction.recipient.get_average_price(
                    security, _date, currency
                )
                amount = avg_price.value_normalized * transaction.shares

        if len(dates) > 0 and _date == dates[-1]:
            cashflows[-1] += amount
        else:
            dates.append(_date)
            cashflows.append(amount)

    if len(dates) == 0:
        return Decimal("NaN")

    # add last fictitious outflow as if all investment was liquidated
    sell_all_amount = Decimal(0)
    price = security.price.convert(currency)
    for account in _accounts:
        sell_all_amount += account.securities.get(security, 0) * price.value_normalized

    return _calculate_irr(dates, cashflows, sell_all_amount)


def calculate_total_irr(
    accounts: Collection[SecurityAccount], currency: Currency
) -> Decimal:
    # REFACTOR: move shared code to separate functions
    accounts = frozenset(accounts)

    # 'transactions' is first created as a set to remove duplicates
    # (as SecurityTransfers can relate to multiple accounts)
    transactions = {
        transaction
        for account in accounts
        for transaction in account.transactions
        if isinstance(transaction, SecurityTransaction | SecurityTransfer)
    }
    transactions = sorted(transactions, key=lambda t: t.datetime_)

    if len(transactions) == 0:
        return Decimal("NaN")

    dates: list[date] = []
    cashflows: list[Decimal] = []
    for transaction in transactions:
        _date = transaction.date_

        if isinstance(transaction, SecurityTransaction):
            amount = (
                transaction.get_amount(transaction.cash_account)
                .convert(currency, _date)
                .value_normalized
            )
        else:
            # SecurityTransfers can be ignored as they do not affect performance
            continue

        if len(dates) > 0 and _date == dates[-1]:
            cashflows[-1] += amount
        else:
            dates.append(_date)
            cashflows.append(amount)

    if len(dates) == 0:
        return Decimal("NaN")

    # add last fictitious outflow as if all investment was liquidated
    sell_all_amount = currency.zero_amount
    for account in accounts:
        for security in account.securities:
            sell_all_amount += account.securities[security] * security.price.convert(
                currency
            )
    sell_all_amount = sell_all_amount.value_normalized
    return _calculate_irr(dates, cashflows, sell_all_amount)


def _calculate_irr(
    dates: list[date], cashflows: list[Decimal], sell_all_amount: Decimal
) -> Decimal:
    if sell_all_amount.is_nan():
        return Decimal("NaN")

    today = datetime.now(user_settings.settings.time_zone).date()
    if today > dates[-1]:
        dates.append(today)
        cashflows.append(sell_all_amount)
    elif today == dates[-1]:
        cashflows[-1] += sell_all_amount
    else:
        raise ValueError("Unable to calculate IRR based on future prices.")

    try:
        irr = xirr(dates, cashflows)
    except InvalidPaymentsError:  # pragma: no cover
        return Decimal("NaN")

    if irr is None:  # solution not found
        return Decimal("NaN")  # pragma: no cover
    return Decimal(irr)
