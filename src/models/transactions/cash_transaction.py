from collections.abc import Collection
from datetime import datetime
from decimal import Decimal

from src.models.accounts.cash_account import CashAccount
from src.models.currency import Currency
from src.models.transactions.attributes.attribute import Attribute
from src.models.transactions.attributes.category import Category
from src.models.transactions.enums import CashTransactionType
from src.models.transactions.transaction import Transaction

# TODO: implement DatetimeEditedMixin
# TODO: test this class

# TODO: figure out split transactions (later)
# TODO: figure out refunds (later)


class CashTransaction(Transaction):
    def __init__(  # noqa: CFQ002, TMN001
        self,
        description: str,
        datetime_: datetime,
        type_: CashTransactionType,
        account: CashAccount,
        amount: Decimal,
        currency: Currency,
        payee: Attribute,
        category: Category,
        tags: Collection[Attribute],
    ) -> None:
        super().__init__(description, datetime_)
        self.type_ = type_
        self.account = account
        self.amount = amount
        self.currency = currency
        self.payee = payee
        self.category = category
        self.tags = tags

    @property
    def type_(self) -> CashTransactionType:
        return self._type

    @type_.setter
    def type_(self, value: CashTransactionType) -> None:
        if not isinstance(value, CashTransactionType):
            raise TypeError("CashTransaction type_ must be a CashTransactionType.")
        self._type = value

    @property
    def account(self) -> CashAccount:
        return self._account

    @account.setter
    def account(self, value: CashAccount) -> None:
        if not isinstance(value, CashAccount):
            raise TypeError("CashTransaction account must be a CashAccount.")
        self._account = value

    @property
    def amount(self) -> Decimal:
        return self._amount

    @amount.setter
    def amount(self, value: Decimal) -> None:
        if not isinstance(value, Decimal):
            raise TypeError("CashTransaction amount must be a Decimal.")
        if not value.is_finite() or value <= 0:
            raise ValueError(
                "CashTransaction amount must be a finite and positive Decimal."
            )
        self._amount = value

    @property
    def currency(self) -> Currency:
        return self._currency

    @currency.setter
    def currency(self, value: Currency) -> None:
        if not isinstance(value, Currency):
            raise TypeError("CashTransaction currency must be a Currency.")
        if self.account.currency != value:
            raise ValueError(
                "CashTransaction currency must match its Account's currency."
            )
        self._currency = value

    @property
    def payee(self) -> Attribute:
        return self._payee

    @payee.setter
    def payee(self, value: Attribute) -> None:
        if not isinstance(value, Attribute):
            raise TypeError("CashTransaction payee must be an Attribute.")
        self._payee = value

    @property
    def category(self) -> Category:
        return self._category

    @category.setter
    def category(self, value: Category) -> None:
        if not isinstance(value, Category):
            raise TypeError("CashTransaction category must be a Category.")
        self._category = value

    @property
    def tags(self) -> tuple[Attribute]:
        return self._tags

    @tags.setter
    def tags(self, values: Collection[Attribute]) -> None:
        if not isinstance(values, Collection) or not all(
            isinstance(value, Attribute) for value in values
        ):
            raise TypeError("CashTransaction tags must be a collection of Attributes.")

        self._tags = tuple(values)
