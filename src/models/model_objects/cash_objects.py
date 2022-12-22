from collections.abc import Collection
from datetime import datetime
from decimal import Decimal
from enum import Enum, auto

from src.models.base_classes.account import Account
from src.models.base_classes.transaction import Transaction
from src.models.constants import tzinfo
from src.models.model_objects.account_group import AccountGroup
from src.models.model_objects.attributes import (
    Attribute,
    AttributeType,
    Category,
    CategoryType,
    InvalidAttributeError,
    InvalidCategoryError,
    InvalidCategoryTypeError,
)
from src.models.model_objects.currency import Currency, CurrencyError


class TransactionPrecedesAccountError(ValueError):
    """Raised when a Transaction.datetime_ precedes the given
    CashAccount.initial_datetime."""


class RefundPrecedesTransactionError(ValueError):
    """Raised when a RefundTransaction.datetime_ precedes the
    refunded transaction datetime_."""


class UnrelatedAccountError(ValueError):
    """Raised when an Account tries to access a Transaction which does
    not relate to it."""


class TransferSameAccountError(ValueError):
    """Raised when an attempt is made to set the recipient and the sender of a
    Transfer to the same Account."""


class InvalidCashTransactionTypeError(ValueError):
    """Raised when the CashTransactionType is incorrect."""


