from typing import Any

import pytest
from hypothesis import assume, given
from hypothesis import strategies as st
from src.models.base_classes.transaction import Transaction
from src.models.model_objects.cash_objects import (
    CashRelatedTransaction,
    CashTransaction,
    CashTransfer,
    RefundTransaction,
)
from src.models.model_objects.currency_objects import (
    CashAmount,
    Currency,
    CurrencyError,
)
from src.models.model_objects.security_objects import SecurityTransaction
from src.models.transaction_filters.base_transaction_filter import FilterMode
from src.models.transaction_filters.cash_amount_filter import CashAmountFilter
from tests.models.test_assets.composites import (
    cash_amount_filters,
    cash_amounts,
    currencies,
    everything_except,
    transactions,
)
from tests.models.test_assets.transaction_list import transaction_list


def check_transaction(filter_: CashAmountFilter, transaction: Transaction) -> bool:
    if filter_.mode == FilterMode.OFF:
        return True
    if not isinstance(transaction, CashRelatedTransaction):
        return True
    if filter_.mode == FilterMode.KEEP:
        if isinstance(
            transaction, CashTransaction | SecurityTransaction | RefundTransaction
        ):
            amounts = (transaction.amount,)
        elif isinstance(transaction, CashTransfer):
            amounts = (transaction.amount_sent, transaction.amount_received)
        else:
            raise TypeError(f"Unexpected transaction type: {type(transaction)}")
        amounts = tuple(amount.convert(filter_._currency) for amount in amounts)
        return any(filter_.minimum <= amount <= filter_.maximum for amount in amounts)
    if isinstance(
        transaction, CashTransaction | SecurityTransaction | RefundTransaction
    ):
        amounts = (transaction.amount,)
    elif isinstance(transaction, CashTransfer):
        amounts = (transaction.amount_sent, transaction.amount_received)
    else:
        raise TypeError(f"Unexpected transaction type: {type(transaction)}")
    amounts = tuple(amount.convert(filter_._currency) for amount in amounts)
    return any(
        amount < filter_.minimum or amount > filter_.maximum for amount in amounts
    )


@given(currency=currencies(), mode=st.sampled_from(FilterMode), data=st.data())
def test_creation(currency: Currency, mode: FilterMode, data: st.DataObject) -> None:
    minimum = data.draw(cash_amounts(currency, min_value=0))
    maximum = data.draw(cash_amounts(currency, min_value=minimum.value_normalized))
    filter_ = CashAmountFilter(minimum, maximum, mode)

    assert filter_.minimum == minimum
    assert filter_.maximum == maximum
    assert filter_.mode == mode
    assert filter_.currency == currency
    assert filter_.__repr__() == (
        f"CashAmountFilter(min={minimum.to_str_rounded()}, "
        f"max={maximum.to_str_rounded()}, mode={mode.name})"
    )


@given(currency=currencies(), mode=st.sampled_from(FilterMode), data=st.data())
def test_creation_minimum_invalid_type(
    currency: Currency, mode: FilterMode, data: st.DataObject
) -> None:
    minimum = data.draw(everything_except(CashAmount))
    maximum = data.draw(cash_amounts(currency, min_value=0))
    with pytest.raises(TypeError, match="Parameter 'minimum' must be a CashAmount."):
        CashAmountFilter(minimum, maximum, mode)


@given(currency=currencies(), mode=st.sampled_from(FilterMode), data=st.data())
def test_creation_maximum_invalid_type(
    currency: Currency, mode: FilterMode, data: st.DataObject
) -> None:
    minimum = data.draw(cash_amounts(currency, min_value=0))
    maximum = data.draw(everything_except(CashAmount))
    with pytest.raises(TypeError, match="Parameter 'maximum' must be a CashAmount."):
        CashAmountFilter(minimum, maximum, mode)


@given(mode=st.sampled_from(FilterMode), data=st.data())
def test_creation_currencies_not_same(mode: FilterMode, data: st.DataObject) -> None:
    currency_1 = data.draw(currencies())
    currency_2 = data.draw(currencies())
    assume(currency_1 != currency_2)
    minimum = data.draw(cash_amounts(currency_1, min_value=0))
    maximum = data.draw(cash_amounts(currency_2, min_value=minimum.value_normalized))
    with pytest.raises(CurrencyError):
        CashAmountFilter(minimum, maximum, mode)


@given(currency=currencies(), mode=st.sampled_from(FilterMode), data=st.data())
def test_creation_minimum_greater_than_maximum(
    currency: Currency, mode: FilterMode, data: st.DataObject
) -> None:
    minimum = data.draw(cash_amounts(currency, min_value=0))
    maximum = data.draw(cash_amounts(currency, max_value=minimum.value_normalized - 1))
    with pytest.raises(
        ValueError, match="Parameter 'minimum' must be less than or equal to 'maximum'."
    ):
        CashAmountFilter(minimum, maximum, mode)


