from datetime import datetime
from decimal import Decimal

from src.models.accounts.account import Account
from src.models.constants import tzinfo
from src.models.currency import Currency


class CashAccount(Account):
    def __init__(self, name: str, currency: Currency, initial_balance: Decimal) -> None:
        super().__init__(name)

        if not isinstance(currency, Currency):
            raise TypeError("CashAccount currency must be of type Currency.")

        self._currency = currency
        self.initial_balance = initial_balance
        self.balance = initial_balance

    @property
    def currency(self) -> Currency:
        return self._currency

    @property
    def initial_balance(self) -> Decimal:
        return self._initial_balance

    @initial_balance.setter
    def initial_balance(self, value: Decimal) -> None:
        if not isinstance(value, Decimal):
            raise TypeError("CashAccount initial balance must be a Decimal.")

        if value.is_signed() or not value.is_finite():
            raise ValueError("CashAccount initial balance must be positive and finite.")

        self._initial_balance = value
        self._date_last_edited = datetime.now(tzinfo)

    @property
    def balance(self) -> Decimal:
        return self._balance

    @balance.setter
    def balance(self, value: Decimal) -> None:
        if not isinstance(value, Decimal):
            raise TypeError("CashAccount balance must be a Decimal.")
        if not value.is_finite():
            raise ValueError("CashAccount balance must be finite.")
        self._balance = value
