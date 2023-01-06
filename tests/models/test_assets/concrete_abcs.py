from src.models.base_classes.account import Account
from src.models.base_classes.transaction import Transaction
from src.models.model_objects.currency import CashAmount, Currency


class ConcreteTransaction(Transaction):
    def is_account_related(self, account: Account) -> bool:
        return super().is_account_related(account)


class ConcreteAccount(Account):
    @property
    def transactions(self) -> tuple[Transaction, ...]:
        return super().transactions

    def get_balance(self, currency: Currency) -> CashAmount:
        return super().get_balance(currency)
