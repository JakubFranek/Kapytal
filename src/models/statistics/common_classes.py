from collections.abc import Collection
from decimal import Decimal
from typing import Self

from src.models.base_classes.transaction import Transaction
from src.models.model_objects.currency_objects import CashAmount


class TransactionBalance:
    """Class of a CashAmount balance and a set of CashTransactions and
    RefundTransactions related to that balance."""

    def __init__(
        self,
        balance: CashAmount,
        transactions: Collection[Transaction] | None = None,
    ) -> None:
        self.balance = balance
        if transactions is not None:
            self.transactions: set[Transaction] = set(transactions)
        else:
            self.transactions = set()

    def __repr__(self) -> str:
        return (
            f"TransactionBalance({self.balance.to_str_normalized()}, "
            f"len={len(self)})"
        )

    def __len__(self) -> int:
        return len(self.transactions)

    def __add__(self, other: Self) -> Self:
        return TransactionBalance(
            self.balance + other.balance, self.transactions.union(other.transactions)
        )

    def __sub__(self, other: Self) -> Self:
        return TransactionBalance(
            self.balance - other.balance, self.transactions.union(other.transactions)
        )

    def __truediv__(self, __o: object) -> Self:
        if not isinstance(__o, int | Decimal):
            return NotImplemented
        return TransactionBalance(self.balance / __o, self.transactions)

    def add_transaction_balance(
        self,
        transactions: set[Transaction],
        balance: CashAmount,
    ) -> None:
        self.transactions = self.transactions.union(transactions)
        self.balance += balance
