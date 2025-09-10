import logging
import operator
from abc import ABC, abstractmethod
from bisect import bisect_right
from collections.abc import Collection
from datetime import date, datetime, timedelta
from decimal import Decimal
from enum import Enum, auto
from types import NoneType
from typing import Any
from uuid import UUID

from src.models.base_classes.account import Account, UnrelatedAccountError
from src.models.base_classes.transaction import Transaction
from src.models.custom_exceptions import (
    AlreadyExistsError,
    InvalidOperationError,
    NotFoundError,
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
from src.models.user_settings import user_settings


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
    __slots__ = ()

    def get_amount(self, account: "CashAccount | None" = None) -> CashAmount:
        """Parameter 'account' is only mandatory for CashTransfer."""

        if isinstance(self, CashTransfer):
            if not isinstance(account, CashAccount):
                raise TypeError("Parameter 'account' must be a CashAccount.")
            if not self.is_account_related(account):
                raise UnrelatedAccountError(
                    f"CashAccount '{account.name}' is not related to this "
                    f"{self.__class__.__name__}."
                )
        return self._get_amount(account)

    @abstractmethod
    def _get_amount(self, account: "CashAccount | None") -> CashAmount:
        raise NotImplementedError

    @property
    @abstractmethod
    def currencies(self) -> tuple[Currency]:
        raise NotImplementedError


class CashTransactionType(Enum):
    INCOME = auto()
    EXPENSE = auto()


class CashAccount(Account):
    __slots__ = (
        "_allow_colon",
        "_allow_slash",
        "_balance_history",
        "_balances",
        "_currency",
        "_initial_balance",
        "_name",
        "_parent",
        "_transactions",
        "_uuid",
        "allow_update_balance",
        "event_balance_updated",
    )

    def __init__(
        self,
        name: str,
        currency: Currency,
        initial_balance: CashAmount,
        parent: AccountGroup | None = None,
    ) -> None:
        if not isinstance(currency, Currency):
            raise TypeError("CashAccount.currency must be a Currency.")
        self._currency = currency

        # allow_update_balance attribute is used to block updating the balance
        # when a transaction is added or removed during deserialization
        self.allow_update_balance = False

        # balance update via initial_balance set is suppressed due to line above
        self.initial_balance = initial_balance
        self._balance_history: list[
            tuple[datetime, CashAmount, CashRelatedTransaction | None]
        ] = [(datetime.now(user_settings.settings.time_zone), initial_balance, None)]
        self._transactions: set[CashRelatedTransaction] = set()

        # parent is set last because it triggers chain of balance updates
        self.allow_update_balance = True
        super().__init__(name=name, parent=parent)

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
        if amount.is_negative():
            raise ValueError("CashAccount.initial_balance must not be negative.")
        self._initial_balance = amount
        if self.allow_update_balance:
            self.update_balance()

    @property
    def balance_history(
        self,
    ) -> tuple[tuple[datetime, CashAmount, CashRelatedTransaction | None], ...]:
        return tuple(self._balance_history)

    @property
    def transactions(
        self,
    ) -> tuple[CashRelatedTransaction, ...]:
        return tuple(self._transactions)

    @property
    def balances(self) -> tuple[CashAmount, ...]:
        return (self._balance_history[-1][1],)

    def get_balance(self, currency: Currency, date_: date | None = None) -> CashAmount:
        if date_ is None:
            amount = self._balance_history[-1][1].convert(currency)
        else:
            index = bisect_right(
                self._balance_history, date_, key=lambda x: x[0].date()
            )
            if index:
                _, amount, _ = self._balance_history[index - 1]
            else:
                amount = currency.zero_amount
        return amount.convert(currency, date_)

    def get_balance_after_transaction(
        self, currency: Currency, transaction: CashRelatedTransaction
    ) -> CashAmount:
        self._validate_transaction(transaction)
        for _, balance, _transaction in self._balance_history:
            if _transaction == transaction:
                return balance.convert(currency)
        raise ValueError(  # pragma: no cover
            "Provided CashRelatedTransaction not found."
        )

    def add_transaction(self, transaction: CashRelatedTransaction) -> None:
        self._validate_transaction(transaction)
        if transaction in self._transactions:
            raise AlreadyExistsError(
                "Provided CashRelatedTransaction is already within this "
                "CashAccount.transactions."
            )
        self._transactions.add(transaction)
        if self.allow_update_balance:
            self.update_balance()

    def remove_transaction(self, transaction: CashRelatedTransaction) -> None:
        self._validate_transaction(transaction)
        self._transactions.remove(transaction)
        if self.allow_update_balance:
            self.update_balance()

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
        account_groups: dict[str, AccountGroup],
        currencies: dict[str, Currency],
    ) -> "CashAccount":
        path: str = data["path"]
        index: int | None = data["index"]
        parent_path, _, name = path.rpartition("/")
        initial_balance_value = data["initial_balance"]
        currency = currencies[data["currency_code"]]

        initial_balance = CashAmount(initial_balance_value, currency)

        obj = CashAccount(name, currency, initial_balance)
        obj._uuid = UUID(data["uuid"])

        if parent_path:
            obj._parent = account_groups[parent_path]
            obj._parent._children_dict[index] = obj  # noqa: SLF001
            obj._parent._update_children_tuple()  # noqa: SLF001
            obj.event_balance_updated.append(
                obj._parent._update_balances  # noqa: SLF001
            )
            obj.event_balance_updated()
        return obj

    def update_balance(self) -> None:
        logging.debug(f"Updating balance of {self}")

        transactions = sorted(self._transactions, key=lambda x: x.timestamp)
        for index, transaction in enumerate(transactions):
            if index > 0 and transaction.datetime_ == transactions[index - 1].datetime_:
                new_datetime = transaction.datetime_ + timedelta(seconds=1)
                transaction.set_attributes(
                    datetime_=new_datetime, block_account_update=True
                )

        if len(self._transactions) > 0:
            oldest_datetime = transactions[0].datetime_
        else:
            oldest_datetime = self._balance_history[0][0] + timedelta(days=1)
        datetime_balance_history: list[
            tuple[datetime, CashAmount, CashRelatedTransaction | None]
        ] = [(oldest_datetime - timedelta(days=1), self._initial_balance, None)]

        for transaction in transactions:
            last_balance = datetime_balance_history[-1][1]
            next_balance = last_balance + transaction.get_amount(self)
            datetime_balance_history.append(
                (transaction.datetime_, next_balance, transaction)
            )

        self._balance_history = datetime_balance_history
        self.event_balance_updated()

    def _validate_transaction(
        self,
        transaction: CashRelatedTransaction,
    ) -> None:
        if not isinstance(transaction, CashRelatedTransaction):
            raise TypeError(
                "Parameter 'transaction' must be a subclass of CashRelatedTransaction."
            )
        if not transaction.is_account_related(self):
            raise UnrelatedAccountError(
                "This CashAccount is not related to the provided "
                "CashRelatedTransaction."
            )


