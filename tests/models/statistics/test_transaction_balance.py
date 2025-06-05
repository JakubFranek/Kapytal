from decimal import Decimal

from hypothesis import given
from hypothesis import strategies as st
from src.models.base_classes.transaction import Transaction
from src.models.model_objects.currency_objects import CashAmount
from src.models.statistics.common_classes import TransactionBalance
from tests.models.test_assets.composites import (
    cash_amounts,
    currencies,
    everything_except,
    transaction_balances,
    transactions,
)


@given(balance=cash_amounts(), transactions=st.one_of(st.just(None), transactions()))
def test_creation(balance: CashAmount, transactions: list[Transaction]) -> None:
    item = TransactionBalance(balance, transactions)

    assert len(item) == (len(transactions) if transactions is not None else 0)
    assert item.balance == balance
    assert item.transactions == (
        set(transactions) if transactions is not None else set()
    )
    assert item.__repr__() == (
        f"TransactionBalance({balance.to_str_normalized()}, "
        f"len={len(transactions) if transactions is not None else 0})"
    )


@given(data=st.data())
def test_add(data: st.DataObject) -> None:
    currency = data.draw(currencies())
    item_1 = data.draw(transaction_balances(currency=currency))
    item_2 = data.draw(transaction_balances(currency=currency))
    result = item_1 + item_2

    assert result.balance == item_1.balance + item_2.balance
    assert result.transactions == set(item_1.transactions.union(item_2.transactions))


@given(data=st.data())
def test_sub(data: st.DataObject) -> None:
    currency = data.draw(currencies())
    item_1 = data.draw(transaction_balances(currency=currency))
    item_2 = data.draw(transaction_balances(currency=currency))
    result = item_1 - item_2

    assert result.balance == item_1.balance - item_2.balance
    assert result.transactions == set(item_1.transactions.union(item_2.transactions))


@given(data=st.data())
def test_truediv(data: st.DataObject) -> None:
    item = data.draw(transaction_balances())
    divisor = data.draw(st.integers(min_value=1))
    result = item / divisor

    assert result.balance == item.balance / divisor
    assert result.transactions == item.transactions


@given(data=st.data())
def test_truediv_notimplemented(data: st.DataObject) -> None:
    item = data.draw(transaction_balances())
    divisor = data.draw(everything_except((int, Decimal)))
    result = item.__truediv__(divisor)

    assert result == NotImplemented


@given(data=st.data())
def test_add_transaction_balance(data: st.DataObject) -> None:
    item = data.draw(transaction_balances())
    prev_balance = item.balance
    prev_transactions = item.transactions

    balance = data.draw(cash_amounts(currency=item.balance.currency))
    _transactions = data.draw(st.lists(transactions()))

    item.add_transaction_balance(_transactions, balance)

    assert item.balance == prev_balance + balance
    assert item.transactions == set(prev_transactions.union(_transactions))
