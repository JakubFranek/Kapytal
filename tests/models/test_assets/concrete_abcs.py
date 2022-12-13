from decimal import Decimal

from src.models.base_classes.account import Account
from src.models.base_classes.transaction import Transaction


class ConcreteTransaction(Transaction):
    def get_amount_for_account(self, account: "Account") -> Decimal:
        super().get_amount_for_account(account)

    def is_account_related(self, account: "Account") -> bool:
        super().is_account_related(account)


class ConcreteAccount(Account):
    @property
    def balance(self) -> Decimal:
        return super().balance
