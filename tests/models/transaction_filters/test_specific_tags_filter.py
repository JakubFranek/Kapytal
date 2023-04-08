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
from src.models.transaction_filters.specific_tags_filter import SpecificTagsFilter
from tests.models.test_assets.composites import (
    attributes,
    everything_except,
    specific_tag_filters,
    transactions,
)
from tests.models.test_assets.transaction_list import transaction_list


def check_transaction(filter_: SpecificTagsFilter, transaction: Transaction) -> bool:
    if filter_.mode == FilterMode.OFF:
        return True
    if filter_.mode == FilterMode.KEEP:
        return (
            any(tag in filter_.tags for tag in transaction.tags)
            or len(transaction.tags) == 0
        )
    return (
        not any(tag in transaction.tags for tag in filter_.tags)
        or len(transaction.tags) == 0
    )


@given(tags=st.lists(attributes(AttributeType.TAG)), mode=st.sampled_from(FilterMode))
def test_creation(tags: list[Attribute], mode: FilterMode) -> None:
    filter_ = SpecificTagsFilter(tags, mode)
    assert filter_.tags == frozenset(tags)
    assert filter_.mode == mode
    assert (
        filter_.__repr__()
        == f"SpecificTagsFilter(tags={frozenset(tags)}, mode={mode.name})"
    )


@given(
    tags=st.lists(everything_except(Attribute), min_size=1, max_size=10),
    mode=st.sampled_from(FilterMode),
)
def test_creation_invalid_type(tags: list[Any], mode: FilterMode) -> None:
    with pytest.raises(TypeError, match="must be a collection of Attributes"):
        SpecificTagsFilter(tags, mode)


@given(
    tags=st.lists(attributes(AttributeType.PAYEE), min_size=1, max_size=10),
    mode=st.sampled_from(FilterMode),
)
def test_creation_invalid_attribute_type(
    tags: list[Attribute], mode: FilterMode
) -> None:
    with pytest.raises(InvalidAttributeError, match="only Attributes with type_=TAG"):
        SpecificTagsFilter(tags, mode)


@given(filter_1=specific_tag_filters(), filter_2=specific_tag_filters())
def test_eq_hash(filter_1: SpecificTagsFilter, filter_2: SpecificTagsFilter) -> None:
    assert filter_1.__eq__(filter_2) == (filter_1.__hash__() == filter_2.__hash__())


@given(filter_1=specific_tag_filters(), filter_2=everything_except(SpecificTagsFilter))
def test_eq_different_type(filter_1: SpecificTagsFilter, filter_2: Any) -> None:
    assert filter_1.__eq__(filter_2) is False


@given(transactions=transactions(), filter_=specific_tag_filters())
def test_filter_off(
    transactions: list[Transaction], filter_: SpecificTagsFilter
) -> None:
    filter_._mode = FilterMode.OFF
    filtered = filter_.filter_transactions(transactions)
    assert filtered == tuple(transactions)


@given(transactions=transactions(), filter_=specific_tag_filters())
def test_filter_keep(
    transactions: list[Transaction], filter_: SpecificTagsFilter
) -> None:
    filter_._mode = FilterMode.KEEP
    filtered = filter_.filter_transactions(transactions)
    assert filtered == tuple(
        transaction
        for transaction in transactions
        if check_transaction(filter_, transaction)
    )


@given(transactions=transactions(), filter_=specific_tag_filters())
def test_filter_discard(
    transactions: list[Transaction], filter_: SpecificTagsFilter
) -> None:
    filter_._mode = FilterMode.DISCARD
    filtered = filter_.filter_transactions(transactions)
    assert filtered == tuple(
        transaction
        for transaction in transactions
        if check_transaction(filter_, transaction)
    )


@given(filter_=specific_tag_filters())
def test_filter_off_premade_transactions(filter_: SpecificTagsFilter) -> None:
    filter_._mode = FilterMode.OFF
    filtered = filter_.filter_transactions(transaction_list)
    assert filtered == tuple(transaction_list)


@given(filter_=specific_tag_filters())
def test_filter_keep_premade_transactions(filter_: SpecificTagsFilter) -> None:
    filter_._mode = FilterMode.KEEP
    filtered = filter_.filter_transactions(transaction_list)
    assert filtered == tuple(
        transaction
        for transaction in transaction_list
        if check_transaction(filter_, transaction)
    )


@given(filter_=specific_tag_filters())
def test_filter_discard_premade_transactions(filter_: SpecificTagsFilter) -> None:
    filter_._mode = FilterMode.DISCARD
    filtered = filter_.filter_transactions(transaction_list)
    assert filtered == tuple(
        transaction
        for transaction in transaction_list
        if check_transaction(filter_, transaction)
    )
