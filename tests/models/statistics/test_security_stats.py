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
from src.models.statistics.security_stats import (
    SecurityAccountStats,
    SecurityStats,
    SecurityStatsData,
    _calculate_return_percentage,
    _safe_convert,
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

    irr = calculate_total_irr([account], currency)
    assert not irr.is_nan()
    assert math.isclose(irr, 0.1)


def test_calculate_total_irr_positive_same_date() -> None:
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

    irr = calculate_total_irr([account], currency)
    assert not irr.is_nan()
    assert irr > 0


def test_calculate_total_irr_no_shares() -> None:
    account = SecurityAccount("Test 1")
    currency = Currency("USD", 2)
    cash_account = CashAccount("Test Cash", currency, CashAmount(0, currency))
    security = Security("Alphabet", "ABC", "Stock", currency, 1)
    today = datetime.now(user_settings.settings.time_zone)

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

    irr = calculate_total_irr([account], currency)
    assert irr.is_nan()


def test_calculate_total_irr_empty() -> None:
    account = SecurityAccount("Test 1")
    currency = Currency("USD", 2)

    irr = calculate_total_irr([account], currency)
    assert irr.is_nan()


def test_calculate_total_irr_no_currency() -> None:
    account = SecurityAccount("Test 1")

    irr = calculate_total_irr([account], None)
    assert irr.is_nan()


def test_calculate_total_irr_only_transfers() -> None:
    account_1 = SecurityAccount("Test 1")
    account_2 = SecurityAccount("Test 2")
    currency = Currency("USD", 2)
    security = Security("Alphabet", "ABC", "Stock", currency, 1)
    today = datetime.now(user_settings.settings.time_zone)

    SecurityTransfer(
        "test",
        today - timedelta(days=365),
        security,
        1,
        account_1,
        account_2,
    )

    irr = calculate_total_irr([account_1, account_2], currency)
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
        "buy",
        today - timedelta(days=365),
        SecurityTransactionType.BUY,
        security,
        2,
        CashAmount(1, usd),
        account,
        cash_account,
    )
    SecurityTransaction(
        "dividend",
        today,
        SecurityTransactionType.DIVIDEND,
        security,
        2,
        CashAmount("0.1", usd),
        account,
        cash_account,
    )
    SecurityTransaction(
        "sell",
        today,
        SecurityTransactionType.SELL,
        security,
        1,
        CashAmount(2, usd),
        account,
        cash_account,
    )

    stats = SecurityAccountStats(security, account, eur, None)

    assert stats.name == account.path
    assert (
        stats.__repr__() == f"SecurityAccountStats('{security.name}', '{account.path}')"
    )
    assert stats.is_base == (eur == security.currency)

    assert stats.shares_owned == Decimal(1)
    assert stats.shares_sold == Decimal(1)
    assert stats.shares_bought == Decimal(2)
    assert stats.shares_transferred == Decimal(0)

    assert stats.price_market_native == CashAmount(4, usd)
    assert stats.price_market_base == CashAmount(4 * rate, eur)
    assert stats.price_avg_buy_native == CashAmount(1, usd)
    assert stats.price_avg_sell_native == CashAmount(2, usd)
    assert stats.price_avg_buy_base == CashAmount(1 * old_rate, eur)
    assert stats.price_avg_sell_base == CashAmount(2 * rate, eur)
    assert stats.amount_avg_dividend_native == CashAmount("0.1", usd)
    assert stats.amount_avg_dividend_base == CashAmount("0.09", eur)

    assert stats.value_current_native == CashAmount(4, usd)
    assert stats.value_current_base == CashAmount(4 * rate, eur)

    assert stats.value_sold_native == CashAmount(2, usd)
    assert stats.value_sold_base == CashAmount(2 * rate, eur)

    assert stats.value_bought_native == CashAmount(2, usd)
    assert stats.value_bought_base == CashAmount(2 * old_rate, eur)

    assert stats.gain_unrealized_native == CashAmount(3, usd)
    assert stats.gain_unrealized_base == CashAmount(4 * rate - 1, eur)
    assert stats.return_pct_unrealized_native == Decimal(300)
    assert stats.return_pct_unrealized_base == Decimal(260)

    assert stats.gain_realized_native == CashAmount("1.2", usd)  # +0.2 for dividend
    assert stats.gain_realized_base == CashAmount("0.98", eur)
    assert stats.value_dividend_native == CashAmount("0.2", usd)
    assert stats.value_dividend_base == CashAmount("0.18", eur)
    assert stats.return_pct_realized_native == Decimal(110)
    assert stats.return_pct_realized_base == Decimal(89)

    assert stats.gain_total_native == CashAmount("4.2", usd)
    assert stats.gain_total_base == CashAmount("3.58", eur)
    assert stats.gain_total_currency == CashAmount(Decimal("-0.2"), eur)
    assert stats.return_pct_total_native == Decimal(210)
    assert stats.return_pct_total_base == Decimal(179)

    assert math.isclose(stats.irr_pct_total_native, 210)
    assert math.isclose(stats.irr_pct_total_base, 179)


