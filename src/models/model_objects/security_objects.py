import copy
import string
import uuid
from abc import ABC, abstractmethod
from collections import defaultdict
from collections.abc import Collection
from datetime import date, datetime
from decimal import Decimal
from enum import Enum, auto
from typing import Any

from src.models.base_classes.account import Account, UnrelatedAccountError
from src.models.base_classes.transaction import Transaction
from src.models.custom_exceptions import InvalidCharacterError, TransferSameAccountError
from src.models.mixins.copyable_mixin import CopyableMixin
from src.models.mixins.json_serializable_mixin import JSONSerializableMixin
from src.models.mixins.name_mixin import NameMixin
from src.models.mixins.uuid_mixin import UUIDMixin
from src.models.model_objects.account_group import AccountGroup
from src.models.model_objects.cash_objects import CashAccount, CashRelatedTransaction
from src.models.model_objects.currency_objects import (
    CashAmount,
    Currency,
    CurrencyError,
)
from src.models.utilities.find_helpers import (
    find_account_by_uuid,
    find_account_group_by_path,
    find_currency_by_code,
    find_security_by_uuid,
)


class PriceNotFoundError(ValueError):
    """Raised when Security price does not exist."""


class SecurityTransactionType(Enum):
    BUY = auto()
    SELL = auto()


class Security(CopyableMixin, NameMixin, UUIDMixin, JSONSerializableMixin):
    NAME_MIN_LENGTH = 1
    NAME_MAX_LENGTH = 64
    TYPE_MIN_LENGTH = 1
    TYPE_MAX_LENGTH = 32
    SYMBOL_MIN_LENGTH = 0
    SYMBOL_MAX_LENGTH = 8
    SYMBOL_ALLOWED_CHARS = string.ascii_letters + string.digits + "."

    def __init__(
        self,
        name: str,
        symbol: str,
        type_: str,
        currency: Currency,
        shares_unit: Decimal | int | str,
        price_places: int | None = None,
    ) -> None:
        super().__init__(name=name, allow_slash=True)
        self.symbol = symbol
        self.type_ = type_

        if not isinstance(currency, Currency):
            raise TypeError("Security.currency must be a Currency.")
        self._currency = currency

        if not isinstance(shares_unit, (Decimal, int, str)):
            raise TypeError(
                "Security.shares_unit must be a Decimal, integer or a string "
                "containing a number."
            )
        _shares_unit = Decimal(shares_unit)
        if not _shares_unit.is_finite() or _shares_unit <= 0:
            raise ValueError("Security.shares_unit must be finite and positive.")
        self._shares_unit = _shares_unit

        if price_places is None:
            self._places = self._currency.places
        else:
            if not isinstance(price_places, int):
                raise TypeError("Security.places must be an integer or None.")
            if price_places < self._currency.places:
                raise ValueError(
                    "Security.places must not be smaller than Security.currency.places."
                )
            self._places = price_places

        self._price_history: dict[date, CashAmount] = {}

    @property
    def type_(self) -> str:
        return self._type

    @type_.setter
    def type_(self, value: str) -> None:
        if not isinstance(value, str):
            raise TypeError("Security.type_ must be a string.")
        if len(value) < self.TYPE_MIN_LENGTH or len(value) > self.TYPE_MAX_LENGTH:
            raise ValueError(
                "Security.type_ length must be within "
                f"{self.TYPE_MIN_LENGTH} and {self.TYPE_MAX_LENGTH}"
            )
        self._type = value

    @property
    def currency(self) -> Currency:
        return self._currency

    @property
    def symbol(self) -> str:
        return self._symbol

    @symbol.setter
    def symbol(self, value: str) -> None:
        if not isinstance(value, str):
            raise TypeError("Security.symbol must be a string.")
        if len(value) < self.SYMBOL_MIN_LENGTH or len(value) > self.SYMBOL_MAX_LENGTH:
            raise ValueError(
                "Security.symbol length must be within "
                f"{self.SYMBOL_MIN_LENGTH} and {self.SYMBOL_MAX_LENGTH}"
            )
        if any(char not in self.SYMBOL_ALLOWED_CHARS for char in value):
            raise InvalidCharacterError(
                "Security.symbol can contain only ASCII letters, digits or a period."
            )
        self._symbol = value.upper()

    @property
    def price(self) -> CashAmount:
        if len(self._price_history) == 0:
            return CashAmount(Decimal(0), self.currency)
        latest_date = self.latest_date
        return self._price_history[latest_date]

    @property
    def latest_date(self) -> date | None:
        if len(self._price_history) == 0:
            return None
        return max(date_ for date_ in self._price_history)

    @property
    def price_history(self) -> dict[date, CashAmount]:
        return copy.deepcopy(self._price_history)

    @property
    def price_places(self) -> int:
        return self._places

    @property
    def shares_unit(self) -> Decimal:
        return self._shares_unit

    def __repr__(self) -> str:
        return f"Security('{self.name}')"

    def set_price(self, date_: date, price: CashAmount) -> None:
        if not isinstance(date_, date):
            raise TypeError("Parameter 'date_' must be a date.")
        if not isinstance(price, CashAmount):
            raise TypeError("Parameter 'price' must be a CashAmount.")
        if price.currency != self.currency:
            raise CurrencyError("Security.currency and price.currency must match.")
        self._price_history[date_] = CashAmount(
            round(price.value, self._places), self.currency
        )

    # TODO: shares_unit can be serialized directly
    # TODO: price history must be saved
    def serialize(self) -> dict[str, Any]:
        return {
            "datatype": "Security",
            "name": self._name,
            "symbol": self._symbol,
            "type_": self._type,
            "currency_code": self._currency.code,
            "shares_unit": self._shares_unit,
            "price_places": self._places,
            "uuid": str(self._uuid),
        }

    @staticmethod
    def deserialize(
        data: dict[str, Any], currencies: Collection[Currency]
    ) -> "Security":
        name = data["name"]
        symbol = data["symbol"]
        type_ = data["type_"]

        currency_code = data["currency_code"]
        security_currency = find_currency_by_code(currency_code, currencies)

        shares_unit = data["shares_unit"]
        price_places = data["price_places"]
        obj = Security(
            name, symbol, type_, security_currency, shares_unit, price_places
        )
        obj._uuid = uuid.UUID(data["uuid"])
        return obj