class CashTransaction(CashRelatedTransaction):
    __slots__ = (
        "_account",
        "_amount",
        "_amount_negative",
        "_are_tags_split",
        "_categories",
        "_category_amount_pairs",
        "_datetime",
        "_datetime_created",
        "_description",
        "_payee",
        "_refunded_ratio",
        "_refunds",
        "_tag_amount_pairs",
        "_tags",
        "_timestamp",
        "_type",
        "_uuid",
    )

    def __init__(  # noqa: PLR0913
        self,
        description: str,
        datetime_: datetime,
        type_: CashTransactionType,
        account: CashAccount,
        payee: Attribute,
        category_amount_pairs: Collection[tuple[Category, CashAmount]],
        tag_amount_pairs: Collection[tuple[Attribute, CashAmount]],
        uuid: UUID | None = None,
    ) -> None:
        super().__init__()
        if uuid is not None:
            self._uuid = uuid
        self._refunds: list[RefundTransaction] = []
        self.set_attributes(
            description=description,
            datetime_=datetime_,
            type_=type_,
            account=account,
            category_amount_pairs=category_amount_pairs,
            tag_amount_pairs=tag_amount_pairs,
            payee=payee,
        )

    @property
    def type_(self) -> CashTransactionType:
        return self._type

    @property
    def account(self) -> CashAccount:
        return self._account

    @property
    def amount(self) -> CashAmount:
        return self._amount

    @property
    def currency(self) -> Currency:
        return self._account.currency

    @property
    def currencies(self) -> tuple[Currency]:
        return (self._account.currency,)

    @property
    def payee(self) -> Attribute:
        return self._payee

    @property
    def category_amount_pairs(self) -> tuple[tuple[Category, CashAmount], ...]:
        return self._category_amount_pairs

    @property
    def categories(self) -> frozenset[Category]:
        return self._categories

    @property
    def category_names(self) -> str:
        category_paths = [category.path for category, _ in self._category_amount_pairs]
        return ", ".join(category_paths)

    @property
    def are_categories_split(self) -> bool:
        return len(self._category_amount_pairs) > 1

    @property
    def tag_amount_pairs(self) -> tuple[tuple[Attribute, CashAmount], ...]:
        return self._tag_amount_pairs

    @property
    def tags(self) -> frozenset[Attribute]:
        return self._tags

    @property
    def tag_names(self) -> str:
        tag_names = [tag.name for tag, _ in self._tag_amount_pairs]
        return ", ".join(tag_names)

    @property
    def are_tags_split(self) -> bool:
        return self._are_tags_split

    @property
    def refunds(self) -> tuple["RefundTransaction", ...]:
        return tuple(self._refunds)

    @property
    def refunded_ratio(self) -> Decimal:
        if self.is_refunded:
            return self._refunded_ratio
        return Decimal(0)

    @property
    def is_refunded(self) -> bool:
        return len(self.refunds) > 0

    def __repr__(self) -> str:
        return (
            f"CashTransaction({self.type_.name}, "
            f"account='{self._account.name}', "
            f"amount={self._amount}, "
            f"category={{{self.category_names}}}, "
            f"{self.datetime_.strftime('%Y-%m-%d')})"
        )

    def serialize(self) -> dict[str, Any]:
        tag_amount_pairs = [
            tag.name + ":" + amount.serialize()
            for tag, amount in self._tag_amount_pairs
        ]
        category_amount_pairs = [
            category.path + ":" + amount.serialize()
            for category, amount in self._category_amount_pairs
        ]
        return {
            "datatype": "CashTransaction",
            "description": self._description,
            "datetime": self._datetime.replace(microsecond=0).isoformat(),
            "type": self._type.name,
            "account_path": self._account.path,
            "payee_name": self._payee.name,
            "category_amount_pairs": category_amount_pairs,
            "tag_amount_pairs": tag_amount_pairs,
            "datetime_created": self._datetime_created.isoformat(),
            "uuid": str(self._uuid),
        }

    @staticmethod
    def deserialize(  # noqa: PLR0913
        data: dict[str, Any],
        accounts: dict[str, Account],
        payees: dict[str, Attribute],
        categories: dict[str, Category],
        tags: dict[str, Attribute],
        currencies: dict[str, Currency],
    ) -> "CashTransaction":
        description = data["description"]
        datetime_ = datetime.fromisoformat(data["datetime"])
        type_ = CashTransactionType[data["type"]]
        cash_account = accounts[data["account_path"]]
        payee = payees[data["payee_name"]]

        category_path_amount_pairs: list[str] = data["category_amount_pairs"]
        decoded_category_amount_pairs: list[tuple[Category, CashAmount]] = []
        for pair_string in category_path_amount_pairs:
            category_path, _, amount_str = pair_string.partition(":")
            category = categories[category_path]
            amount = CashAmount.deserialize(amount_str, currencies)
            decoded_category_amount_pairs.append((category, amount))

        tag_name_amount_pairs: list[str] = data["tag_amount_pairs"]
        decoded_tag_amount_pairs: list[tuple[Attribute, CashAmount]] = []
        for pair_string in tag_name_amount_pairs:
            tag_name, _, amount_str = pair_string.partition(":")
            tag = tags[tag_name]
            amount = CashAmount.deserialize(amount_str, currencies)
            decoded_tag_amount_pairs.append((tag, amount))

        obj = CashTransaction(
            description=description,
            datetime_=datetime_,
            type_=type_,
            account=cash_account,
            payee=payee,
            category_amount_pairs=decoded_category_amount_pairs,
            tag_amount_pairs=decoded_tag_amount_pairs,
            uuid=UUID(data["uuid"]),
        )
        obj._datetime_created = datetime.fromisoformat(
            data["datetime_created"]
        )
        return obj

    def add_refund(self, refund: "RefundTransaction") -> None:
        self._validate_refund(refund)
        self._refunds.append(refund)
        self._update_refunded_ratio()

    def remove_refund(self, refund: "RefundTransaction") -> None:
        self._validate_refund(refund)
        self._refunds.remove(refund)
        self._update_refunded_ratio()

    def get_max_refundable_for_category(
        self, category: Category, ignore_refund: "RefundTransaction|None"
    ) -> CashAmount:
        for _category, amount in self._category_amount_pairs:
            if _category == category:
                max_amount = amount
                break
        else:
            raise ValueError(
                f"Category {category} not in this CashTransaction's categories."
            )

        refunds = [refund for refund in self._refunds if refund != ignore_refund]
        for refund in refunds:
            for _category, _amount in refund.category_amount_pairs:
                if _category != category:
                    continue
                max_amount -= _amount

        return max_amount

    def get_max_refundable_for_tag(
        self,
        tag: Attribute,
        ignore_refund: "RefundTransaction|None",
        refund_amount: CashAmount | None,
    ) -> CashAmount:
        if tag not in self.tags:
            raise ValueError(f"Tag {tag} not in this CashTransaction's tags.")

        max_amount = next(
            _amount for _tag, _amount in self._tag_amount_pairs if _tag == tag
        )

        other_refunds = [refund for refund in self._refunds if refund != ignore_refund]
        for refund in other_refunds:
            max_amount -= next(
                (_amount for _tag, _amount in refund.tag_amount_pairs if _tag == tag),
                self.currency.zero_amount,
            )

        if refund_amount is not None:
            return min(max_amount, refund_amount)
        return max_amount

    def get_min_refundable_for_tag(
        self,
        tag: Attribute,
        ignored_refund: "RefundTransaction|None",
        refund_amount: CashAmount | None,
    ) -> CashAmount:
        if tag not in self.tags:
            raise ValueError(f"Tag {tag} not in this CashTransaction's tags.")
        if refund_amount is None:
            return self.currency.zero_amount

        max_amount = next(
            _amount for _tag, _amount in self._tag_amount_pairs if _tag == tag
        )

        other_refunds = [refund for refund in self._refunds if refund != ignored_refund]
        remaining_amount = self._amount - sum(
            (refund.amount for refund in other_refunds),
            start=self.currency.zero_amount,
        )
        for refund in other_refunds:
            max_amount -= next(
                (_amount for _tag, _amount in refund.tag_amount_pairs if _tag == tag),
                self.currency.zero_amount,
            )

        return max(
            max_amount - (remaining_amount - refund_amount),
            self.currency.zero_amount,
        )

    def is_account_related(self, account: Account) -> bool:
        return self._account == account

    def is_accounts_related(self, accounts: Collection[Account]) -> bool:
        return self._account in accounts

    def get_amount_for_category(self, category: Category, *, total: bool) -> CashAmount:
        return _get_amount_for_category(self, category, total=total)

    def get_amount_for_tag(self, tag: Attribute) -> CashAmount:
        for tag_, amount in self._tag_amount_pairs:
            if tag_ == tag:
                if self._type == CashTransactionType.INCOME:
                    return amount
                return -amount
        raise ValueError(f"Tag '{tag.name}' not found in this CashTransaction's tags.")

    def prepare_for_deletion(self) -> None:
        if self.is_refunded:
            raise InvalidOperationError(
                "Refunded CashTransaction cannot be deleted. Delete the refunds first."
            )
        self._account.remove_transaction(self)

    def add_tags(self, tags: Collection[Attribute]) -> None:
        if self.is_refunded:
            raise InvalidOperationError(
                "Cannot add Tags to a refunded CashTransaction."
            )
        self._validate_tags(tags)
        new_tags = tuple(tag for tag in tags if tag not in self.tags)
        tag_amount_pairs = list(self._tag_amount_pairs)
        for tag in new_tags:
            tup = (tag, self._amount)
            tag_amount_pairs.append(tup)
        self._validate_tag_amount_pairs(tag_amount_pairs, self._amount, self.currency)
        self._tag_amount_pairs = tuple(tag_amount_pairs)
        self._tags = frozenset(tag for tag, _ in tag_amount_pairs)

    def remove_tags(self, tags: Collection[Attribute]) -> None:
        if self.is_refunded:
            raise InvalidOperationError(
                "Cannot remove Tags from a refunded CashTransaction."
            )
        self._validate_tags(tags)
        tags_to_remove = tuple(tag for tag in tags if tag in self.tags)
        tag_amount_pairs = [
            (tag, amount)
            for tag, amount in self._tag_amount_pairs
            if tag not in tags_to_remove
        ]
        self._validate_tag_amount_pairs(tag_amount_pairs, self._amount, self.currency)
        self._tag_amount_pairs = tuple(tag_amount_pairs)
        self._tags = frozenset(tag for tag, _ in tag_amount_pairs)

    def replace_tag(self, replaced_tag: Attribute, replacement_tag: Attribute) -> None:
        self._validate_tags((replaced_tag, replacement_tag))
        if replaced_tag not in self._tags:
            raise NotFoundError(
                f"Tag '{replaced_tag.name}' not found in this CashTransaction's Tags."
            )
        tag_amount_pairs = list(self._tag_amount_pairs)
        if replacement_tag not in self._tags:
            for index, pair in enumerate(self._tag_amount_pairs):
                tag, amount = pair
                if tag == replaced_tag:
                    tag_amount_pairs[index] = (replacement_tag, amount)
        else:
            replaced_amount = abs(self.get_amount_for_tag(replaced_tag))
            replacement_amount = abs(self.get_amount_for_tag(replacement_tag))
            new_amount = min(self.amount, replaced_amount + replacement_amount)
            for index, pair in enumerate(self._tag_amount_pairs):
                tag, amount = pair
                if tag == replacement_tag:
                    tag_amount_pairs[index] = (replacement_tag, new_amount)
            tag_amount_pairs.remove((replaced_tag, replaced_amount))
        self._validate_tag_amount_pairs(tag_amount_pairs, self._amount, self.currency)
        self._tag_amount_pairs = tuple(tag_amount_pairs)
        self._tags = frozenset(tag for tag, _ in tag_amount_pairs)

    def replace_payee(self, replacement_payee: Attribute) -> None:
        _validate_payee(replacement_payee)
        self._payee = replacement_payee

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
        block_account_update: bool = False,
    ) -> None:
        if self.is_refunded and (
            type_ is not None
            or account is not None
            or category_amount_pairs is not None
            or tag_amount_pairs is not None
        ):
            raise InvalidOperationError(
                "Only the payee, description or datetime_ of a refunded "
                "CashTransaction can be changed."
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

        valid_category_amount_pairs, valid_tag_amount_pairs = self.validate_attributes(
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
            tag_amount_pairs=valid_tag_amount_pairs,
            payee=payee,
            block_account_update=block_account_update,
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
        tag_amount_pairs: Collection[tuple[Attribute, CashAmount | None]] | None = None,
        payee: Attribute | None = None,
    ) -> tuple[tuple[tuple[Category, CashAmount]], tuple[tuple[Attribute, CashAmount]]]:
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
        (
            valid_category_amount_pairs,
            max_tag_amount,
        ) = self._validate_category_amount_pairs(
            category_amount_pairs=category_amount_pairs,
            valid_category_types=valid_category_types,
            currency=currency,
        )

        valid_tag_amount_pairs = self._validate_tag_amount_pairs(
            tag_amount_pairs=tag_amount_pairs,
            max_tag_amount=max_tag_amount,
            currency=currency,
        )
        return valid_category_amount_pairs, valid_tag_amount_pairs

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
        block_account_update: bool = False,
    ) -> None:
        update_account = False

        self._description = description.strip()
        if not block_account_update and hasattr(self, "_datetime"):
            update_account = datetime_ != self._datetime
        self._datetime = datetime_
        self._timestamp = datetime_.timestamp()

        if not block_account_update and hasattr(self, "_type") and not update_account:
            update_account = type_ != self._type
        self._type = type_
        self._payee = payee

        _category_amount_pairs = tuple(category_amount_pairs)
        if (
            not block_account_update
            and hasattr(self, "_category_amount_pairs")
            and not update_account
        ):
            update_account = self._category_amount_pairs != _category_amount_pairs

        self._category_amount_pairs = _category_amount_pairs
        self._tag_amount_pairs = tuple(tag_amount_pairs)
        self._update_cached_data(account.currency)
        self._set_account(account, balance_changed=update_account)

    def _set_account(self, account: CashAccount, *, balance_changed: bool) -> None:
        if hasattr(self, "_account"):
            if self._account == account:
                if balance_changed:
                    self._account.update_balance()
                return
            self._account.remove_transaction(self)
        self._account = account
        self._account.add_transaction(self)

    def _update_cached_data(self, currency: Currency) -> None:
        total_amount = currency.zero_amount
        categories: set[Category] = set()
        for category, amount in self._category_amount_pairs:
            total_amount += amount
            categories.add(category)
        self._amount = total_amount
        self._amount_negative = -total_amount
        self._categories = frozenset(categories)

        tags: set[Attribute] = set()
        self._are_tags_split = False
        for tag, amount in self._tag_amount_pairs:
            tags.add(tag)
            if not self._are_tags_split and amount != self._amount:
                self._are_tags_split = True
        self._tags = frozenset(tags)

    def _validate_datetime(self, value: datetime) -> None:
        super()._validate_datetime(value)
        if self.is_refunded:
            refund_datetimes = [refund.datetime_ for refund in self._refunds]
            if any(refund_datetime < value for refund_datetime in refund_datetimes):
                raise ValueError(
                    "The datetime_ of a refunded CashTransaction must "
                    "precede the datetimes of its refunds."
                )

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
    ) -> tuple[tuple[tuple[Category, CashAmount], ...], CashAmount]:
        validated_pairs = self._validate_category_amount_pairs_types(
            category_amount_pairs,
        )

        categories = [category for category, _ in validated_pairs]
        if len(categories) > len(set(categories)):
            raise ValueError("Categories in category_amount_pairs must be unique.")

        total_amount = currency.zero_amount
        for category, amount in validated_pairs:
            if category.type_ not in valid_category_types:
                invalid_categories = [
                    category.path
                    for category in categories
                    if category.type_ not in valid_category_types
                ]
                valid_category_type_names = [
                    type_.name for type_ in valid_category_types
                ]
                raise InvalidCategoryTypeError(
                    f"Expected Category types: {', '.join(valid_category_type_names)}. "
                    "The following Categories are of different type: "
                    f"{', '.join(invalid_categories)}"
                )
            if amount.currency != currency:
                raise CurrencyError(
                    "Currency of CashAmounts in category_amount_pairs must match the "
                    "currency of the CashAccount."
                )
            if not amount.is_positive():
                raise ValueError(
                    "Second member of CashTransaction.category_amount_pairs "
                    "tuples must be a positive CashAmount."
                )
            total_amount += amount

        return validated_pairs, total_amount

    def _validate_category_amount_pairs_types(
        self,
        collection: Collection[tuple[Category, CashAmount | None]],
    ) -> tuple[tuple[Category, CashAmount]]:
        if len(collection) < 1:
            raise ValueError("Length of 'collection' must be at least 1.")

        if len(collection) == 1:
            category, amount = collection[0]
            if not isinstance(category, Category):
                raise TypeError(
                    "First element of 'collection' tuples must be of type Category."
                )
            if isinstance(amount, CashAmount):
                return collection
            if amount is None:
                # This means a split transaction can be made single-category without
                # specifying amount, using the current total.
                return ((category, self._amount),)
            raise TypeError(
                "Second element of 'collection' tuples must be of type CashAmount "
                "or None."
            )

        for first_member, second_member in collection:
            if not isinstance(first_member, Category):
                raise TypeError(
                    "First element of 'collection' tuples must be of type Category."
                )
            if not isinstance(second_member, CashAmount):
                raise TypeError(
                    "Second element of 'collection' tuples must be of type CashAmount."
                )
        return collection

    def _validate_tag_amount_pairs(
        self,
        tag_amount_pairs: Collection[tuple[Attribute, CashAmount | None]],
        max_tag_amount: CashAmount,
        currency: Currency,
    ) -> tuple[tuple[Attribute, CashAmount]]:
        _validate_collection_of_tuple_pairs(
            tag_amount_pairs, Attribute, (CashAmount, NoneType), 0
        )

        _tag_amount_pairs: list[tuple[Attribute, CashAmount]] = []
        for tag, amount in tag_amount_pairs:
            if tag.type_ != AttributeType.TAG:
                raise ValueError(
                    "The type_ of CashTransaction.tag_amount_pairs Attributes "
                    "must be TAG."
                )
            if amount is None:  # Tag amount unspecified
                for _tag, _amount in self._tag_amount_pairs:
                    if tag == _tag:
                        # If the Tag already exists, preserve amount
                        _tag_amount_pairs.append((tag, _amount))
                        break
                else:
                    # If the Tag is new, use the maximum amount
                    _tag_amount_pairs.append((tag, self._amount))
            else:
                if amount.currency != currency:
                    raise CurrencyError(
                        "Currency of CashAmounts in tag_amount_pairs must match the "
                        "currency of the CashAccount."
                    )
                if not (amount.is_positive() and amount <= max_tag_amount):
                    raise ValueError(
                        "Second member of CashTransaction.tag_amount_pairs "
                        "tuples must be a positive CashAmount which "
                        "does not exceed CashTransaction.amount."
                    )
                _tag_amount_pairs.append((tag, amount))

        return _tag_amount_pairs

    def _validate_refund(self, refund: "RefundTransaction") -> None:
        if not isinstance(refund, RefundTransaction):
            raise TypeError("Parameter 'refund' must be a RefundTransaction.")
        if refund.refunded_transaction != self:
            raise UnrelatedTransactionError(
                "Supplied RefundTransaction is not related to this CashTransaction."
            )

    def _get_valid_category_types(
        self, type_: CashTransactionType | None = None
    ) -> frozenset[CategoryType]:
        if type_ is None:
            type_ = self._type

        if type_ == CashTransactionType.INCOME:
            return frozenset((CategoryType.INCOME, CategoryType.DUAL_PURPOSE))
        return frozenset((CategoryType.EXPENSE, CategoryType.DUAL_PURPOSE))

    def _get_amount(self, account: CashAccount | None) -> CashAmount:  # noqa: ARG002
        if self.type_ == CashTransactionType.INCOME:
            return self._amount
        return self._amount_negative

    def _update_refunded_ratio(self) -> None:
        self._refunded_ratio = (
            sum(
                (refund.amount for refund in self.refunds),
                start=self.currency.zero_amount,
            )
            / self._amount
        )