def test_security_stats() -> None:
    account_1 = SecurityAccount("Test 1")
    account_2 = SecurityAccount("Test 2")
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
        account_1,
        cash_account,
    )
    SecurityTransaction(
        "test",
        today,
        SecurityTransactionType.SELL,
        security,
        1,
        CashAmount(2, usd),
        account_1,
        cash_account,
    )

    SecurityTransaction(
        "test",
        today - timedelta(days=365),
        SecurityTransactionType.BUY,
        security,
        1,
        CashAmount(1, usd),
        account_2,
        cash_account,
    )
    SecurityTransaction(
        "test",
        today,
        SecurityTransactionType.DIVIDEND,
        security,
        1,
        CashAmount("0.1", usd),
        account_2,
        cash_account,
    )
    SecurityTransaction(
        "test",
        today,
        SecurityTransactionType.SELL,
        security,
        1,
        CashAmount(2, usd),
        account_2,
        cash_account,
    )

    stats = SecurityStats(security, [account_1, account_2], eur)

    assert stats.name == security.name
    assert stats.__repr__() == "SecurityStats('Alphabet')"
    assert stats.is_base == (eur == security.currency)

    assert stats.shares_owned == Decimal(1)
    assert stats.shares_sold == Decimal(2)
    assert stats.shares_bought == Decimal(3)
    assert stats.shares_transferred == Decimal(0)

    assert stats.price_market_native == CashAmount(4, usd)
    assert stats.price_avg_buy_native == CashAmount(1, usd)
    assert stats.price_avg_sell_native == CashAmount(2, usd)
    assert stats.price_avg_buy_base == CashAmount(1 * old_rate, eur)
    assert stats.price_avg_sell_base == CashAmount(2 * rate, eur)

    assert stats.value_current_native == CashAmount(4, usd)
    assert stats.value_current_base == CashAmount(4 * rate, eur)

    assert stats.value_sold_native == CashAmount(4, usd)
    assert stats.value_sold_base == CashAmount(4 * rate, eur)

    assert stats.value_bought_native == CashAmount(3, usd)
    assert stats.value_bought_base == CashAmount(3 * old_rate, eur)

    assert stats.gain_unrealized_native == CashAmount(3, usd)
    assert stats.gain_unrealized_base == CashAmount(4 * rate - 1, eur)
    assert stats.return_pct_unrealized_native == Decimal(300)
    assert stats.return_pct_unrealized_base == Decimal(260)

    assert stats.gain_realized_native == CashAmount("2.1", usd)
    assert stats.gain_realized_base == CashAmount(
        4 * rate - 2 + rate * Decimal("0.1"), eur
    )
    assert stats.return_pct_realized_native == Decimal(110)
    assert stats.return_pct_realized_base == Decimal(89)

    assert stats.gain_total_native == CashAmount("5.1", usd)
    assert stats.gain_total_base == CashAmount(
        4 * rate - 1 + 4 * rate - 2 + rate * Decimal("0.1"), eur
    )
    assert stats.gain_total_currency == CashAmount(Decimal("-0.3"), eur)
    assert stats.return_pct_total_native == Decimal(170)
    assert stats.return_pct_total_base == Decimal(143)

    assert math.isclose(stats.irr_pct_total_native, 170)
    assert math.isclose(stats.irr_pct_total_base, 143)


