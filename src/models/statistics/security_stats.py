from datetime import date, datetime
from decimal import Decimal

from pyxirr import InvalidPaymentsError, xirr
from src.models.model_objects.currency_objects import Currency
from src.models.model_objects.security_objects import (
    Security,
    SecurityAccount,
    SecurityTransaction,
    SecurityTransfer,
)
from src.models.record_keeper import RecordKeeper
from src.models.user_settings import user_settings


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
        sell_all_amount += account.securities[security] * price.value_normalized

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
    if sell_all_amount.is_zero() or sell_all_amount.is_nan():
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
