import math
from datetime import datetime, timedelta
from decimal import Decimal

import pytest
from src.models.model_objects.cash_objects import CashAccount
from src.models.model_objects.currency_objects import CashAmount, Currency
from src.models.model_objects.security_objects import (
    Security,
    SecurityAccount,
    SecurityTransaction,
    SecurityTransactionType,
    SecurityTransfer,
)
from src.models.record_keeper import RecordKeeper
from src.models.statistics.security_stats import calculate_irr, calculate_total_irr
from src.models.user_settings import user_settings


def test_calculate_irr_empty() -> None:
    account = SecurityAccount("Test 1")
    usd = Currency("USD", 2)
    security = Security("Alphabet", "ABC", "Stock", usd, 1)

    irr = calculate_irr(security, [account])
    assert irr.is_nan()


def test_calculate_irr_zero() -> None:
    account = SecurityAccount("Test 1")
    usd = Currency("USD", 2)
    cash_account = CashAccount("Test Cash", usd, CashAmount(0, usd))
    security = Security("Alphabet", "ABC", "Stock", usd, 1)
    today = datetime.now(user_settings.settings.time_zone)

    security.set_price(today.date() - timedelta(days=365), CashAmount(1, usd))

    SecurityTransaction(
        "test",
        today - timedelta(days=365),
        SecurityTransactionType.BUY,
        security,
        1,
        CashAmount(1, usd),
        account,
        cash_account,
    )

    irr = calculate_irr(security, [account])
    assert not irr.is_nan()
    assert abs(irr) < Decimal("1e-12")


def test_calculate_irr_positive() -> None:
    account = SecurityAccount("Test 1")
    usd = Currency("USD", 2)
    cash_account = CashAccount("Test Cash", usd, CashAmount(0, usd))
    security = Security("Alphabet", "ABC", "Stock", usd, 1)
    today = datetime.now(user_settings.settings.time_zone)

    security.set_price(today.date() - timedelta(days=365), CashAmount(1, usd))
    security.set_price(today.date(), CashAmount("1.1", usd))

    SecurityTransaction(
        "test",
        today - timedelta(days=365),
        SecurityTransactionType.BUY,
        security,
        1,
        CashAmount(1, usd),
        account,
        cash_account,
    )

    irr = calculate_irr(security, [account])
    assert not irr.is_nan()
    assert math.isclose(irr, 0.1)


def test_calculate_irr_no_shares() -> None:
    account = SecurityAccount("Test 1")
    usd = Currency("USD", 2)
    cash_account = CashAccount("Test Cash", usd, CashAmount(0, usd))
    security = Security("Alphabet", "ABC", "Stock", usd, 1)
    today = datetime.now(user_settings.settings.time_zone)

    SecurityTransaction(
        "test",
        today - timedelta(days=365),
        SecurityTransactionType.BUY,
        security,
        1,
        CashAmount(1, usd),
        account,
        cash_account,
    )
    SecurityTransaction(
        "test",
        today - timedelta(days=365),
        SecurityTransactionType.SELL,
        security,
        1,
        CashAmount(1, usd),
        account,
        cash_account,
    )

    irr = calculate_irr(security, [account])
    assert irr.is_nan()


def test_calculate_irr_future_dates() -> None:
    account = SecurityAccount("Test 1")
    usd = Currency("USD", 2)
    cash_account = CashAccount("Test Cash", usd, CashAmount(0, usd))
    security = Security("Alphabet", "ABC", "Stock", usd, 1)
    today = datetime.now(user_settings.settings.time_zone)

    security.set_price(today.date(), CashAmount(1, usd))

    SecurityTransaction(
        "test",
        today + timedelta(days=1),
        SecurityTransactionType.BUY,
        security,
        1,
        CashAmount(1, usd),
        account,
        cash_account,
    )

    with pytest.raises(
        ValueError, match="Unable to calculate IRR based on future prices."
    ):
        calculate_irr(security, [account])


def test_calculate_irr_positive_same_date() -> None:
    account = SecurityAccount("Test 1")
    currency = Currency("USD", 2)
    cash_account = CashAccount("Test Cash", currency, CashAmount(0, currency))
    security = Security("Alphabet", "ABC", "Stock", currency, 1)
    today = datetime.now(user_settings.settings.time_zone)

    security.set_price(today.date() - timedelta(days=365), CashAmount(1, currency))
    security.set_price(today.date(), CashAmount("1.1", currency))

    SecurityTransaction(
        "test",
        today - timedelta(days=365),
        SecurityTransactionType.BUY,
        security,
        1,
        CashAmount(1, currency),
        account,
        cash_account,
    )

    SecurityTransaction(
        "test",
        today,
        SecurityTransactionType.BUY,
        security,
        1,
        CashAmount(1, currency),
        account,
        cash_account,
    )

    irr = calculate_irr(security, [account])
    assert not irr.is_nan()
    assert irr > 0


