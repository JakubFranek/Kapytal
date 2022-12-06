from collections.abc import Collection
from datetime import datetime
from decimal import Decimal

from src.models.accounts.cash_account import CashAccount
from src.models.constants import tzinfo
from src.models.currencies.currency import Currency
from src.models.transactions.attributes.attribute import Attribute
from src.models.transactions.attributes.category import Category
from src.models.transactions.enums import CashTransactionType
from src.models.transactions.transaction import Transaction

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
        payee: Attribute,
        category: Category,
        tags: Collection[Attribute],
    ) -> None:
        super().__init__(description, datetime_)
        self.type_ = type_
        self.account = account
        self.amount = amount
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
        self._datetime_edited = datetime.now(tzinfo)

    @property
    def account(self) -> CashAccount:
        return self._account

    @account.setter
    def account(self, value: CashAccount) -> None:
        if not isinstance(value, CashAccount):
            raise TypeError("CashTransaction account must be a CashAccount.")
        self._account = value
        self._currency = value.currency
        self._datetime_edited = datetime.now(tzinfo)

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
        self._datetime_edited = datetime.now(tzinfo)

    @property
    def currency(self) -> Currency:
        return self._currency

    @property
    def payee(self) -> Attribute:
        return self._payee

    @payee.setter
    def payee(self, value: Attribute) -> None:
        if not isinstance(value, Attribute):
            raise TypeError("CashTransaction payee must be an Attribute.")
        self._payee = value
        self._datetime_edited = datetime.now(tzinfo)

    @property
    def category(self) -> Category:
        return self._category

    @category.setter
    def category(self, value: Category) -> None:
        if not isinstance(value, Category):
            raise TypeError("CashTransaction category must be a Category.")
        self._category = value
        self._datetime_edited = datetime.now(tzinfo)

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
        self._datetime_edited = datetime.now(tzinfo)
