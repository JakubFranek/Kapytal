import math
from datetime import datetime, timedelta
from decimal import Decimal

import pytest
from src.models.model_objects.cash_objects import CashAccount
from src.models.model_objects.currency_objects import CashAmount, Currency, ExchangeRate
from src.models.model_objects.security_objects import (
    Security,
    SecurityAccount,
    SecurityTransaction,
    SecurityTransactionType,
    SecurityTransfer,
)
from src.models.record_keeper import RecordKeeper
from src.models.statistics.security_stats import (
    SecurityAccountStats,
    calculate_irr,
    calculate_total_irr,
)
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


def test_calculate_irr_with_full_sell() -> None:
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
    SecurityTransaction(
        "test",
        today,
        SecurityTransactionType.SELL,
        security,
        1,
        CashAmount(1, usd),
        account,
        cash_account,
    )

    irr = calculate_irr(security, [account])
    assert not irr.is_nan()
    assert math.isclose(irr, 0, abs_tol=1e-12)


def test_calculate_irr_with_partial_sell() -> None:
    account = SecurityAccount("Test 1")
    usd = Currency("USD", 2)
    cash_account = CashAccount("Test Cash", usd, CashAmount(0, usd))
    security = Security("Alphabet", "ABC", "Stock", usd, 1)
    today = datetime.now(user_settings.settings.time_zone)

    security.set_price(today.date() - timedelta(days=365), CashAmount(1, usd))
    security.set_price(today.date(), CashAmount(2, usd))

    SecurityTransaction(
        "test",
        today - timedelta(days=365),
        SecurityTransactionType.BUY,
        security,
        2,
        CashAmount(1, usd),
        account,
        cash_account,
    )
    SecurityTransaction(
        "test",
        today,
        SecurityTransactionType.SELL,
        security,
        1,
        CashAmount(2, usd),
        account,
        cash_account,
    )

    irr = calculate_irr(security, [account])
    assert not irr.is_nan()
    assert math.isclose(irr, 1)


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


def test_security_account_stats() -> None:
    account = SecurityAccount("Test 1")
    usd = Currency("USD", 2)
    eur = Currency("EUR", 2)

    cash_account = CashAccount("Test Cash", usd, CashAmount(0, usd))
    security = Security("Alphabet", "ABC", "Stock", usd, 1)
    today = datetime.now(user_settings.settings.time_zone)

    security.set_price(today.date() - timedelta(days=365), CashAmount(1, usd))
    security.set_price(today.date(), CashAmount(4, usd))

    exchange_rate = ExchangeRate(usd, eur)
    old_rate = Decimal(1)
    exchange_rate.set_rate(today.date() - timedelta(days=365), old_rate)
    rate = Decimal("0.9")
    exchange_rate.set_rate(today.date(), rate)

    SecurityTransaction(
        "test",
        today - timedelta(days=365),
        SecurityTransactionType.BUY,
        security,
        2,
        CashAmount(1, usd),
        account,
        cash_account,
    )
    SecurityTransaction(
        "test",
        today,
        SecurityTransactionType.SELL,
        security,
        1,
        CashAmount(2, usd),
        account,
        cash_account,
    )

    stats = SecurityAccountStats(security, account, eur)

    assert stats.name == account.path

    assert stats.shares_owned == Decimal(1)
    assert stats.shares_sold == Decimal(1)
    assert stats.shares_bought == Decimal(2)
    assert stats.shares_transferred == Decimal(0)

    assert stats.price_market_native == CashAmount(4, usd)
    assert stats.price_avg_buy_native == CashAmount(1, usd)
    assert stats.price_avg_sell_native == CashAmount(2, usd)
    assert stats.price_avg_buy_base == CashAmount(1 * old_rate, eur)
    assert stats.price_avg_sell_base == CashAmount(2 * rate, eur)

    assert stats.value_current_native == CashAmount(4, usd)
    assert stats.value_current_base == CashAmount(4 * rate, eur)

    assert stats.value_sold_native == CashAmount(2, usd)
    assert stats.value_sold_base == CashAmount(2 * rate, eur)

    assert stats.value_bought_native == CashAmount(2, usd)
    assert stats.value_bought_base == CashAmount(2 * old_rate, eur)

    assert stats.gain_native_unrealized == CashAmount(3, usd)
    assert stats.gain_base_unrealized == CashAmount(4 * rate - 1, eur)
    assert stats.return_native_unrealized_pct == Decimal(300)
    assert stats.return_base_unrealized_pct == Decimal(260)

    assert stats.gain_native_realized == CashAmount(1, usd)
    assert stats.gain_base_realized == CashAmount(2 * rate - 1, eur)
    assert stats.return_native_realized_pct == Decimal(100)
    assert stats.return_base_realized_pct == Decimal(80)

    assert stats.gain_native_total == CashAmount(4, usd)
    assert stats.gain_base_total == CashAmount(4 * rate - 1 + 2 * rate - 1, eur)
    assert stats.return_native_total_pct == Decimal(200)
    assert stats.return_base_total_pct == Decimal(170)

    assert math.isclose(stats.irr_native_total_pct, 200)
    assert math.isclose(stats.irr_base_total_pct, 170)
