import re
from datetime import timedelta
from typing import Any

from hypothesis import assume, given
from hypothesis import strategies as st
from src.models.base_classes.account import Account
from src.models.base_classes.transaction import Transaction
from src.models.model_objects.attributes import Attribute, AttributeType
from src.models.model_objects.cash_objects import (
    CashTransactionType,
    CashTransfer,
    RefundTransaction,
)
from src.models.model_objects.currency_objects import Currency
from src.models.model_objects.security_objects import (
    Security,
    SecurityTransactionType,
    SecurityTransfer,
)
from src.models.transaction_filters.base_transaction_filter import FilterMode
from src.models.transaction_filters.transaction_filter import TransactionFilter
from src.models.user_settings import user_settings
from tests.models.test_assets.composites import (
    attributes,
    cash_accounts,
    cash_amounts,
    currencies,
    everything_except,
    securities,
    security_accounts,
    transactions,
)
from tests.models.test_assets.transaction_list import transaction_list

valid_types = (
    CashTransactionType.INCOME,
    CashTransactionType.EXPENSE,
    RefundTransaction,
    CashTransfer,
    SecurityTransfer,
    SecurityTransactionType.BUY,
    SecurityTransactionType.SELL,
)


def test_creation() -> None:
    filter_ = TransactionFilter()
    assert filter_.__repr__() == "TransactionFilter"


def test_eq_hash() -> None:
    filter_1 = TransactionFilter()
    filter_2 = TransactionFilter()
    assert filter_1.__eq__(filter_2) is True
    assert filter_1.__hash__() == filter_2.__hash__()

    filter_1.set_description_filter("test pattern", FilterMode.KEEP)
    assert filter_1.__eq__(filter_2) is False
    assert filter_1.__hash__() != filter_2.__hash__()


@given(other=everything_except(TransactionFilter))
def test_eq_hash_different_type(other: Any) -> None:
    filter_ = TransactionFilter()
    assert filter_.__eq__(other) is False


@given(
    types=st.lists(st.sampled_from(valid_types), min_size=0, unique=True),
    mode=st.sampled_from(FilterMode),
)
def test_set_type_filter(
    types: list[type[Transaction] | CashTransactionType | SecurityTransactionType],
    mode: FilterMode,
) -> None:
    filter_ = TransactionFilter()
    filter_.set_type_filter(types, mode)
    assert filter_.type_filter.types == frozenset(types)
    assert filter_.type_filter.mode == mode


@given(
    data=st.data(),
    mode=st.sampled_from(FilterMode),
)
def test_set_datetime_filter(
    data: st.DataObject,
    mode: FilterMode,
) -> None:
    start = data.draw(st.datetimes(timezones=st.just(user_settings.settings.time_zone)))
    end = data.draw(
        st.datetimes(
            min_value=start.replace(tzinfo=None) + timedelta(days=1),
            timezones=st.just(user_settings.settings.time_zone),
        )
    )

    filter_ = TransactionFilter()
    filter_.set_datetime_filter(start, end, mode)
    assert filter_.datetime_filter.start == start
    assert filter_.datetime_filter.end == end
    assert filter_.datetime_filter.mode == mode


@given(
    pattern=st.text(),
    mode=st.sampled_from(FilterMode),
)
def test_set_description_filter(
    pattern: str,
    mode: FilterMode,
) -> None:
    try:
        re.compile(pattern)
        is_pattern_valid = True
    except re.error:
        is_pattern_valid = False
    assume(is_pattern_valid)

    filter_ = TransactionFilter()
    filter_.set_description_filter(pattern, mode)
    assert filter_.description_filter.regex_pattern == pattern
    assert filter_.description_filter.mode == mode


@given(
    accounts=st.lists(st.one_of(cash_accounts(), security_accounts())),
    mode=st.sampled_from(FilterMode),
)
def test_set_account_filter(
    accounts: list[Account],
    mode: FilterMode,
) -> None:
    filter_ = TransactionFilter()
    filter_.set_account_filter(accounts, mode)
    assert filter_.account_filter.accounts == tuple(accounts)
    assert filter_.account_filter.mode == mode