# IDEA: maybe add shares / balance history
class SecurityAccount(Account):
    def __init__(self, name: str, parent: AccountGroup | None = None) -> None:
        super().__init__(name, parent)
        self._securities: defaultdict[Security, Decimal] = defaultdict(
            lambda: Decimal(0)
        )
        self._transactions: list[SecurityRelatedTransaction] = []

    @property
    def securities(self) -> dict[Security, Decimal]:
        return copy.deepcopy(self._securities)

    @property
    def transactions(self) -> tuple["SecurityRelatedTransaction", ...]:
        return tuple(self._transactions)

    def __repr__(self) -> str:
        return f"SecurityAccount(path='{self.path}')"

    def get_balance(self, currency: Currency) -> CashAmount:
        return sum(
            (
                security.price.convert(currency) * shares
                for security, shares in self._securities.items()
            ),
            start=CashAmount(0, currency),
        )

    def add_transaction(self, transaction: "SecurityRelatedTransaction") -> None:
        self._validate_transaction(transaction)
        self._securities[transaction.security] += transaction.get_shares(self)
        self._transactions.append(transaction)

    def remove_transaction(self, transaction: "SecurityRelatedTransaction") -> None:
        self._validate_transaction(transaction)
        self._securities[transaction.security] -= transaction.get_shares(self)
        self._transactions.remove(transaction)

    def serialize(self) -> dict[str, Any]:
        index = self.parent.children.index(self) if self.parent is not None else None
        return {
            "datatype": "SecurityAccount",
            "path": self.path,
            "index": index,
            "uuid": str(self._uuid),
        }

    @staticmethod
    def deserialize(
        data: dict[str, Any], account_groups: Collection[AccountGroup]
    ) -> "SecurityAccount":
        path: str = data["path"]
        index: int | None = data["index"]
        parent_path, _, name = path.rpartition("/")

        obj = SecurityAccount(name)
        obj._uuid = uuid.UUID(data["uuid"])

        if parent_path != "":
            obj._parent = find_account_group_by_path(parent_path, account_groups)
            obj._parent._children[index] = obj
        return obj

    def _validate_transaction(self, transaction: "SecurityRelatedTransaction") -> None:
        if not isinstance(transaction, SecurityRelatedTransaction):
            raise TypeError(
                "Parameter 'transaction' must be a SecurityRelatedTransaction."
            )
        if not transaction.is_account_related(self):
            raise UnrelatedAccountError(
                "This SecurityAccount is not related to the provided "
                "SecurityRelatedTransaction."
            )
        return


