import string
from datetime import datetime
from decimal import Decimal
from typing import Any, Literal

from hypothesis import strategies as st

from src.models.constants import tzinfo
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
from src.models.model_objects.security_objects import (
    Security,
    SecurityAccount,
    SecurityType,
)
from tests.models.test_assets.concrete_abcs import ConcreteTransaction
from tests.models.test_assets.constants import max_datetime, min_datetime


def everything_except(excluded_types: type | tuple[type, ...]) -> Any:
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
        st.datetimes(
            min_value=min_datetime,
            max_value=max_datetime,
            timezones=st.just(tzinfo),
        )
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
    datetime_ = draw(
        st.datetimes(
            min_value=min_datetime, max_value=max_datetime, timezones=st.just(tzinfo)
        )
    )
    category_amount_pairs_list = draw(
        st.lists(category_amount_pairs(type_), min_size=1, max_size=5)
    )
    max_tag_amount = Decimal(sum(amount for _, amount in category_amount_pairs_list))
    payee = draw(attributes(AttributeType.PAYEE))
    tag_amount_pairs_list = draw(
        st.lists(tag_amount_pairs(max_tag_amount), min_size=0, max_size=5)
    )
    return CashTransaction(
        description,
        datetime_,
        type_,
        account,
        category_amount_pairs_list,
        payee,
        tag_amount_pairs_list,
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
    datetime_ = draw(
        st.datetimes(
            min_value=min_datetime, max_value=max_datetime, timezones=st.just(tzinfo)
        )
    )
    amount_sent = draw(
        st.decimals(
            min_value="0.01",
            max_value=1e10,
            allow_infinity=False,
            allow_nan=False,
            places=3,
        )
    )
    amount_received = draw(
        st.decimals(
            min_value="0.01",
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
    draw: st.DrawFn, transaction_type: CashTransactionType | None = None
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
) -> tuple[Category, Decimal]:
    category = draw(categories(transaction_type))
    amount = draw(
        st.decimals(
            min_value="0.01",
            max_value=1e10,
            allow_infinity=False,
            allow_nan=False,
            places=3,
        )
    )
    return (category, amount)


@st.composite
def currencies(draw: st.DrawFn) -> Currency:
    name = draw(st.text(alphabet=string.ascii_letters, min_size=3, max_size=3))
    return Currency(name)


@st.composite
def securities(draw: st.DrawFn) -> Security:
    name = draw(st.text(min_size=1, max_size=32))
    symbol = draw(
        st.text(alphabet=Security.SYMBOL_ALLOWED_CHARS, min_size=1, max_size=8)
    )
    type_ = draw(st.sampled_from(SecurityType))
    return Security(name, symbol, type_)


@st.composite
def security_accounts(draw: st.DrawFn) -> SecurityAccount:
    name = draw(st.text(min_size=1, max_size=32))
    parent = draw(st.none() | account_groups())
    return SecurityAccount(name, parent)


@st.composite
def tag_amount_pairs(
    draw: st.DrawFn, max_value: Decimal | Literal[0] | None = None
) -> tuple[Attribute, Decimal]:
    attribute = draw(attributes(type_=AttributeType.TAG))
    if max_value is None:
        max_value = Decimal("1e10")
    amount = draw(
        st.decimals(
            min_value="0.01",
            max_value=max_value,
            allow_infinity=False,
            allow_nan=False,
            places=3,
        )
    )
    return (attribute, amount)


@st.composite
def transactions(draw: st.DrawFn) -> ConcreteTransaction:
    description = draw(st.text(min_size=0, max_size=256))
    datetime_ = draw(st.datetimes(timezones=st.just(tzinfo)))
    return ConcreteTransaction(description, datetime_)
