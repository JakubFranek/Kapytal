from datetime import datetime, timedelta

import pytest
from dateutil.relativedelta import relativedelta
from src.models.model_objects.attributes import (
    Attribute,
    AttributeType,
    Category,
    CategoryType,
)
from src.models.model_objects.cash_objects import (
    CashAccount,
    CashTransaction,
    CashTransactionType,
    RefundTransaction,
)
from src.models.model_objects.currency_objects import CashAmount, Currency
from src.models.statistics.attribute_stats import (
    calculate_attribute_stats,
    calculate_periodic_attribute_stats,
    calculate_periodic_totals_and_averages,
)
from src.models.user_settings import user_settings


def test_calculate_attribute_stats() -> None:
    currency = Currency("USD", 2)
    cash_account = CashAccount("Test CashAccount", currency, currency.zero_amount)

    tag_1 = Attribute("tag1", AttributeType.TAG)
    tag_2 = Attribute("tag2", AttributeType.TAG)

    payee_1 = Attribute("payee1", AttributeType.PAYEE)
    payee_2 = Attribute("payee2", AttributeType.PAYEE)

    category = Category("Category", CategoryType.INCOME_AND_EXPENSE)

    now = datetime.now(user_settings.settings.time_zone)

    t1 = CashTransaction(
        "test",
        now,
        CashTransactionType.INCOME,
        cash_account,
        payee_1,
        [(category, CashAmount(1, currency))],
        [(tag_1, CashAmount(1, currency))],
    )

    t2 = CashTransaction(
        "test",
        now,
        CashTransactionType.EXPENSE,
        cash_account,
        payee_2,
        [(category, CashAmount(2, currency))],
        [(tag_2, CashAmount(2, currency))],
    )

    t3 = CashTransaction(
        "test",
        now,
        CashTransactionType.EXPENSE,
        cash_account,
        payee_1,
        [(category, CashAmount(2, currency))],
        [(tag_1, CashAmount(2, currency))],
    )

    tag_stats = calculate_attribute_stats([t1, t2, t3], currency, [tag_1, tag_2])
    assert tag_stats[tag_1].no_of_transactions == 2
    assert tag_stats[tag_2].no_of_transactions == 1
    assert tag_stats[tag_1].balance == CashAmount(-1, currency)
    assert tag_stats[tag_2].balance == CashAmount(-2, currency)
    assert tag_stats[tag_1].transactions == {t1, t3}
    assert tag_stats[tag_2].transactions == {t2}
    assert tag_stats[tag_1].attribute == tag_1
    assert tag_stats[tag_2].attribute == tag_2

    payee_stats = calculate_attribute_stats([t1, t2, t3], currency, [payee_1, payee_2])
    assert payee_stats[payee_1].no_of_transactions == 2
    assert payee_stats[payee_2].no_of_transactions == 1
    assert payee_stats[payee_1].balance == CashAmount(-1, currency)
    assert payee_stats[payee_2].balance == CashAmount(-2, currency)
    assert payee_stats[payee_1].transactions == {t1, t3}
    assert payee_stats[payee_2].transactions == {t2}
    assert payee_stats[payee_1].attribute == payee_1
    assert payee_stats[payee_2].attribute == payee_2


def test_calculate_attribute_stats_multiple_types() -> None:
    currency = Currency("USD", 2)
    tag_1 = Attribute("tag1", AttributeType.TAG)
    payee_1 = Attribute("payee1", AttributeType.PAYEE)

    with pytest.raises(ValueError, match="All Attributes must be of the same type_."):
        calculate_attribute_stats([], currency, [tag_1, payee_1])


