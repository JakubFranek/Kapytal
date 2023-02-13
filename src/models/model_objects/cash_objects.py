import logging
import operator
import uuid
from abc import ABC, abstractmethod
from collections.abc import Collection
from datetime import datetime, timedelta
from enum import Enum, auto
from typing import Any

from src.models.base_classes.account import Account, UnrelatedAccountError
from src.models.base_classes.transaction import Transaction
from src.models.constants import tzinfo
from src.models.custom_exceptions import (
    AlreadyExistsError,
    InvalidOperationError,
    TransferSameAccountError,
)
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
from src.models.model_objects.currency_objects import (
    CashAmount,
    Currency,
    CurrencyError,
)
from src.models.utilities.find_helpers import (
    find_account_by_uuid,
    find_account_group_by_path,
    find_attribute_by_name,
    find_category_by_path,
    find_currency_by_code,
    find_transaction_by_uuid,
)


class UnrelatedTransactionError(ValueError):
    """Raised when an unrelated Transaction is supplied."""


class TransactionPrecedesAccountError(ValueError):
    """Raised when a Transaction.datetime_ precedes the given
    CashAccount.initial_datetime."""


class RefundPrecedesTransactionError(ValueError):
    """Raised when a RefundTransaction.datetime_ precedes the
    refunded transaction datetime_."""


class InvalidCashTransactionTypeError(ValueError):
    """Raised when the CashTransactionType is incorrect."""


class CashRelatedTransaction(Transaction, ABC):
    def get_amount(self, account: "CashAccount") -> CashAmount:
        if not isinstance(account, CashAccount):
            raise TypeError("Parameter 'account' must be a CashAccount.")
        if not self.is_account_related(account):
            raise UnrelatedAccountError(
                f"CashAccount '{account.name}' is not related to this "
                f"{self.__class__.__name__}."
            )
        return self._get_amount(account)

    @abstractmethod
    def _get_amount(self, account: "CashAccount") -> CashAmount:
        raise NotImplementedError

    @property
    @abstractmethod
    def currencies(self) -> tuple[Currency]:
        raise NotImplementedError


class CashTransactionType(Enum):
    INCOME = auto()
    EXPENSE = auto()


class CashAccount(Account):
    def __init__(
        self,
        name: str,
        currency: Currency,
        initial_balance: CashAmount,
        parent: AccountGroup | None = None,
    ) -> None:
        super().__init__(name=name, parent=parent)

        if not isinstance(currency, Currency):
            raise TypeError("CashAccount.currency must be a Currency.")
        self._currency = currency

        self._balance_history = [(datetime.now(tzinfo), initial_balance)]
        self._transactions: list[CashRelatedTransaction] = []

        self.initial_balance = initial_balance

    @property
    def currency(self) -> Currency:
        return self._currency

    @property
    def initial_balance(self) -> CashAmount:
        return self._initial_balance

    @initial_balance.setter
    def initial_balance(self, amount: CashAmount) -> None:
        if not isinstance(amount, CashAmount):
            raise TypeError("CashAccount.initial_balance must be a CashAmount.")
        if hasattr(self, "_initial_balance") and self._initial_balance == amount:
            return
        if self.currency != amount.currency:
            raise CurrencyError(
                "CashAccount.initial_balance.currency must match CashAccount.currency."
            )
        logging.info(f"Setting initial_balance={amount}")
        self._initial_balance = amount
        self._update_balance()

    @property
    def balance_history(self) -> tuple[tuple[datetime, CashAmount], ...]:
        return tuple(self._balance_history)

    @property
    def transactions(
        self,
    ) -> tuple[CashRelatedTransaction, ...]:
        self._transactions.sort(key=lambda transaction: transaction.datetime_)
        return tuple(self._transactions)

    def __repr__(self) -> str:
        return f"CashAccount(path='{self.path}', currency='{self.currency.code}')"

    def get_balance(self, currency: Currency) -> CashAmount:
        return self._balance_history[-1][1].convert(currency)

    def add_transaction(self, transaction: CashRelatedTransaction) -> None:
        self._validate_transaction(transaction)
        if transaction in self._transactions:
            raise AlreadyExistsError(
                "Provided CashRelatedTransaction is already within this "
                "CashAccount.transactions."
            )
        self._transactions.append(transaction)
        self._update_balance()

    def remove_transaction(self, transaction: CashRelatedTransaction) -> None:
        self._validate_transaction(transaction)
        self._transactions.remove(transaction)
        self._update_balance()

    def serialize(self) -> dict[str, Any]:
        index = self.parent.children.index(self) if self.parent is not None else None
        return {
            "datatype": "CashAccount",
            "path": self.path,
            "index": index,
            "currency_code": self._currency.code,
            "initial_balance": str(self._initial_balance.value_rounded),
            "uuid": str(self._uuid),
        }

    @staticmethod
    def deserialize(
        data: dict[str, Any],
        account_groups: Collection[AccountGroup],
        currencies: Collection[Currency],
    ) -> "CashAccount":
        path: str = data["path"]
        index: int | None = data["index"]
        parent_path, _, name = path.rpartition("/")
        initial_balance_value = data["initial_balance"]

        currency_code = data["currency_code"]
        currency = find_currency_by_code(currency_code, currencies)

        initial_balance = CashAmount(initial_balance_value, currency)

        obj = CashAccount(name, currency, initial_balance)
        obj._uuid = uuid.UUID(data["uuid"])

        if parent_path != "":
            obj._parent = find_account_group_by_path(parent_path, account_groups)
            obj._parent._children[index] = obj
        return obj

    def _update_balance(self) -> None:
        logging.debug(f"Updating balance of CashAccount at path='{self.path}'")
        if len(self.transactions) > 0:
            oldest_datetime = min(
                transaction.datetime_ for transaction in self.transactions
            )
        else:
            oldest_datetime = self.balance_history[0][0] + timedelta(days=1)
        datetime_balance_history = [
            (oldest_datetime - timedelta(days=1), self.initial_balance)
        ]
        for transaction in self.transactions:
            last_balance = datetime_balance_history[-1][1]
            next_balance = last_balance + transaction.get_amount(self)
            datetime_balance_history.append((transaction.datetime_, next_balance))
        self._balance_history = datetime_balance_history

    def _validate_transaction(
        self,
        transaction: CashRelatedTransaction,
    ) -> None:
        if not isinstance(transaction, CashRelatedTransaction):
            raise TypeError(
                "Parameter 'transaction' must be a subclass of "
                "CashRelatedTransaction."
            )
        if not transaction.is_account_related(self):
            raise UnrelatedAccountError(
                "This CashAccount is not related to the provided "
                "CashRelatedTransaction."
            )
        return


