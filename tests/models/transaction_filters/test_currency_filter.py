from typing import Any

import pytest
from hypothesis import given
from hypothesis import strategies as st
from src.models.base_classes.transaction import Transaction
from src.models.model_objects.cash_objects import CashRelatedTransaction
from src.models.model_objects.currency_objects import Currency
from src.models.transaction_filters.base_transaction_filter import FilterMode
from src.models.transaction_filters.currency_filter import CurrencyFilter
from tests.models.test_assets.composites import (
    currencies,
    currency_filters,
    everything_except,
    transactions,
)
from tests.models.test_assets.transaction_list import transaction_list


def check_transaction(filter_: CurrencyFilter, transaction: Transaction) -> bool:
    if filter_.mode == FilterMode.OFF:
        return True
    if not isinstance(transaction, CashRelatedTransaction):
        return True
    if filter_.mode == FilterMode.KEEP:
        return any(
            currency in transaction.currencies for currency in filter_.currencies
        )
    return not any(
        currency in transaction.currencies for currency in filter_.currencies
    )


@given(currencies=st.lists(currencies(), unique=True), mode=st.sampled_from(FilterMode))
def test_creation(currencies: list[Currency], mode: FilterMode) -> None:
    filter_ = CurrencyFilter(currencies, mode)
    assert filter_.currencies == frozenset(currencies)
    assert filter_.currency_codes == tuple(
        sorted(currency.code for currency in currencies)
    )
    assert filter_.mode == mode
    assert (
        filter_.__repr__()
        == f"CurrencyFilter(currencies={filter_.currency_codes}, mode={mode.name})"
    )


@given(
    currencies=st.lists(everything_except(Currency), min_size=1, max_size=10),
    mode=st.sampled_from(FilterMode),
)
def test_creation_invalid_type(currencies: list[Any], mode: FilterMode) -> None:
    with pytest.raises(TypeError, match="must be a Collection of Currencies"):
        CurrencyFilter(currencies, mode)


@given(filter_1=currency_filters(), filter_2=currency_filters())
def test_eq_hash(filter_1: CurrencyFilter, filter_2: CurrencyFilter) -> None:
    assert filter_1.__eq__(filter_2) == (
        filter_1.__hash__() == filter_2.__hash__()
    ) or (filter_1.mode == FilterMode.OFF and filter_2.mode == FilterMode.OFF)


@given(filter_1=currency_filters(), filter_2=everything_except(CurrencyFilter))
def test_eq_different_type(filter_1: CurrencyFilter, filter_2: Any) -> None:
    assert filter_1.__eq__(filter_2) is False


@given(transactions=transactions(), filter_=currency_filters())
def test_filter_off(transactions: list[Transaction], filter_: CurrencyFilter) -> None:
    filter_._mode = FilterMode.OFF
    filtered = filter_.filter_transactions(transactions)
    assert filtered == tuple(transactions)


@given(transactions=transactions(), filter_=currency_filters())
def test_filter_keep(transactions: list[Transaction], filter_: CurrencyFilter) -> None:
    filter_._mode = FilterMode.KEEP
    filtered = filter_.filter_transactions(transactions)
    assert filtered == tuple(
        transaction
        for transaction in transactions
        if check_transaction(filter_, transaction)
    )


@given(transactions=transactions(), filter_=currency_filters())
def test_filter_discard(
    transactions: list[Transaction], filter_: CurrencyFilter
) -> None:
    filter_._mode = FilterMode.DISCARD
    filtered = filter_.filter_transactions(transactions)
    assert filtered == tuple(
        transaction
        for transaction in transactions
        if check_transaction(filter_, transaction)
    )


@given(filter_=currency_filters())
def test_filter_off_premade_transactions(filter_: CurrencyFilter) -> None:
    filter_._mode = FilterMode.OFF
    filtered = filter_.filter_transactions(transaction_list)
    assert filtered == tuple(transaction_list)


@given(filter_=currency_filters())
def test_filter_keep_premade_transactions(filter_: CurrencyFilter) -> None:
    filter_._mode = FilterMode.KEEP
    filtered = filter_.filter_transactions(transaction_list)
    assert filtered == tuple(
        transaction
        for transaction in transaction_list
        if check_transaction(filter_, transaction)
    )


@given(filter_=currency_filters())
def test_filter_discard_premade_transactions(filter_: CurrencyFilter) -> None:
    filter_._mode = FilterMode.DISCARD
    filtered = filter_.filter_transactions(transaction_list)
    assert filtered == tuple(
        transaction
        for transaction in transaction_list
        if check_transaction(filter_, transaction)
    )
