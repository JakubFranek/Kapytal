from datetime import datetime
from decimal import Decimal

from pyxirr import InvalidPaymentsError, xirr
from src.models.model_objects.security_objects import (
    Security,
    SecurityAccount,
    SecurityTransaction,
    SecurityTransfer,
)
from src.models.user_settings import user_settings


def calculate_irr(security: Security, accounts: list[SecurityAccount]) -> Decimal:
    # 'transactions' is first created as a set to remove duplicates
    # (SecurityTransfers can relate to multiple accounts)
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

    dates = []
    cashflows = []
    for transaction in transactions:
        _date = transaction.datetime_.date()

        if isinstance(transaction, SecurityTransaction):
            amount = transaction.get_amount(transaction.cash_account).value_normalized
        elif isinstance(transaction, SecurityTransfer):
            if transaction.sender in accounts and transaction.recipient in accounts:
                continue
            if transaction.recipient in accounts:
                avg_price = transaction.sender.get_average_price(security, _date)
                amount = -avg_price.value_normalized * transaction.shares
            else:
                avg_price = transaction.recipient.get_average_price(security, _date)
                amount = avg_price.value_normalized * transaction.shares
        else:
            raise TypeError("Unknown Transaction type.")

        if len(dates) > 0 and _date == dates[-1]:
            cashflows[-1] += amount
        else:
            dates.append(_date)
            cashflows.append(amount)

    if len(dates) == 0:
        return Decimal("NaN")

    # add last fictitious outflow as if all investment was liquidated
    sell_all_amount = Decimal(0)
    price = security.price
    for account in accounts:
        sell_all_amount += account.securities[security] * price.value_normalized
    if sell_all_amount.is_zero():
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
    except InvalidPaymentsError:
        return Decimal("NaN")
    if irr is None:  # solution not found
        return Decimal("NaN")
    return Decimal(irr)
