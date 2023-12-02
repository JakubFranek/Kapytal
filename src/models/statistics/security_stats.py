from datetime import datetime
from decimal import Decimal

from pyxirr import xirr
from src.models.model_objects.security_objects import (
    Security,
    SecurityAccount,
    SecurityTransaction,
)
from src.models.user_settings import user_settings


def calculate_irr(security: Security, accounts: list[SecurityAccount]) -> Decimal:
    transactions = [
        transaction
        for account in accounts
        for transaction in account.transactions
        if transaction.security == security
        and isinstance(transaction, SecurityTransaction)
    ]
    transactions.sort(key=lambda t: t.datetime_)

    dates = []
    cashflows = []
    for transaction in transactions:
        _date = transaction.datetime_.date()
        amount = transaction.get_amount(transaction.cash_account).value_normalized
        if len(dates) > 0 and _date == dates[-1]:
            cashflows[-1] += amount
        else:
            dates.append(_date)
            cashflows.append(amount)

    # add last fictitious outflow as if all investment was liquidated
    sell_all_amount = Decimal(0)
    price = security.price
    for account in accounts:
        sell_all_amount += account.securities[security] * price.value_normalized

    dates.append(datetime.now(user_settings.settings.time_zone).date())
    cashflows.append(sell_all_amount)

    irr = xirr(dates, cashflows)
    if irr is None:  # solution not found
        return Decimal("NaN")
    return Decimal(irr)
