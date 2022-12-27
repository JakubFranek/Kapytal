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
from src.models.model_objects.currency import CashAmount, Currency
from src.models.model_objects.security_objects import (
    Security,
    SecurityAccount,
    SecurityTransaction,
    SecurityTransactionType,
    SecurityTransfer,
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
def cash_amounts(draw: st.DrawFn) -> CashAmount:
    value = draw(
        st.decimals(min_value=0, max_value=1e10, allow_infinity=False, allow_nan=False)
    )
    currency = draw(currencies())
    return CashAmount(value, currency)


@st.composite
def cash_accounts(
    draw: st.DrawFn,
    min_datetime: datetime = datetime.min,
    max_datetime: datetime = max_datetime,
    currency: Currency | None = None,
) -> CashAccount:
    name = draw(st.text(min_size=1, max_size=32))
    if currency is None:
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
    places = draw(st.integers(min_value=0, max_value=8))
    return Currency(name, places)


@st.composite
def securities(draw: st.DrawFn, currency: Currency | None = None) -> Security:
    name = draw(st.text(min_size=1, max_size=32))
    symbol = draw(
        st.text(alphabet=Security.SYMBOL_ALLOWED_CHARS, min_size=1, max_size=8)
    )
    type_ = draw(st.sampled_from(SecurityType))
    if currency is None:
        currency = draw(currencies())
    return Security(name, symbol, type_, currency)


@st.composite
def security_accounts(draw: st.DrawFn) -> SecurityAccount:
    name = draw(st.text(min_size=1, max_size=32))
    parent = draw(st.none() | account_groups())
    return SecurityAccount(name, parent)


@st.composite
def security_transactions(
    draw: st.DrawFn,
    min_datetime: datetime = min_datetime,
    max_datetime: datetime = datetime.max,
) -> SecurityTransaction:
    description = draw(st.text(min_size=1, max_size=256))
    datetime_ = draw(
        st.datetimes(
            min_value=min_datetime, max_value=max_datetime, timezones=st.just(tzinfo)
        )
    )
    type_ = draw(st.sampled_from(SecurityTransactionType))

    shares = draw(st.integers(min_value=1))
    price_per_share = draw(
        st.decimals(
            min_value=0, max_value=1e10, allow_infinity=False, allow_nan=False, places=3
        )
    )
    fees = draw(
        st.decimals(
            min_value=0, max_value=1e10, allow_infinity=False, allow_nan=False, places=3
        )
    )
    security_account = draw(security_accounts())
    cash_account = draw(cash_accounts())
    security = draw(securities(currency=cash_account.currency))
    return SecurityTransaction(
        description,
        datetime_,
        type_,
        security,
        shares,
        price_per_share,
        fees,
        security_account,
        cash_account,
    )


@st.composite
def security_transfers(draw: st.DrawFn) -> SecurityTransfer:
    description = draw(st.text(min_size=1, max_size=256))
    datetime_ = draw(st.datetimes(timezones=st.just(tzinfo)))
    security = draw(securities())
    shares = draw(st.integers(min_value=1))
    account_sender = draw(security_accounts())
    account_recipient = draw(security_accounts())
    return SecurityTransfer(
        description, datetime_, security, shares, account_sender, account_recipient
    )


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