def test_calculate_periodic_attribute_stats() -> None:
    currency = Currency("USD", 2)
    cash_account = CashAccount("Test CashAccount", currency, currency.zero_amount)

    tag_1 = Attribute("tag1", AttributeType.TAG)
    payee_1 = Attribute("payee1", AttributeType.PAYEE)

    category = Category("Category", CategoryType.INCOME_AND_EXPENSE)

    now = datetime.now(user_settings.settings.time_zone)
    y1 = (now - relativedelta(years=2)).strftime("%Y")
    y2 = (now - relativedelta(years=1)).strftime("%Y")
    y3 = (now - relativedelta(years=0)).strftime("%Y")

    t1 = CashTransaction(
        "test",
        now - relativedelta(years=2),
        CashTransactionType.INCOME,
        cash_account,
        payee_1,
        [(category, CashAmount(1, currency))],
        [(tag_1, CashAmount(1, currency))],
    )

    t2 = CashTransaction(
        "test",
        now - relativedelta(years=1),
        CashTransactionType.INCOME,
        cash_account,
        payee_1,
        [(category, CashAmount(2, currency))],
        [(tag_1, CashAmount(2, currency))],
    )

    t3 = CashTransaction(
        "test",
        now,
        CashTransactionType.INCOME,
        cash_account,
        payee_1,
        [(category, CashAmount(3, currency))],
        [(tag_1, CashAmount(3, currency))],
    )

    tag_stats = calculate_periodic_attribute_stats(
        [t1, t2, t3], currency, [tag_1], period_format="%Y"
    )
    assert len(tag_stats[y1]) == 1
    assert tag_stats[y1][0].attribute == tag_1
    assert tag_stats[y1][0].no_of_transactions == 1
    assert tag_stats[y1][0].transactions == {t1}
    assert tag_stats[y1][0].balance == CashAmount(1, currency)

    assert len(tag_stats[y2]) == 1
    assert tag_stats[y2][0].attribute == tag_1
    assert tag_stats[y2][0].no_of_transactions == 1
    assert tag_stats[y2][0].transactions == {t2}
    assert tag_stats[y2][0].balance == CashAmount(2, currency)

    assert len(tag_stats[y3]) == 1
    assert tag_stats[y3][0].attribute == tag_1
    assert tag_stats[y3][0].no_of_transactions == 1
    assert tag_stats[y3][0].transactions == {t3}
    assert tag_stats[y3][0].balance == CashAmount(3, currency)


def test_calculate_periodic_totals_and_averages() -> None:
    currency = Currency("USD", 2)
    cash_account = CashAccount("Test CashAccount", currency, currency.zero_amount)

    tag_1 = Attribute("tag1", AttributeType.TAG)
    payee_1 = Attribute("payee1", AttributeType.PAYEE)

    category = Category("Category", CategoryType.INCOME_AND_EXPENSE)

    now = datetime.now(user_settings.settings.time_zone)
    y1 = (now - relativedelta(years=2)).strftime("%B %Y")
    y2 = (now - relativedelta(years=1)).strftime("%B %Y")
    y3 = (now - relativedelta(years=0)).strftime("%B %Y")

    t1a = CashTransaction(
        "test",
        now - relativedelta(years=2),
        CashTransactionType.INCOME,
        cash_account,
        payee_1,
        [(category, CashAmount(1, currency))],
        [(tag_1, CashAmount(1, currency))],
    )
    t1b = CashTransaction(
        "test",
        now - relativedelta(years=2),
        CashTransactionType.INCOME,
        cash_account,
        payee_1,
        [(category, CashAmount(3, currency))],
        [(tag_1, CashAmount(3, currency))],
    )

    t2 = CashTransaction(
        "test",
        now - relativedelta(years=1),
        CashTransactionType.INCOME,
        cash_account,
        payee_1,
        [(category, CashAmount(2, currency))],
        [(tag_1, CashAmount(2, currency))],
    )

    t3 = CashTransaction(
        "test",
        now,
        CashTransactionType.INCOME,
        cash_account,
        payee_1,
        [(category, CashAmount(3, currency))],
        [(tag_1, CashAmount(3, currency))],
    )

    periodic_stats = calculate_periodic_attribute_stats(
        [t1a, t1b, t2, t3], currency, [tag_1]
    )
    period_totals, attr_averages, attr_totals = calculate_periodic_totals_and_averages(
        periodic_stats, currency
    )

    assert len(period_totals[y1]) == 2
    assert period_totals[y1].transactions == {t1a, t1b}
    assert period_totals[y1].balance == CashAmount(4, currency)

    assert len(period_totals[y2]) == 1
    assert period_totals[y2].transactions == {t2}
    assert period_totals[y2].balance == CashAmount(2, currency)

    assert len(period_totals[y3]) == 1
    assert period_totals[y3].transactions == {t3}
    assert period_totals[y3].balance == CashAmount(3, currency)

    assert len(attr_averages) == 1
    assert attr_averages[tag_1].transactions == {t1a, t1b, t2, t3}
    assert attr_averages[tag_1].balance == CashAmount(3, currency)

    assert len(attr_totals) == 1
    assert attr_totals[tag_1].transactions == {t1a, t1b, t2, t3}
    assert attr_totals[tag_1].balance == CashAmount(9, currency)


