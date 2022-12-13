from collections.abc import Collection
from datetime import datetime
from decimal import Decimal
from enum import Enum, auto

from src.models.base_classes.account import Account
from src.models.base_classes.transaction import Transaction
from src.models.constants import tzinfo
from src.models.model_objects.attributes import Attribute, Category
from src.models.model_objects.currency import Currency

# TODO: custom exceptions for unrelated account, transaction too early etc.


class CashTransactionType(Enum):
    INCOME = auto()
    EXPENSE = auto()


class CashAccount(Account):
    def __init__(
        self,
        name: str,
        currency: Currency,
        initial_balance: Decimal,
        initial_datetime: datetime,
    ) -> None:
        super().__init__(name)

        if not isinstance(currency, Currency):
            raise TypeError("CashAccount.currency must be a Currency.")
        self._currency = currency

        self.initial_balance = initial_balance
        self.initial_datetime = initial_datetime
        self._balance_history = [(initial_datetime, initial_balance)]

        self._transactions: list["CashTransaction|CashTransfer"] = []

    @property
    def currency(self) -> Currency:
        return self._currency

    @property
    def initial_balance(self) -> Decimal:
        return self._initial_balance

    @initial_balance.setter
    def initial_balance(self, value: Decimal) -> None:
        if not isinstance(value, Decimal):
            raise TypeError("CashAccount.initial_balance must be a Decimal.")

        if value.is_signed() or not value.is_finite():
            raise ValueError("CashAccount.initial_balance must be positive and finite.")

        self._initial_balance = value
        self._date_last_edited = datetime.now(tzinfo)

    @property
    def initial_datetime(self) -> datetime:
        return self._initial_datetime

    @initial_datetime.setter
    def initial_datetime(self, value: datetime) -> None:
        if not isinstance(value, datetime):
            raise TypeError("CashAccount.initial_datetime must be a datetime.")

        self._initial_datetime = value
        self._date_last_edited = datetime.now(tzinfo)

    @property
    def balance(self) -> Decimal:
        return self._balance_history[-1][1]

    @property
    def balance_history(self) -> tuple[tuple[datetime, Decimal]]:
        return tuple(self._balance_history)

    @property
    def transactions(self) -> tuple["CashTransaction | CashTransfer"]:
        self._transactions.sort(key=lambda transaction: transaction.datetime_)
        return tuple(self._transactions)

    def add_transaction(self, transaction: "CashTransaction | CashTransfer") -> None:
        self._validate_transaction(transaction)
        self._transactions.append(transaction)
        self._update_balance()

    def remove_transaction(self, transaction: "CashTransaction | CashTransfer") -> None:
        self._validate_transaction(transaction)
        self._transactions.remove(transaction)
        self._update_balance()

    def _update_balance(self) -> None:
        datetime_balance_history = [(self.initial_datetime, self.initial_balance)]
        for transaction in self.transactions:
            last_balance = datetime_balance_history[-1][1]
            next_balance = last_balance + transaction.get_amount_for_account(self)
            datetime_balance_history.append((transaction.datetime_, next_balance))
        self._balance_history = datetime_balance_history

    def _validate_transaction(
        self, transaction: "CashTransaction | CashTransfer"
    ) -> None:
        if not isinstance(transaction, (CashTransaction, CashTransfer)):
            raise TypeError(
                "Argument transaction must be a CashTransaction or a CashTransfer."
            )
        if not transaction.is_account_related(self):
            raise ValueError(
                "This CashAccount is not related to the provided Transaction."
            )
        if transaction.datetime_ < self.initial_datetime:
            raise ValueError(
                (
                    "The provided Transaction precedes this"
                    " CashAccount.initial_datetime."
                )
            )
        return


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
        self.amount = amount
        self.payee = payee
        self.category = category
        self.tags = tags
        self.account = account

    @property
    def type_(self) -> CashTransactionType:
        return self._type

    @type_.setter
    def type_(self, value: CashTransactionType) -> None:
        if not isinstance(value, CashTransactionType):
            raise TypeError("CashTransaction.type_ must be a CashTransactionType.")
        self._type = value
        self._datetime_edited = datetime.now(tzinfo)

    @property
    def account(self) -> CashAccount:
        return self._account

    @account.setter
    def account(self, new_account: CashAccount) -> None:
        if not isinstance(new_account, CashAccount):
            raise TypeError("CashTransaction.account must be a CashAccount.")

        if hasattr(self, "_account"):
            self._account.remove_transaction(self)

        self._account = new_account
        self._currency = new_account.currency

        self._account.add_transaction(self)

        self._datetime_edited = datetime.now(tzinfo)

    @property
    def amount(self) -> Decimal:
        return self._amount

    @amount.setter
    def amount(self, value: Decimal) -> None:
        if not isinstance(value, Decimal):
            raise TypeError("CashTransaction.amount must be a Decimal.")
        if not value.is_finite() or value <= 0:
            raise ValueError(
                "CashTransaction.amount must be a finite and positive Decimal."
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
            raise TypeError("CashTransaction.payee must be an Attribute.")
        self._payee = value
        self._datetime_edited = datetime.now(tzinfo)

    @property
    def category(self) -> Category:
        return self._category

    @category.setter
    def category(self, value: Category) -> None:
        if not isinstance(value, Category):
            raise TypeError("CashTransaction.category must be a Category.")
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
            raise TypeError("CashTransaction.tags must be a collection of Attributes.")

        self._tags = tuple(values)
        self._datetime_edited = datetime.now(tzinfo)

    def get_amount_for_account(self, account: Account) -> Decimal:
        if not self.is_account_related(account):
            raise ValueError(
                'The argument "account" is not related to this CashTransaction.'
            )
        if self.type_ == CashTransactionType.INCOME:
            return self.amount
        return -self.amount

    def is_account_related(self, account: Account) -> None:
        if self.account == account:
            return True
        return False


# TODO: disallow account_sender and account_recipient to be the same
class CashTransfer(Transaction):
    def __init__(  # noqa: TMN001, CFQ002
        self,
        description: str,
        datetime_: datetime,
        account_sender: CashAccount,
        account_recipient: CashAccount,
        amount_sent: Decimal,
        amount_received: Decimal,
    ) -> None:
        super().__init__(description, datetime_)
        self._is_initialized = False
        self.amount_sent = amount_sent
        self.amount_received = amount_received
        self.account_sender = account_sender
        self.account_recipient = account_recipient
        self.account_sender.add_transaction(self)
        self.account_recipient.add_transaction(self)
        self._is_initialized = True

    @property
    def account_sender(self) -> CashAccount:
        return self._account_sender

    @account_sender.setter
    def account_sender(self, new_sender: CashAccount) -> None:
        if not isinstance(new_sender, CashAccount):
            raise TypeError("CashTransfer.account_sender must be a CashAccount.")

        if hasattr(self, "_account_sender"):
            self._account_sender.remove_transaction(self)

        self._account_sender = new_sender
        if self._is_initialized:
            self._account_sender.add_transaction(self)

        self._datetime_edited = datetime.now(tzinfo)

    @property
    def account_recipient(self) -> CashAccount:
        return self._account_recipient

    @account_recipient.setter
    def account_recipient(self, new_recipient: CashAccount) -> None:
        if not isinstance(new_recipient, CashAccount):
            raise TypeError("CashTransfer.account_recipient must be a CashAccount.")

        if hasattr(self, "_account_recipient"):
            self._account_recipient.remove_transaction(self)

        self._account_recipient = new_recipient
        if self._is_initialized:
            self._account_recipient.add_transaction(self)

        self._datetime_edited = datetime.now(tzinfo)

    @property
    def amount_sent(self) -> Decimal:
        return self._amount_sent

    @amount_sent.setter
    def amount_sent(self, value: Decimal) -> None:
        if not isinstance(value, Decimal):
            raise TypeError("CashTransfer.amount_sent must be a Decimal.")
        if not value.is_finite() or value <= 0:
            raise ValueError(
                "CashTransfer.amount_sent must be a finite and positive Decimal."
            )
        self._amount_sent = value
        self._datetime_edited = datetime.now(tzinfo)

    @property
    def amount_received(self) -> Decimal:
        return self._amount_received

    @amount_received.setter
    def amount_received(self, value: Decimal) -> None:
        if not isinstance(value, Decimal):
            raise TypeError("CashTransfer.amount_received must be a Decimal.")
        if not value.is_finite() or value <= 0:
            raise ValueError(
                "CashTransfer.amount_received must be a finite and positive Decimal."
            )
        self._amount_received = value
        self._datetime_edited = datetime.now(tzinfo)

    def get_amount_for_account(self, account: Account) -> Decimal:
        if self.account_recipient == account:
            return self.amount_received
        if self.account_sender == account:
            return -self.amount_sent
        raise ValueError('The argument "account" is not related to this CashTransfer.')

    def is_account_related(self, account: Account) -> None:
        if self.account_sender == account or self.account_recipient == account:
            return True
        return False