@given(currency=currencies(), mode=st.sampled_from(FilterMode), data=st.data())
def test_creation_minimum_negative(
    currency: Currency, mode: FilterMode, data: st.DataObject
) -> None:
    minimum = data.draw(cash_amounts(currency, max_value=-1))
    maximum = data.draw(cash_amounts(currency, min_value=0))
    with pytest.raises(ValueError, match="Parameter 'minimum' must not be negative."):
        CashAmountFilter(minimum, maximum, mode)


@given(filter_1=cash_amount_filters(), filter_2=cash_amount_filters())
def test_eq_hash(filter_1: CashAmountFilter, filter_2: CashAmountFilter) -> None:
    assert filter_1.__eq__(filter_2) == (
        filter_1.__hash__() == filter_2.__hash__()
    ) or (filter_1.mode == FilterMode.OFF and filter_2.mode == FilterMode.OFF)


@given(filter_1=cash_amount_filters(), filter_2=everything_except(CashAmountFilter))
def test_eq_different_type(filter_1: CashAmountFilter, filter_2: Any) -> None:
    if filter_2 is None:
        assert filter_1.__eq__(filter_2) is (filter_1.mode == FilterMode.OFF)
    else:
        assert filter_1.__eq__(filter_2) is False


@given(transactions=transactions(), filter_=cash_amount_filters())
def test_filter_off(transactions: list[Transaction], filter_: CashAmountFilter) -> None:
    filter_._mode = FilterMode.OFF
    filtered = filter_.filter_transactions(transactions)
    assert filtered == tuple(transactions)


@given(filter_=cash_amount_filters())
def test_filter_off_premade_transactions(filter_: CashAmountFilter) -> None:
    filter_._mode = FilterMode.OFF
    filtered = filter_.filter_transactions(transaction_list)
    assert filtered == tuple(transaction_list)


@given(data=st.data())
def test_filter_keep_premade_transactions(data: st.DataObject) -> None:
    mode = FilterMode.KEEP
    currency_tuples = tuple(
        transaction.currencies
        for transaction in transaction_list
        if isinstance(transaction, CashRelatedTransaction)
    )
    currencies = tuple(
        {currency for currency_tuple in currency_tuples for currency in currency_tuple}
    )
    currency = data.draw(st.sampled_from(currencies))
    minimum = data.draw(cash_amounts(currency, min_value=0))
    maximum = data.draw(cash_amounts(currency, min_value=minimum.value_normalized))
    filter_ = CashAmountFilter(minimum, maximum, mode)
    filter_._mode = FilterMode.KEEP
    filtered = filter_.filter_transactions(transaction_list)
    assert filtered == tuple(
        transaction
        for transaction in transaction_list
        if check_transaction(filter_, transaction)
    )


@given(data=st.data())
def test_filter_discard_premade_transactions(data: st.DataObject) -> None:
    mode = FilterMode.DISCARD
    currency_tuples = tuple(
        transaction.currencies
        for transaction in transaction_list
        if isinstance(transaction, CashRelatedTransaction)
    )
    currencies = tuple(
        {currency for currency_tuple in currency_tuples for currency in currency_tuple}
    )
    currency = data.draw(st.sampled_from(currencies))
    minimum = data.draw(cash_amounts(currency, min_value=0))
    maximum = data.draw(cash_amounts(currency, min_value=minimum.value_normalized))
    filter_ = CashAmountFilter(minimum, maximum, mode)
    filtered = filter_.filter_transactions(transaction_list)
    assert filtered == tuple(
        transaction
        for transaction in transaction_list
        if check_transaction(filter_, transaction)
    )


@given(data=st.data())
def test_filter_keep_premade_transactions_conversion_factor_not_found(
    data: st.DataObject,
) -> None:
    mode = FilterMode.KEEP
    currency = data.draw(currencies())
    minimum = data.draw(cash_amounts(currency, min_value=0))
    maximum = data.draw(cash_amounts(currency, min_value=minimum.value_normalized))
    filter_ = CashAmountFilter(minimum, maximum, mode)
    filter_._mode = FilterMode.KEEP
    filtered = filter_.filter_transactions(transaction_list)
    assert filtered == tuple(transaction_list)


@given(data=st.data())
def test_filter_discard_premade_transactions_conversion_factor_not_found(
    data: st.DataObject,
) -> None:
    mode = FilterMode.DISCARD
    currency = data.draw(currencies())
    minimum = data.draw(cash_amounts(currency, min_value=0))
    maximum = data.draw(cash_amounts(currency, min_value=minimum.value_normalized))
    filter_ = CashAmountFilter(minimum, maximum, mode)
    filtered = filter_.filter_transactions(transaction_list)
    assert filtered == tuple(transaction_list)
