from typing import Any

from hypothesis import given
from hypothesis import strategies as st
from src.models.base_classes.transaction import Transaction
from src.models.model_objects.cash_objects import CashTransaction, RefundTransaction
from src.models.transaction_filters.base_transaction_filter import FilterMode
from src.models.transaction_filters.multiple_categories_filter import (
    MultipleCategoriesFilter,
)
from tests.models.test_assets.composites import (
    everything_except,
    multiple_categories_filters,
    transactions,
)
from tests.models.test_assets.transaction_list import transaction_list


def check_transaction(
    filter_: MultipleCategoriesFilter, transaction: Transaction
) -> bool:
    if filter_.mode == FilterMode.OFF:
        return True
    if not isinstance(transaction, CashTransaction | RefundTransaction):
        return True
    return (
        len(transaction.categories) > 1
        if filter_.mode == FilterMode.KEEP
        else not len(transaction.categories) > 1
    )


@given(mode=st.sampled_from(FilterMode))
def test_creation(mode: FilterMode) -> None:
    filter_ = MultipleCategoriesFilter(mode)
    assert filter_.mode == mode
    assert filter_.__repr__() == f"MultipleCategoriesFilter(mode={mode.name})"


@given(filter_1=multiple_categories_filters(), filter_2=multiple_categories_filters())
def test_eq_hash(
    filter_1: MultipleCategoriesFilter, filter_2: MultipleCategoriesFilter
) -> None:
    assert filter_1.__eq__(filter_2) == (filter_1.__hash__() == filter_2.__hash__())


@given(
    filter_1=multiple_categories_filters(),
    filter_2=everything_except(MultipleCategoriesFilter),
)
def test_eq_different_type(filter_1: MultipleCategoriesFilter, filter_2: Any) -> None:
    assert filter_1.__eq__(filter_2) is False


@given(transactions=transactions())
def test_filter_off(transactions: list[Transaction]) -> None:
    filter_ = MultipleCategoriesFilter(FilterMode.OFF)
    filtered = filter_.filter_transactions(transactions)
    assert filtered == tuple(transactions)


@given(transactions=transactions())
def test_filter_keep(
    transactions: list[Transaction],
) -> None:
    filter_ = MultipleCategoriesFilter(FilterMode.KEEP)
    filtered = filter_.filter_transactions(transactions)
    assert filtered == tuple(
        transaction
        for transaction in transactions
        if check_transaction(filter_, transaction)
    )


@given(transactions=transactions())
def test_filter_discard(
    transactions: list[Transaction],
) -> None:
    filter_ = MultipleCategoriesFilter(FilterMode.DISCARD)
    filtered = filter_.filter_transactions(transactions)
    assert filtered == tuple(
        transaction
        for transaction in transactions
        if check_transaction(filter_, transaction)
    )


@given(filter_=multiple_categories_filters())
def test_filter_off_premade_transactions(filter_: MultipleCategoriesFilter) -> None:
    filter_._mode = FilterMode.OFF
    filtered = filter_.filter_transactions(transaction_list)
    assert filtered == tuple(transaction_list)


def test_filter_keep_premade_transactions() -> None:
    filter_ = MultipleCategoriesFilter(FilterMode.KEEP)
    filtered = filter_.filter_transactions(transaction_list)
    expected = tuple(
        transaction
        for transaction in transaction_list
        if check_transaction(filter_, transaction)
    )
    assert filtered == expected


def test_filter_discard_premade_transactions() -> None:
    filter_ = MultipleCategoriesFilter(FilterMode.DISCARD)
    filtered = filter_.filter_transactions(transaction_list)
    assert filtered == tuple(
        transaction
        for transaction in transaction_list
        if check_transaction(filter_, transaction)
    )
