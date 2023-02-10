from datetime import datetime, timedelta

from src.models.constants import tzinfo
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
)
from src.models.model_objects.currency_objects import CashAmount, Currency
from src.models.utilities.calculation import get_attribute_stats

payee = Attribute("Payee 1", AttributeType.PAYEE)
payee_dummy = Attribute("Dummy", AttributeType.PAYEE)
category_expense = Category("Cat 1", CategoryType.EXPENSE)
category_income = Category("Cat 1", CategoryType.INCOME)
tag = Attribute("Tag 1", AttributeType.TAG)
tag_dummy = Attribute("Dummy", AttributeType.TAG)
currency = Currency("CZK", 2)
account = CashAccount("Account", currency, CashAmount(0, currency))


def test_calculate_attribute_stats() -> None:
    transactions = get_transactions()
    payee_stats = get_attribute_stats(
        payee,
        transactions,
        currency,
        date_start=datetime.now(tzinfo).date() - timedelta(days=1),
        date_end=datetime.now(tzinfo).date() + timedelta(days=1),
    )
    tag_stats = get_attribute_stats(
        tag,
        transactions,
        currency,
        date_start=datetime.now(tzinfo).date() - timedelta(days=1),
        date_end=datetime.now(tzinfo).date() + timedelta(days=1),
    )
    assert payee_stats.attribute == payee
    assert payee_stats.no_of_transactions == 4
    assert payee_stats.balance.value_rounded == -1 - 2 + 3 + 5
    assert tag_stats.attribute == tag
    assert tag_stats.no_of_transactions == 4
    assert tag_stats.balance.value_rounded == -1 - 2 + 3 + 4


def get_transactions() -> list[CashTransaction]:
    transactions = []
    transactions.append(
        CashTransaction(
            description="",
            datetime_=datetime.now(tzinfo),
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
            datetime_=datetime.now(tzinfo),
            type_=CashTransactionType.EXPENSE,
            account=account,
            payee=payee,
            category_amount_pairs=[(category_expense, CashAmount(2, currency))],
            tag_amount_pairs=[(tag, CashAmount(2, currency))],
        )
    )
    transactions.append(
        CashTransaction(
            description="",
            datetime_=datetime.now(tzinfo),
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
            datetime_=datetime.now(tzinfo),
            type_=CashTransactionType.INCOME,
            account=account,
            payee=payee_dummy,
            category_amount_pairs=[(category_income, CashAmount(4, currency))],
            tag_amount_pairs=[(tag, CashAmount(4, currency))],
        )
    )
    transactions.append(
        CashTransaction(
            description="",
            datetime_=datetime.now(tzinfo),
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
            datetime_=datetime.now(tzinfo) - timedelta(days=365),
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
            datetime_=datetime.now(tzinfo) + timedelta(days=365),
            type_=CashTransactionType.INCOME,
            account=account,
            payee=payee,
            category_amount_pairs=[(category_income, CashAmount(7, currency))],
            tag_amount_pairs=[(tag, CashAmount(7, currency))],
        )
    )
    return transactions