class CashTransaction(CashRelatedTransaction):
    def __init__(  # noqa: CFQ002, TMN001
        self,
        description: str,
        datetime_: datetime,
        type_: CashTransactionType,
        account: CashAccount,
        payee: Attribute,
        category_amount_pairs: Collection[tuple[Category, CashAmount]],
        tag_amount_pairs: Collection[tuple[Attribute, CashAmount]],
    ) -> None:
        super().__init__()
        self.set_attributes(
            description=description,
            datetime_=datetime_,
            type_=type_,
            account=account,
            category_amount_pairs=category_amount_pairs,
            tag_amount_pairs=tag_amount_pairs,
            payee=payee,
        )
        self._refunds: list[RefundTransaction] = []

    @property
    def type_(self) -> CashTransactionType:
        return self._type

    @property
    def account(self) -> CashAccount:
        return self._account

    @property
    def amount(self) -> CashAmount:
        return sum(
            (amount for _, amount in self._category_amount_pairs),
            start=CashAmount(0, self.currency),
        )

    @property
    def currency(self) -> Currency:
        return self._account.currency

    @property
    def currencies(self) -> tuple[Currency]:
        return (self.currency,)

    @property
    def payee(self) -> Attribute:
        return self._payee

    @property
    def category_amount_pairs(self) -> tuple[tuple[Category, CashAmount], ...]:
        return tuple(self._category_amount_pairs)

    @property
    def categories(self) -> tuple[Category]:
        return tuple(category for category, _ in self._category_amount_pairs)

    @property
    def category_names(self) -> str:
        category_paths = [category.path for category, _ in self._category_amount_pairs]
        return ", ".join(category_paths)

    @property
    def tag_amount_pairs(self) -> tuple[tuple[Attribute, CashAmount], ...]:
        return tuple(self._tag_amount_pairs)

    @property
    def tags(self) -> tuple[Attribute]:
        return tuple(tag for tag, _ in self._tag_amount_pairs)

    @property
    def tag_names(self) -> str:
        tag_names = [tag.name for tag, _ in self._tag_amount_pairs]
        return ", ".join(tag_names)

    @property
    def refunds(self) -> tuple["RefundTransaction", ...]:
        if hasattr(self, "_refunds"):
            return tuple(self._refunds)
        return ()

    @property
    def is_refunded(self) -> bool:
        return len(self.refunds) > 0

    def __repr__(self) -> str:
        return (
            f"CashTransaction({self.type_.name}, "
            f"account='{self.account.name}', "
            f"amount={self.amount}, "
            f"category={{{self.category_names}}}, "
            f"{self.datetime_.strftime('%Y-%m-%d')})"
        )

    def serialize(self) -> dict[str, Any]:
        tag_name_amount_pairs = [
            (tag.name, amount) for tag, amount in self._tag_amount_pairs
        ]
        category_path_amount_pairs = [
            (category.path, amount) for category, amount in self._category_amount_pairs
        ]
        return {
            "datatype": "CashTransaction",
            "description": self._description,
            "datetime_": self._datetime,
            "type_": self._type.name,
            "account_uuid": str(self._account.uuid),
            "payee_name": self._payee.name,
            "category_path_amount_pairs": category_path_amount_pairs,
            "tag_name_amount_pairs": tag_name_amount_pairs,
            "datetime_created": self._datetime_created,
            "uuid": str(self._uuid),
        }

    @staticmethod
    def deserialize(
        data: dict[str, Any],
        accounts: Collection[Account],
        payees: Collection[Attribute],
        categories: Collection[Category],
        tags: Collection[Attribute],
        currencies: Collection[Currency],
    ) -> "CashTransaction":
        description = data["description"]
        datetime_ = data["datetime_"]
        type_ = CashTransactionType[data["type_"]]

        account_uuid = uuid.UUID(data["account_uuid"])
        cash_account = find_account_by_uuid(account_uuid, accounts)

        payee_name = data["payee_name"]
        payee = find_attribute_by_name(payee_name, payees)

        category_path_amount_pairs: list[list[str, dict[str, Any]]] = data[
            "category_path_amount_pairs"
        ]
        decoded_category_amount_pairs = []
        for category_path, amount_dict in category_path_amount_pairs:
            category = find_category_by_path(category_path, categories)
            amount = CashAmount.deserialize(amount_dict, currencies)
            tup = (category, amount)
            decoded_category_amount_pairs.append(tup)

        tag_name_amount_pairs: list[list[str, CashAmount]] = data[
            "tag_name_amount_pairs"
        ]
        decoded_tag_amount_pairs = []
        for tag_name, amount_dict in tag_name_amount_pairs:
            tag = find_attribute_by_name(tag_name, tags)
            amount = CashAmount.deserialize(amount_dict, currencies)
            tup = (tag, amount)
            decoded_tag_amount_pairs.append(tup)

        obj = CashTransaction(
            description=description,
            datetime_=datetime_,
            type_=type_,
            account=cash_account,
            payee=payee,
            category_amount_pairs=decoded_category_amount_pairs,
            tag_amount_pairs=decoded_tag_amount_pairs,
        )
        obj._datetime_created = data["datetime_created"]
        obj._uuid = uuid.UUID(data["uuid"])
        return obj

    def add_refund(self, refund: "RefundTransaction") -> None:
        self._validate_refund(refund)
        self._refunds.append(refund)

    def remove_refund(self, refund: "RefundTransaction") -> None:
        self._validate_refund(refund)
        self._refunds.remove(refund)

    def is_account_related(self, account: Account) -> bool:
        return self.account == account

    def is_category_related(self, category: Category) -> bool:
        direct_match = category in self.categories
        indirect_match = any(
            category.parent == category for category in self.categories
        )
        return direct_match or indirect_match

    def get_amount_for_category(self, category: Category, total: bool) -> CashAmount:
        running_sum = CashAmount(0, self.currency)

        if not self.is_category_related(category):
            return running_sum

        func = (
            operator.add if self.type_ == CashTransactionType.INCOME else operator.sub
        )

        for _category, _amount in self._category_amount_pairs:
            if _category == category:
                running_sum = func(running_sum, _amount)
                continue
            if total and _category.parent == category:
                running_sum = func(running_sum, _amount)
        return running_sum

    def get_amount_for_tag(self, tag: Attribute) -> CashAmount:
        running_sum = CashAmount(0, self.currency)

        if tag not in self.tags:
            return running_sum

        func = (
            operator.add if self.type_ == CashTransactionType.INCOME else operator.sub
        )

        for _tag, _amount in self._tag_amount_pairs:
            if _tag == tag:
                running_sum = func(running_sum, _amount)
        return running_sum

    def prepare_for_deletion(self) -> None:
        if self.is_refunded:
            raise InvalidOperationError(
                "Refunded CashTransaction cannot be deleted. Delete the refunds first."
            )
        self._account.remove_transaction(self)

    def add_tags(self, tags: Collection[Attribute]) -> None:
        self._validate_tags(tags)
        new_tags = tuple(tag for tag in tags if tag not in self.tags)
        tag_amount_pairs = list(self._tag_amount_pairs)
        for tag in new_tags:
            tup = (tag, self.amount)
            tag_amount_pairs.append(tup)
        self._validate_tag_amount_pairs(tag_amount_pairs, self.amount, self.currency)
        self._tag_amount_pairs = tag_amount_pairs

    def remove_tags(self, tags: Collection[Attribute]) -> None:
        self._validate_tags(tags)
        tags_to_remove = tuple(tag for tag in tags if tag in self.tags)
        tag_amount_pairs = [
            (tag, amount)
            for tag, amount in self._tag_amount_pairs
            if tag not in tags_to_remove
        ]
        self._validate_tag_amount_pairs(tag_amount_pairs, self.amount, self.currency)
        self._tag_amount_pairs = tag_amount_pairs

    def set_attributes(
        self,
        *,
        type_: CashTransactionType | None = None,
        account: CashAccount | None = None,
        category_amount_pairs: Collection[tuple[Category, CashAmount | None]]
        | None = None,
        tag_amount_pairs: Collection[tuple[Attribute, CashAmount]] | None = None,
        payee: Attribute | None = None,
        description: str | None = None,
        datetime_: datetime | None = None,
    ) -> None:
        if self.is_refunded:
            raise InvalidOperationError(
                "Refunded CashTransactions cannot be edited. Delete the refunds first."
            )
        if type_ is None:
            type_ = self._type
        if account is None:
            account = self._account
        if category_amount_pairs is None:
            category_amount_pairs = self._category_amount_pairs
        if tag_amount_pairs is None:
            tag_amount_pairs = self._tag_amount_pairs
        if payee is None:
            payee = self._payee
        if description is None:
            description = self._description
        if datetime_ is None:
            datetime_ = self._datetime

        valid_category_amount_pairs = self.validate_attributes(
            description=description,
            datetime_=datetime_,
            type_=type_,
            account=account,
            category_amount_pairs=category_amount_pairs,
            tag_amount_pairs=tag_amount_pairs,
            payee=payee,
        )

        self._set_attributes(
            description=description,
            datetime_=datetime_,
            type_=type_,
            account=account,
            category_amount_pairs=valid_category_amount_pairs,
            tag_amount_pairs=tag_amount_pairs,
            payee=payee,
        )

    def validate_attributes(
        self,
        *,
        description: str | None = None,
        datetime_: datetime | None = None,
        type_: CashTransactionType | None = None,
        account: CashAccount | None = None,
        category_amount_pairs: Collection[tuple[Category, CashAmount | None]]
        | None = None,
        tag_amount_pairs: Collection[tuple[Attribute, CashAmount]] | None = None,
        payee: Attribute | None = None,
    ) -> Collection[tuple[Category, CashAmount]]:
        if type_ is None:
            type_ = self._type
        if account is None:
            account = self._account
        if category_amount_pairs is None:
            category_amount_pairs = self._category_amount_pairs
        if tag_amount_pairs is None:
            tag_amount_pairs = self._tag_amount_pairs
        if payee is None:
            payee = self._payee
        if description is None:
            description = self._description
        if datetime_ is None:
            datetime_ = self._datetime

        self._validate_description(description)
        self._validate_datetime(datetime_)
        self._validate_type(type_)
        _validate_payee(payee)
        self._validate_account(account)
        currency = account.currency

        valid_category_types = self._get_valid_category_types(type_)
        valid_category_amount_pairs = self._validate_category_amount_pairs(
            category_amount_pairs=category_amount_pairs,
            valid_category_types=valid_category_types,
            currency=currency,
        )

        max_tag_amount = sum(
            (amount for _, amount in valid_category_amount_pairs),
            start=CashAmount(0, currency),
        )
        self._validate_tag_amount_pairs(
            tag_amount_pairs=tag_amount_pairs,
            max_tag_amount=max_tag_amount,
            currency=currency,
        )
        return valid_category_amount_pairs

    def _set_attributes(
        self,
        *,
        description: str,
        datetime_: datetime,
        type_: CashTransactionType,
        account: CashAccount,
        category_amount_pairs: Collection[tuple[Category, CashAmount]],
        tag_amount_pairs: Collection[tuple[Attribute, CashAmount]],
        payee: Attribute,
    ) -> None:
        self._description = description
        self._datetime = datetime_
        self._type = type_
        self._payee = payee
        self._category_amount_pairs = list(category_amount_pairs)
        self._tag_amount_pairs = list(tag_amount_pairs)
        self._set_account(account)

    # IDEA: looks very similar to its Security counterpart
    def _set_account(self, account: CashAccount) -> None:
        if hasattr(self, "_account"):
            if self._account == account:
                return
            self._account.remove_transaction(self)
        self._account = account
        self._account.add_transaction(self)

    def _validate_type(self, type_: CashTransactionType) -> None:
        if not isinstance(type_, CashTransactionType):
            raise TypeError("CashTransaction.type_ must be a CashTransactionType.")

    def _validate_account(self, account: CashAccount) -> None:
        if not isinstance(account, CashAccount):
            raise TypeError("CashTransaction.account must be a CashAccount.")

    def _validate_category_amount_pairs(
        self,
        category_amount_pairs: Collection[tuple[Category, CashAmount | None]],
        valid_category_types: Collection[CategoryType],
        currency: Currency,
    ) -> tuple[tuple[Category, CashAmount]]:
        validated_pairs = self._validate_category_amount_pairs_types(
            category_amount_pairs,
        )

        categories = [category for category, _ in category_amount_pairs]
        if len(categories) > len(set(categories)):
            raise ValueError("Categories in category_amount_pairs must be unique.")
        if not all(category.type_ in valid_category_types for category in categories):
            raise InvalidCategoryTypeError("Invalid Category.type_.")

        if not all(amount.currency == currency for _, amount in validated_pairs):
            raise CurrencyError(
                "Currency of CashAmounts in category_amount_pairs must match the "
                "currency of the CashAccount."
            )
        if not all(amount.is_positive() for _, amount in validated_pairs):
            raise ValueError(
                "Second member of CashTransaction.category_amount_pairs "
                "tuples must be a positive CashAmount."
            )

        return validated_pairs

    def _validate_category_amount_pairs_types(
        self,
        collection: Collection[tuple[Category, CashAmount | None]],
    ) -> tuple[tuple[Category, CashAmount]]:
        if not isinstance(collection, Collection):
            raise TypeError("Parameter 'collection' must be a Collection.")
        if len(collection) < 1:
            raise ValueError("Length of 'collection' must be at least 1.")
        if not all(isinstance(element, tuple) for element in collection):
            raise TypeError("Elements of 'collection' must be tuples.")
        if not all(
            isinstance(first_member, Category) for first_member, _ in collection
        ):
            raise TypeError(
                "First element of 'collection' tuples must be of type Category."
            )

        if len(collection) == 1:
            tup: tuple[Category, CashAmount | None] = collection[0]
            category, amount = tup
            if isinstance(amount, CashAmount):
                return ((category, amount),)
            if amount is None:
                # This means a split transaction can be made single-category without
                # specifying amount, using the current total.
                return ((category, self.amount),)
            raise TypeError(
                "Second element of 'collection' tuples must be of type CashAmount "
                "or None."
            )

        if not all(
            isinstance(second_member, CashAmount) for _, second_member in collection
        ):
            raise TypeError(
                "Second element of 'collection' tuples must be of type CashAmount."
            )
        return collection

    def _validate_tag_amount_pairs(
        self,
        tag_amount_pairs: Collection[tuple[Attribute, CashAmount]],
        max_tag_amount: CashAmount,
        currency: Currency,
    ) -> None:
        validate_collection_of_tuple_pairs(
            collection=tag_amount_pairs,
            first_type=Attribute,
            second_type=CashAmount,
            min_length=0,
        )

        if not all(
            attribute.type_ == AttributeType.TAG for attribute, _ in tag_amount_pairs
        ):
            raise ValueError(
                "The type_ of CashTransaction.tag_amount_pairs Attributes must be TAG."
            )

        if not all(amount.currency == currency for _, amount in tag_amount_pairs):
            raise CurrencyError(
                "Currency of CashAmounts in tag_amount_pairs must match the "
                "currency of the CashAccount."
            )
        if not all(
            amount.is_positive() and amount <= max_tag_amount
            for _, amount in tag_amount_pairs
        ):
            raise ValueError(
                "Second member of CashTransaction.tag_amount_pairs "
                "tuples must be a positive CashAmount which "
                "does not exceed CashTransaction.amount."
            )

    def _validate_refund(self, refund: "RefundTransaction") -> None:
        if not isinstance(refund, RefundTransaction):
            raise TypeError("Parameter 'refund' must be a RefundTransaction.")
        if refund.refunded_transaction != self:
            raise UnrelatedTransactionError(
                "Supplied RefundTransaction is not related to this CashTransaction."
            )

    def _get_valid_category_types(
        self, type_: CashTransactionType | None = None
    ) -> tuple[CategoryType, ...]:
        if type_ is None:
            type_ = self._type

        if type_ == CashTransactionType.INCOME:
            return (CategoryType.INCOME, CategoryType.INCOME_AND_EXPENSE)
        return (CategoryType.EXPENSE, CategoryType.INCOME_AND_EXPENSE)

    def _get_amount(self, account: CashAccount) -> CashAmount:  # noqa: U100
        if self.type_ == CashTransactionType.INCOME:
            return self.amount
        return -self.amount