class CashTransfer(CashRelatedTransaction):
    __slots__ = (
        "_accounts",
        "_amount_received",
        "_amount_sent",
        "_datetime",
        "_datetime_created",
        "_description",
        "_recipient",
        "_sender",
        "_tags",
        "_timestamp",
        "_uuid",
    )

    def __init__(  # noqa: PLR0913
        self,
        description: str,
        datetime_: datetime,
        sender: CashAccount,
        recipient: CashAccount,
        amount_sent: CashAmount,
        amount_received: CashAmount,
        uuid: UUID | None = None,
    ) -> None:
        super().__init__()
        if uuid is not None:
            self._uuid = uuid
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
    def accounts(self) -> frozenset[Account]:
        return self._accounts

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
            f"sender='{self._sender.name}', "
            f"received={self.amount_received}, "
            f"recipient='{self._recipient.name}', "
            f"{self.datetime_.strftime('%Y-%m-%d')})"
        )

    def is_account_related(self, account: Account) -> bool:
        return account in self._accounts

    def is_accounts_related(self, accounts: Collection[Account]) -> bool:
        return not self._accounts.isdisjoint(accounts)

    def prepare_for_deletion(self) -> None:
        self._sender.remove_transaction(self)
        self._recipient.remove_transaction(self)

    def serialize(self) -> dict[str, Any]:
        return {
            "datatype": "CashTransfer",
            "description": self._description,
            "datetime": self._datetime.replace(microsecond=0).isoformat(),
            "sender_path": self._sender.path,
            "recipient_path": self._recipient.path,
            "amount_sent": self._amount_sent.serialize(),
            "amount_received": self._amount_received.serialize(),
            "datetime_created": self._datetime_created.isoformat(),
            "uuid": str(self._uuid),
        }

    @staticmethod
    def deserialize(
        data: dict[str, Any],
        accounts: dict[str, Account],
        currencies: dict[str, Currency],
    ) -> "CashTransaction":
        description = data["description"]
        datetime_ = datetime.fromisoformat(data["datetime"])

        sender = accounts[data["sender_path"]]
        recipient = accounts[data["recipient_path"]]

        amount_sent = CashAmount.deserialize(data["amount_sent"], currencies)
        amount_received = CashAmount.deserialize(data["amount_received"], currencies)

        obj = CashTransfer(
            description=description,
            datetime_=datetime_,
            sender=sender,
            recipient=recipient,
            amount_sent=amount_sent,
            amount_received=amount_received,
            uuid=UUID(data["uuid"]),
        )
        obj._datetime_created = datetime.fromisoformat(
            data["datetime_created"]
        )
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
        block_account_update: bool = False,
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
            block_account_update=block_account_update,
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
        block_account_update: bool = False,
    ) -> None:
        update_sender = False
        update_recipient = False

        self._description = description.strip()
        if not block_account_update and hasattr(self, "_datetime"):
            update_sender = self._datetime != datetime_
            update_recipient = self._datetime != datetime_
        self._datetime = datetime_
        self._timestamp = datetime_.timestamp()

        if (
            not block_account_update
            and hasattr(self, "_amount_sent")
            and not update_sender
        ):
            update_sender = amount_sent != self._amount_sent
        if (
            not block_account_update
            and hasattr(self, "_amount_received")
            and not update_recipient
        ):
            update_recipient = amount_received != self._amount_received

        self._amount_sent = amount_sent
        self._amount_received = amount_received
        self._set_accounts(
            sender,
            recipient,
            update_sender=update_sender,
            update_recipient=update_recipient,
        )

    def _set_accounts(
        self,
        sender: CashAccount,
        recipient: CashAccount,
        *,
        update_sender: bool,
        update_recipient: bool,
    ) -> None:
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
        self._accounts = frozenset((self._sender, self._recipient))

        if add_sender:
            self._sender.add_transaction(self)
        elif update_sender:
            self._sender.update_balance()

        if add_recipient:
            self._recipient.add_transaction(self)
        elif update_recipient:
            self._recipient.update_balance()

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

    def _get_amount(self, account: CashAccount | None) -> CashAmount:
        if account is None:
            raise TypeError("Parameter 'account' must be a CashAccount.")
        if self.recipient == account:
            return self._amount_received
        return -self._amount_sent


