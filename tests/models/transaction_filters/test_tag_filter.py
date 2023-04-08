from typing import Any

import pytest
from hypothesis import given
from hypothesis import strategies as st
from src.models.base_classes.transaction import Transaction
from src.models.model_objects.attributes import (
    Attribute,
    AttributeType,
    InvalidAttributeError,
)
from src.models.transaction_filters.filter_mode_mixin import FilterMode
from src.models.transaction_filters.tag_filter import TagFilter
from tests.models.test_assets.composites import (
    attributes,
    everything_except,
    tag_filters,
    transactions,
)
from tests.models.test_assets.transaction_list import transaction_list


def check_transaction(filter_: TagFilter, transaction: Transaction) -> bool:
    if filter_.mode == FilterMode.OFF:
        return True
    return any(tag in transaction.tags for tag in filter_.tags)


@given(tags=st.lists(attributes(AttributeType.TAG)), mode=st.sampled_from(FilterMode))
def test_creation(tags: list[Attribute], mode: FilterMode) -> None:
    filter_ = TagFilter(tags, mode)
    assert filter_.tags == tuple(tags)
    assert filter_.mode == mode
    assert filter_.__repr__() == f"TagFilter(tags={tuple(tags)}, mode={mode.name})"


@given(
    tags=st.lists(everything_except(Attribute), min_size=1, max_size=10),
    mode=st.sampled_from(FilterMode),
)
def test_creation_invalid_type(tags: list[Any], mode: FilterMode) -> None:
    with pytest.raises(TypeError, match="must be a collection of Attributes"):
        TagFilter(tags, mode)


@given(
    tags=st.lists(attributes(AttributeType.PAYEE), min_size=1, max_size=10),
    mode=st.sampled_from(FilterMode),
)
def test_creation_invalid_attribute_type(
    tags: list[Attribute], mode: FilterMode
) -> None:
    with pytest.raises(InvalidAttributeError, match="only Attributes with type_=TAG"):
        TagFilter(tags, mode)


@given(filter_1=tag_filters(), filter_2=tag_filters())
def test_eq_hash(filter_1: TagFilter, filter_2: TagFilter) -> None:
    assert filter_1.__eq__(filter_2) == (filter_1.__hash__() == filter_2.__hash__())


@given(filter_1=tag_filters(), filter_2=everything_except(TagFilter))
def test_eq_different_type(filter_1: TagFilter, filter_2: Any) -> None:
    assert filter_1.__eq__(filter_2) is False


@given(transactions=transactions(), filter_=tag_filters())
def test_filter(transactions: list[Transaction], filter_: TagFilter) -> None:
    filter_._mode = FilterMode.OFF
    filtered = filter_.filter_transactions(transactions)
    assert filtered == tuple(transactions)


@given(transactions=transactions(), filter_=tag_filters())
def test_filter_keep(transactions: list[Transaction], filter_: TagFilter) -> None:
    filter_._mode = FilterMode.KEEP
    filtered = filter_.filter_transactions(transactions)
    assert filtered == tuple(
        transaction
        for transaction in transactions
        if check_transaction(filter_, transaction)
    )


@given(transactions=transactions(), filter_=tag_filters())
def test_filter_discard(transactions: list[Transaction], filter_: TagFilter) -> None:
    filter_._mode = FilterMode.DISCARD
    filtered = filter_.filter_transactions(transactions)
    assert filtered == tuple(
        transaction
        for transaction in transactions
        if not check_transaction(filter_, transaction)
    )


@given(filter_=tag_filters())
def test_filter_off_premade_transactions(filter_: TagFilter) -> None:
    filter_._mode = FilterMode.OFF
    filtered = filter_.filter_transactions(transaction_list)
    assert filtered == tuple(transaction_list)


@given(filter_=tag_filters())
def test_filter_keep_premade_transactions(filter_: TagFilter) -> None:
    filter_._mode = FilterMode.KEEP
    filtered = filter_.filter_transactions(transaction_list)
    assert filtered == tuple(
        transaction
        for transaction in transaction_list
        if check_transaction(filter_, transaction)
    )


@given(filter_=tag_filters())
def test_filter_discard_premade_transactions(filter_: TagFilter) -> None:
    filter_._mode = FilterMode.DISCARD
    filtered = filter_.filter_transactions(transaction_list)
    assert filtered == tuple(
        transaction
        for transaction in transaction_list
        if not check_transaction(filter_, transaction)
    )
