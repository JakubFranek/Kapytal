import string
from collections.abc import Callable
from datetime import datetime
from decimal import Decimal
from typing import Any

from hypothesis import given
from hypothesis import strategies as st

from src.models.accounts.cash_account import CashAccount
from src.models.currency import Currency
from src.models.transactions.attributes.attribute import Attribute
from src.models.transactions.attributes.category import Category
from src.models.transactions.attributes.enums import CategoryType
from src.models.transactions.cash_transaction import CashTransaction
from src.models.transactions.enums import CashTransactionType


@st.composite
def currencies(draw: Callable[[st.SearchStrategy[str]], str]) -> Currency:
    name = draw(st.text(alphabet=string.ascii_letters, min_size=3, max_size=3))
    return Currency(name)


@st.composite
def cash_accounts(draw: Callable[[st.SearchStrategy[Any]], Any]) -> CashAccount:
    name = draw(st.text(alphabet=string.ascii_letters, min_size=3, max_size=3))
    currency = draw(currencies())
    initial_balance = draw(
        st.decimals(min_value=0, allow_infinity=False, allow_nan=False)
    )
    return CashAccount(name, currency, initial_balance)


@st.composite
def attributes(draw: Callable[[st.SearchStrategy[str]], str]) -> Attribute:
    name = draw(st.text(alphabet=string.ascii_letters, min_size=1, max_size=32))
    return Attribute(name)


@st.composite
def categories(
    draw: Callable[[st.SearchStrategy[str | CategoryType]], str | CategoryType]
) -> Category:
    name = draw(st.text(min_size=1, max_size=32))
    category_type = draw(st.sampled_from(CategoryType))
    return Category(name, category_type)


@given(
    description=st.text(min_size=0, max_size=256),
    datetime_=st.datetimes(),
    type_=st.sampled_from(CashTransactionType),
    account=cash_accounts(),
    amount=st.decimals(min_value=0.01, allow_infinity=False, allow_nan=False),
    payee=attributes(),
    category=categories(),
    tags=st.lists(attributes()),
)
def test_creation_pass(  # noqa: CFQ002,TMN001
    description: str,
    datetime_: datetime,
    type_: CashTransactionType,
    account: CashAccount,
    amount: Decimal,
    payee: Attribute,
    category: Category,
    tags: list[Attribute],
) -> None:
    currency = account.currency
    cash_transaction = CashTransaction(
        description, datetime_, type_, account, amount, currency, payee, category, tags
    )
    assert cash_transaction.description == description
    assert cash_transaction.datetime_ == datetime_
    assert cash_transaction.account == account
    assert cash_transaction.amount == amount
    assert cash_transaction.currency == currency
    assert cash_transaction.category == category
    assert cash_transaction.payee == payee
    assert cash_transaction.tags == tuple(tags)