class SecurityRelatedTransaction(Transaction, ABC):
    def __init__(
        self,
    ) -> None:
        super().__init__()

    @property
    def security(self) -> Security:
        return self._security

    @property
    def shares(self) -> Decimal:
        return self._shares

    def get_shares(self, account: SecurityAccount) -> Decimal:
        if not isinstance(account, SecurityAccount):
            raise TypeError("Parameter 'account' must be a SecurityAccount.")
        if not self.is_account_related(account):
            raise UnrelatedAccountError(
                f"SecurityAccount '{account.name}' is not related to this "
                f"{self.__class__.__name__}."
            )
        return self._get_shares(account)

    def _validate_security(self, security: Security) -> None:
        if not isinstance(security, Security):
            raise TypeError(f"{self.__class__.__name__}.security must be a Security.")

    def _validate_shares(
        self, value: Decimal | int | str, shares_unit: Decimal
    ) -> None:
        if not isinstance(value, (Decimal, int, str)):
            raise TypeError(
                f"{self.__class__.__name__}.shares must be a Decimal, integer "
                "or a string containing a number."
            )
        _value = Decimal(value)
        if not _value.is_finite() or _value <= 0:
            raise ValueError(
                f"{self.__class__.__name__}.shares must be a finite positive number."
            )
        if _value % shares_unit != 0:
            raise ValueError(
                f"{self.__class__.__name__}.shares must be a multiple of "
                f"{shares_unit}."
            )

    @abstractmethod
    def _get_shares(self, account: SecurityAccount) -> Decimal:
        raise NotImplementedError


