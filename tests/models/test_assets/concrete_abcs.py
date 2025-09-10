from collections.abc import Collection
from datetime import date, datetime
from typing import Any, Self

from src.models.base_classes.account import Account
from src.models.base_classes.transaction import Transaction
from src.models.model_objects.currency_objects import CashAmount, Currency


class ConcreteTransaction(Transaction):
    def __init__(self, description: str, datetime_: datetime) -> None:
        super().__init__()
        self.set_attributes(description=description, datetime_=datetime_)

    def is_account_related(self, account: Account) -> bool:
        return super().is_account_related(account)

    def is_accounts_related(self, accounts: Collection[Account]) -> bool:
        return super().is_account_related(accounts)

    def prepare_for_deletion(self) -> None:
        return super().prepare_for_deletion()

    def serialize(self) -> dict[str, Any]:
        return super().serialize()

    @staticmethod
    def deserialize(data: dict[str, Any]) -> "ConcreteTransaction":
        return Transaction().deserialize(data)


class ConcreteAccount(Account):
    @property
    def transactions(self) -> tuple[Transaction, ...]:
        return super().transactions

    @property
    def currency(self) -> Currency | None:
        return super().currency

    def get_balance(self, currency: Currency, date_: date | None = None) -> CashAmount:
        return super().get_balance(currency, date_)

    def serialize(self) -> dict[str, Any]:
        return super().serialize()

    @staticmethod
    def deserialize(data: dict[str, Any]) -> "ConcreteAccount":
        return Account().deserialize(data)
