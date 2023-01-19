from datetime import datetime
from typing import Any, Self

from src.models.base_classes.account import Account
from src.models.base_classes.transaction import Transaction
from src.models.model_objects.currency import CashAmount, Currency


class ConcreteTransaction(Transaction):
    def __init__(self, description: str, datetime_: datetime) -> None:
        super().__init__()
        self.set_attributes(description=description, datetime_=datetime_)

    def is_account_related(self, account: Account) -> bool:
        return super().is_account_related(account)

    def prepare_for_deletion(self) -> None:
        return super().prepare_for_deletion()

    def to_dict(self) -> dict[str, Any]:
        return super().to_dict()

    @staticmethod
    def from_dict(data: dict[str, Any]) -> "ConcreteTransaction":
        return super().from_dict(data)


class ConcreteAccount(Account):
    @property
    def transactions(self) -> tuple[Transaction, ...]:
        return super().transactions

    def get_balance(self, currency: Currency) -> CashAmount:
        return super().get_balance(currency)

    def to_dict(self) -> dict[str, Any]:
        return super().to_dict()

    @staticmethod
    def from_dict(data: dict[str, Any]) -> Self:
        return super().from_dict(data)