class SecurityTransaction(CashRelatedTransaction, SecurityRelatedTransaction):
    def __init__(
        self,
        description: str,
        datetime_: datetime,
        type_: SecurityTransactionType,
        security: Security,
        shares: Decimal | int | str,
        price_per_share: CashAmount,
        security_account: SecurityAccount,
        cash_account: CashAccount,
    ) -> None:
        super().__init__()
        self.set_attributes(
            description=description,
            datetime_=datetime_,
            type_=type_,
            security=security,
            shares=shares,
            price_per_share=price_per_share,
            security_account=security_account,
            cash_account=cash_account,
        )

    @property
    def type_(self) -> SecurityTransactionType:
        return self._type

    @property
    def security_account(self) -> SecurityAccount:
        return self._security_account

    @property
    def cash_account(self) -> CashAccount:
        return self._cash_account

    @property
    def price_per_share(self) -> CashAmount:
        return self._price_per_share

    @property
    def currency(self) -> Currency:
        return self._cash_account.currency

    @property
    def currencies(self) -> tuple[Currency]:
        return (self._cash_account.currency,)

    def __repr__(self) -> str:
        return (
            f"SecurityTransaction({self.type_.name}, "
            f"security='{self.security.symbol}', "
            f"shares={self.shares}, "
            f"{self.datetime_.strftime('%Y-%m-%d')})"
        )

    def is_account_related(self, account: Account) -> bool:
        return account == self._cash_account or account == self._security_account

    def prepare_for_deletion(self) -> None:
        self._cash_account.remove_transaction(self)
        self._security_account.remove_transaction(self)

    def serialize(self) -> dict[str, Any]:
        return {
            "datatype": "SecurityTransaction",
            "description": self._description,
            "datetime_": self._datetime,
            "type_": self._type.name,
            "security_uuid": str(self._security.uuid),
            "shares": self._shares,
            "price_per_share": self._price_per_share,
            "security_account_uuid": str(self._security_account.uuid),
            "cash_account_uuid": str(self._cash_account.uuid),
            "datetime_created": self._datetime_created,
            "uuid": str(self._uuid),
        }

    @staticmethod
    def deserialize(
        data: dict[str, Any],
        accounts: list[Account],
        currencies: list[Currency],
        securities: list[Security],
    ) -> "SecurityTransaction":
        description = data["description"]
        datetime_ = data["datetime_"]
        type_ = SecurityTransactionType[data["type_"]]
        shares = data["shares"]
        price_per_share = CashAmount.deserialize(data["price_per_share"], currencies)

        security_uuid = uuid.UUID(data["security_uuid"])
        security = find_security_by_uuid(security_uuid, securities)

        cash_account_uuid = uuid.UUID(data["cash_account_uuid"])
        security_account_uuid = uuid.UUID(data["security_account_uuid"])
        cash_account = find_account_by_uuid(cash_account_uuid, accounts)
        security_account = find_account_by_uuid(security_account_uuid, accounts)

        obj = SecurityTransaction(
            description=description,
            datetime_=datetime_,
            type_=type_,
            security=security,
            shares=shares,
            price_per_share=price_per_share,
            security_account=security_account,
            cash_account=cash_account,
        )
        obj._datetime_created = data["datetime_created"]
        obj._uuid = uuid.UUID(data["uuid"])
        return obj

    def set_attributes(
        self,
        *,
        description: str | None = None,
        datetime_: datetime | None = None,
        type_: SecurityTransactionType | None = None,
        security: Security | None = None,
        shares: Decimal | None = None,
        price_per_share: CashAmount | None = None,
        security_account: SecurityAccount | None = None,
        cash_account: CashAccount | None = None,
    ) -> None:
        if description is None:
            description = self._description
        if datetime_ is None:
            datetime_ = self._datetime
        if type_ is None:
            type_ = self._type
        if security is None:
            security = self._security
        if shares is None:
            shares = self._shares
        if price_per_share is None:
            price_per_share = self._price_per_share
        if security_account is None:
            security_account = self._security_account
        if cash_account is None:
            cash_account = self._cash_account

        self.validate_attributes(
            description=description,
            datetime_=datetime_,
            type_=type_,
            security=security,
            shares=shares,
            price_per_share=price_per_share,
            security_account=security_account,
            cash_account=cash_account,
        )

        self._set_attributes(
            description=description,
            datetime_=datetime_,
            type_=type_,
            security=security,
            shares=shares,
            price_per_share=price_per_share,
            security_account=security_account,
            cash_account=cash_account,
        )

    def validate_attributes(
        self,
        *,
        description: str | None = None,
        datetime_: datetime | None = None,
        type_: SecurityTransactionType | None = None,
        security: Security | None = None,
        shares: Decimal | None = None,
        price_per_share: CashAmount | None = None,
        security_account: SecurityAccount | None = None,
        cash_account: CashAccount | None = None,
    ) -> None:
        if description is None:
            description = self._description
        if datetime_ is None:
            datetime_ = self._datetime
        if type_ is None:
            type_ = self._type
        if security is None:
            security = self._security
        if shares is None:
            shares = self._shares
        if price_per_share is None:
            price_per_share = self._price_per_share
        if security_account is None:
            security_account = self._security_account
        if cash_account is None:
            cash_account = self._cash_account

        self._validate_type(type_)
        self._validate_description(description)
        self._validate_datetime(datetime_)
        self._validate_security(security)
        self._validate_shares(shares, security.shares_unit)
        self._validate_cash_account(cash_account, security.currency)
        self._validate_security_account(security_account)
        self._validate_amount(price_per_share, cash_account.currency)

    def _set_attributes(
        self,
        *,
        description: str,
        datetime_: datetime,
        type_: SecurityTransactionType,
        security: Security,
        shares: Decimal,
        price_per_share: CashAmount,
        security_account: SecurityAccount,
        cash_account: CashAccount,
    ) -> None:
        self._description = description
        self._datetime = datetime_
        self._type = type_
        self._security = security
        self._shares = Decimal(shares)
        self._price_per_share = price_per_share
        self._set_accounts(security_account, cash_account)

    def _set_accounts(
        self, security_account: SecurityAccount, cash_account: CashAccount
    ) -> None:
        add_security_account = True
        add_cash_account = True

        if hasattr(self, "_security_account"):
            if self._security_account != security_account:
                self._security_account.remove_transaction(self)
            else:
                add_security_account = False
        if hasattr(self, "_cash_account"):
            if self._cash_account != cash_account:
                self._cash_account.remove_transaction(self)
            else:
                add_cash_account = False

        self._security_account = security_account
        self._cash_account = cash_account

        if add_security_account:
            self._security_account.add_transaction(self)
        if add_cash_account:
            self._cash_account.add_transaction(self)

    def _validate_type(self, type_: SecurityTransactionType) -> None:
        if not isinstance(type_, SecurityTransactionType):
            raise TypeError(
                "SecurityTransaction.type_ must be a SecurityTransactionType."
            )

    def _validate_security_account(self, new_account: SecurityAccount) -> None:
        if not isinstance(new_account, SecurityAccount):
            raise TypeError(
                "SecurityTransaction.security_account must be a SecurityAccount."
            )

    def _validate_cash_account(
        self, new_account: CashAccount, currency: Currency
    ) -> None:
        if not isinstance(new_account, CashAccount):
            raise TypeError("SecurityTransaction.cash_account must be a CashAccount.")
        if new_account.currency != currency:
            raise CurrencyError(
                "The currencies of SecurityTransaction.security and "
                "SecurityTransaction.cash_account must match."
            )

    def _validate_amount(self, amount: CashAmount, currency: Currency) -> None:
        if not isinstance(amount, CashAmount):
            raise TypeError("SecurityTransaction amounts must be CashAmounts.")
        if amount.is_negative():
            raise ValueError("SecurityTransaction amounts must not be negative.")
        if amount.currency != currency:
            raise CurrencyError("Invalid CashAmount currency.")

    def _get_amount(self, account: CashAccount) -> CashAmount:  # noqa: U100
        if self.type_ == SecurityTransactionType.BUY:
            return -self._shares * self.price_per_share
        return self._shares * self.price_per_share

    def _get_shares(self, account: SecurityAccount) -> Decimal:  # noqa: U100
        if self.type_ == SecurityTransactionType.BUY:
            return self.shares
        return -self.shares


