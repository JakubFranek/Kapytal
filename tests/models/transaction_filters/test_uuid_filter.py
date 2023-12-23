from datetime import datetime
from typing import Any
from uuid import UUID

import pytest
from hypothesis import given
from hypothesis import strategies as st
from src.models.base_classes.transaction import Transaction
from src.models.transaction_filters.base_transaction_filter import FilterMode
from src.models.transaction_filters.uuid_filter import UUIDFilter
from tests.models.test_assets.composites import (
    everything_except,
    transactions,
    uuid_filters,
)
from tests.models.test_assets.transaction_list import transaction_list

uuids = [transaction.uuid for transaction in transaction_list]


def check_transaction(filter_: UUIDFilter, transaction: Transaction) -> bool:
    if filter_.mode == FilterMode.OFF:
        return True
    return transaction.uuid in filter_.uuids


@given(
    mode=st.sampled_from(FilterMode), uuids=st.lists(st.uuids(version=4), min_size=0)
)
def test_creation(mode: FilterMode, uuids: list[UUID]) -> None:
    filter_ = UUIDFilter(uuids, mode)
    assert filter_.uuids == tuple(uuids)
    assert filter_.uuids_set == frozenset(uuids)
    assert filter_.mode == mode
    assert filter_.__repr__() == f"UUIDFilter(uuids={tuple(uuids)}, mode={mode.name})"


@given(
    mode=st.sampled_from(FilterMode),
    uuids=st.lists(everything_except(UUID), min_size=1),
)
def test_creation_invalid_type(mode: FilterMode, uuids: list[UUID]) -> None:
    with pytest.raises(TypeError):
        UUIDFilter(uuids, mode)


@given(
    filter_1=uuid_filters(uuids_to_draw_from=uuids),
    filter_2=uuid_filters(uuids_to_draw_from=uuids),
)
def test_eq_hash(filter_1: UUIDFilter, filter_2: UUIDFilter) -> None:
    assert filter_1.__eq__(filter_2) == (
        filter_1.__hash__() == filter_2.__hash__()
    ) or (filter_1.mode == FilterMode.OFF and filter_2.mode == FilterMode.OFF)


@given(
    filter_1=uuid_filters(uuids_to_draw_from=uuids),
    filter_2=everything_except(UUIDFilter),
)
def test_eq_different_type(filter_1: datetime, filter_2: Any) -> None:
    assert filter_1.__eq__(filter_2) is False


@given(transactions=transactions(), data=st.data())
def test_filter_off(transactions: list[Transaction], data: st.DataObject) -> None:
    filter_ = data.draw(
        uuid_filters([transaction.uuid for transaction in transactions])
    )
    filter_._mode = FilterMode.OFF
    filtered = filter_.filter_transactions(transactions)
    assert filtered == tuple(transactions)


@given(transactions=transactions(), data=st.data())
def test_filter_keep(transactions: list[Transaction], data: st.DataObject) -> None:
    filter_ = data.draw(
        uuid_filters([transaction.uuid for transaction in transactions])
    )
    filter_._mode = FilterMode.KEEP
    filtered = filter_.filter_transactions(transactions)
    assert filtered == tuple(
        transaction
        for transaction in transactions
        if check_transaction(filter_, transaction)
    )


@given(transactions=transactions(), data=st.data())
def test_filter_discard(transactions: list[Transaction], data: st.DataObject) -> None:
    filter_ = data.draw(
        uuid_filters([transaction.uuid for transaction in transactions])
    )
    filter_._mode = FilterMode.DISCARD
    filtered = filter_.filter_transactions(transactions)
    assert filtered == tuple(
        transaction
        for transaction in transactions
        if not check_transaction(filter_, transaction)
    )


@given(filter_=uuid_filters(uuids_to_draw_from=uuids))
def test_filter_off_premade_transactions(filter_: UUIDFilter) -> None:
    filter_._mode = FilterMode.OFF
    filtered = filter_.filter_transactions(transaction_list)
    assert filtered == tuple(transaction_list)


@given(filter_=uuid_filters(uuids_to_draw_from=uuids))
def test_filter_keep_premade_transactions(filter_: UUIDFilter) -> None:
    filter_._mode = FilterMode.KEEP
    filtered = filter_.filter_transactions(transaction_list)
    checked = tuple(
        transaction
        for transaction in transaction_list
        if check_transaction(filter_, transaction)
    )
    assert filtered == checked


@given(filter_=uuid_filters(uuids_to_draw_from=uuids))
def test_filter_discard_premade_transactions(filter_: UUIDFilter) -> None:
    filter_._mode = FilterMode.DISCARD
    filtered = filter_.filter_transactions(transaction_list)
    assert filtered == tuple(
        transaction
        for transaction in transaction_list
        if not check_transaction(filter_, transaction)
    )
