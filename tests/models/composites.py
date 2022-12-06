import string
from collections.abc import Callable
from typing import Any

from hypothesis import strategies as st

from src.models.accounts.account_group import AccountGroup
from src.models.accounts.cash_account import CashAccount
from src.models.currencies.currency import Currency
from src.models.transactions.attributes.attribute import Attribute
from src.models.transactions.attributes.category import Category
from src.models.transactions.attributes.enums import CategoryType
from src.models.transactions.cash_transaction import CashTransaction
from src.models.transactions.cash_transfer import CashTransfer
from src.models.transactions.enums import CashTransactionType
from src.models.transactions.transaction import Transaction


@st.composite
def account_groups(draw: Callable[[st.SearchStrategy[str]], str]) -> AccountGroup:
    name = draw(st.text(min_size=1, max_size=32))
    return AccountGroup(name)


@st.composite
def attributes(draw: Callable[[st.SearchStrategy[str]], str]) -> Attribute:
    name = draw(st.text(alphabet=string.ascii_letters, min_size=1, max_size=32))
    return Attribute(name)


@st.composite
def cash_accounts(draw: Callable[[st.SearchStrategy[Any]], Any]) -> CashAccount:
    name = draw(st.text(alphabet=string.ascii_letters, min_size=3, max_size=3))
    currency = draw(currencies())
    initial_balance = draw(
        st.decimals(min_value=0, allow_infinity=False, allow_nan=False)
    )
    return CashAccount(name, currency, initial_balance)


@st.composite
def cash_transactions(draw: Callable[[st.SearchStrategy[Any]], Any]) -> CashTransaction:
    description = draw(st.text(min_size=0, max_size=256))
    datetime_ = draw(st.datetimes())
    type_ = draw(st.sampled_from(CashTransactionType))
    account = draw(cash_accounts())
    amount = draw(st.decimals(min_value=0.01, allow_infinity=False, allow_nan=False))
    payee = draw(attributes())
    category = draw(categories())
    tags = draw(st.lists(attributes()))
    return CashTransaction(
        description, datetime_, type_, account, amount, payee, category, tags
    )


@st.composite
def cash_transfers(draw: Callable[[st.SearchStrategy[Any]], Any]) -> CashTransfer:
    description = draw(st.text(min_size=0, max_size=256))
    datetime_ = draw(st.datetimes())
    account_sender = draw(cash_accounts())
    account_recipient = draw(cash_accounts())
    amount_sent = draw(
        st.decimals(min_value=0.01, allow_infinity=False, allow_nan=False)
    )
    amount_received = draw(
        st.decimals(min_value=0.01, allow_infinity=False, allow_nan=False)
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
def categories(draw: Callable[[st.SearchStrategy[Any]], Any]) -> Category:
    name = draw(st.text(min_size=1, max_size=32))
    category_type = draw(st.sampled_from(CategoryType))
    return Category(name, category_type)


@st.composite
def currencies(draw: Callable[[st.SearchStrategy[str]], str]) -> Currency:
    name = draw(st.text(alphabet=string.ascii_letters, min_size=3, max_size=3))
    return Currency(name)


@st.composite
def transactions(draw: Callable[[Any], Any]) -> Transaction:
    description = draw(st.text(min_size=0, max_size=256))
    datetime_ = draw(st.datetimes())
    return Transaction(description, datetime_)
