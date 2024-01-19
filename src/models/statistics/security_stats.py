from abc import ABC, abstractmethod
from collections.abc import Collection
from datetime import date, datetime
from decimal import Decimal

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


class SecurityStatsItem(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        raise NotImplementedError  # pragma: no cover

    @property
    @abstractmethod
    def is_base(self) -> bool:
        raise NotImplementedError  # pragma: no cover


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

        self.total_stats = TotalSecurityStats(_security_stats, base_currency)

        self.stats: tuple[SecurityStats | TotalSecurityStats, ...] = (
            *_security_stats,
            self.total_stats,
        )

    def __repr__(self) -> str:
        return f"SecurityStatsData(len={len(self.stats)-1})"


class SecurityStats(SecurityStatsItem):
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
            stats = SecurityAccountStats(security, account, base_currency, parent=self)
            _account_stats.append(stats)
            _transactions.update(stats.transactions)
        self.account_stats = tuple(_account_stats)
        self.transactions = frozenset(_transactions)

        self._name = security.name

        self.shares_owned = sum(
            (stats.shares_owned for stats in self.account_stats), start=Decimal(0)
        )
        self.shares_bought = sum(
            (stats.shares_bought for stats in self.account_stats), start=Decimal(0)
        )
        self.shares_sold = sum(
            (stats.shares_sold for stats in self.account_stats), start=Decimal(0)
        )
        self.shares_transferred = Decimal(0)

        self.price_market_native = security.price
        self.price_market_base = security.price.convert(base_currency)
        self.price_avg_buy_native = (
            (
                sum(
                    (
                        stats.price_avg_buy_native * stats.shares_bought
                        for stats in self.account_stats
                    ),
                    start=security.currency.zero_amount,
                )
                / self.shares_bought
            )
            if self.shares_bought != 0
            else security.currency.zero_amount
        )
        self.price_avg_buy_base = (
            (
                sum(
                    (
                        stats.price_avg_buy_base * stats.shares_bought
                        for stats in self.account_stats
                    ),
                    start=base_currency.zero_amount,
                )
                / self.shares_bought
            )
            if self.shares_bought != 0
            else base_currency.zero_amount
        )
        self.price_avg_sell_native = (
            (
                sum(
                    (
                        stats.price_avg_sell_native * stats.shares_sold
                        for stats in self.account_stats
                    ),
                    start=security.currency.zero_amount,
                )
                / self.shares_sold
            )
            if self.shares_sold != 0
            else security.currency.zero_amount
        )
        self.price_avg_sell_base = (
            (
                sum(
                    (
                        stats.price_avg_sell_base * stats.shares_sold
                        for stats in self.account_stats
                    ),
                    start=base_currency.zero_amount,
                )
                / self.shares_sold
            )
            if self.shares_sold != 0
            else base_currency.zero_amount
        )

        self.value_current_native = self.price_market_native * self.shares_owned
        self.value_current_base = self.price_market_base * self.shares_owned
        self.value_sold_native = self.price_avg_sell_native * self.shares_sold
        self.value_sold_base = self.price_avg_sell_base * self.shares_sold
        self.value_bought_native = self.price_avg_buy_native * self.shares_bought
        self.value_bought_base = self.price_avg_buy_base * self.shares_bought

        self.cost_basis_unrealized_native = (
            self.shares_owned * self.price_avg_buy_native
        )
        self.cost_basis_unrealized_base = self.shares_owned * self.price_avg_buy_base
        self.cost_basis_realized_native = self.shares_sold * self.price_avg_buy_native
        self.cost_basis_realized_base = self.shares_sold * self.price_avg_buy_base

        self.gain_unrealized_native = self.shares_owned * (
            self.price_market_native - self.price_avg_buy_native
        )
        self.gain_unrealized_base = self.shares_owned * (
            self.price_market_base - self.price_avg_buy_base
        )
        self.return_pct_unrealized_native = (
            100 * (self.gain_unrealized_native / self.cost_basis_unrealized_native)
            if self.cost_basis_unrealized_native.value_normalized != 0
            else Decimal(0)
        )
        self.return_pct_unrealized_base = (
            100 * (self.gain_unrealized_base / self.cost_basis_unrealized_base)
            if self.cost_basis_unrealized_base.value_normalized != 0
            else Decimal(0)
        )

        self.gain_realized_native = self.shares_sold * (
            self.price_avg_sell_native - self.price_avg_buy_native
        )
        self.gain_realized_base = self.shares_sold * (
            self.price_avg_sell_base - self.price_avg_buy_base
        )
        self.return_pct_realized_native = (
            (100 * self.gain_realized_native / self.cost_basis_realized_native)
            if self.cost_basis_realized_native.value_normalized != 0
            else Decimal(0)
        )
        self.return_pct_realized_base = (
            (100 * self.gain_realized_base / self.cost_basis_realized_base)
            if self.cost_basis_realized_base.value_normalized != 0
            else Decimal(0)
        )

        self.gain_total_native = self.gain_unrealized_native + self.gain_realized_native
        self.gain_total_base = self.gain_unrealized_base + self.gain_realized_base
        self.gain_total_currency = (
            self.gain_total_base - self.gain_total_native.convert(base_currency)
        )
        self.return_pct_total_native = (
            (100 * self.gain_total_native / self.value_bought_native)
            if self.value_bought_native.value_normalized != 0
            else Decimal(0)
        )
        self.return_pct_total_base = (
            (100 * self.gain_total_base / self.value_bought_base)
            if self.value_bought_base.value_normalized != 0
            else Decimal(0)
        )

        self.irr_pct_total_native = 100 * calculate_irr(security, self.accounts)
        self.irr_pct_total_base = 100 * calculate_irr(
            security, self.accounts, base_currency
        )

    def __repr__(self) -> str:
        return f"SecurityStats('{self.name}')"

    @property
    def name(self) -> str:
        return self._name

    @property
    def is_base(self) -> bool:
        return self.security.currency == self.base_currency


class SecurityAccountStats(SecurityStatsItem):
    def __init__(
        self,
        security: Security,
        account: SecurityAccount,
        base_currency: Currency,
        parent: SecurityStats,
    ) -> None:
        self.parent = parent
        self.security = security
        self.account = account
        self.base_currency = base_currency

        self.transactions = frozenset(
            t for t in account.transactions if t.security == security
        )

        self._name = account.path

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
        if self.price_avg_sell_native.is_nan():
            self.price_avg_sell_native = security.currency.zero_amount
            self.price_avg_sell_base = base_currency.zero_amount

        self.value_current_native = self.shares_owned * self.price_market_native
        self.value_current_base = self.value_current_native.convert(base_currency)
        self.value_sold_native = self.shares_sold * self.price_avg_sell_native
        self.value_sold_base = self.shares_sold * self.price_avg_sell_base
        self.value_bought_native = self.shares_bought * self.price_avg_buy_native
        self.value_bought_base = self.shares_bought * self.price_avg_buy_base

        self.cost_basis_native_unrealized = (
            self.shares_owned * self.price_avg_buy_native
        )
        self.cost_basis_unrealized_base = self.shares_owned * self.price_avg_buy_base
        self.cost_basis_realized_native = self.shares_sold * self.price_avg_buy_native
        self.cost_basis_realized_base = self.shares_sold * self.price_avg_buy_base

        self.gain_unrealized_native = self.shares_owned * (
            self.price_market_native - self.price_avg_buy_native
        )
        self.gain_unrealized_base = self.shares_owned * (
            self.price_market_base - self.price_avg_buy_base
        )
        self.return_pct_unrealized_native = (
            100 * (self.gain_unrealized_native / self.cost_basis_native_unrealized)
            if self.shares_owned != 0
            else Decimal(0)
        )
        self.return_pct_unrealized_base = (
            100 * (self.gain_unrealized_base / self.cost_basis_unrealized_base)
            if self.shares_owned != 0
            else Decimal(0)
        )

        self.gain_realized_native = self.shares_sold * (
            self.price_avg_sell_native - self.price_avg_buy_native
        )
        self.gain_realized_base = self.shares_sold * (
            self.price_avg_sell_base - self.price_avg_buy_base
        )
        self.return_pct_realized_native = (
            (100 * self.gain_realized_native / self.cost_basis_realized_native)
            if self.cost_basis_realized_native.value_normalized != 0
            else Decimal(0)
        )
        self.return_pct_realized_base = (
            100 * self.gain_realized_base / self.cost_basis_realized_base
            if self.cost_basis_realized_base.value_normalized != 0
            else Decimal(0)
        )

        self.gain_total_native = self.gain_unrealized_native + self.gain_realized_native
        self.gain_total_base = self.gain_unrealized_base + self.gain_realized_base
        self.gain_total_currency = (
            self.gain_total_base - self.gain_total_native.convert(base_currency)
        )
        self.return_pct_total_native = (
            100 * self.gain_total_native / self.value_bought_native
        )
        self.return_pct_total_base = 100 * self.gain_total_base / self.value_bought_base

        self.irr_pct_total_native = 100 * calculate_irr(security, [account])
        self.irr_pct_total_base = 100 * calculate_irr(
            security, [account], base_currency
        )

    def __repr__(self) -> str:
        return f"SecurityAccountStats('{self.security.name}', '{self.name}')"

    @property
    def name(self) -> str:
        return self._name

    @property
    def is_base(self) -> bool:
        return self.security.currency == self.base_currency


class TotalSecurityStats(SecurityStatsItem):
    def __init__(
        self, security_stats: Collection[SecurityStats], base_currency: Currency | None
    ) -> None:
        _accounts: set[SecurityAccount] = set()
        _transactions: set[SecurityRelatedTransaction] = set()
        for stats in security_stats:
            _accounts.update(stats.accounts)
            _transactions.update(stats.transactions)
        self.transactions = frozenset(_transactions)

        self.base_currency = base_currency

        _currencies = {stat.security.currency for stat in security_stats}
        if len(_currencies) > 1:
            single_native_currency = _currencies.difference({base_currency}).pop()
            if not all(
                stats.security.currency == single_native_currency
                for stats in security_stats
            ):
                single_native_currency = None
        else:
            single_native_currency = None

        self.value_current_native = (
            sum(
                (stats.value_current_native for stats in security_stats),
                start=single_native_currency.zero_amount,
            )
            if single_native_currency is not None
            else None
        )
        self.value_current_base = (
            sum(
                (stats.value_current_base for stats in security_stats),
                start=base_currency.zero_amount,
            )
            if base_currency is not None
            else None
        )
        self.value_bought_native = (
            sum(
                (stats.value_bought_native for stats in security_stats),
                start=single_native_currency.zero_amount,
            )
            if single_native_currency is not None
            else None
        )
        self.value_bought_base = (
            sum(
                (stats.value_bought_base for stats in security_stats),
                start=base_currency.zero_amount,
            )
            if base_currency is not None
            else None
        )
        self.value_sold_native = (
            sum(
                (stats.value_sold_native for stats in security_stats),
                start=single_native_currency.zero_amount,
            )
            if single_native_currency is not None
            else None
        )
        self.value_sold_base = (
            sum(
                (stats.value_sold_base for stats in security_stats),
                start=base_currency.zero_amount,
            )
            if base_currency is not None
            else None
        )

        self.cost_basis_unrealized_native = (
            sum(
                (stats.cost_basis_unrealized_native for stats in security_stats),
                start=single_native_currency.zero_amount,
            )
            if single_native_currency is not None
            else None
        )
        self.cost_basis_unrealized_base = (
            sum(
                (stats.cost_basis_unrealized_base for stats in security_stats),
                start=base_currency.zero_amount,
            )
            if base_currency is not None
            else None
        )
        self.cost_basis_realized_native = (
            sum(
                (stats.cost_basis_realized_native for stats in security_stats),
                start=single_native_currency.zero_amount,
            )
            if single_native_currency is not None
            else None
        )
        self.cost_basis_realized_base = (
            sum(
                (stats.cost_basis_realized_base for stats in security_stats),
                start=base_currency.zero_amount,
            )
            if base_currency is not None
            else None
        )

        self.gain_unrealized_native = (
            sum(
                (stats.gain_unrealized_native for stats in security_stats),
                start=single_native_currency.zero_amount,
            )
            if single_native_currency is not None
            else None
        )
        self.gain_unrealized_base = (
            sum(
                (stats.gain_unrealized_base for stats in security_stats),
                start=base_currency.zero_amount,
            )
            if base_currency is not None
            else None
        )
        self.return_pct_unrealized_native = (
            100 * self.gain_unrealized_native / self.cost_basis_unrealized_native
            if single_native_currency is not None
            else None
        )
        self.return_pct_unrealized_base = (
            (100 * self.gain_unrealized_base / self.cost_basis_unrealized_base)
            if self.cost_basis_unrealized_base is not None
            and self.cost_basis_unrealized_base.value_normalized != 0
            else Decimal(0)
        )

        self.gain_realized_native = (
            sum(
                (stats.gain_realized_native for stats in security_stats),
                start=single_native_currency.zero_amount,
            )
            if single_native_currency is not None
            else None
        )
        self.gain_realized_base = (
            sum(
                (stats.gain_realized_base for stats in security_stats),
                start=base_currency.zero_amount,
            )
            if base_currency is not None
            else None
        )
        self.return_pct_realized_native = (
            (100 * self.gain_realized_native / self.cost_basis_realized_native)
            if single_native_currency is not None
            else None
        )
        self.return_pct_realized_base = (
            (100 * self.gain_realized_base / self.cost_basis_realized_base)
            if self.cost_basis_realized_base is not None
            and self.cost_basis_realized_base.value_normalized != 0
            else Decimal(0)
        )

        self.gain_total_native = (
            self.gain_unrealized_native + self.gain_realized_native
            if self.gain_unrealized_native is not None
            and self.gain_realized_native is not None
            else None
        )
        self.gain_total_base = (
            self.gain_unrealized_base + self.gain_realized_base
            if (
                self.gain_unrealized_base is not None
                and self.gain_realized_base is not None
            )
            else None
        )
        self.gain_total_currency = (
            sum(
                (s.gain_total_currency for s in security_stats),
                start=base_currency.zero_amount,
            )
            if base_currency is not None
            else None
        )
        self.return_pct_total_native = (
            (
                100
                * (self.gain_realized_native - self.gain_unrealized_native)
                / (self.cost_basis_realized_native + self.cost_basis_unrealized_native)
            )
            if self.gain_realized_native is not None
            and self.cost_basis_realized_native is not None
            else None
        )
        self.return_pct_total_base = (
            (
                100
                * (self.gain_realized_base + self.gain_unrealized_base)
                / (self.cost_basis_realized_base + self.cost_basis_unrealized_base)
            )
            if self.gain_realized_base is not None
            and self.gain_unrealized_base is not None
            and self.cost_basis_realized_base is not None
            and self.cost_basis_unrealized_base is not None
            and (
                self.cost_basis_realized_base.value_normalized
                + self.cost_basis_unrealized_base.value_normalized
            )
            != 0
            else Decimal(0)
        )

        self.irr_pct_total_native = (
            100 * calculate_total_irr(_accounts, single_native_currency)
            if single_native_currency is not None
            else None
        )
        self.irr_pct_total_base = 100 * calculate_total_irr(_accounts, base_currency)

    def __repr__(self) -> str:
        return "TotalSecurityStats()"

    @property
    def name(self) -> str:
        return "Total"

    @property
    def is_base(self) -> bool:
        return True


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
    accounts = frozenset(accounts)

    if currency is None:
        return Decimal("NaN")

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