class CashTransfer(CashRelatedTransaction):
    def __init__(  # noqa: TMN001, CFQ002
        self,
        description: str,
        datetime_: datetime,
        sender: CashAccount,
        recipient: CashAccount,
        amount_sent: CashAmount,
        amount_received: CashAmount,
    ) -> None:
        super().__init__()
        self.set_attributes(
            description=description,
            datetime_=datetime_,
            amount_sent=amount_sent,
            amount_received=amount_received,
            sender=sender,
            recipient=recipient,
        )

    @property
    def sender(self) -> CashAccount:
        return self._sender

    @property
    def recipient(self) -> CashAccount:
        return self._recipient

    @property
    def amount_sent(self) -> CashAmount:
        return self._amount_sent

    @property
    def amount_received(self) -> CashAmount:
        return self._amount_received

    @property
    def currencies(self) -> tuple[Currency]:
        return (self._sender.currency, self._recipient.currency)

    def __repr__(self) -> str:
        return (
            f"CashTransfer(sent={self.amount_sent}, "
            f"sender='{self.sender.name}', "
            f"received={self.amount_received}, "
            f"recipient='{self.recipient.name}', "
            f"{self.datetime_.strftime('%Y-%m-%d')})"
        )

    def is_account_related(self, account: Account) -> bool:
        return self.sender == account or self.recipient == account

    def prepare_for_deletion(self) -> None:
        self._sender.remove_transaction(self)
        self._recipient.remove_transaction(self)

    def serialize(self) -> dict[str, Any]:
        return {
            "datatype": "CashTransfer",
            "description": self._description,
            "datetime_": self._datetime,
            "sender_uuid": str(self._sender.uuid),
            "recipient_uuid": str(self._recipient.uuid),
            "amount_sent": self._amount_sent,
            "amount_received": self._amount_received,
            "datetime_created": self._datetime_created,
            "uuid": str(self._uuid),
        }

    @staticmethod
    def deserialize(
        data: dict[str, Any],
        accounts: Collection[Account],
        currencies: Collection[Currency],
    ) -> "CashTransaction":
        description = data["description"]
        datetime_ = data["datetime_"]

        sender_uuid = uuid.UUID(data["sender_uuid"])
        recipient_uuid = uuid.UUID(data["recipient_uuid"])
        sender = find_account_by_uuid(sender_uuid, accounts)
        recipient = find_account_by_uuid(recipient_uuid, accounts)

        amount_sent = CashAmount.deserialize(data["amount_sent"], currencies)
        amount_received = CashAmount.deserialize(data["amount_received"], currencies)

        obj = CashTransfer(
            description=description,
            datetime_=datetime_,
            sender=sender,
            recipient=recipient,
            amount_sent=amount_sent,
            amount_received=amount_received,
        )
        obj._datetime_created = data["datetime_created"]
        obj._uuid = uuid.UUID(data["uuid"])
        return obj

    def set_attributes(
        self,
        *,
        description: str | None = None,
        datetime_: datetime | None = None,
        amount_sent: CashAmount | None = None,
        amount_received: CashAmount | None = None,
        sender: CashAccount | None = None,
        recipient: CashAccount | None = None,
    ) -> None:
        if description is None:
            description = self._description
        if datetime_ is None:
            datetime_ = self._datetime
        if amount_sent is None:
            amount_sent = self._amount_sent
        if amount_received is None:
            amount_received = self._amount_received
        if sender is None:
            sender = self._sender
        if recipient is None:
            recipient = self._recipient

        self.validate_attributes(
            description=description,
            datetime_=datetime_,
            amount_sent=amount_sent,
            amount_received=amount_received,
            sender=sender,
            recipient=recipient,
        )

        self._set_attributes(
            description=description,
            datetime_=datetime_,
            amount_sent=amount_sent,
            amount_received=amount_received,
            sender=sender,
            recipient=recipient,
        )

    def validate_attributes(
        self,
        *,
        description: str | None = None,
        datetime_: datetime | None = None,
        amount_sent: CashAmount | None = None,
        amount_received: CashAmount | None = None,
        sender: CashAccount | None = None,
        recipient: CashAccount | None = None,
    ) -> None:
        if description is None:
            description = self._description
        if datetime_ is None:
            datetime_ = self._datetime
        if amount_sent is None:
            amount_sent = self._amount_sent
        if amount_received is None:
            amount_received = self._amount_received
        if sender is None:
            sender = self._sender
        if recipient is None:
            recipient = self._recipient

        self._validate_description(description)
        self._validate_datetime(datetime_)
        self._validate_accounts(sender, recipient)
        self._validate_amount(amount_sent, sender.currency)
        self._validate_amount(amount_received, recipient.currency)

    def _set_attributes(
        self,
        *,
        description: str,
        datetime_: datetime,
        amount_sent: CashAmount,
        amount_received: CashAmount,
        sender: CashAccount,
        recipient: CashAccount,
    ) -> None:
        self._description = description
        self._datetime = datetime_
        self._amount_sent = amount_sent
        self._amount_received = amount_received
        self._set_accounts(sender, recipient)

    # IDEA: looks very similar to its Security counterpart
    def _set_accounts(self, sender: CashAccount, recipient: CashAccount) -> None:
        add_sender = True
        add_recipient = True

        if hasattr(self, "_sender"):
            if self._sender != sender:
                self._sender.remove_transaction(self)
            else:
                add_sender = False
        if hasattr(self, "_recipient"):
            if self._recipient != recipient:
                self._recipient.remove_transaction(self)
            else:
                add_recipient = False

        self._sender = sender
        self._recipient = recipient

        if add_sender:
            self._sender.add_transaction(self)
        if add_recipient:
            self._recipient.add_transaction(self)

    def _validate_accounts(self, sender: CashAccount, recipient: CashAccount) -> None:
        if not isinstance(sender, CashAccount):
            raise TypeError("Parameter 'sender' must be a CashAccount.")
        if not isinstance(recipient, CashAccount):
            raise TypeError("Parameter 'recipient' must be a CashAccount.")
        if recipient == sender:
            raise TransferSameAccountError(
                "Parameters 'sender' and 'recipient' must be different CashAccounts."
            )

    def _validate_amount(self, amount: CashAmount, currency: Currency) -> None:
        if not isinstance(amount, CashAmount):
            raise TypeError("CashTransfer amounts must be CashAmounts.")
        if not amount.is_positive():
            raise ValueError("CashTransfer amounts must be positive.")
        if amount.currency != currency:
            raise CurrencyError("Invalid CashAmount currency.")

    def _get_amount(self, account: CashAccount) -> CashAmount:
        if self.recipient == account:
            return self.amount_received
        return -self.amount_sent


