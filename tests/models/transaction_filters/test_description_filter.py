import re
from datetime import datetime
from typing import Any

from hypothesis import assume, given
from hypothesis import strategies as st
from src.models.base_classes.transaction import Transaction
from src.models.transaction_filters.base_transaction_filter import FilterMode
from src.models.transaction_filters.description_filter import DescriptionFilter
from tests.models.test_assets.composites import (
    description_filters,
    everything_except,
    transactions,
)
from tests.models.test_assets.transaction_list import transaction_list


def check_transaction(filter_: DescriptionFilter, transaction: Transaction) -> bool:
    if filter_.mode == FilterMode.OFF:
        return True
    return re.search(filter_.regex_pattern, transaction.description, re.IGNORECASE)


@given(pattern=st.text(), mode=st.sampled_from(FilterMode))
def test_creation(pattern: str, mode: FilterMode) -> None:
    try:
        re.compile(pattern)
        is_pattern_valid = True
    except re.error:
        is_pattern_valid = False
    assume(is_pattern_valid)
    filter_ = DescriptionFilter(pattern, mode)
    assert filter_.regex_pattern == pattern
    assert filter_.mode == mode
    assert filter_.__repr__() == (
        f"DescriptionFilter(pattern='{pattern}', mode={mode.name})"
    )


@given(filter_1=description_filters(), filter_2=description_filters())
def test_eq_hash(filter_1: DescriptionFilter, filter_2: DescriptionFilter) -> None:
    assert filter_1.__eq__(filter_2) == (
        filter_1.__hash__() == filter_2.__hash__()
    ) or (filter_1.mode == FilterMode.OFF and filter_2.mode == FilterMode.OFF)


@given(filter_1=description_filters(), filter_2=everything_except(DescriptionFilter))
def test_eq_different_type(filter_1: datetime, filter_2: Any) -> None:
    assert filter_1.__eq__(filter_2) is False


@given(transactions=transactions(), filter_=description_filters())
def test_filter_off(
    transactions: list[Transaction], filter_: DescriptionFilter
) -> None:
    filter_._mode = FilterMode.OFF
    filtered = filter_.filter_transactions(transactions)
    assert filtered == tuple(transactions)


@given(transactions=transactions(), filter_=description_filters())
def test_filter_keep(
    transactions: list[Transaction], filter_: DescriptionFilter
) -> None:
    filter_._mode = FilterMode.KEEP
    filtered = filter_.filter_transactions(transactions)
    assert filtered == tuple(
        transaction
        for transaction in transactions
        if check_transaction(filter_, transaction)
    )


@given(transactions=transactions(), filter_=description_filters())
def test_filter_discard(
    transactions: list[Transaction], filter_: DescriptionFilter
) -> None:
    filter_._mode = FilterMode.DISCARD
    filtered = filter_.filter_transactions(transactions)
    assert filtered == tuple(
        transaction
        for transaction in transactions
        if not check_transaction(filter_, transaction)
    )


@given(filter_=description_filters())
def test_filter_off_premade_transactions(filter_: DescriptionFilter) -> None:
    filter_._mode = FilterMode.OFF
    filtered = filter_.filter_transactions(transaction_list)
    assert filtered == tuple(transaction_list)


@given(filter_=description_filters())
def test_filter_keep_premade_transactions(filter_: DescriptionFilter) -> None:
    filter_._mode = FilterMode.KEEP
    filtered = filter_.filter_transactions(transaction_list)
    checked = tuple(
        transaction
        for transaction in transaction_list
        if check_transaction(filter_, transaction)
    )
    assert filtered == checked


@given(filter_=description_filters())
def test_filter_discard_premade_transactions(filter_: DescriptionFilter) -> None:
    filter_._mode = FilterMode.DISCARD
    filtered = filter_.filter_transactions(transaction_list)
    assert filtered == tuple(
        transaction
        for transaction in transaction_list
        if not check_transaction(filter_, transaction)
    )