def test_calculate_attribute_stats_no_base_currency() -> None:
    tag_1 = Attribute("tag1", AttributeType.TAG)
    tag_2 = Attribute("tag2", AttributeType.TAG)

    payee_1 = Attribute("payee1", AttributeType.PAYEE)
    payee_2 = Attribute("payee2", AttributeType.PAYEE)

    tag_stats = calculate_attribute_stats([], None, [tag_1, tag_2])
    assert tag_stats[tag_1].no_of_transactions == 0
    assert tag_stats[tag_2].no_of_transactions == 0
    assert tag_stats[tag_1].balance is None
    assert tag_stats[tag_2].balance is None
    assert tag_stats[tag_1].transactions == set()
    assert tag_stats[tag_2].transactions == set()
    assert tag_stats[tag_1].attribute == tag_1
    assert tag_stats[tag_2].attribute == tag_2

    payee_stats = calculate_attribute_stats([], None, [payee_1, payee_2])
    assert payee_stats[payee_1].no_of_transactions == 0
    assert payee_stats[payee_2].no_of_transactions == 0
    assert payee_stats[payee_1].balance is None
    assert payee_stats[payee_2].balance is None
    assert payee_stats[payee_1].transactions == set()
    assert payee_stats[payee_2].transactions == set()
    assert payee_stats[payee_1].attribute == payee_1
    assert payee_stats[payee_2].attribute == payee_2


def test_calculate_attribute_stats_with_refund() -> None:
    currency = Currency("USD", 2)
    cash_account = CashAccount("Test CashAccount", currency, currency.zero_amount)

    tag_1 = Attribute("tag1", AttributeType.TAG)
    tag_2 = Attribute("tag2", AttributeType.TAG)
    payee = Attribute("payee", AttributeType.PAYEE)
    category = Category("Category", CategoryType.INCOME_AND_EXPENSE)

    now = datetime.now(user_settings.settings.time_zone)

    t1 = CashTransaction(
        "test",
        now - timedelta(days=1),
        CashTransactionType.EXPENSE,
        cash_account,
        payee,
        [(category, CashAmount(2, currency))],
        [(tag_1, CashAmount(2, currency)), (tag_2, CashAmount(1, currency))],
    )

    t2 = RefundTransaction(
        "refund",
        now,
        cash_account,
        t1,
        payee,
        [(category, CashAmount(1, currency))],
        [(tag_1, CashAmount(1, currency)), (tag_2, currency.zero_amount)],
    )

    tag_stats = calculate_attribute_stats(
        [t1, t2],
        currency,
        [tag_1, tag_2],
    )
    assert tag_stats[tag_1].no_of_transactions == 2
    assert tag_stats[tag_1].balance == CashAmount(-1, currency)
    assert tag_stats[tag_1].transactions == {t1, t2}
    assert tag_stats[tag_1].attribute == tag_1
    assert tag_stats[tag_2].no_of_transactions == 1
    assert tag_stats[tag_2].balance == CashAmount(-1, currency)
    assert tag_stats[tag_2].transactions == {t1}
    assert tag_stats[tag_2].attribute == tag_2

    payee_stats = calculate_attribute_stats([t1, t2], currency, [payee])
    assert payee_stats[payee].no_of_transactions == 2
    assert payee_stats[payee].balance == CashAmount(-1, currency)
    assert payee_stats[payee].transactions == {t1, t2}
    assert payee_stats[payee].attribute == payee
