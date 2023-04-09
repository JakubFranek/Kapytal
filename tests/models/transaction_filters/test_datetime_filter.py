from datetime import datetime, timedelta
from typing import Any

import pytest
from hypothesis import assume, given
from hypothesis import strategies as st
from src.models.base_classes.transaction import Transaction
from src.models.transaction_filters.base_transaction_filter import FilterMode
from src.models.transaction_filters.datetime_filter import DatetimeFilter
from src.models.user_settings import user_settings
from tests.models.test_assets.composites import (
    datetime_filters,
    everything_except,
    transactions,
)
from tests.models.test_assets.transaction_list import (
    earliest_datetime,
    latest_datetime,
    transaction_list,
)


def check_transaction(filter_: DatetimeFilter, transaction: Transaction) -> bool:
    if filter_.mode == FilterMode.OFF:
        return True
    return filter_._start <= transaction.datetime_ <= filter_._end


@given(start=st.datetimes(), end=st.datetimes(), mode=st.sampled_from(FilterMode))
def test_creation(start: datetime, end: datetime, mode: FilterMode) -> None:
    start.replace(tzinfo=user_settings.settings.time_zone)
    end.replace(tzinfo=user_settings.settings.time_zone)
    assume(end > start)
    filter_ = DatetimeFilter(start, end, mode)

    assert filter_.start == start
    assert filter_.end == end
    assert filter_.mode == mode
    assert filter_.__repr__() == (
        f"DatetimeFilter(start={start.strftime('%Y-%m-%d %H:%M:%S')}, "
        f"end={end.strftime('%Y-%m-%d %H:%M:%S')}, mode={mode.name})"
    )


@given(
    start=everything_except(datetime),
    end=st.datetimes(),
    mode=st.sampled_from(FilterMode),
)
def test_creation_invalid_start_type(
    start: Any, end: datetime, mode: FilterMode
) -> None:
    with pytest.raises(TypeError):
        DatetimeFilter(start, end, mode)


@given(
    start=st.datetimes(),
    end=everything_except(datetime),
    mode=st.sampled_from(FilterMode),
)
def test_creation_invalid_end_type(start: datetime, end: Any, mode: FilterMode) -> None:
    with pytest.raises(TypeError):
        DatetimeFilter(start, end, mode)


@given(
    start=st.datetimes(),
    end=st.datetimes(),
    mode=st.sampled_from(FilterMode),
)
def test_creation_end_precedes_start(
    start: datetime, end: Any, mode: FilterMode
) -> None:
    assume(start > end)
    with pytest.raises(ValueError, match="'start' must be an earlier datetime"):
        DatetimeFilter(start, end, mode)


@given(filter_1=datetime_filters(), filter_2=datetime_filters())
def test_eq_hash(filter_1: DatetimeFilter, filter_2: DatetimeFilter) -> None:
    assert filter_1.__eq__(filter_2) == (filter_1.__hash__() == filter_2.__hash__())


@given(filter_1=datetime_filters(), filter_2=everything_except(DatetimeFilter))
def test_eq_different_type(filter_1: DatetimeFilter, filter_2: Any) -> None:
    assert filter_1.__eq__(filter_2) is False


@given(transactions=transactions(), filter_=datetime_filters())
def test_filter_off(transactions: list[Transaction], filter_: DatetimeFilter) -> None:
    filter_._mode = FilterMode.OFF
    filtered = filter_.filter_transactions(transactions)
    assert filtered == tuple(transactions)


@given(transactions=transactions(), filter_=datetime_filters())
def test_filter_keep(transactions: list[Transaction], filter_: DatetimeFilter) -> None:
    filter_._mode = FilterMode.KEEP
    filtered = filter_.filter_transactions(transactions)
    assert filtered == tuple(
        transaction
        for transaction in transactions
        if check_transaction(filter_, transaction)
    )


@given(transactions=transactions(), filter_=datetime_filters())
def test_filter_discard(
    transactions: list[Transaction], filter_: DatetimeFilter
) -> None:
    filter_._mode = FilterMode.DISCARD
    filtered = filter_.filter_transactions(transactions)
    assert filtered == tuple(
        transaction
        for transaction in transactions
        if not check_transaction(filter_, transaction)
    )


@given(filter_=datetime_filters())
def test_filter_off_premade_transactions(filter_: DatetimeFilter) -> None:
    filter_._mode = FilterMode.OFF
    filtered = filter_.filter_transactions(transaction_list)
    assert filtered == tuple(transaction_list)


@given(filter_=datetime_filters())
def test_filter_keep_premade_transactions(filter_: DatetimeFilter) -> None:
    filter_._mode = FilterMode.KEEP
    filtered = filter_.filter_transactions(transaction_list)
    assert filtered == tuple(
        transaction
        for transaction in transaction_list
        if check_transaction(filter_, transaction)
    )


@given(filter_=datetime_filters())
def test_filter_discard_premade_transactions(filter_: DatetimeFilter) -> None:
    filter_._mode = FilterMode.DISCARD
    filtered = filter_.filter_transactions(transaction_list)
    assert filtered == tuple(
        transaction
        for transaction in transaction_list
        if not check_transaction(filter_, transaction)
    )


def test_filter_keep_premade_transactions_custom() -> None:
    filter_ = DatetimeFilter(
        start=earliest_datetime + timedelta(days=1),
        end=latest_datetime - timedelta(days=1),
        mode=FilterMode.KEEP,
    )
    filter_._mode = FilterMode.KEEP
    filtered = filter_.filter_transactions(transaction_list)
    assert filtered == tuple(
        transaction
        for transaction in transaction_list
        if check_transaction(filter_, transaction)
    )
