import string
from datetime import datetime
from decimal import Decimal
from typing import Any

from hypothesis import strategies as st

from src.models.model_objects.account_group import AccountGroup
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
    CashTransfer,
)
from src.models.model_objects.currency import Currency
from tests.models.test_assets.concrete_abcs import ConcreteTransaction
from tests.models.test_assets.constants import max_datetime, min_datetime


def everything_except(excluded_types: tuple[type]) -> Any:
    return (
        st.from_type(type)
        .flatmap(st.from_type)
        .filter(lambda x: not isinstance(x, excluded_types))
    )


@st.composite
def account_groups(draw: st.DrawFn) -> AccountGroup:
    name = draw(st.text(min_size=1, max_size=32))
    return AccountGroup(name)


@st.composite
def attributes(draw: st.DrawFn, type_: AttributeType | None = None) -> Attribute:
    name = draw(st.text(min_size=1, max_size=32))
    if type_ is None:
        attr_type = draw(st.sampled_from(AttributeType))
    else:
        attr_type = type_
    return Attribute(name, attr_type)


@st.composite
def cash_accounts(
    draw: st.DrawFn,
    min_datetime: datetime = datetime.min,
    max_datetime: datetime = max_datetime,
) -> CashAccount:
    name = draw(st.text(min_size=1, max_size=32))
    currency = draw(currencies())
    initial_balance = draw(
        st.decimals(
            min_value=0, max_value=1e10, allow_infinity=False, allow_nan=False, places=3
        )
    )
    initial_datetime = draw(
        st.datetimes(min_value=min_datetime, max_value=max_datetime)
    )
    return CashAccount(name, currency, initial_balance, initial_datetime)


@st.composite
def cash_transactions(
    draw: st.DrawFn,
    min_datetime: datetime = min_datetime,
    max_datetime: datetime = datetime.max,
) -> CashTransaction:
    description = draw(st.text(min_size=0, max_size=256))
    type_ = draw(st.sampled_from(CashTransactionType))
    account: CashAccount = draw(cash_accounts())
    datetime_ = draw(st.datetimes(min_value=min_datetime, max_value=max_datetime))
    category_amount_pairs_list = draw(
        st.lists(category_amount_pairs(type_), min_size=1, max_size=5)
    )
    payee = draw(attributes(AttributeType.PAYEE))
    tags = draw(st.lists(attributes(AttributeType.TAG)))
    return CashTransaction(
        description, datetime_, type_, account, category_amount_pairs_list, payee, tags
    )


@st.composite
def cash_transfers(
    draw: st.DrawFn,
    min_datetime: datetime = min_datetime,
    max_datetime: datetime = datetime.max,
) -> CashTransfer:
    description = draw(st.text(min_size=0, max_size=256))
    account_sender: CashAccount = draw(cash_accounts())
    account_recipient: CashAccount = draw(cash_accounts())
    datetime_ = draw(st.datetimes(min_value=min_datetime, max_value=max_datetime))
    amount_sent = draw(
        st.decimals(
            min_value=0.01,
            max_value=1e10,
            allow_infinity=False,
            allow_nan=False,
            places=3,
        )
    )
    amount_received = draw(
        st.decimals(
            min_value=0.01,
            max_value=1e10,
            allow_infinity=False,
            allow_nan=False,
            places=3,
        )
    )
    return CashTransfer(
        description,
        datetime_,
        account_sender,
        account_recipient,
        amount_sent,
        amount_received,
    )


@st.composite
def categories(
    draw: st.DrawFn, transaction_type: CashTransactionType = None
) -> Category:
    name = draw(st.text(min_size=1, max_size=32))

    if transaction_type is None:
        category_type = draw(st.sampled_from(CategoryType))
    elif transaction_type == CashTransactionType.INCOME:
        category_type = draw(
            st.sampled_from((CategoryType.INCOME, CategoryType.INCOME_AND_EXPENSE))
        )
    else:
        category_type = draw(
            st.sampled_from((CategoryType.EXPENSE, CategoryType.INCOME_AND_EXPENSE))
        )

    return Category(name, category_type)


@st.composite
def category_amount_pairs(
    draw: st.DrawFn, transaction_type: CashTransactionType
) -> list[Category, Decimal]:
    category = draw(categories(transaction_type))
    amount = draw(
        st.decimals(
            min_value=0.01,
            max_value=1e10,
            allow_infinity=False,
            allow_nan=False,
            places=3,
        )
    )
    return [category, amount]


@st.composite
def currencies(draw: st.DrawFn) -> Currency:
    name = draw(st.text(alphabet=string.ascii_letters, min_size=3, max_size=3))
    return Currency(name)


@st.composite
def transactions(draw: st.DrawFn) -> ConcreteTransaction:
    description = draw(st.text(min_size=0, max_size=256))
    datetime_ = draw(st.datetimes())
    return ConcreteTransaction(description, datetime_)