class SecurityTransfer(SecurityRelatedTransaction):
    def __init__(
        self,
        description: str,
        datetime_: datetime,
        security: Security,
        shares: Decimal | int | str,
        sender: SecurityAccount,
        recipient: SecurityAccount,
    ) -> None:
        super().__init__()
        self.set_attributes(
            description=description,
            datetime_=datetime_,
            security=security,
            shares=shares,
            sender=sender,
            recipient=recipient,
        )

    @property
    def sender(self) -> SecurityAccount:
        return self._sender

    @property
    def recipient(self) -> SecurityAccount:
        return self._recipient

    def __repr__(self) -> str:
        return (
            f"SecurityTransfer(security='{self.security.symbol}', "
            f"shares={self.shares}, "
            f"from='{self.sender.name}', "
            f"to='{self.recipient.name}', "
            f"{self.datetime_.strftime('%Y-%m-%d')})"
        )

    def is_account_related(self, account: Account) -> bool:
        return account == self.sender or account == self.recipient

    def prepare_for_deletion(self) -> None:
        self._sender.remove_transaction(self)
        self._recipient.remove_transaction(self)

    def serialize(self) -> dict[str, Any]:
        return {
            "datatype": "SecurityTransfer",
            "description": self._description,
            "datetime_": self._datetime,
            "security_uuid": str(self._security.uuid),
            "shares": self._shares,
            "sender_uuid": str(self._sender.uuid),
            "recipient_uuid": str(self._recipient.uuid),
            "datetime_created": self._datetime_created,
            "uuid": str(self._uuid),
        }

    @staticmethod
    def deserialize(
        data: dict[str, Any],
        accounts: list[Account],
        securities: list[Security],
    ) -> "SecurityTransfer":
        description = data["description"]
        datetime_ = data["datetime_"]
        shares = data["shares"]

        security_uuid = uuid.UUID(data["security_uuid"])
        security = find_security_by_uuid(security_uuid, securities)

        sender_uuid = uuid.UUID(data["sender_uuid"])
        recipient_uuid = uuid.UUID(data["recipient_uuid"])
        sender = find_account_by_uuid(sender_uuid, accounts)
        recipient = find_account_by_uuid(recipient_uuid, accounts)

        obj = SecurityTransfer(
            description=description,
            datetime_=datetime_,
            security=security,
            shares=shares,
            sender=sender,
            recipient=recipient,
        )
        obj._datetime_created = data["datetime_created"]
        obj._uuid = uuid.UUID(data["uuid"])
        return obj

    def set_attributes(
        self,
        *,
        description: str | None = None,
        datetime_: datetime | None = None,
        security: Security | None = None,
        shares: Decimal | None = None,
        sender: SecurityAccount | None = None,
        recipient: SecurityAccount | None = None,
    ) -> None:
        if description is None:
            description = self._description
        if datetime_ is None:
            datetime_ = self._datetime
        if security is None:
            security = self._security
        if shares is None:
            shares = self._shares
        if sender is None:
            sender = self._sender
        if recipient is None:
            recipient = self._recipient

        self.validate_attributes(
            description=description,
            datetime_=datetime_,
            security=security,
            shares=shares,
            sender=sender,
            recipient=recipient,
        )

        self._set_attributes(
            description=description,
            datetime_=datetime_,
            security=security,
            shares=shares,
            sender=sender,
            recipient=recipient,
        )

    def validate_attributes(
        self,
        *,
        description: str | None = None,
        datetime_: datetime | None = None,
        security: Security | None = None,
        shares: Decimal | None = None,
        sender: SecurityAccount | None = None,
        recipient: SecurityAccount | None = None,
    ) -> None:
        if description is None:
            description = self._description
        if datetime_ is None:
            datetime_ = self._datetime
        if security is None:
            security = self._security
        if shares is None:
            shares = self._shares
        if sender is None:
            sender = self._sender
        if recipient is None:
            recipient = self._recipient

        self._validate_description(description)
        self._validate_datetime(datetime_)
        self._validate_security(security)
        self._validate_shares(shares, security.shares_unit)
        self._validate_accounts(sender, recipient)

    def _set_attributes(
        self,
        *,
        description: str,
        datetime_: datetime,
        security: Security,
        shares: Decimal,
        sender: SecurityAccount,
        recipient: SecurityAccount,
    ) -> None:
        self._description = description
        self._datetime = datetime_
        self._security = security
        self._shares = shares
        self._set_accounts(sender, recipient)

    def _validate_accounts(
        self, sender: SecurityAccount, recipient: SecurityAccount
    ) -> None:
        if not isinstance(sender, SecurityAccount):
            raise TypeError("SecurityTransfer.sender must be a SecurityAccount.")
        if not isinstance(recipient, SecurityAccount):
            raise TypeError("SecurityTransfer.recipient must be a SecurityAccount.")
        if sender == recipient:
            raise TransferSameAccountError(
                "SecurityTransaction sender and recipient must be different "
                "SecurityAccounts."
            )

    def _set_accounts(
        self, sender: SecurityAccount, recipient: SecurityAccount
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

        if add_sender:
            self._sender.add_transaction(self)
        if add_recipient:
            self._recipient.add_transaction(self)

    def _get_shares(self, account: SecurityAccount) -> Decimal:
        if account == self._sender:
            return -self.shares
        return self.shares
