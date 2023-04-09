from typing import Any

from hypothesis import given
from hypothesis import strategies as st
from src.models.base_classes.transaction import Transaction
from src.models.transaction_filters.base_transaction_filter import FilterMode
from src.models.transaction_filters.tagless_filter import TaglessFilter
from tests.models.test_assets.composites import (
    everything_except,
    tagless_filters,
    transactions,
)
from tests.models.test_assets.transaction_list import transaction_list


def check_transaction(filter_: TaglessFilter, transaction: Transaction) -> bool:
    if filter_.mode == FilterMode.OFF:
        return True
    return len(transaction.tags) == 0


@given(mode=st.sampled_from(FilterMode))
def test_creation(mode: FilterMode) -> None:
    filter_ = TaglessFilter(mode)
    assert filter_.mode == mode
    assert filter_.__repr__() == f"TaglessFilter(mode={mode.name})"


@given(filter_1=tagless_filters(), filter_2=tagless_filters())
def test_eq_hash(filter_1: TaglessFilter, filter_2: TaglessFilter) -> None:
    assert filter_1.__eq__(filter_2) == (filter_1.__hash__() == filter_2.__hash__())


@given(filter_1=tagless_filters(), filter_2=everything_except(TaglessFilter))
def test_eq_different_type(filter_1: TaglessFilter, filter_2: Any) -> None:
    assert filter_1.__eq__(filter_2) is False


@given(transactions=transactions(), filter_=tagless_filters())
def test_filter_off(transactions: list[Transaction], filter_: TaglessFilter) -> None:
    filter_._mode = FilterMode.OFF
    filtered = filter_.filter_transactions(transactions)
    assert filtered == tuple(transactions)


@given(transactions=transactions(), filter_=tagless_filters())
def test_filter_keep(transactions: list[Transaction], filter_: TaglessFilter) -> None:
    filter_._mode = FilterMode.KEEP
    filtered = filter_.filter_transactions(transactions)
    assert filtered == tuple(
        transaction
        for transaction in transactions
        if check_transaction(filter_, transaction)
    )


@given(transactions=transactions(), filter_=tagless_filters())
def test_filter_discard(
    transactions: list[Transaction], filter_: TaglessFilter
) -> None:
    filter_._mode = FilterMode.DISCARD
    filtered = filter_.filter_transactions(transactions)
    assert filtered == tuple(
        transaction
        for transaction in transactions
        if not check_transaction(filter_, transaction)
    )


@given(filter_=tagless_filters())
def test_filter_off_premade_transactions(filter_: TaglessFilter) -> None:
    filter_._mode = FilterMode.OFF
    filtered = filter_.filter_transactions(transaction_list)
    assert filtered == tuple(transaction_list)


@given(filter_=tagless_filters())
def test_filter_keep_premade_transactions(filter_: TaglessFilter) -> None:
    filter_._mode = FilterMode.KEEP
    filtered = filter_.filter_transactions(transaction_list)
    assert filtered == tuple(
        transaction
        for transaction in transaction_list
        if check_transaction(filter_, transaction)
    )


@given(filter_=tagless_filters())
def test_filter_discard_premade_transactions(filter_: TaglessFilter) -> None:
    filter_._mode = FilterMode.DISCARD
    filtered = filter_.filter_transactions(transaction_list)
    assert filtered == tuple(
        transaction
        for transaction in transaction_list
        if not check_transaction(filter_, transaction)
    )