class RefundTransaction(CashRelatedTransaction):
    """A refund which attaches itself to an expense CashTransaction"""

    def __init__(
        self,
        description: str,
        datetime_: datetime,
        account: CashAccount,
        refunded_transaction: CashTransaction,
        payee: Attribute,
        category_amount_pairs: Collection[tuple[Category, CashAmount]],
        tag_amount_pairs: Collection[tuple[Attribute, CashAmount]],
    ) -> None:
        super().__init__()
        self._set_refunded_transaction(refunded_transaction)
        self.set_attributes(
            description=description,
            datetime_=datetime_,
            account=account,
            category_amount_pairs=category_amount_pairs,
            tag_amount_pairs=tag_amount_pairs,
            payee=payee,
        )

    @property
    def account(self) -> CashAccount:
        return self._account

    @property
    def amount(self) -> CashAmount:
        return sum(
            (amount for _, amount in self._category_amount_pairs),
            start=CashAmount(0, self.currency),
        )

    @property
    def currency(self) -> Currency:
        return self._account.currency

    @property
    def currencies(self) -> tuple[Currency]:
        return (self.currency,)

    @property
    def refunded_transaction(self) -> CashTransaction:
        return self._refunded_transaction

    @property
    def category_amount_pairs(self) -> tuple[tuple[Category, CashAmount], ...]:
        return tuple(self._category_amount_pairs)

    @property
    def categories(self) -> tuple[Category]:
        return tuple(category for category, _ in self._category_amount_pairs)

    @property
    def category_names(self) -> str:
        category_paths = [category.path for category, _ in self._category_amount_pairs]
        return ", ".join(category_paths)

    @property
    def tags(self) -> tuple[Attribute]:
        return tuple(tag for tag, _ in self._tag_amount_pairs)

    @property
    def tag_amount_pairs(self) -> tuple[tuple[Attribute, CashAmount], ...]:
        return self._tag_amount_pairs

    @property
    def payee(self) -> Attribute:
        return self._payee

    def __repr__(self) -> str:
        return (
            f"RefundTransaction(account='{self.account.name}', "
            f"amount={self.amount}, "
            f"category={{{self.category_names}}}, "
            f"{self.datetime_.strftime('%Y-%m-%d')})"
        )

    def is_account_related(self, account: "Account") -> bool:
        return self.account == account

    def is_category_related(self, category: Category) -> bool:
        direct_match = category in self.categories
        indirect_match = any(
            category.parent == category for category in self.categories
        )
        return direct_match or indirect_match

    def get_amount_for_category(self, category: Category, total: bool) -> CashAmount:
        running_sum = CashAmount(0, self.currency)

        if not self.is_category_related(category):
            return running_sum

        for _category, _amount in self._category_amount_pairs:
            if _category == category:
                running_sum += _amount
                continue
            if total and _category.parent == category:
                running_sum += _amount
        return running_sum

    def get_amount_for_tag(self, tag: Attribute) -> CashAmount:
        running_sum = CashAmount(0, self.currency)

        if tag not in self.tags:
            return running_sum

        for _tag, _amount in self._tag_amount_pairs:
            if _tag == tag:
                running_sum += _amount
        return running_sum

    def prepare_for_deletion(self) -> None:
        self._refunded_transaction.remove_refund(self)
        self._account.remove_transaction(self)

    def serialize(self) -> dict[str, Any]:
        tag_name_amount_pairs = [
            (tag.name, amount) for tag, amount in self._tag_amount_pairs
        ]
        category_path_amount_pairs = [
            (category.path, amount) for category, amount in self._category_amount_pairs
        ]
        return {
            "datatype": "RefundTransaction",
            "description": self._description,
            "datetime_": self._datetime,
            "account_uuid": str(self._account.uuid),
            "refunded_transaction_uuid": str(self._refunded_transaction.uuid),
            "payee_name": self._payee.name,
            "category_path_amount_pairs": category_path_amount_pairs,
            "tag_name_amount_pairs": tag_name_amount_pairs,
            "datetime_created": self._datetime_created,
            "uuid": str(self._uuid),
        }

    @staticmethod
    def deserialize(
        data: dict[str, Any],
        accounts: Collection[Account],
        transactions: Collection[Transaction],
        payees: Collection[Attribute],
        categories: Collection[Category],
        tags: Collection[Attribute],
        currencies: Collection[Currency],
    ) -> "CashTransaction":
        description = data["description"]
        datetime_ = data["datetime_"]

        account_uuid = uuid.UUID(data["account_uuid"])
        cash_account = find_account_by_uuid(account_uuid, accounts)

        transaction_uuid = uuid.UUID(data["refunded_transaction_uuid"])
        refunded_transaction = find_transaction_by_uuid(transaction_uuid, transactions)

        payee = find_attribute_by_name(data["payee_name"], payees)

        category_path_amount_pairs: list[list[str, dict[str, Any]]] = data[
            "category_path_amount_pairs"
        ]
        decoded_category_amount_pairs = []
        for category_path, amount_dict in category_path_amount_pairs:
            category = find_category_by_path(category_path, categories)
            amount = CashAmount.deserialize(amount_dict, currencies)
            tup = (category, amount)
            decoded_category_amount_pairs.append(tup)

        tag_name_amount_pairs: list[list[str, CashAmount]] = data[
            "tag_name_amount_pairs"
        ]
        decoded_tag_amount_pairs = []
        for tag_name, amount_dict in tag_name_amount_pairs:
            tag = find_attribute_by_name(tag_name, tags)
            amount = CashAmount.deserialize(amount_dict, currencies)
            tup = (tag, amount)
            decoded_tag_amount_pairs.append(tup)

        obj = RefundTransaction(
            description=description,
            datetime_=datetime_,
            account=cash_account,
            refunded_transaction=refunded_transaction,
            payee=payee,
            category_amount_pairs=decoded_category_amount_pairs,
            tag_amount_pairs=decoded_tag_amount_pairs,
        )
        obj._datetime_created = data["datetime_created"]
        obj._uuid = uuid.UUID(data["uuid"])
        return obj

    def add_tags(self, tags: Collection[Attribute]) -> None:  # noqa: U100
        raise InvalidOperationError("Adding tags to RefundTransaction is forbidden.")

    def remove_tags(self, tags: Collection[Attribute]) -> None:  # noqa: U100
        raise InvalidOperationError(
            "Removing tags from RefundTransaction is forbidden."
        )

    def set_attributes(
        self,
        *,
        description: str | None = None,
        datetime_: datetime | None = None,
        account: CashAccount | None = None,
        category_amount_pairs: Collection[tuple[Category, CashAmount]] | None = None,
        tag_amount_pairs: Collection[tuple[Attribute, CashAmount]] | None = None,
        payee: Attribute | None = None,
    ) -> None:
        if description is None:
            description = self._description
        if datetime_ is None:
            datetime_ = self._datetime
        if account is None:
            account = self._account
        if category_amount_pairs is None:
            category_amount_pairs = self._category_amount_pairs
        if tag_amount_pairs is None:
            tag_amount_pairs = self._tag_amount_pairs
        if payee is None:
            payee = self._payee

        self.validate_attributes(
            description=description,
            datetime_=datetime_,
            account=account,
            category_amount_pairs=category_amount_pairs,
            tag_amount_pairs=tag_amount_pairs,
            payee=payee,
        )

        self._set_attributes(
            description=description,
            datetime_=datetime_,
            account=account,
            category_amount_pairs=category_amount_pairs,
            tag_amount_pairs=tag_amount_pairs,
            payee=payee,
        )

    def validate_attributes(
        self,
        *,
        description: str | None = None,
        datetime_: datetime | None = None,
        account: CashAccount | None = None,
        category_amount_pairs: Collection[tuple[Category, CashAmount]] | None = None,
        tag_amount_pairs: Collection[tuple[Attribute, CashAmount]] | None = None,
        payee: Attribute | None = None,
    ) -> None:
        if description is None:
            description = self._description
        if datetime_ is None:
            datetime_ = self._datetime
        if account is None:
            account = self._account
        if category_amount_pairs is None:
            category_amount_pairs = self._category_amount_pairs
        if tag_amount_pairs is None:
            tag_amount_pairs = self._tag_amount_pairs
        if payee is None:
            payee = self._payee

        self._validate_description(description)
        self._validate_account(account, self._refunded_transaction.currency)
        currency = account.currency
        self._validate_datetime(datetime_, self._refunded_transaction.datetime_)
        self._validate_category_amount_pairs(
            category_amount_pairs, self._refunded_transaction, currency
        )
        max_tag_amount = sum(
            (amount for _, amount in category_amount_pairs),
            start=CashAmount(0, currency),
        )
        self._validate_tag_amount_pairs(
            tag_amount_pairs, self._refunded_transaction, currency, max_tag_amount
        )
        _validate_payee(payee)

    def _set_attributes(
        self,
        *,
        description: str,
        datetime_: datetime,
        account: CashAccount,
        category_amount_pairs: Collection[tuple[Category, CashAmount]],
        tag_amount_pairs: Collection[tuple[Category, CashAmount]],
        payee: Attribute,
    ) -> None:
        self._description = description
        self._datetime = datetime_
        self._category_amount_pairs = tuple(category_amount_pairs)
        self._tag_amount_pairs = tuple(tag_amount_pairs)
        self._payee = payee
        self._set_account(account)

    def _validate_datetime(
        self, datetime_: datetime, refunded_transaction_datetime: datetime
    ) -> None:
        super()._validate_datetime(datetime_)
        if datetime_ < refunded_transaction_datetime:
            raise RefundPrecedesTransactionError(
                "Supplied RefundTransaction.datetime_ precedes this "
                "CashTransaction.datetime_."
            )

    def _set_account(self, account: CashAccount) -> None:
        if hasattr(self, "_account"):
            if self._account == account:
                return
            self._account.remove_transaction(self)
        self._account = account
        self._account.add_transaction(self)

    def _validate_account(
        self, account: CashAccount, refunded_transaction_currency: Currency
    ) -> None:
        if not isinstance(account, CashAccount):
            raise TypeError("RefundTransaction.account must be a CashAccount.")
        if account.currency != refunded_transaction_currency:
            raise CurrencyError(
                "Currencies of the refunded CashTransaction and the refunded "
                "CashAccount must match."
            )

    def _set_refunded_transaction(self, refunded_transaction: CashTransaction) -> None:
        if not isinstance(refunded_transaction, CashTransaction):
            raise TypeError("Refunded transaction must be a CashTransaction.")
        if refunded_transaction.type_ != CashTransactionType.EXPENSE:
            raise InvalidCashTransactionTypeError(
                "Only expense CashTransactions can be refunded."
            )

        self._refunded_transaction = refunded_transaction
        self._refunded_transaction.add_refund(self)

    def _validate_category_amount_pairs(
        self,
        pairs: Collection[tuple[Category, CashAmount]],
        refunded_transaction: CashTransaction,
        currency: Currency,
    ) -> None:
        no_of_categories = len(refunded_transaction.category_amount_pairs)
        validate_collection_of_tuple_pairs(
            pairs, Category, CashAmount, no_of_categories
        )
        valid_categories = [
            category for category, _ in refunded_transaction.category_amount_pairs
        ]
        if not all(category in valid_categories for category, _ in pairs):
            raise InvalidCategoryError(
                "Only categories present in the refunded CashTransaction are accepted."
            )
        if not all(amount.value_rounded >= 0 for _, amount in pairs):
            raise ValueError(
                "Second member of RefundTransaction.category_amount_pairs "
                "tuples must be a non-negative CashAmount."
            )
        refund_amount = sum(
            (amount for _, amount in pairs), start=CashAmount(0, currency)
        )
        if not refund_amount.value_rounded > 0:
            raise ValueError("Total refunded amount must be positive.")

        max_values = {}
        for category, amount in refunded_transaction.category_amount_pairs:
            max_values[category] = amount
        other_refunds = [
            refund for refund in refunded_transaction.refunds if refund != self
        ]
        for other_refund in other_refunds:
            for category, amount in other_refund.category_amount_pairs:
                max_values[category] -= amount
        for category, amount in pairs:
            if amount > max_values[category]:
                raise ValueError(
                    f"Refunded amount for category '{category.path}' must not exceed "
                    f"{max_values[category]}."
                )

    def _validate_tag_amount_pairs(
        self,
        pairs: Collection[tuple[Attribute, CashAmount]],
        refunded_transaction: CashTransaction,
        currency: Currency,
        refund_amount: CashAmount,
    ) -> None:
        expected_tags = {tag for tag, _ in refunded_transaction.tag_amount_pairs}
        no_of_tags = len(expected_tags)
        validate_collection_of_tuple_pairs(pairs, Attribute, CashAmount, no_of_tags)

        if not all(attribute.type_ == AttributeType.TAG for attribute, _ in pairs):
            raise InvalidAttributeError(
                "The type_ of RefundTransaction.tag_amount_pairs Attributes must "
                "be TAG."
            )
        delivered_tags = {tag for tag, _ in pairs}
        if delivered_tags != expected_tags:
            raise InvalidAttributeError("Delivered tags do not match expected tags.")
        if not all(amount.value_rounded >= 0 for _, amount in pairs):
            raise ValueError(
                "Second member of RefundTransaction.tag_amount_pairs "
                "tuples must be a non-negative CashAmount."
            )

        max_values: dict[Attribute, CashAmount] = {}
        min_values: dict[Attribute, CashAmount] = {}
        for tag, amount in refunded_transaction.tag_amount_pairs:
            max_values[tag] = refunded_transaction.amount
            min_values[tag] = amount
        other_refunds = [
            refund for refund in refunded_transaction.refunds if refund != self
        ]
        remaining_amount = refunded_transaction.amount - sum(
            (refund.amount for refund in other_refunds),
            start=CashAmount(0, currency=currency),
        )
        for other_refund in other_refunds:
            for tag, amount in other_refund.tag_amount_pairs:
                max_values[tag] -= amount
                min_values[tag] -= amount

        for tag, amount in pairs:
            min_expected = min_values[tag] - (remaining_amount - refund_amount)
            min_values[tag] = max(min_expected, CashAmount(0, currency))
            if amount > max_values[tag] or amount < min_values[tag]:
                raise ValueError(
                    f"Refunded amount for tag '{tag.name}' must be within "
                    f"{min_values[tag]} and {max_values[tag]}."
                )

    def _get_amount(self, account: CashAccount) -> CashAmount:  # noqa: U100
        return self.amount


