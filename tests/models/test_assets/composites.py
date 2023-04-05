import numbers
import string
from datetime import datetime
from decimal import Decimal
from typing import Any

from hypothesis import assume
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
from src.models.model_objects.currency_objects import CashAmount, Currency
from src.models.model_objects.security_objects import (
    Security,
    SecurityAccount,
    SecurityTransaction,
    SecurityTransactionType,
    SecurityTransfer,
)
from src.models.user_settings import user_settings
from tests.models.test_assets.concrete_abcs import ConcreteTransaction
from tests.models.test_assets.constants import MIN_DATETIME

# IDEA: check if optional params for some composites can help optimize tests


def everything_except(excluded_types: type | tuple[type, ...]) -> Any:
    return (
        st.from_type(type)
        .flatmap(st.from_type)
        .filter(lambda x: not isinstance(x, excluded_types))
    )


@st.composite
def valid_decimals(
    draw: st.DrawFn,
    min_value: numbers.Real | str | None = None,
    max_value: numbers.Real | str | None = None,
    places: int | None = None,
) -> Decimal:
    if min_value is None:
        min_value = -1e12
    if max_value is None:
        max_value = 1e12
    if places is None:
        places = 10
    return draw(
        st.decimals(
            min_value, max_value, places=places, allow_infinity=False, allow_nan=False
        )
    )


@st.composite
def decimal_powers_of_10(draw: st.DrawFn) -> Decimal:
    exponent = draw(st.integers(min_value=-10, max_value=10))
    return Decimal("10") ** exponent


@st.composite
def account_groups(draw: st.DrawFn) -> AccountGroup:
    name = draw(names())
    return AccountGroup(name)


@st.composite
def attributes(draw: st.DrawFn, type_: AttributeType | None = None) -> Attribute:
    name = draw(names())
    attr_type = draw(st.sampled_from(AttributeType)) if type_ is None else type_
    return Attribute(name, attr_type)


@st.composite
def cash_amounts(
    draw: st.DrawFn,
    currency: Currency | None = None,
    min_value: numbers.Real | str | None = -1e10,
    max_value: numbers.Real | str | None = 1e10,
) -> CashAmount:
    if currency is None:
        currency = draw(currencies())
    value = draw(
        valid_decimals(min_value=min_value, max_value=max_value, places=currency.places)
    )
    return CashAmount(value, currency)


@st.composite
def cash_accounts(
    draw: st.DrawFn,
    currency: Currency | None = None,
) -> CashAccount:
    name = draw(names())
    if currency is None:
        currency = draw(currencies())
    initial_amount = draw(cash_amounts(currency=currency))
    return CashAccount(name, currency, initial_amount)


@st.composite
def cash_transactions(  # noqa: PLR0913
    draw: st.DrawFn,
    currency: Currency | None = None,
    min_datetime: datetime = MIN_DATETIME,
    max_datetime: datetime = datetime.max,
    account: CashAccount = None,
    type_: CashTransactionType | None = None,
) -> CashTransaction:
    description = draw(st.text(min_size=0, max_size=256))
    if type_ is None:
        type_ = draw(st.sampled_from(CashTransactionType))
    if account is None:
        account = draw(cash_accounts(currency=currency))
    currency = account.currency
    datetime_ = draw(
        st.datetimes(
            min_value=min_datetime,
            max_value=max_datetime,
            timezones=st.just(user_settings.settings.time_zone),
        )
    )
    category_amount_pairs_list: list[tuple[Category, CashAmount]] = draw(
        st.lists(
            category_amount_pairs(
                transaction_type=type_,
                currency=currency,
            ),
            min_size=1,
            max_size=5,
        )
    )
    max_tag_amount = sum(
        (amount for _, amount in category_amount_pairs_list),
        start=CashAmount(0, currency),
    )
    payee = draw(attributes(AttributeType.PAYEE))
    tag_amount_pairs_list = draw(
        st.lists(
            tag_amount_pairs(
                currency=currency,
                max_value=max_tag_amount.value_rounded,
            ),
            min_size=0,
            max_size=5,
        )
    )
    return CashTransaction(
        description,
        datetime_,
        type_,
        account,
        payee,
        category_amount_pairs_list,
        tag_amount_pairs_list,
    )


@st.composite
def cash_transfers(
    draw: st.DrawFn,
    min_datetime: datetime = MIN_DATETIME,
    max_datetime: datetime = datetime.max,
    currency_sender: Currency | None = None,
    currency_recipient: Currency | None = None,
) -> CashTransfer:
    description = draw(st.text(min_size=0, max_size=256))
    account_sender: CashAccount = draw(cash_accounts(currency=currency_sender))
    account_recipient: CashAccount = draw(cash_accounts(currency=currency_recipient))
    assume(account_sender.path != account_recipient.path)
    datetime_ = draw(
        st.datetimes(
            min_value=min_datetime,
            max_value=max_datetime,
            timezones=st.just(user_settings.settings.time_zone),
        )
    )
    amount_sent = draw(cash_amounts(account_sender.currency, min_value="0.01"))
    amount_received = draw(cash_amounts(account_recipient.currency, min_value="0.01"))
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
    draw: st.DrawFn,
    transaction_type: CashTransactionType | None = None,
    category_type: CategoryType | None = None,
) -> Category:
    name = draw(names())

    if transaction_type is None:
        if category_type is None:
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
    draw: st.DrawFn,
    transaction_type: CashTransactionType,
    currency: Currency,
    min_value: numbers.Real | str | None = "0.01",
    max_value: numbers.Real | str | None = 1e10,
) -> tuple[Category, CashAmount]:
    category = draw(categories(transaction_type))
    amount = draw(
        cash_amounts(currency=currency, min_value=min_value, max_value=max_value)
    )
    return (category, amount)


