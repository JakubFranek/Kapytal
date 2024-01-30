from abc import ABC, abstractmethod
from collections.abc import Collection
from datetime import date, datetime
from decimal import Decimal

from pyxirr import InvalidPaymentsError, xirr
from src.models.model_objects.currency_objects import (
    CashAmount,
    ConversionFactorNotFoundError,
    Currency,
)
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
        self.shares_paid_dividend = sum(
            (stats.shares_paid_dividend for stats in self.account_stats),
            start=Decimal(0),
        )

        self.price_market_native = security.price
        self.price_market_base = _safe_convert(security.price, base_currency)

        self.price_avg_buy_native = _average_of_sum_of_attribute_products(
            "price_avg_buy_native",
            "shares_bought",
            self.shares_bought,
            self.account_stats,
            security.currency,
        )
        self.price_avg_buy_base = _average_of_sum_of_attribute_products(
            "price_avg_buy_base",
            "shares_bought",
            self.shares_bought,
            self.account_stats,
            base_currency,
        )
        self.price_avg_sell_native = _average_of_sum_of_attribute_products(
            "price_avg_sell_native",
            "shares_sold",
            self.shares_sold,
            self.account_stats,
            security.currency,
        )
        self.price_avg_sell_base = _average_of_sum_of_attribute_products(
            "price_avg_sell_base",
            "shares_sold",
            self.shares_sold,
            self.account_stats,
            base_currency,
        )
        self.amount_avg_dividend_native = _average_of_sum_of_attribute_products(
            "amount_avg_dividend_native",
            "shares_paid_dividend",
            self.shares_paid_dividend,
            self.account_stats,
            security.currency,
        )
        self.amount_avg_dividend_base = _average_of_sum_of_attribute_products(
            "amount_avg_dividend_base",
            "shares_paid_dividend",
            self.shares_paid_dividend,
            self.account_stats,
            base_currency,
        )

        self.value_current_native = self.price_market_native * self.shares_owned
        self.value_current_base = self.price_market_base * self.shares_owned
        self.value_sold_native = self.price_avg_sell_native * self.shares_sold
        self.value_sold_base = self.price_avg_sell_base * self.shares_sold
        self.value_bought_native = self.price_avg_buy_native * self.shares_bought
        self.value_bought_base = self.price_avg_buy_base * self.shares_bought
        self.value_dividend_native = (
            self.amount_avg_dividend_native * self.shares_paid_dividend
        )
        self.value_dividend_base = (
            self.amount_avg_dividend_base * self.shares_paid_dividend
        )

        self.cost_basis_unrealized_native = _zero_if_nan(
            self.shares_owned * self.price_avg_buy_native
        )
        self.cost_basis_unrealized_base = _zero_if_nan(
            self.shares_owned * self.price_avg_buy_base
        )
        self.cost_basis_realized_native = _zero_if_nan(
            self.shares_sold * self.price_avg_buy_native
        )
        self.cost_basis_realized_base = _zero_if_nan(
            self.shares_sold * self.price_avg_buy_base
        )
        self.cost_basis_dividend_native = _zero_if_nan(
            self.shares_paid_dividend * self.price_avg_buy_native
        )
        self.cost_basis_dividend_base = _zero_if_nan(
            self.shares_paid_dividend * self.price_avg_buy_base
        )

        self.gain_unrealized_native = _zero_if_nan(
            self.shares_owned * (self.price_market_native - self.price_avg_buy_native)
        )
        self.gain_unrealized_base = _zero_if_nan(
            self.shares_owned * (self.price_market_base - self.price_avg_buy_base)
        )
        self.return_pct_unrealized_native = _calculate_return_percentage(
            nom=self.gain_unrealized_native,
            denom=self.cost_basis_unrealized_native,
        )
        self.return_pct_unrealized_base = _calculate_return_percentage(
            nom=self.gain_unrealized_base,
            denom=self.cost_basis_unrealized_base,
        )

        self.gain_realized_native = _zero_if_nan(
            self.shares_sold * (self.price_avg_sell_native - self.price_avg_buy_native)
            + self.value_dividend_native
        )
        self.gain_realized_base = _zero_if_nan(
            self.shares_sold * (self.price_avg_sell_base - self.price_avg_buy_base)
            + self.value_dividend_base
        )
        self.return_pct_realized_native = _calculate_return_percentage(
            nom=self.shares_sold
            * (self.price_avg_sell_native - self.price_avg_buy_native),
            denom=self.cost_basis_realized_native,
        ) + _calculate_return_percentage(
            nom=self.value_dividend_native,
            denom=self.cost_basis_dividend_native,
        )
        self.return_pct_realized_base = _calculate_return_percentage(
            nom=self.shares_sold * (self.price_avg_sell_base - self.price_avg_buy_base),
            denom=self.cost_basis_realized_base,
        ) + _calculate_return_percentage(
            nom=self.value_dividend_base,
            denom=self.cost_basis_dividend_base,
        )

        self.gain_total_native = self.gain_unrealized_native + self.gain_realized_native
        self.gain_total_base = self.gain_unrealized_base + self.gain_realized_base
        self.gain_total_currency = self.gain_total_base - _safe_convert(
            self.gain_total_native, base_currency
        )
        self.return_pct_total_native = _calculate_return_percentage(
            nom=self.gain_total_native,
            denom=self.value_bought_native,
        )
        self.return_pct_total_base = _calculate_return_percentage(
            nom=self.gain_total_base,
            denom=self.value_bought_base,
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
        self.shares_paid_dividend = account.get_shares(
            security, SharesType.PAID_DIVIDEND
        )

        self.price_market_native = security.price
        self.price_market_base = _safe_convert(security.price, base_currency)
        self.price_avg_buy_native = account.get_average_amount_per_share(
            security, type_=SecurityTransactionType.BUY
        )
        self.price_avg_buy_base = account.get_average_amount_per_share(
            security, currency=base_currency, type_=SecurityTransactionType.BUY
        )
        self.price_avg_sell_native = account.get_average_amount_per_share(
            security, type_=SecurityTransactionType.SELL
        )
        self.price_avg_sell_base = account.get_average_amount_per_share(
            security, currency=base_currency, type_=SecurityTransactionType.SELL
        )
        self.amount_avg_dividend_native = account.get_average_amount_per_share(
            security, type_=SecurityTransactionType.DIVIDEND
        )
        self.amount_avg_dividend_base = account.get_average_amount_per_share(
            security, currency=base_currency, type_=SecurityTransactionType.DIVIDEND
        )
        if self.price_avg_sell_native.is_nan():
            self.price_avg_sell_native = security.currency.zero_amount
            self.price_avg_sell_base = base_currency.zero_amount
        if self.amount_avg_dividend_native.is_nan():
            self.amount_avg_dividend_native = security.currency.zero_amount
            self.amount_avg_dividend_base = base_currency.zero_amount

        self.value_current_native = self.shares_owned * self.price_market_native
        self.value_current_base = _safe_convert(
            self.value_current_native, base_currency
        )
        self.value_sold_native = self.shares_sold * self.price_avg_sell_native
        self.value_sold_base = self.shares_sold * self.price_avg_sell_base
        self.value_bought_native = self.shares_bought * self.price_avg_buy_native
        self.value_bought_base = self.shares_bought * self.price_avg_buy_base
        self.value_dividend_native = (
            self.shares_paid_dividend * self.amount_avg_dividend_native
        )
        self.value_dividend_base = (
            self.shares_paid_dividend * self.amount_avg_dividend_base
        )

        self.cost_basis_unrealized_native = (
            self.shares_owned * self.price_avg_buy_native
        )
        self.cost_basis_unrealized_base = self.shares_owned * self.price_avg_buy_base
        self.cost_basis_realized_native = self.shares_sold * self.price_avg_buy_native
        self.cost_basis_realized_base = self.shares_sold * self.price_avg_buy_base
        self.cost_basis_total_native = (
            self.cost_basis_unrealized_native + self.cost_basis_realized_native
        )
        self.cost_basis_total_base = (
            self.cost_basis_unrealized_base + self.cost_basis_realized_base
        )
        self.cost_basis_dividend_native = (
            self.shares_paid_dividend * self.price_avg_buy_native
        )
        self.cost_basis_dividend_base = (
            self.shares_paid_dividend * self.price_avg_buy_base
        )

        self.gain_unrealized_native = _zero_if_nan(
            self.shares_owned * (self.price_market_native - self.price_avg_buy_native)
        )
        self.gain_unrealized_base = _zero_if_nan(
            self.shares_owned * (self.price_market_base - self.price_avg_buy_base)
        )
        self.return_pct_unrealized_native = _calculate_return_percentage(
            nom=self.gain_unrealized_native,
            denom=self.cost_basis_unrealized_native,
        )
        self.return_pct_unrealized_base = _calculate_return_percentage(
            nom=self.gain_unrealized_base,
            denom=self.cost_basis_unrealized_base,
        )

        self.gain_realized_native = _zero_if_nan(
            self.shares_sold * (self.price_avg_sell_native - self.price_avg_buy_native)
            + self.value_dividend_native
        )
        self.gain_realized_base = _zero_if_nan(
            self.shares_sold * (self.price_avg_sell_base - self.price_avg_buy_base)
            + self.value_dividend_base
        )
        self.return_pct_realized_native = _calculate_return_percentage(
            nom=self.shares_sold
            * (self.price_avg_sell_native - self.price_avg_buy_native),
            denom=self.cost_basis_realized_native,
        ) + _calculate_return_percentage(
            nom=self.value_dividend_native,
            denom=self.cost_basis_dividend_native,
        )
        self.return_pct_realized_base = _calculate_return_percentage(
            nom=self.shares_sold * (self.price_avg_sell_base - self.price_avg_buy_base),
            denom=self.cost_basis_realized_base,
        ) + _calculate_return_percentage(
            nom=self.value_dividend_base,
            denom=self.cost_basis_dividend_base,
        )

        self.gain_total_native = self.gain_unrealized_native + self.gain_realized_native
        self.gain_total_base = self.gain_unrealized_base + self.gain_realized_base
        self.gain_total_currency = self.gain_total_base - _safe_convert(
            self.gain_total_native, base_currency
        )
        self.return_pct_total_native = _calculate_return_percentage(
            nom=self.gain_total_native,
            denom=self.cost_basis_total_native,
        )
        self.return_pct_total_base = _calculate_return_percentage(
            nom=self.gain_total_base,
            denom=self.cost_basis_total_base,
        )

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

        self.value_current_native = _sum_attribute(
            "value_current_native", security_stats, single_native_currency
        )
        self.value_current_base = _sum_attribute(
            "value_current_base", security_stats, base_currency
        )
        self.value_bought_native = _sum_attribute(
            "value_bought_native", security_stats, single_native_currency
        )
        self.value_bought_base = _sum_attribute(
            "value_bought_base", security_stats, base_currency
        )
        self.value_sold_native = _sum_attribute(
            "value_sold_native", security_stats, single_native_currency
        )
        self.value_sold_base = _sum_attribute(
            "value_sold_base", security_stats, base_currency
        )
        self.value_dividend_native = _sum_attribute(
            "value_dividend_native", security_stats, single_native_currency
        )
        self.value_dividend_base = _sum_attribute(
            "value_dividend_base", security_stats, base_currency
        )

        self.cost_basis_unrealized_native = _sum_attribute(
            "cost_basis_unrealized_native", security_stats, single_native_currency
        )
        self.cost_basis_unrealized_base = _sum_attribute(
            "cost_basis_unrealized_base", security_stats, base_currency
        )
        self.cost_basis_realized_native = _sum_attribute(
            "cost_basis_realized_native", security_stats, single_native_currency
        )
        self.cost_basis_realized_base = _sum_attribute(
            "cost_basis_realized_base", security_stats, base_currency
        )

        self.gain_unrealized_native = _sum_attribute(
            "gain_unrealized_native", security_stats, single_native_currency
        )
        self.gain_unrealized_base = _sum_attribute(
            "gain_unrealized_base", security_stats, base_currency
        )
        self.return_pct_unrealized_native = _calculate_return_percentage(
            nom=self.gain_unrealized_native,
            denom=self.cost_basis_unrealized_native,
        )
        self.return_pct_unrealized_base = _calculate_return_percentage(
            nom=self.gain_unrealized_base,
            denom=self.cost_basis_unrealized_base,
        )

        self.gain_realized_native = _sum_attribute(
            "gain_realized_native", security_stats, single_native_currency
        )
        self.gain_realized_base = _sum_attribute(
            "gain_realized_base", security_stats, base_currency
        )
        self.return_pct_realized_native = _calculate_return_percentage(
            nom=self.gain_realized_native,
            denom=self.cost_basis_realized_native,
        )
        self.return_pct_realized_base = _calculate_return_percentage(
            nom=self.gain_realized_base,
            denom=self.cost_basis_realized_base,
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
        self.gain_total_currency = _sum_attribute(
            "gain_total_currency", security_stats, base_currency
        )
        self.return_pct_total_native = _calculate_return_percentage(
            nom=(self.gain_realized_native, self.gain_unrealized_native),
            denom=(self.cost_basis_realized_native, self.cost_basis_unrealized_native),
        )
        self.return_pct_total_base = _calculate_return_percentage(
            nom=(self.gain_realized_base, self.gain_unrealized_base),
            denom=(self.cost_basis_realized_base, self.cost_basis_unrealized_base),
        )

        self.irr_pct_total_native = 100 * calculate_total_irr(
            _accounts, single_native_currency
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
            amount = _safe_convert(
                transaction.get_amount(transaction.cash_account), currency, _date
            ).value_normalized
        else:
            if transaction.sender in _accounts and transaction.recipient in _accounts:
                continue
            if transaction.recipient in _accounts:
                avg_price = transaction.sender.get_average_amount_per_share(
                    security, _date, currency
                )
                amount = -avg_price.value_normalized * transaction.shares
            else:
                avg_price = transaction.recipient.get_average_amount_per_share(
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
    price = _safe_convert(security.price, currency)
    for account in _accounts:
        sell_all_amount += account.securities.get(security, 0) * price.value_normalized

    return _calculate_irr(dates, cashflows, sell_all_amount)


def calculate_total_irr(
    accounts: Collection[SecurityAccount], currency: Currency | None
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
            amount = _safe_convert(
                transaction.get_amount(transaction.cash_account), currency, _date
            ).value_normalized
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
            sell_all_amount += account.securities[security] * _safe_convert(
                security.price, currency
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


def _calculate_return_percentage(
    nom: CashAmount | None | Collection[CashAmount | None],
    denom: CashAmount | None | Collection[CashAmount | None],
) -> Decimal:
    if nom is None:
        return Decimal(0)
    if isinstance(nom, CashAmount):
        _nominator = nom
    else:
        _nom = tuple(nom)
        if any(not isinstance(num, CashAmount) for num in _nom) or len(_nom) == 0:
            return Decimal(0)
        _nominator: CashAmount = sum(nom, start=_nom[0].currency.zero_amount)
        if _nominator.value_normalized == 0:
            return Decimal(0)

    if denom is None:
        return Decimal(0)
    if isinstance(denom, CashAmount):
        if denom.value_normalized == 0:
            return Decimal(0)
        _denominator = denom
    else:
        _denom = tuple(denom)
        if any(not isinstance(num, CashAmount) for num in _denom) or len(_denom) == 0:
            return Decimal(0)
        _denominator: CashAmount = sum(_denom, start=_denom[0].currency.zero_amount)
        if _denominator.value_normalized == 0:
            return Decimal(0)

    _return = 100 * _nominator / _denominator

    return _return if not _return.is_nan() else Decimal(0)


def _sum_attribute(
    attr: str,
    items: Collection,
    currency: Currency | None,
) -> CashAmount | None:
    if currency is None:
        return None
    return sum((getattr(item, attr) for item in items), start=currency.zero_amount)


def _average_of_sum_of_attribute_products(
    attr1: str, attr2: str, denom: Decimal, items: Collection, currency: Currency
) -> CashAmount:
    _sum_of_products = sum(
        (getattr(item, attr1) * getattr(item, attr2) for item in items),
        start=currency.zero_amount,
    )

    if _sum_of_products.is_nan():
        return _sum_of_products
    if denom == 0:
        return currency.zero_amount
    return _sum_of_products / denom


def _zero_if_nan(value: CashAmount) -> CashAmount:
    if value.is_nan():
        return value.currency.zero_amount
    return value


def _safe_convert(
    value: CashAmount, currency: Currency, date_: date | None = None
) -> CashAmount:
    try:
        return value.convert(currency, date_)
    except ConversionFactorNotFoundError:
        return CashAmount("NaN", currency)
