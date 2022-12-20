from collections.abc import Collection
from datetime import datetime
from decimal import Decimal
from enum import Enum, auto

from src.models.base_classes.account import Account
from src.models.base_classes.transaction import Transaction
from src.models.constants import tzinfo
from src.models.model_objects.attributes import (
    Attribute,
    AttributeType,
    Category,
    CategoryType,
)
from src.models.model_objects.currency import Currency


class TransactionPrecedesAccountError(ValueError):
    """Raised when a Transaction.datetime_ precedes the given
    CashAccount.initial_datetime."""


class UnrelatedAccountError(ValueError):
    """Raised when an Account tries to access a Transaction which does
    not relate to it."""


class TransferSameAccountError(ValueError):
    """Raised when an attempt is made to set the recipient and the sender of a
    Transfer to the same Account."""


class InvalidCategoryTypeError(ValueError):
    """Raised when Category.type_ is incompatible with given CashTransaction.type_."""


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
                "Argument 'transaction' must be a CashTransaction or a CashTransfer."
            )
        if not transaction.is_account_related(self):
            raise UnrelatedAccountError(
                "This CashAccount is not related to the provided Transaction."
            )
        if transaction.datetime_ < self.initial_datetime:
            raise TransactionPrecedesAccountError(
                (
                    "The provided Transaction precedes this"
                    " CashAccount.initial_datetime."
                )
            )
        return


# TODO: make tags also accept tuples of tag and amount


class CashTransaction(Transaction):
    def __init__(  # noqa: CFQ002, TMN001
        self,
        description: str,
        datetime_: datetime,
        type_: CashTransactionType,
        account: CashAccount,
        category_amount_pairs: Collection[tuple[Category, Decimal]],
        payee: Attribute,
        tags: Collection[Attribute],
    ) -> None:
        super().__init__(description, datetime_)
        self.type_ = type_
        self.category_amount_pairs = category_amount_pairs
        self.payee = payee
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
        return sum(pair[1] for pair in self.category_amount_pairs)

    @property
    def currency(self) -> Currency:
        return self._currency

    @property
    def payee(self) -> Attribute:
        return self._payee

    @payee.setter
    def payee(self, attribute: Attribute) -> None:
        if not isinstance(attribute, Attribute):
            raise TypeError("CashTransaction.payee must be an Attribute.")
        if not attribute.type_ == AttributeType.PAYEE:
            raise ValueError("CashTransaction.payee Attribute must be type_ PAYEE.")
        self._payee = attribute
        self._datetime_edited = datetime.now(tzinfo)

    @property
    def category_amount_pairs(self) -> tuple[tuple[Category, Decimal]]:
        return tuple(self._category_amount_pairs)

    @category_amount_pairs.setter
    def category_amount_pairs(
        self, pairs: Collection[tuple[Category, Decimal]]
    ) -> None:
        if not isinstance(pairs, Collection):
            raise TypeError(
                "CashTransaction.category_amount_pairs must be a Collection."
            )
        if len(pairs) == 0:
            raise ValueError(
                "Length of CashTransaction.category_amount_pairs must be at least 1."
            )
        if not all(isinstance(tup[0], Category) for tup in pairs):
            raise TypeError(
                "First member of CashTransaction.category_amount_pairs"
                " tuples must be a Category."
            )
        if not all(tup[0].type_ in self._valid_category_types for tup in pairs):
            raise InvalidCategoryTypeError("Invalid Category.type_.")
        if not all(isinstance(tup[1], Decimal) for tup in pairs):
            raise TypeError(
                "Second member of CashTransaction.category_amount_pairs"
                " tuples must be a Decimal."
            )
        if not all(tup[1].is_finite() and tup[1] > 0 for tup in pairs):
            raise ValueError(
                "Second member of CashTransaction.category_amount_pairs"
                " tuples must be a positive and finite Decimal."
            )

        self._category_amount_pairs = tuple(pairs)
        self._datetime_edited = datetime.now(tzinfo)

    @property
    def category_names(self) -> str:
        categories = [str(tup[0]) for tup in self._category_amount_pairs]
        return ", ".join(categories)

    @property
    def tags(self) -> tuple[Attribute]:
        return self._tags

    @tags.setter
    def tags(self, attributes: Collection[Attribute]) -> None:
        if not isinstance(attributes, Collection) or not all(
            isinstance(attribute, Attribute) for attribute in attributes
        ):
            raise TypeError("CashTransaction.tags must be a collection of Attributes.")
        if not all(attribute.type_ == AttributeType.TAG for attribute in attributes):
            raise ValueError("CashTransaction.tags Attributes must be type_ TAG.")

        self._tags = tuple(attributes)
        self._datetime_edited = datetime.now(tzinfo)

    @property
    def _valid_category_types(self) -> tuple[CategoryType]:
        if self.type_ == CashTransactionType.INCOME:
            return (CategoryType.INCOME, CategoryType.INCOME_AND_EXPENSE)
        return (CategoryType.EXPENSE, CategoryType.INCOME_AND_EXPENSE)

    def get_amount_for_account(self, account: Account) -> Decimal:
        if not self.is_account_related(account):
            raise UnrelatedAccountError(
                'Argument "account" is not related to this CashTransaction.'
            )
        if self.type_ == CashTransactionType.INCOME:
            return self.amount
        return -self.amount

    def is_account_related(self, account: Account) -> None:
        return self.account == account


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
        self.amount_sent = amount_sent
        self.amount_received = amount_received
        self.set_accounts(account_sender, account_recipient)

    @property
    def account_sender(self) -> CashAccount:
        return self._account_sender

    @property
    def account_recipient(self) -> CashAccount:
        return self._account_recipient

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

    def set_accounts(
        self, account_sender: CashAccount, account_recipient: CashAccount
    ) -> None:
        if not isinstance(account_sender, CashAccount):
            raise TypeError("Argument 'account_sender' must be a CashAccount.")
        if not isinstance(account_recipient, CashAccount):
            raise TypeError("Argument 'account_recipient' must be a CashAccount.")
        if account_recipient == account_sender:
            raise TransferSameAccountError(
                "Arguments 'account_sender' and 'account_recipient' must be"
                " different CashAccounts."
            )

        # Remove self from "old" accounts
        if hasattr(self, "_account_recipient"):
            self._account_recipient.remove_transaction(self)
        if hasattr(self, "_account_sender"):
            self._account_sender.remove_transaction(self)

        self._account_recipient = account_recipient
        self._account_sender = account_sender

        # Add self to "new" accounts
        self._account_recipient.add_transaction(self)
        self._account_sender.add_transaction(self)

        self._datetime_edited = datetime.now(tzinfo)

    def get_amount_for_account(self, account: CashAccount) -> Decimal:
        if self.account_recipient == account:
            return self.amount_received
        if self.account_sender == account:
            return -self.amount_sent
        raise UnrelatedAccountError(
            'Argument "account" is not related to this CashTransfer.'
        )

    def is_account_related(self, account: CashAccount) -> bool:
        return self.account_sender == account or self.account_recipient == account
