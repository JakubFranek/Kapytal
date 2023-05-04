from typing import Any

from hypothesis import given
from hypothesis import strategies as st
from src.models.base_classes.transaction import Transaction
from src.models.model_objects.cash_objects import CashTransaction
from src.models.transaction_filters.base_transaction_filter import FilterMode
from src.models.transaction_filters.split_tags_filter import SplitTagsFilter
from tests.models.test_assets.composites import (
    everything_except,
    split_tags_filters,
    transactions,
)
from tests.models.test_assets.transaction_list import transaction_list


def check_transaction(filter_: SplitTagsFilter, transaction: Transaction) -> bool:
    if filter_.mode == FilterMode.OFF:
        return True
    if not isinstance(transaction, CashTransaction):
        return True
    return (
        transaction.are_tags_split
        if filter_.mode == FilterMode.KEEP
        else not transaction.are_tags_split
    )


@given(mode=st.sampled_from(FilterMode))
def test_creation(mode: FilterMode) -> None:
    filter_ = SplitTagsFilter(mode)
    assert filter_.mode == mode
    assert filter_.__repr__() == f"SplitTagsFilter(mode={mode.name})"


@given(filter_1=split_tags_filters(), filter_2=split_tags_filters())
def test_eq_hash(filter_1: SplitTagsFilter, filter_2: SplitTagsFilter) -> None:
    assert filter_1.__eq__(filter_2) == (filter_1.__hash__() == filter_2.__hash__())


@given(filter_1=split_tags_filters(), filter_2=everything_except(SplitTagsFilter))
def test_eq_different_type(filter_1: SplitTagsFilter, filter_2: Any) -> None:
    assert filter_1.__eq__(filter_2) is False


@given(transactions=transactions(), filter_=split_tags_filters())
def test_filter_off(transactions: list[Transaction], filter_: SplitTagsFilter) -> None:
    filter_._mode = FilterMode.OFF
    filtered = filter_.filter_transactions(transactions)
    assert filtered == tuple(transactions)


@given(transactions=transactions())
def test_filter_keep(transactions: list[Transaction]) -> None:
    filter_ = SplitTagsFilter(FilterMode.KEEP)
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
    filter_ = SplitTagsFilter(FilterMode.DISCARD)
    filtered = filter_.filter_transactions(transactions)
    assert filtered == tuple(
        transaction
        for transaction in transactions
        if check_transaction(filter_, transaction)
    )


def test_filter_off_premade_transactions() -> None:
    filter_ = SplitTagsFilter(FilterMode.OFF)
    filtered = filter_.filter_transactions(transaction_list)
    assert filtered == tuple(transaction_list)


def test_filter_keep_premade_transactions() -> None:
    filter_ = SplitTagsFilter(FilterMode.KEEP)
    filtered = filter_.filter_transactions(transaction_list)
    assert filtered == tuple(
        transaction
        for transaction in transaction_list
        if check_transaction(filter_, transaction)
    )


def test_filter_discard_premade_transactions() -> None:
    filter_ = SplitTagsFilter(FilterMode.DISCARD)
    filtered = filter_.filter_transactions(transaction_list)
    assert filtered == tuple(
        transaction
        for transaction in transaction_list
        if check_transaction(filter_, transaction)
    )
