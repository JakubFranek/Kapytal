from decimal import Decimal

from src.models.base_classes.account import Account
from src.models.base_classes.transaction import Transaction
from src.models.model_objects.cash_objects import (
    CashAccount,
    CashRelatedTransactionMixin,
)


class ConcreteTransaction(Transaction):
    def is_account_related(self, account: "Account") -> bool:
        return super().is_account_related(account)


class ConcreteAccount(Account):
    @property
    def balance(self) -> Decimal:
        return super().balance

    @property
    def transactions(self) -> tuple["Transaction", ...]:
        return super().transactions


class ConcreteCashRelatedTransactionMixin(CashRelatedTransactionMixin):
    def get_amount_for_account(self, account: CashAccount) -> Decimal:
        return super().get_amount_for_account(account)