class UnrelatedTransactionError(ValueError):
    """Raised when an unrelated Transaction is supplied."""


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
        parent: AccountGroup | None = None,
    ) -> None:
        super().__init__(name=name, parent=parent)

        if not isinstance(currency, Currency):
            raise TypeError("CashAccount.currency must be a Currency.")
        self._currency = currency

        self.initial_balance = initial_balance
        self.initial_datetime = initial_datetime
        self._balance_history = [(initial_datetime, initial_balance)]

        self._transactions: list[
            "CashTransaction | CashTransfer | RefundTransaction"
        ] = []

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
    def balance_history(self) -> tuple[tuple[datetime, Decimal], ...]:
        return tuple(self._balance_history)

    @property
    def transactions(
        self,
    ) -> tuple["CashTransaction | CashTransfer | RefundTransaction", ...]:
        self._transactions.sort(key=lambda transaction: transaction.datetime_)
        return tuple(self._transactions)

    def __repr__(self) -> str:
        return f"CashAccount('{self.name}', currency='{self.currency.code}')"

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
        self, transaction: "CashTransaction | CashTransfer | RefundTransaction"
    ) -> None:
        if not isinstance(
            transaction, (CashTransaction, CashTransfer, RefundTransaction)
        ):
            raise TypeError(
                "Argument 'transaction' must be a CashTransaction, CashTransfer or"
                " a RefundTransactiono."
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


# TODO: add __repr__ with UUID, categories and amount?
class CashTransaction(Transaction):
    def __init__(  # noqa: CFQ002, TMN001
        self,
        description: str,
        datetime_: datetime,
        type_: CashTransactionType,
        account: CashAccount,
        category_amount_pairs: Collection[tuple[Category, Decimal]],
        payee: Attribute,
        tag_amount_pairs: Collection[tuple[Attribute, Decimal]],
    ) -> None:
        super().__init__(description, datetime_)

        if not isinstance(type_, CashTransactionType):
            raise TypeError("CashTransaction.type_ must be a CashTransactionType.")
        self._type = type_

        self.category_amount_pairs = category_amount_pairs
        self.payee = payee
        self.tag_amount_pairs = tag_amount_pairs
        self.account = account

        self._refunds: list[RefundTransaction] = []

    @property
    def type_(self) -> CashTransactionType:
        return self._type

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
        return Decimal(sum(amount for _, amount in self._category_amount_pairs))

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
            raise ValueError(
                "The type_ of CashTransaction.payee Attribute must be PAYEE."
            )
        self._payee = attribute
        self._datetime_edited = datetime.now(tzinfo)

    @property
    def category_amount_pairs(self) -> tuple[tuple[Category, Decimal], ...]:
        return tuple(self._category_amount_pairs)

    @category_amount_pairs.setter
    def category_amount_pairs(
        self, pairs: Collection[tuple[Category, Decimal]]
    ) -> None:
        validate_collection_of_tuple_pairs(pairs, Category, Decimal, 1)
        if not all(
            category.type_ in self._valid_category_types for category, _ in pairs
        ):
            raise InvalidCategoryTypeError("Invalid Category.type_.")

        if not all(amount.is_finite() and amount > 0 for _, amount in pairs):
            raise ValueError(
                "Second member of CashTransaction.category_amount_pairs"
                " tuples must be a positive and finite Decimal."
            )

        self._category_amount_pairs = tuple(pairs)
        self._datetime_edited = datetime.now(tzinfo)

    @property
    def category_names(self) -> str:
        category_paths = [str(category) for category, _ in self._category_amount_pairs]
        return ", ".join(category_paths)

    @property
    def tag_amount_pairs(self) -> tuple[tuple[Attribute, Decimal], ...]:
        return self._tag_amount_pairs

    # TODO: what happens when self.amount changes and some tag-amounts are now invalid?
    @tag_amount_pairs.setter
    def tag_amount_pairs(self, pairs: Collection[tuple[Attribute, Decimal]]) -> None:
        validate_collection_of_tuple_pairs(pairs, Attribute, Decimal, 0)
        if not all(attribute.type_ == AttributeType.TAG for attribute, _ in pairs):
            raise ValueError(
                "The type_ of CashTransaction.tag_amount_pairs Attributes must be TAG."
            )
        if not all(
            amount.is_finite() and amount > 0 and amount <= self.amount
            for _, amount in pairs
        ):
            raise ValueError(
                "Second member of CashTransaction.tag_amount_pairs"
                " tuples must be a positive and finite Decimal which"
                " does not exceed CashTransaction.amount."
            )

        self._tag_amount_pairs = tuple(pairs)
        self._datetime_edited = datetime.now(tzinfo)

    @property
    def tag_names(self) -> str:
        tag_names = [tag.name for tag, _ in self._tag_amount_pairs]
        return ", ".join(tag_names)

    @property
    def _valid_category_types(self) -> tuple[CategoryType, ...]:
        if self.type_ == CashTransactionType.INCOME:
            return (CategoryType.INCOME, CategoryType.INCOME_AND_EXPENSE)
        return (CategoryType.EXPENSE, CategoryType.INCOME_AND_EXPENSE)

    @property
    def refunds(self) -> tuple["RefundTransaction", ...]:
        return tuple(self._refunds)

    def add_refund(self, refund: "RefundTransaction") -> None:
        self._validate_refund(refund)

        self._refunds.append(refund)
        self._datetime_edited = datetime.now(tzinfo)

    def remove_refund(self, refund: "RefundTransaction") -> None:
        self._validate_refund(refund)

        self._refunds.remove(refund)
        self._datetime_edited = datetime.now(tzinfo)

    def get_amount_for_account(self, account: Account) -> Decimal:
        if not self.is_account_related(account):
            raise UnrelatedAccountError(
                'Argument "account" is not related to this CashTransaction.'
            )
        if self.type_ == CashTransactionType.INCOME:
            return self.amount
        return -self.amount

    def is_account_related(self, account: Account) -> bool:
        return self.account == account

    def _validate_refund(self, refund: "RefundTransaction") -> None:
        if not isinstance(refund, RefundTransaction):
            raise TypeError("Argument 'refund' must be a RefundTransaction.")
        if refund.refunded_transaction != self:
            raise UnrelatedTransactionError(
                "Supplied RefundTransaction is not related to this CashTransaction."
            )


# TODO: add __repr__
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

    def get_amount_for_account(self, account: Account) -> Decimal:
        if self.account_recipient == account:
            return self.amount_received
        if self.account_sender == account:
            return -self.amount_sent
        raise UnrelatedAccountError(
            'Argument "account" is not related to this CashTransfer.'
        )

    def is_account_related(self, account: Account) -> bool:
        return self.account_sender == account or self.account_recipient == account


# TODO: add __repr__
class RefundTransaction(Transaction):
    """A refund which attaches itself to an expense CashTransaction.
    Instances of this class are immutable."""

    def __init__(
        self,
        description: str,
        datetime_: datetime,
        account: CashAccount,
        refunded_transaction: CashTransaction,
        category_amount_pairs: Collection[tuple[Category, Decimal]],
        tag_amount_pairs: Collection[tuple[Attribute, Decimal]],
    ) -> None:
        if not isinstance(refunded_transaction, CashTransaction):
            raise TypeError("Refunded transaction must be a CashTransaction.")
        if refunded_transaction.type_ != CashTransactionType.EXPENSE:
            raise InvalidCashTransactionTypeError(
                "Only expense CashTransactions can be refunded."
            )
        self._refunded_transaction = refunded_transaction
        self._refunded_transaction.add_refund(self)

        super().__init__(description, datetime_)

        self._set_category_amount_pairs(category_amount_pairs)
        self._set_tag_amount_pairs(tag_amount_pairs)

        self._set_account(account)

    @Transaction.datetime_.setter
    def datetime_(self, value: datetime) -> None:
        Transaction.datetime_.fset(self, value)
        if self.datetime_ < self._refunded_transaction.datetime_:
            raise RefundPrecedesTransactionError(
                "Supplied RefundTransaction.datetime_ precedes this"
                " CashTransaction.datetime_."
            )

    @property
    def account(self) -> CashAccount:
        return self._account

    @property
    def amount(self) -> Decimal:
        return Decimal(sum(amount for _, amount in self.category_amount_pairs))

    @property
    def currency(self) -> Currency:
        return self._currency

    @property
    def refunded_transaction(self) -> CashTransaction:
        return self._refunded_transaction

    @property
    def category_amount_pairs(self) -> tuple[tuple[Category, Decimal], ...]:
        return tuple(self._category_amount_pairs)

    @property
    def category_names(self) -> str:
        category_paths = [str(category) for category, _ in self._category_amount_pairs]
        return ", ".join(category_paths)

    @property
    def tag_amount_pairs(self) -> tuple[tuple[Attribute, Decimal], ...]:
        return self._tag_amount_pairs

    def _set_account(self, account: CashAccount) -> None:
        if not isinstance(account, CashAccount):
            raise TypeError("RefundTransaction.account must be a CashAccount.")
        if account.currency != self.refunded_transaction.currency:
            raise CurrencyError(
                "Currencies of the refunded CashTransaction and the refunded"
                " CashAccount must match."
            )

        self._account = account
        self._currency = account.currency

        self._account.add_transaction(self)

        self._datetime_edited = datetime.now(tzinfo)

    def _set_category_amount_pairs(
        self, pairs: Collection[tuple[Category, Decimal]]
    ) -> None:
        no_of_categories = len(self.refunded_transaction.category_amount_pairs)
        validate_collection_of_tuple_pairs(pairs, Category, Decimal, no_of_categories)
        valid_categories = [
            category for category, _ in self.refunded_transaction.category_amount_pairs
        ]
        if not all(category in valid_categories for category, _ in pairs):
            raise InvalidCategoryError(
                "Only categories present in the refunded CashTransaction are accepted."
            )
        if not all(amount.is_finite() and amount >= 0 for _, amount in pairs):
            raise ValueError(
                "Second member of RefundTransaction.category_amount_pairs"
                " tuples must be a finite non-negative Decimal."
            )
        refund_amount = sum(amount for _, amount in pairs)
        if not refund_amount > 0:
            raise ValueError("Total refunded amount must be positive.")

        max_values = {}
        for category, amount in self.refunded_transaction.category_amount_pairs:
            max_values[category] = amount
        other_refunds = [
            refund for refund in self.refunded_transaction.refunds if refund != self
        ]
        for other_refund in other_refunds:
            for category, amount in other_refund.category_amount_pairs:
                max_values[category] -= amount
        for category, amount in pairs:
            if amount > max_values[category]:
                raise ValueError(
                    f"Refunded amount for category '{str(category)}' must not exceed"
                    f" {max_values[category]}."
                )

        self._category_amount_pairs = tuple(pairs)
        self._datetime_edited = datetime.now(tzinfo)

    def _set_tag_amount_pairs(
        self, pairs: Collection[tuple[Attribute, Decimal]]
    ) -> None:
        expected_tags = {tag for tag, _ in self.refunded_transaction.tag_amount_pairs}
        no_of_tags = len(expected_tags)
        validate_collection_of_tuple_pairs(pairs, Attribute, Decimal, no_of_tags)

        if not all(attribute.type_ == AttributeType.TAG for attribute, _ in pairs):
            raise InvalidAttributeError(
                "The type_ of RefundTransaction.tag_amount_pairs Attributes must"
                " be TAG."
            )
        delivered_tags = {tag for tag, _ in pairs}
        if delivered_tags != expected_tags:
            raise InvalidAttributeError("Delivered tags do not match expected tags.")
        if not all(amount.is_finite() and amount >= 0 for _, amount in pairs):
            raise ValueError(
                "Second member of RefundTransaction.tag_amount_pairs"
                " tuples must be a finite non-negative Decimal."
            )

        max_values: dict[Attribute, Decimal] = {}
        min_values: dict[Attribute, Decimal] = {}
        for tag, amount in self.refunded_transaction.tag_amount_pairs:
            max_values[tag] = self.refunded_transaction.amount
            min_values[tag] = amount
        other_refunds = [
            refund for refund in self.refunded_transaction.refunds if refund != self
        ]
        remaining_amount = self.refunded_transaction.amount - sum(
            refund.amount for refund in other_refunds
        )
        for other_refund in other_refunds:
            for tag, amount in other_refund.tag_amount_pairs:
                max_values[tag] -= amount
                min_values[tag] -= amount

        for tag, amount in pairs:
            min_expected = min_values[tag] - (remaining_amount - self.amount)
            min_values[tag] = max(min_expected, 0)
            if amount > max_values[tag] or amount < min_values[tag]:
                raise ValueError(
                    f"Refunded amount for tag '{tag.name}' must be within"
                    f" {min_values[tag]} and {max_values[tag]}."
                )

        self._tag_amount_pairs = tuple(pairs)
        self._datetime_edited = datetime.now(tzinfo)

    def get_amount_for_account(self, account: Account) -> Decimal:
        if not self.is_account_related(account):
            raise UnrelatedAccountError(
                'Argument "account" is not related to this RefundTransaction.'
            )
        return self.amount

    def is_account_related(self, account: "Account") -> bool:
        return self.account == account


def validate_collection_of_tuple_pairs(
    collection: Collection, first_type: type, second_type: type, min_length: int
) -> None:
    if not isinstance(collection, Collection):
        raise TypeError("Argument 'collection' must be a Collection.")
    if len(collection) < min_length:
        raise ValueError(f"Length of 'collection' must be at least {min_length}.")
    if not all(isinstance(element, tuple) for element in collection):
        raise TypeError("Elements of 'collection' must be tuples.")
    if not all(isinstance(first_member, first_type) for first_member, _ in collection):
        raise TypeError(
            f"First element of 'collection' tuples must be of type {first_type}."
        )
    if not all(
        isinstance(second_member, second_type) for _, second_member in collection
    ):
        raise TypeError(
            f"Second element of 'collection' tuples must be of type {first_type}."
        )