def test_security_stats_data() -> None:
    account_1 = SecurityAccount("Test 1")
    account_2 = SecurityAccount("Test 2")
    usd = Currency("USD", 2)
    eur = Currency("EUR", 2)

    cash_account = CashAccount("Test Cash", usd, CashAmount(0, usd))
    security_1 = Security("Alphabet", "ABC", "Stock", usd, 1)
    security_2 = Security("Wowazon", "WAZ", "Stock", usd, 1)
    today = datetime.now(user_settings.settings.time_zone)

    security_1.set_price(today.date() - timedelta(days=365), CashAmount(1, usd))
    security_1.set_price(today.date(), CashAmount(4, usd))

    security_2.set_price(today.date() - timedelta(days=365), CashAmount(2, usd))
    security_2.set_price(today.date(), CashAmount(4, usd))

    exchange_rate = ExchangeRate(usd, eur)
    old_rate = Decimal(1)
    exchange_rate.set_rate(today.date() - timedelta(days=365), old_rate)
    rate = Decimal("0.9")
    exchange_rate.set_rate(today.date(), rate)

    SecurityTransaction(
        "test",
        today - timedelta(days=365),
        SecurityTransactionType.BUY,
        security_1,
        2,
        CashAmount(1, usd),
        account_1,
        cash_account,
    )
    SecurityTransaction(
        "test",
        today,
        SecurityTransactionType.SELL,
        security_1,
        1,
        CashAmount(2, usd),
        account_1,
        cash_account,
    )

    SecurityTransaction(
        "test",
        today - timedelta(days=365),
        SecurityTransactionType.BUY,
        security_2,
        2,
        CashAmount(1, usd),
        account_2,
        cash_account,
    )
    SecurityTransaction(
        "test",
        today,
        SecurityTransactionType.DIVIDEND,
        security_2,
        1,
        CashAmount("0.1", usd),
        account_2,
        cash_account,
    )
    SecurityTransaction(
        "test",
        today,
        SecurityTransactionType.SELL,
        security_2,
        1,
        CashAmount(2, usd),
        account_2,
        cash_account,
    )

    stats = SecurityStatsData([security_1, security_2], [account_1, account_2], eur)

    total_stats = stats.total_stats

    assert stats.__repr__() == "SecurityStatsData(len=2)"
    assert total_stats.__repr__() == "TotalSecurityStats()"
    assert total_stats.name == "Total"
    assert total_stats.is_base is True

    assert total_stats.value_current_base == CashAmount((4 + 4) * rate, eur)
    assert total_stats.value_current_native is None

    assert total_stats.cost_basis_realized_base == CashAmount(4 * old_rate - 2, eur)
    assert total_stats.cost_basis_realized_native is None

    assert total_stats.cost_basis_unrealized_base == CashAmount(4 * old_rate - 2, eur)
    assert total_stats.cost_basis_unrealized_native is None

    assert total_stats.gain_unrealized_base == CashAmount(8 * rate - 2, eur)
    assert total_stats.gain_unrealized_native is None

    assert total_stats.gain_realized_base == CashAmount(
        4 * rate - 2 + rate * Decimal("0.1"), eur
    )
    assert total_stats.gain_realized_native is None

    assert total_stats.gain_total_base == CashAmount(
        12 * rate - 4 + rate * Decimal("0.1"), eur
    )
    assert total_stats.gain_total_native is None

    assert total_stats.gain_total_currency == CashAmount("-0.4", eur)

    assert total_stats.return_pct_unrealized_base == Decimal(260)
    assert total_stats.return_pct_unrealized_native == Decimal(0)

    assert total_stats.return_pct_realized_base == Decimal(84.5)
    assert total_stats.return_pct_realized_native == Decimal(0)

    assert total_stats.return_pct_total_base == Decimal("172.25")
    assert total_stats.return_pct_total_native == Decimal(0)

    assert math.isclose(total_stats.irr_pct_total_base, 172.25)


def test_security_stats_data_no_transactions() -> None:
    account_1 = SecurityAccount("Test 1")
    account_2 = SecurityAccount("Test 2")
    usd = Currency("USD", 2)
    eur = Currency("EUR", 2)

    security_1 = Security("Alphabet", "ABC", "Stock", usd, 1)
    security_2 = Security("Wowazon", "WAZ", "Stock", usd, 1)
    today = datetime.now(user_settings.settings.time_zone)

    security_1.set_price(today.date() - timedelta(days=365), CashAmount(1, usd))
    security_1.set_price(today.date(), CashAmount(4, usd))

    security_2.set_price(today.date() - timedelta(days=365), CashAmount(2, usd))
    security_2.set_price(today.date(), CashAmount(4, usd))

    exchange_rate = ExchangeRate(usd, eur)
    old_rate = Decimal(1)
    exchange_rate.set_rate(today.date() - timedelta(days=365), old_rate)
    rate = Decimal("0.9")
    exchange_rate.set_rate(today.date(), rate)

    stats = SecurityStatsData([security_1, security_2], [account_1, account_2], eur)

    total_stats = stats.total_stats

    assert stats.__repr__() == "SecurityStatsData(len=2)"
    assert total_stats.__repr__() == "TotalSecurityStats()"
    assert total_stats.is_base is True


def test_calculate_return_percentage_empty_tuple_denom() -> None:
    result = _calculate_return_percentage(
        nom=CashAmount(1, Currency("USD", 2)), denom=()
    )
    assert result == Decimal(0)


def test_calculate_return_percentage_tuple_of_none_denom() -> None:
    result = _calculate_return_percentage(
        nom=CashAmount(1, Currency("USD", 2)), denom=(None,)
    )
    assert result == Decimal(0)


def test_calculate_return_percentage_none_denom() -> None:
    result = _calculate_return_percentage(
        nom=CashAmount(1, Currency("USD", 2)), denom=None
    )
    assert result == Decimal(0)


def test_calculate_return_percentage_tuple_of_zero_denom() -> None:
    currency = Currency("USD", 2)
    result = _calculate_return_percentage(
        nom=CashAmount(1, currency),
        denom=(CashAmount(0, currency), CashAmount(0, currency)),
    )
    assert result == Decimal(0)


def test_safe_convert_no_conversion_found() -> None:
    result = _safe_convert(CashAmount(1, Currency("EUR", 2)), Currency("USD", 2))
    assert result.is_nan()