class RefundTransaction(CashRelatedTransaction):
    """A refund which attaches itself to an expense CashTransaction"""

    __slots__ = (
        "_account",
        "_amount",
        "_are_tags_split",
        "_categories",
        "_category_amount_pairs",
        "_datetime",
        "_datetime_created",
        "_description",
        "_payee",
        "_refund_ratio",
        "_refunded_transaction",
        "_tag_amount_pairs",
        "_tags",
        "_timestamp",
        "_type",
        "_uuid",
    )

    def __init__(  # noqa: PLR0913
        self,
        description: str,
        datetime_: datetime,
        account: CashAccount,
        refunded_transaction: CashTransaction,
        payee: Attribute,
        category_amount_pairs: Collection[tuple[Category, CashAmount]],
        tag_amount_pairs: Collection[tuple[Attribute, CashAmount]],
        uuid: UUID | None = None,
    ) -> None:
        super().__init__()
        if uuid is not None:
            self._uuid = uuid
        self._set_refunded_transaction(refunded_transaction)
        self.set_attributes(
            description=description,
            datetime_=datetime_,
            account=account,
            category_amount_pairs=category_amount_pairs,
            tag_amount_pairs=tag_amount_pairs,
            payee=payee,
        )
        self._refunded_transaction.add_refund(self)

    @property
    def account(self) -> CashAccount:
        return self._account

    @property
    def amount(self) -> CashAmount:
        return self._amount

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
    def categories(self) -> frozenset[Category]:
        return self._categories

    @property
    def are_categories_split(self) -> bool:
        return len(self._category_amount_pairs) > 1

    @property
    def category_names(self) -> str:
        category_paths = [category.path for category, _ in self._category_amount_pairs]
        return ", ".join(category_paths)

    @property
    def tags(self) -> frozenset[Attribute]:
        return self._tags

    @property
    def tag_amount_pairs(self) -> tuple[tuple[Attribute, CashAmount], ...]:
        return self._tag_amount_pairs

    @property
    def are_tags_split(self) -> bool:
        return self._are_tags_split

    @property
    def payee(self) -> Attribute:
        return self._payee

    @property
    def refund_ratio(self) -> Decimal:
        return Decimal(self._amount / self.refunded_transaction.amount)

    def __repr__(self) -> str:
        return (
            f"RefundTransaction(account='{self._account.name}', "
            f"amount={self._amount}, "
            f"category={{{self.category_names}}}, "
            f"{self.datetime_.strftime('%Y-%m-%d')})"
        )

    def is_account_related(self, account: "Account") -> bool:
        return self._account == account

    def is_accounts_related(self, accounts: Collection[Account]) -> bool:
        return self._account in accounts

    def get_amount_for_category(self, category: Category, *, total: bool) -> CashAmount:
        return _get_amount_for_category(self, category, total=total)

    def get_amount_for_tag(self, tag: Attribute) -> CashAmount:
        for tag_, amount in self._tag_amount_pairs:
            if tag_ == tag:
                return amount
        raise ValueError(
            f"Tag '{tag.name}' not found in this RefundTransaction's tags."
        )

    def prepare_for_deletion(self) -> None:
        self._refunded_transaction.remove_refund(self)
        self._account.remove_transaction(self)

    def serialize(self) -> dict[str, Any]:
        tag_amount_pairs = [
            tag.name + ":" + amount.serialize()
            for tag, amount in self._tag_amount_pairs
        ]
        category_amount_pairs = [
            category.path + ":" + amount.serialize()
            for category, amount in self._category_amount_pairs
        ]
        return {
            "datatype": "RefundTransaction",
            "description": self._description,
            "datetime": self._datetime.replace(microsecond=0).isoformat(),
            "account_path": self._account.path,
            "refunded_transaction_uuid": str(self._refunded_transaction.uuid),
            "payee_name": self._payee.name,
            "category_amount_pairs": category_amount_pairs,
            "tag_amount_pairs": tag_amount_pairs,
            "datetime_created": self._datetime_created.isoformat(),
            "uuid": str(self._uuid),
        }

    @staticmethod
    def deserialize(  # noqa: PLR0913
        data: dict[str, Any],
        accounts: dict[str, Account],
        transactions: dict[UUID, Transaction],
        payees: dict[str, Attribute],
        categories: dict[str, Category],
        tags: dict[str, Attribute],
        currencies: dict[str, Currency],
    ) -> "CashTransaction":
        description = data["description"]
        datetime_ = datetime.fromisoformat(data["datetime"])
        cash_account = accounts[data["account_path"]]
        refunded_transaction_uuid = UUID(data["refunded_transaction_uuid"])
        refunded_transaction = transactions[refunded_transaction_uuid]
        payee = payees[data["payee_name"]]

        category_path_amount_pairs: list[str] = data["category_amount_pairs"]
        decoded_category_amount_pairs: list[tuple[Category, CashAmount]] = []
        for pair_string in category_path_amount_pairs:
            category_path, _, amount_str = pair_string.partition(":")
            category = categories[category_path]
            amount = CashAmount.deserialize(amount_str, currencies)
            decoded_category_amount_pairs.append((category, amount))

        tag_name_amount_strings: list[str] = data["tag_amount_pairs"]
        decoded_tag_amount_pairs: list[tuple[Attribute, CashAmount]] = []
        for pair_string in tag_name_amount_strings:
            tag_name, _, amount_str = pair_string.partition(":")
            tag = tags[tag_name]
            amount = CashAmount.deserialize(amount_str, currencies)
            decoded_tag_amount_pairs.append((tag, amount))

        obj = RefundTransaction(
            description=description,
            datetime_=datetime_,
            account=cash_account,
            refunded_transaction=refunded_transaction,
            payee=payee,
            category_amount_pairs=decoded_category_amount_pairs,
            tag_amount_pairs=decoded_tag_amount_pairs,
            uuid=UUID(data["uuid"]),
        )
        obj._datetime_created = datetime.fromisoformat(
            data["datetime_created"]
        )
        return obj

    def add_tags(self, tags: Collection[Attribute]) -> None:  # noqa: ARG002
        raise InvalidOperationError("Adding tags to RefundTransaction is forbidden.")

    def remove_tags(self, tags: Collection[Attribute]) -> None:  # noqa: ARG002
        raise InvalidOperationError(
            "Removing tags from RefundTransaction is forbidden."
        )

    def replace_tag(self, replaced_tag: Attribute, replacement_tag: Attribute) -> None:
        self._validate_tags((replaced_tag, replacement_tag))
        if replaced_tag not in self._tags:
            raise NotFoundError(
                f"Tag '{replaced_tag.name}' not found in this RefundTransaction's Tags."
            )
        tag_amount_pairs = list(self._tag_amount_pairs)
        if replacement_tag not in self._tags:
            for index, pair in enumerate(self._tag_amount_pairs):
                tag, amount = pair
                if tag == replaced_tag:
                    tag_amount_pairs[index] = (replacement_tag, amount)
        else:
            replaced_amount = abs(self.get_amount_for_tag(replaced_tag))
            replacement_amount = abs(self.get_amount_for_tag(replacement_tag))
            new_amount = min(self.amount, replaced_amount + replacement_amount)
            for index, pair in enumerate(self._tag_amount_pairs):
                tag, amount = pair
                if tag == replacement_tag:
                    tag_amount_pairs[index] = (replacement_tag, new_amount)
            tag_amount_pairs.remove((replaced_tag, replaced_amount))
        self._validate_tag_amount_pairs(
            tag_amount_pairs, self._refunded_transaction, self._amount
        )
        self._tag_amount_pairs = tuple(tag_amount_pairs)
        self._tags = frozenset(tag for tag, _ in tag_amount_pairs)

    def replace_payee(self, replacement_payee: Attribute) -> None:
        _validate_payee(replacement_payee)
        self._payee = replacement_payee

    def set_attributes(
        self,
        *,
        description: str | None = None,
        datetime_: datetime | None = None,
        account: CashAccount | None = None,
        category_amount_pairs: Collection[tuple[Category, CashAmount]] | None = None,
        tag_amount_pairs: Collection[tuple[Attribute, CashAmount]] | None = None,
        payee: Attribute | None = None,
        block_account_update: bool = False,
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
            block_account_update=block_account_update,
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
            start=currency.zero_amount,
        )
        self._validate_tag_amount_pairs(
            tag_amount_pairs, self._refunded_transaction, max_tag_amount
        )
        _validate_payee(payee)

    def _set_attributes(
        self,
        *,
        description: str,
        datetime_: datetime,
        account: CashAccount,
        category_amount_pairs: Collection[tuple[Category, CashAmount]],
        tag_amount_pairs: Collection[tuple[Attribute, CashAmount]],
        payee: Attribute,
        block_account_update: bool = False,
    ) -> None:
        update_account = False

        self._description = description.strip()
        if not block_account_update and hasattr(self, "_datetime"):
            update_account = self._datetime != datetime_

        self._datetime = datetime_
        self._timestamp = datetime_.timestamp()

        _category_amount_pairs = tuple(category_amount_pairs)
        if (
            not block_account_update
            and hasattr(self, "_category_amount_pairs")
            and not update_account
        ):
            update_account = self._category_amount_pairs != _category_amount_pairs

        self._category_amount_pairs = tuple(category_amount_pairs)
        self._tag_amount_pairs = tuple(tag_amount_pairs)
        self._payee = payee

        self._update_cached_data(account.currency)
        self._set_account(account, update_account=update_account)

    def _set_account(self, account: CashAccount, *, update_account: bool) -> None:
        if hasattr(self, "_account"):
            if self._account == account:
                if update_account:
                    self._account.update_balance()
                return
            self._account.remove_transaction(self)
        self._account = account
        self._account.add_transaction(self)

    def _update_cached_data(self, currency: Currency) -> None:
        total_amount = currency.zero_amount
        categories: set[Category] = set()
        for category, amount in self._category_amount_pairs:
            total_amount += amount
            categories.add(category)
        self._amount = total_amount
        self._categories = frozenset(categories)

        tags: set[Attribute] = set()
        self._are_tags_split = False
        for tag, amount in self._tag_amount_pairs:
            tags.add(tag)
            if not self._are_tags_split and amount != self._amount:
                self._are_tags_split = True
        self._tags = frozenset(tags)

    def _validate_datetime(
        self, value: datetime, refunded_transaction_datetime: datetime
    ) -> None:
        super()._validate_datetime(value)
        if value < refunded_transaction_datetime:
            raise RefundPrecedesTransactionError(
                "Supplied RefundTransaction.datetime_ precedes this "
                "CashTransaction.datetime_."
            )

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

    def _validate_category_amount_pairs(
        self,
        pairs: Collection[tuple[Category, CashAmount]],
        refunded_transaction: CashTransaction,
        currency: Currency,
    ) -> None:
        no_of_categories = len(refunded_transaction.category_amount_pairs)
        _validate_collection_of_tuple_pairs(
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
        refund_amount = sum((amount for _, amount in pairs), start=currency.zero_amount)
        if not refund_amount.value_rounded > 0:
            raise ValueError("Total refunded amount must be positive.")

        for category, amount in pairs:
            max_amount = refunded_transaction.get_max_refundable_for_category(
                category, ignore_refund=self
            )
            if amount > max_amount:
                raise ValueError(
                    f"Refunded amount for category '{category.path}' must not exceed "
                    f"{max_amount}."
                )

    def _validate_tag_amount_pairs(
        self,
        pairs: Collection[tuple[Attribute, CashAmount]],
        refunded_transaction: CashTransaction,
        refund_amount: CashAmount,
    ) -> None:
        expected_tags = {tag for tag, _ in refunded_transaction.tag_amount_pairs}
        no_of_tags = len(expected_tags)
        _validate_collection_of_tuple_pairs(pairs, Attribute, CashAmount, no_of_tags)

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

        for tag, amount in pairs:
            max_value = refunded_transaction.get_max_refundable_for_tag(
                tag, ignore_refund=self, refund_amount=refund_amount
            )
            min_value = refunded_transaction.get_min_refundable_for_tag(
                tag, ignored_refund=self, refund_amount=refund_amount
            )
            if amount > max_value or amount < min_value:
                raise ValueError(
                    f"Refunded amount for tag '{tag.name}' must be within "
                    f"{min_value} and {max_value}."
                )

    def _get_amount(self, account: CashAccount | None) -> CashAmount:  # noqa: ARG002
        return self._amount


def _validate_payee(payee: Attribute) -> None:
    if not isinstance(payee, Attribute):
        raise TypeError("Payee must be an Attribute.")
    if not payee.type_ == AttributeType.PAYEE:
        raise ValueError("The type_ of payee Attribute must be PAYEE.")


def _validate_collection_of_tuple_pairs(
    collection: Collection[tuple[Any, Any]],
    first_type: type | tuple[type, ...],
    second_type: type | tuple[type, ...],
    min_length: int,
) -> None:
    if not isinstance(collection, Collection):
        raise TypeError("Parameter 'collection' must be a Collection.")
    if len(collection) < min_length:
        raise ValueError(f"Length of 'collection' must be at least {min_length}.")
    for element in collection:
        if not isinstance(element, tuple):
            raise TypeError("Elements of 'collection' must be tuples.")
    first_members = []
    for first_member, second_member in collection:
        if not isinstance(first_member, first_type):
            raise TypeError(
                "First element of 'collection' tuples must be of type "
                f"{first_type.__name__}."
            )
        if not isinstance(second_member, second_type):
            if isinstance(second_type, type):
                raise TypeError(
                    "Second element of 'collection' tuples must be of type "
                    f"{second_type.__name__}."
                )
            raise TypeError(
                "Second element of 'collection' tuples must be any of following types: "
                f"{second_type}."
            )
        first_members.append(first_member)
    if len(first_members) > len(set(first_members)):
        raise ValueError("Categories or Tags in tuple pairs must be unique.")


def _is_category_related(category: Category, categories: Collection[Category]) -> bool:
    if category in categories:
        return True
    # check if 'category' is a parent of any of the Categories in 'categories'
    descendants = category.descendants
    for _category in categories:  # noqa: SIM110
        if _category in descendants:
            return True
    return False


def _get_amount_for_category(
    transaction: CashTransaction | RefundTransaction, category: Category, *, total: bool
) -> CashAmount:
    running_sum = transaction.currency.zero_amount

    func = (
        operator.add
        if isinstance(transaction, RefundTransaction)
        or transaction.type_ == CashTransactionType.INCOME
        else operator.sub
    )

    descendants = category.descendants if total else ()

    for _category, _amount in transaction.category_amount_pairs:
        if _category == category:
            running_sum = func(running_sum, _amount)
            continue
        if total and _category in descendants:
            running_sum = func(running_sum, _amount)
    return running_sum
