from datetime import datetime, timedelta

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
from src.models.user_settings import user_settings
from src.models.utilities.calculation import (
    calculate_category_stats,
    calculate_payee_stats,
    calculate_tag_stats,
)

payee = Attribute("Payee 1", AttributeType.PAYEE)
payee_dummy = Attribute("Dummy", AttributeType.PAYEE)
category_expense = Category("Cat Expense", CategoryType.EXPENSE)
category_expense_child = Category(
    "Expense child", CategoryType.EXPENSE, category_expense
)
category_income = Category("Cat Income", CategoryType.INCOME)
tag = Attribute("Tag 1", AttributeType.TAG)
tag_dummy = Attribute("Dummy", AttributeType.TAG)
currency = Currency("CZK", 2)
account = CashAccount("Account", currency, currency.zero_amount)


def test_calculate_attribute_stats() -> None:
    transactions = get_transactions()
    payee_stats = calculate_payee_stats(
        transactions,
        currency,
    )
    tag_stats = calculate_tag_stats(
        transactions,
        currency,
    )
    payee_stats = payee_stats[payee]
    tag_stats = tag_stats[tag]
    assert payee_stats.attribute == payee
    assert payee_stats.no_of_transactions == 7  # noqa: PLR2004
    assert payee_stats.balance.value_rounded == -1 - 2 + 3 + 5 + 6 + 7 + 1
    assert tag_stats.attribute == tag
    assert tag_stats.no_of_transactions == 7  # noqa: PLR2004
    assert tag_stats.balance.value_rounded == -1 - 2 + 3 - 4 + 6 + 7 + 1


def test_calculate_category_stats() -> None:
    transactions = get_transactions()
    category_stats_dict = calculate_category_stats(
        transactions,
        currency,
        [category_income, category_expense, category_expense_child],
    )
    category_stats = category_stats_dict[category_expense]
    category_child_stats = category_stats_dict[category_expense_child]

    assert category_stats.category == category_expense
    assert category_stats.transactions_self == 3  # noqa: PLR2004
    assert category_stats.transactions_total == 4  # noqa: PLR2004
    assert category_stats.balance.value_rounded == -1 - 2 - 4 - 4 + 1

    assert category_child_stats.category == category_expense_child
    assert category_child_stats.transactions_self == 2  # noqa: PLR2004
    assert category_child_stats.transactions_total == 2  # noqa: PLR2004
    assert category_child_stats.balance.value_rounded == -2 - 4


def get_transactions() -> list[CashTransaction]:
    transactions = []
    transactions.append(
        CashTransaction(
            description="",
            datetime_=datetime.now(user_settings.settings.time_zone),
            type_=CashTransactionType.EXPENSE,
            account=account,
            payee=payee,
            category_amount_pairs=[(category_expense, CashAmount(1, currency))],
            tag_amount_pairs=[(tag, CashAmount(1, currency))],
        )
    )
    transactions.append(
        CashTransaction(
            description="",
            datetime_=datetime.now(user_settings.settings.time_zone),
            type_=CashTransactionType.EXPENSE,
            account=account,
            payee=payee,
            category_amount_pairs=[(category_expense_child, CashAmount(2, currency))],
            tag_amount_pairs=[(tag, CashAmount(2, currency))],
        )
    )
    transactions.append(
        CashTransaction(
            description="",
            datetime_=datetime.now(user_settings.settings.time_zone),
            type_=CashTransactionType.INCOME,
            account=account,
            payee=payee,
            category_amount_pairs=[(category_income, CashAmount(3, currency))],
            tag_amount_pairs=[(tag, CashAmount(3, currency))],
        )
    )
    transactions.append(
        CashTransaction(
            description="",
            datetime_=datetime.now(user_settings.settings.time_zone),
            type_=CashTransactionType.EXPENSE,
            account=account,
            payee=payee_dummy,
            category_amount_pairs=[
                (category_expense, CashAmount(4, currency)),
                (category_expense_child, CashAmount(4, currency)),
            ],
            tag_amount_pairs=[(tag, CashAmount(4, currency))],
        )
    )
    transactions.append(
        CashTransaction(
            description="",
            datetime_=datetime.now(user_settings.settings.time_zone),
            type_=CashTransactionType.INCOME,
            account=account,
            payee=payee,
            category_amount_pairs=[(category_income, CashAmount(5, currency))],
            tag_amount_pairs=[(tag_dummy, CashAmount(5, currency))],
        )
    )
    transactions.append(
        CashTransaction(
            description="",
            datetime_=datetime.now(user_settings.settings.time_zone)
            - timedelta(days=365),
            type_=CashTransactionType.INCOME,
            account=account,
            payee=payee,
            category_amount_pairs=[(category_income, CashAmount(6, currency))],
            tag_amount_pairs=[(tag, CashAmount(6, currency))],
        )
    )
    transactions.append(
        CashTransaction(
            description="",
            datetime_=datetime.now(user_settings.settings.time_zone)
            + timedelta(days=365),
            type_=CashTransactionType.INCOME,
            account=account,
            payee=payee,
            category_amount_pairs=[(category_income, CashAmount(7, currency))],
            tag_amount_pairs=[(tag, CashAmount(7, currency))],
        )
    )
    transactions.append(
        RefundTransaction(
            description="",
            datetime_=datetime.now(user_settings.settings.time_zone),
            account=account,
            refunded_transaction=transactions[0],
            payee=payee,
            category_amount_pairs=[(category_expense, CashAmount(1, currency))],
            tag_amount_pairs=[(tag, CashAmount(1, currency))],
        )
    )
    return transactions
