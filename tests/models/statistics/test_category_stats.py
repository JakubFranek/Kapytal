from datetime import datetime, timedelta

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
from src.models.statistics.category_stats import (
    calculate_category_stats,
    calculate_periodic_category_stats,
    calculate_periodic_totals_and_averages,
)
from src.models.user_settings import user_settings


def test_calculate_attribute_stats() -> None:
    currency = Currency("USD", 2)
    cash_account = CashAccount("Test CashAccount", currency, currency.zero_amount)

    payee = Attribute("payee1", AttributeType.PAYEE)

    category_1 = Category("Category1", CategoryType.DUAL_PURPOSE)
    category_2 = Category("Category2", CategoryType.DUAL_PURPOSE)
    category_2a = Category("Category2a", CategoryType.DUAL_PURPOSE, category_2)

    now = datetime.now(user_settings.settings.time_zone)

    t1 = CashTransaction(
        "test",
        now,
        CashTransactionType.INCOME,
        cash_account,
        payee,
        [(category_1, CashAmount(1, currency))],
        [],
    )

    t2 = CashTransaction(
        "test",
        now,
        CashTransactionType.EXPENSE,
        cash_account,
        payee,
        [(category_2, CashAmount(2, currency))],
        [],
    )

    t3 = CashTransaction(
        "test",
        now,
        CashTransactionType.EXPENSE,
        cash_account,
        payee,
        [(category_1, CashAmount(2, currency))],
        [],
    )

    t4 = CashTransaction(
        "test",
        now,
        CashTransactionType.EXPENSE,
        cash_account,
        payee,
        [(category_2a, CashAmount(3, currency))],
        [],
    )

    category_stats = calculate_category_stats(
        [t1, t2, t3, t4], currency, [category_1, category_2, category_2a]
    )
    assert category_stats[category_1].transactions_total == 2
    assert category_stats[category_2].transactions_total == 2
    assert category_stats[category_2a].transactions_total == 1
    assert category_stats[category_1].transactions_self == 2
    assert category_stats[category_2].transactions_self == 1
    assert category_stats[category_2a].transactions_self == 1
    assert category_stats[category_1].balance == CashAmount(-1, currency)
    assert category_stats[category_2].balance == CashAmount(-5, currency)
    assert category_stats[category_2a].balance == CashAmount(-3, currency)
    assert category_stats[category_1].transactions == {t1, t3}
    assert category_stats[category_2].transactions == {t2, t4}
    assert category_stats[category_2a].transactions == {t4}
    assert category_stats[category_1].category == category_1
    assert category_stats[category_2].category == category_2
    assert category_stats[category_2a].category == category_2a


def test_calculate_periodic_category_stats() -> None:
    currency = Currency("USD", 2)
    cash_account = CashAccount("Test CashAccount", currency, currency.zero_amount)

    payee = Attribute("payee1", AttributeType.PAYEE)

    category = Category("Category", CategoryType.DUAL_PURPOSE)

    now = datetime.now(user_settings.settings.time_zone)
    y1 = (now - relativedelta(years=2)).strftime("%Y")
    y2 = (now - relativedelta(years=1)).strftime("%Y")
    y3 = (now - relativedelta(years=0)).strftime("%Y")

    t1 = CashTransaction(
        "test",
        now - relativedelta(years=2),
        CashTransactionType.INCOME,
        cash_account,
        payee,
        [(category, CashAmount(1, currency))],
        [],
    )

    t2 = CashTransaction(
        "test",
        now - relativedelta(years=1),
        CashTransactionType.INCOME,
        cash_account,
        payee,
        [(category, CashAmount(2, currency))],
        [],
    )

    t3 = CashTransaction(
        "test",
        now,
        CashTransactionType.INCOME,
        cash_account,
        payee,
        [(category, CashAmount(3, currency))],
        [],
    )

    periodic_stats = calculate_periodic_category_stats(
        [t1, t2, t3], currency, [category], period_format="%Y"
    )
    assert len(periodic_stats[y1]) == 1
    assert periodic_stats[y1][0].category == category
    assert periodic_stats[y1][0].transactions_total == 1
    assert periodic_stats[y1][0].transactions_self == 1
    assert periodic_stats[y1][0].transactions == {t1}
    assert periodic_stats[y1][0].balance == CashAmount(1, currency)

    assert len(periodic_stats[y2]) == 1
    assert periodic_stats[y2][0].category == category
    assert periodic_stats[y2][0].transactions_total == 1
    assert periodic_stats[y2][0].transactions_self == 1
    assert periodic_stats[y2][0].transactions == {t2}
    assert periodic_stats[y2][0].balance == CashAmount(2, currency)

    assert len(periodic_stats[y3]) == 1
    assert periodic_stats[y3][0].category == category
    assert periodic_stats[y3][0].transactions_total == 1
    assert periodic_stats[y3][0].transactions_self == 1
    assert periodic_stats[y3][0].transactions == {t3}
    assert periodic_stats[y3][0].balance == CashAmount(3, currency)