@st.composite
def currencies(draw: st.DrawFn, min_places: int = 2, max_places: int = 8) -> Currency:
    code = draw(st.text(alphabet=string.ascii_letters, min_size=3, max_size=3))
    places = draw(st.integers(min_value=min_places, max_value=max_places))
    return Currency(code, places)


@st.composite
def securities(draw: st.DrawFn, currency: Currency | None = None) -> Security:
    name = draw(names())
    symbol = draw(
        st.text(alphabet=Security.SYMBOL_ALLOWED_CHARS, min_size=1, max_size=8)
    )
    type_ = draw(names(min_size=1, max_size=32))
    if currency is None:
        currency = draw(currencies())
    shares_unit = draw(decimal_powers_of_10())
    return Security(
        name,
        symbol,
        type_,
        currency,
        shares_unit,
    )


@st.composite
def security_accounts(draw: st.DrawFn) -> SecurityAccount:
    name = draw(names())
    parent = draw(st.none() | account_groups())
    return SecurityAccount(name, parent)


@st.composite
def security_transactions(
    draw: st.DrawFn,
    min_datetime: datetime = MIN_DATETIME,
    max_datetime: datetime = datetime.max,
) -> SecurityTransaction:
    cash_account = draw(cash_accounts())
    security_account = draw(security_accounts())
    assume(cash_account.path != security_account.path)

    price_per_share = draw(
        cash_amounts(currency=cash_account.currency, min_value=0, max_value=1e10)
    )
    security = draw(securities(currency=cash_account.currency))

    description = draw(st.text(min_size=1, max_size=256))
    datetime_ = draw(
        st.datetimes(
            min_value=min_datetime,
            max_value=max_datetime,
            timezones=st.just(user_settings.settings.time_zone),
        )
    )
    type_ = draw(st.sampled_from(SecurityTransactionType))

    if price_per_share.value_normalized != 0:
        max_shares = Decimal("1e9") // price_per_share.value_normalized
    else:
        max_shares = Decimal("1e9")
    if max_shares == 0:
        max_shares = 1
    shares = draw(
        share_decimals(shares_unit=security.shares_unit, max_value=max_shares)
    )

    return SecurityTransaction(
        description,
        datetime_,
        type_,
        security,
        shares,
        price_per_share,
        security_account,
        cash_account,
    )


@st.composite
def security_transfers(draw: st.DrawFn) -> SecurityTransfer:
    account_sender = draw(security_accounts())
    account_recipient = draw(security_accounts())
    assume(account_sender.path != account_recipient.path)

    description = draw(st.text(min_size=1, max_size=256))
    datetime_ = draw(st.datetimes(timezones=st.just(user_settings.settings.time_zone)))
    security = draw(securities())
    shares = draw(share_decimals(security.shares_unit))

    return SecurityTransfer(
        description, datetime_, security, shares, account_sender, account_recipient
    )


@st.composite
def share_decimals(
    draw: st.DrawFn, shares_unit: Decimal, max_value: int = 1e6
) -> Decimal:
    integer = draw(st.integers(min_value=1, max_value=max_value))
    return shares_unit * integer


@st.composite
def tag_amount_pairs(
    draw: st.DrawFn,
    currency: Currency,
    min_value: numbers.Real | str | None = "0.01",
    max_value: numbers.Real | str | None = None,
) -> tuple[Attribute, CashAmount]:
    attribute = draw(attributes(type_=AttributeType.TAG))
    if max_value is None:
        max_value = "1e10"
    amount = draw(
        cash_amounts(currency=currency, min_value=min_value, max_value=max_value)
    )
    return (attribute, amount)


@st.composite
def transactions(draw: st.DrawFn) -> ConcreteTransaction:
    description = draw(st.text(min_size=0, max_size=256))
    datetime_ = draw(st.datetimes(timezones=st.just(user_settings.settings.time_zone)))
    return ConcreteTransaction(description, datetime_)


@st.composite
def names(
    draw: st.DrawFn, min_size: int | None = None, max_size: int | None = None
) -> str:
    if min_size is None:
        min_size = 1
        if max_size is None:
            max_size = 32
    return draw(
        st.text(
            alphabet=st.characters(blacklist_characters=("/")),
            min_size=min_size,
            max_size=max_size,
        )
    )