def _validate_payee(payee: Attribute) -> None:
    if not isinstance(payee, Attribute):
        raise TypeError("Payee must be an Attribute.")
    if not payee.type_ == AttributeType.PAYEE:
        raise ValueError("The type_ of payee Attribute must be PAYEE.")


def validate_collection_of_tuple_pairs(
    collection: Collection[tuple[Any, Any]],
    first_type: type,
    second_type: type,
    min_length: int,
) -> None:
    if not isinstance(collection, Collection):
        raise TypeError("Parameter 'collection' must be a Collection.")
    if len(collection) < min_length:
        raise ValueError(f"Length of 'collection' must be at least {min_length}.")
    if not all(isinstance(element, tuple) for element in collection):
        raise TypeError("Elements of 'collection' must be tuples.")
    if not all(isinstance(first_member, first_type) for first_member, _ in collection):
        raise TypeError(
            "First element of 'collection' tuples must be of type "
            f"{first_type.__name__}."
        )
    first_members = [first_member for first_member, _ in collection]
    if len(first_members) > len(set(first_members)):
        raise ValueError("Categories or Tags in tuple pairs must be unique.")
    if not all(
        isinstance(second_member, second_type) for _, second_member in collection
    ):
        raise TypeError(
            "Second element of 'collection' tuples must be of type "
            f"{second_type.__name__}."
        )
