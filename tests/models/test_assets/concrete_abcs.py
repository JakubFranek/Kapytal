from decimal import Decimal

from src.models.base_classes.account import Account
from src.models.base_classes.transaction import Transaction
from src.models.model_objects.cash_objects import CashAccount, CashRelatedTransaction
from src.models.model_objects.security_objects import (
    SecurityAccount,
    SecurityRelatedTransaction,
)


class ConcreteTransaction(Transaction):
    def is_account_related(self, account: Account) -> bool:
        return super().is_account_related(account)


class ConcreteAccount(Account):
    @property
    def balance(self) -> Decimal:
        return super().balance

    @property
    def transactions(self) -> tuple[Transaction, ...]:
        return super().transactions


class ConcreteCashRelatedTransaction(CashRelatedTransaction):
    def _get_amount(self, account: CashAccount) -> Decimal:
        return super()._get_amount(account)

    def is_account_related(self, account: Account) -> bool:
        return super().is_account_related(account)


class ConcreteSecurityRelatedTransaction(SecurityRelatedTransaction):
    def _get_shares(self, account: SecurityAccount) -> int:
        return super()._get_shares(account)

    def is_account_related(self, account: Account) -> bool:
        return super().is_account_related(account)
