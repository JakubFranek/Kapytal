from datetime import date, datetime
from decimal import Decimal
from enum import Enum, auto

from pyxirr import InvalidPaymentsError, xirr
from src.models.model_objects.currency_objects import Currency
from src.models.model_objects.security_objects import (
    Security,
    SecurityAccount,
    SecurityTransaction,
    SecurityTransactionType,
    SecurityTransfer,
    SharesType,
)
from src.models.record_keeper import RecordKeeper
from src.models.user_settings import user_settings


class SecurityStatsType(Enum):
    TOTAL = auto()
    REALIZED = auto()
    UNREALIZED = auto()


class SecurityStatsData:
    pass


class SecurityStats:
    """
    _Security
    [SecurityAccountStats]
    Name
    Shares
    Shares sold
    Market Price
    Avg. Buy Price
    Avg. Sell Price
    Native Value
    Base Value
    Native Gain Total
    Native Gain Realized
    Native Gain Unrealized
    Native Return Total
    Native Return Realized
    Native Return Unrealized
    Native IRR p.a. Total
    Base Gain Total
    Base Gain Realized
    Base Gain Unrealized
    Base Return Total
    Base Return Realized
    Base Return Unrealized
    Base IRR p.a. Total
    """


class SecurityAccountStats:
    def __init__(
        self, security: Security, account: SecurityAccount, base_currency: Currency
    ) -> None:
        self.security = security
        self.account = account
        self.base_currency = base_currency

        self.transactions = {t for t in account.transactions if t.security == security}

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

        self.gain_native_unrealized = self.shares_owned * (
            self.price_market_native - self.price_avg_buy_native
        )
        self.gain_base_unrealized = self.shares_owned * (
            self.price_market_base - self.price_avg_buy_base
        )
        self.return_native_unrealized_pct = 100 * (
            self.gain_native_unrealized
            / (self.shares_owned * self.price_avg_buy_native)
        )
        self.return_base_unrealized_pct = 100 * (
            self.gain_base_unrealized / (self.shares_owned * self.price_avg_buy_base)
        )

        self.gain_native_realized = self.shares_sold * (
            self.price_avg_sell_native - self.price_avg_buy_native
        )
        self.gain_base_realized = self.shares_sold * (
            self.price_avg_sell_base - self.price_avg_buy_base
        )
        self.return_native_realized_pct = (
            100
            * self.gain_native_realized
            / (self.shares_sold * self.price_avg_buy_native)
        )
        self.return_base_realized_pct = (
            100 * self.gain_base_realized / (self.shares_sold * self.price_avg_buy_base)
        )

        self.gain_native_total = self.gain_native_unrealized + self.gain_native_realized
        self.gain_base_total = self.gain_base_unrealized + self.gain_base_realized
        self.return_native_total_pct = (
            100 * self.gain_native_total / self.value_bought_native
        )
        self.return_base_total_pct = 100 * self.gain_base_total / self.value_bought_base

        self.irr_native_total_pct = 100 * calculate_irr(security, [account])
        self.irr_base_total_pct = 100 * calculate_irr(
            security, [account], base_currency
        )

    def __repr__(self) -> str:
        return f"SecurityAccountStats({self.security.name}, {self.name})"


class TotalSecurityStats:
    """
    Name
    Native Value
    Base Value
    Native Gain Total
    Native Gain Realized
    Native Gain Unrealized
    Native Return Total
    Native Return Realized
    Native Return Unrealized
    Native IRR p.a. Total
    Base Gain Total
    Base Gain Realized
    Base Gain Unrealized
    Base Return Total
    Base Return Realized
    Base Return Unrealized
    Base IRR p.a. Total"""


def calculate_irr(
    security: Security,
    accounts: list[SecurityAccount],
    currency: Currency | None = None,
) -> Decimal:
    # 'transactions' is first created as a set to remove duplicates
    # (as SecurityTransfers can relate to multiple accounts)
    transactions = {
        transaction
        for account in accounts
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
            if transaction.sender in accounts and transaction.recipient in accounts:
                continue
            if transaction.recipient in accounts:
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
    for account in accounts:
        sell_all_amount += account.securities.get(security, 0) * price.value_normalized

    return _calculate_irr(dates, cashflows, sell_all_amount)


def calculate_total_irr(record_keeper: RecordKeeper) -> Decimal:
    # REFACTOR: move shared code to separate functions

    currency = record_keeper.base_currency
    accounts = record_keeper.security_accounts

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