@given(
    tags=st.lists(attributes(AttributeType.TAG)),
    mode=st.sampled_from(FilterMode),
)
def test_set_specific_tag_filter(
    tags: list[Attribute],
    mode: FilterMode,
) -> None:
    filter_ = TransactionFilter()
    filter_.set_specific_tags_filter(tags, mode)
    assert filter_.specific_tags_filter.tags == frozenset(tags)
    assert filter_.specific_tags_filter.mode == mode


@given(
    mode=st.sampled_from(FilterMode),
)
def test_set_tagless_filter(
    mode: FilterMode,
) -> None:
    filter_ = TransactionFilter()
    filter_.set_tagless_filter(mode)
    assert filter_.tagless_filter.mode == mode


@given(
    mode=st.sampled_from(FilterMode),
)
def test_set_split_tags_filter(
    mode: FilterMode,
) -> None:
    filter_ = TransactionFilter()
    filter_.set_split_tags_filter(mode)
    assert filter_.split_tags_filter.mode == mode


@given(
    payees=st.lists(attributes(AttributeType.PAYEE)),
    mode=st.sampled_from(FilterMode),
)
def test_set_payee_filter(
    payees: list[Attribute],
    mode: FilterMode,
) -> None:
    filter_ = TransactionFilter()
    filter_.set_payee_filter(payees, mode)
    assert filter_.payee_filter.payees == frozenset(payees)
    assert filter_.payee_filter.mode == mode


@given(
    currencies=st.lists(currencies()),
    mode=st.sampled_from(FilterMode),
)
def test_set_currency_filter(
    currencies: list[Currency],
    mode: FilterMode,
) -> None:
    filter_ = TransactionFilter()
    filter_.set_currency_filter(currencies, mode)
    assert filter_.currency_filter.currencies == frozenset(currencies)
    assert filter_.currency_filter.mode == mode


@given(
    securities=st.lists(securities()),
    mode=st.sampled_from(FilterMode),
)
def test_set_security_filter(
    securities: list[Security],
    mode: FilterMode,
) -> None:
    filter_ = TransactionFilter()
    filter_.set_security_filter(securities, mode)
    assert filter_.security_filter.securities == frozenset(securities)
    assert filter_.security_filter.mode == mode


@given(
    data=st.data(),
    mode=st.sampled_from(FilterMode),
)
def test_set_cash_amount_filter(
    data: st.DataObject,
    mode: FilterMode,
) -> None:
    currency = data.draw(currencies())
    minimum = data.draw(cash_amounts(currency, min_value=0))
    maximum = data.draw(cash_amounts(currency, min_value=minimum.value_normalized))
    filter_ = TransactionFilter()
    filter_.set_cash_amount_filter(minimum, maximum, mode)

    assert filter_.cash_amount_filter is not None
    assert filter_.cash_amount_filter.minimum == minimum
    assert filter_.cash_amount_filter.maximum == maximum
    assert filter_.cash_amount_filter.mode == mode

    filter_.filter_transactions(transaction_list)
    filter_.validate_transaction(transaction_list[0])


@given(transactions=transactions())
def test_filter_transactions(transactions: list[Transaction]) -> None:
    filter_ = TransactionFilter()
    assert filter_.filter_transactions(transactions) == tuple(transactions)


def test_filter_premade_transactions() -> None:
    filter_ = TransactionFilter()
    assert filter_.filter_transactions(transaction_list) == tuple(transaction_list)


@given(transactions=transactions())
def test_accept_transactions(transactions: list[Transaction]) -> None:
    filter_ = TransactionFilter()
    for transaction in transactions:
        assert filter_.validate_transaction(transaction) is True


def test_accept_premade_transactions() -> None:
    filter_ = TransactionFilter()
    for transaction in transaction_list:
        assert filter_.validate_transaction(transaction) is True