def test_calculate_total_irr_positive() -> None:
    account = SecurityAccount("Test 1")
    currency = Currency("USD", 2)
    cash_account = CashAccount("Test Cash", currency, CashAmount(0, currency))
    security = Security("Alphabet", "ABC", "Stock", currency, 1)
    today = datetime.now(user_settings.settings.time_zone)

    record_keeper = RecordKeeper()
    record_keeper._security_accounts = [account]
    record_keeper._base_currency = currency

    security.set_price(today.date() - timedelta(days=365), CashAmount(1, currency))
    security.set_price(today.date(), CashAmount("1.1", currency))

    SecurityTransaction(
        "test",
        today - timedelta(days=365),
        SecurityTransactionType.BUY,
        security,
        1,
        CashAmount(1, currency),
        account,
        cash_account,
    )

    irr = calculate_total_irr(record_keeper)
    assert not irr.is_nan()
    assert math.isclose(irr, 0.1)


def test_calculate_total_irr_positive_same_date() -> None:
    account = SecurityAccount("Test 1")
    currency = Currency("USD", 2)
    cash_account = CashAccount("Test Cash", currency, CashAmount(0, currency))
    security = Security("Alphabet", "ABC", "Stock", currency, 1)
    today = datetime.now(user_settings.settings.time_zone)

    record_keeper = RecordKeeper()
    record_keeper._security_accounts = [account]
    record_keeper._base_currency = currency

    security.set_price(today.date() - timedelta(days=365), CashAmount(1, currency))
    security.set_price(today.date(), CashAmount("1.1", currency))

    SecurityTransaction(
        "test",
        today - timedelta(days=365),
        SecurityTransactionType.BUY,
        security,
        1,
        CashAmount(1, currency),
        account,
        cash_account,
    )

    SecurityTransaction(
        "test",
        today,
        SecurityTransactionType.BUY,
        security,
        1,
        CashAmount(1, currency),
        account,
        cash_account,
    )

    irr = calculate_total_irr(record_keeper)
    assert not irr.is_nan()
    assert irr > 0


def test_calculate_total_irr_no_shares() -> None:
    account = SecurityAccount("Test 1")
    currency = Currency("USD", 2)
    cash_account = CashAccount("Test Cash", currency, CashAmount(0, currency))
    security = Security("Alphabet", "ABC", "Stock", currency, 1)
    today = datetime.now(user_settings.settings.time_zone)

    record_keeper = RecordKeeper()
    record_keeper._security_accounts = [account]
    record_keeper._base_currency = currency

    SecurityTransaction(
        "test",
        today - timedelta(days=365),
        SecurityTransactionType.BUY,
        security,
        1,
        CashAmount(1, currency),
        account,
        cash_account,
    )
    SecurityTransaction(
        "test",
        today - timedelta(days=365),
        SecurityTransactionType.SELL,
        security,
        1,
        CashAmount(1, currency),
        account,
        cash_account,
    )

    irr = calculate_total_irr(record_keeper)
    assert irr.is_nan()


def test_calculate_total_irr_empty() -> None:
    account = SecurityAccount("Test 1")
    currency = Currency("USD", 2)

    record_keeper = RecordKeeper()
    record_keeper._security_accounts = [account]
    record_keeper._base_currency = currency

    irr = calculate_total_irr(record_keeper)
    assert irr.is_nan()


def test_calculate_total_irr_only_transfers() -> None:
    account_1 = SecurityAccount("Test 1")
    account_2 = SecurityAccount("Test 2")
    currency = Currency("USD", 2)
    security = Security("Alphabet", "ABC", "Stock", currency, 1)
    today = datetime.now(user_settings.settings.time_zone)

    record_keeper = RecordKeeper()
    record_keeper._security_accounts = [account_1]
    record_keeper._base_currency = currency

    SecurityTransfer(
        "test",
        today - timedelta(days=365),
        security,
        1,
        account_1,
        account_2,
    )

    irr = calculate_total_irr(record_keeper)
    assert irr.is_nan()