def test_calculate_periodic_totals_and_averages() -> None:
    currency = Currency("USD", 2)
    cash_account = CashAccount("Test CashAccount", currency, currency.zero_amount)

    payee = Attribute("payee1", AttributeType.PAYEE)

    category = Category("Category", CategoryType.DUAL_PURPOSE)

    now = datetime.now(user_settings.settings.time_zone)
    y1 = (now - relativedelta(years=2)).strftime("%B %Y")
    y2 = (now - relativedelta(years=1)).strftime("%B %Y")
    y3 = (now - relativedelta(years=0)).strftime("%B %Y")

    t1a = CashTransaction(
        "test",
        now - relativedelta(years=2),
        CashTransactionType.INCOME,
        cash_account,
        payee,
        [(category, CashAmount(1, currency))],
        [],
    )
    t1b = CashTransaction(
        "test",
        now - relativedelta(years=2),
        CashTransactionType.EXPENSE,
        cash_account,
        payee,
        [(category, CashAmount(3, currency))],
        [],
    )

    t2 = CashTransaction(
        "test",
        now - relativedelta(years=1),
        CashTransactionType.INCOME,
        cash_account,
        payee,
        [(category, CashAmount(2, currency))],
        [],
    )

    t3 = CashTransaction(
        "test",
        now,
        CashTransactionType.INCOME,
        cash_account,
        payee,
        [(category, CashAmount(3, currency))],
        [],
    )

    periodic_stats = calculate_periodic_category_stats(
        [t1a, t1b, t2, t3], currency, [category]
    )
    (
        period_totals,
        period_income_totals,
        period_expense_totals,
        category_averages,
        category_totals,
    ) = calculate_periodic_totals_and_averages(periodic_stats, currency)

    assert len(period_totals[y1]) == 2
    assert period_totals[y1].transactions == {t1a, t1b}
    assert period_totals[y1].balance == CashAmount(-2, currency)

    assert len(period_totals[y2]) == 1
    assert period_totals[y2].transactions == {t2}
    assert period_totals[y2].balance == CashAmount(2, currency)

    assert len(period_totals[y3]) == 1
    assert period_totals[y3].transactions == {t3}
    assert period_totals[y3].balance == CashAmount(3, currency)

    assert len(period_income_totals[y1]) == 1
    assert period_income_totals[y1].transactions == {t1a}
    assert period_income_totals[y1].balance == CashAmount(1, currency)

    assert len(period_expense_totals[y1]) == 1
    assert period_expense_totals[y1].transactions == {t1b}
    assert period_expense_totals[y1].balance == CashAmount(-3, currency)

    assert len(period_expense_totals[y2]) == 0

    assert len(period_income_totals[y2]) == 1
    assert period_income_totals[y2].transactions == {t2}
    assert period_income_totals[y2].balance == CashAmount(2, currency)

    assert len(period_expense_totals[y3]) == 0

    assert len(period_income_totals[y3]) == 1
    assert period_income_totals[y3].transactions == {t3}
    assert period_income_totals[y3].balance == CashAmount(3, currency)

    assert len(category_averages) == 1
    assert category_averages[category].transactions == {t1a, t1b, t2, t3}
    assert category_averages[category].balance == CashAmount(1, currency)

    assert len(category_totals) == 1
    assert category_totals[category].transactions == {t1a, t1b, t2, t3}
    assert category_totals[category].balance == CashAmount(3, currency)


def test_calculate_attribute_stats_no_base_currency() -> None:
    category_1 = Category("Category1", CategoryType.DUAL_PURPOSE)
    category_2 = Category("Category2", CategoryType.DUAL_PURPOSE)
    category_2a = Category("Category2a", CategoryType.DUAL_PURPOSE, category_2)

    category_stats = calculate_category_stats(
        [], None, [category_1, category_2, category_2a]
    )
    assert category_stats[category_1].transactions_total == 0
    assert category_stats[category_2].transactions_total == 0
    assert category_stats[category_2a].transactions_total == 0
    assert category_stats[category_1].transactions_self == 0
    assert category_stats[category_2].transactions_self == 0
    assert category_stats[category_2a].transactions_self == 0
    assert category_stats[category_1].balance is None
    assert category_stats[category_2].balance is None
    assert category_stats[category_2a].balance is None
    assert category_stats[category_1].transactions == set()
    assert category_stats[category_2].transactions == set()
    assert category_stats[category_2a].transactions == set()
    assert category_stats[category_1].category == category_1
    assert category_stats[category_2].category == category_2
    assert category_stats[category_2a].category == category_2a


def test_calculate_attribute_stats_with_refund() -> None:
    currency = Currency("USD", 2)
    cash_account = CashAccount("Test CashAccount", currency, currency.zero_amount)

    payee = Attribute("payee1", AttributeType.PAYEE)

    category_1 = Category("Category1", CategoryType.DUAL_PURPOSE)
    category_2 = Category("Category2", CategoryType.DUAL_PURPOSE)

    now = datetime.now(user_settings.settings.time_zone)

    t1 = CashTransaction(
        "test",
        now - timedelta(days=1),
        CashTransactionType.EXPENSE,
        cash_account,
        payee,
        [(category_1, CashAmount(2, currency)), (category_2, CashAmount(1, currency))],
        [],
    )
    t2 = RefundTransaction(
        "refund",
        now,
        cash_account,
        t1,
        payee,
        [(category_1, CashAmount(1, currency)), (category_2, currency.zero_amount)],
        [],
    )

    category_stats = calculate_category_stats(
        [t1, t2], currency, [category_1, category_2]
    )
    assert category_stats[category_1].transactions_total == 2
    assert category_stats[category_2].transactions_total == 1
    assert category_stats[category_1].transactions_self == 2
    assert category_stats[category_2].transactions_self == 1
    assert category_stats[category_1].balance == CashAmount(-1, currency)
    assert category_stats[category_2].balance == CashAmount(-1, currency)
    assert category_stats[category_1].transactions == {t1, t2}
    assert category_stats[category_2].transactions == {t1}
    assert category_stats[category_1].category == category_1
    assert category_stats[category_2].category == category_2
