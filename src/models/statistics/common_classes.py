from dataclasses import dataclass, field
from typing import Self

from src.models.model_objects.cash_objects import (
    CashTransaction,
    RefundTransaction,
)
from src.models.model_objects.currency_objects import CashAmount


@dataclass
class TransactionBalance:
    """Dataclass of a CashAmount balance and a set of CashTransactions and
    RefundTransactions related to that balance."""

    balance: CashAmount
    transactions: set[CashTransaction | RefundTransaction] = field(default_factory=set)

    def __add__(self, other: Self) -> Self:
        return TransactionBalance(
            self.balance + other.balance, self.transactions.union(other.transactions)
        )

    def add_transaction_balance(
        self,
        transactions: set[CashTransaction | RefundTransaction],
        balance: CashAmount,
    ) -> None:
        self.transactions = self.transactions.union(transactions)
        self.balance += balance
