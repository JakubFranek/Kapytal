import copy
import logging
import string
from abc import ABC, abstractmethod
from bisect import bisect_right
from collections import defaultdict
from collections.abc import Collection
from datetime import date, datetime, timedelta
from decimal import Decimal
from enum import Enum, auto
from types import NoneType
from typing import Any
from uuid import UUID

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
from src.models.user_settings import user_settings
from src.presenters.utilities.event import Event


class PriceNotFoundError(ValueError):
    """Raised when Security price does not exist."""


class SecurityTransactionType(Enum):
    BUY = auto()
    SELL = auto()
    DIVIDEND = auto()


class SharesType(Enum):
    BOUGHT = auto()
    SOLD = auto()
    TRANSFERRED = auto()
    PAID_DIVIDEND = auto()


class Security(CopyableMixin, NameMixin, UUIDMixin, JSONSerializableMixin):
    __slots__ = (
        "_uuid",
        "_name",
        "_symbol",
        "_type",
        "_currency",
        "_shares_decimals",
        "_price_history",
        "_price_history_pairs",
        "_price_decimals",
        "_earliest_date",
        "_latest_date",
        "_latest_price",
        "_allow_slash",
        "_allow_colon",
        "event_price_updated",
        "_recalculate_price_history_pairs",
    )

    NAME_MIN_LENGTH = 1
    NAME_MAX_LENGTH = 64
    TYPE_MIN_LENGTH = 1
    TYPE_MAX_LENGTH = 32
    SYMBOL_MIN_LENGTH = 0
    SYMBOL_MAX_LENGTH = 8
    SYMBOL_ALLOWED_CHARS = string.ascii_letters + string.digits + "."
    SHARES_DECIMALS_MAX = 18

    def __init__(  # noqa: PLR0913
        self,
        name: str,
        symbol: str,
        type_: str,
        currency: Currency,
        shares_decimals: int,
    ) -> None:
        super().__init__(name=name, allow_slash=True)
        self.symbol = symbol
        self.type_ = type_

        if not isinstance(currency, Currency):
            raise TypeError("Security.currency must be a Currency.")
        self._currency = currency

        if not isinstance(shares_decimals, int):
            raise TypeError("Security.shares_decimals must be an integer.")
        if shares_decimals < 0:
            raise ValueError("Security.shares_decimals must not be negative.")
        if shares_decimals > self.SHARES_DECIMALS_MAX:
            raise ValueError(
                "Security.shares_decimals must be less than or equal to "
                f"{self.SHARES_DECIMALS_MAX}."
            )
        self._shares_decimals = shares_decimals

        self._price_history: dict[date, CashAmount] = {}
        self._price_history_pairs: tuple[tuple[date, CashAmount], ...] = ()
        self._price_decimals = 0
        self._recalculate_price_history_pairs = False
        self.event_price_updated = Event()

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

        value_capitalized = value.upper()
        self._symbol = value_capitalized

    @property
    def price(self) -> CashAmount:
        if hasattr(self, "_latest_price"):
            return self._latest_price
        return CashAmount(Decimal("NaN"), self._currency)

    @property
    def earliest_date(self) -> date | None:
        if hasattr(self, "_earliest_date"):
            return self._earliest_date
        return None

    @property
    def latest_date(self) -> date | None:
        if hasattr(self, "_latest_date"):
            return self._latest_date
        return None

    @property
    def price_history(self) -> dict[date, CashAmount]:
        return self._price_history

    @property
    def price_history_pairs(self) -> tuple[tuple[date, CashAmount], ...]:
        if self._recalculate_price_history_pairs:
            pairs = sorted(self._price_history.items())
            self._price_history_pairs = tuple(pairs)
            self._recalculate_price_history_pairs = False
        return self._price_history_pairs

    @property
    def decimal_price_history_pairs(self) -> tuple[tuple[date, Decimal]]:
        return tuple(
            (date_, price.value_normalized) for date_, price in self.price_history_pairs
        )

    @property
    def shares_decimals(self) -> int:
        return self._shares_decimals

    @property
    def price_decimals(self) -> int:
        return self._price_decimals

    def __repr__(self) -> str:
        return f"Security('{self._name}')"

    def __str__(self) -> str:
        return self._name

    def get_price(self, date_: date | None = None) -> CashAmount:
        if date_ is None:
            return self.price
        try:
            return self._price_history[date_]
        except KeyError:
            index = bisect_right(self.price_history_pairs, date_, key=lambda x: x[0])
            if index:  # zero if date_ is earliest or history is empty
                _, price = self.price_history_pairs[index - 1]
                return price
            logging.warning(f"{self!s}: no price found, returning CashAmount('NaN')")
            return CashAmount(Decimal("NaN"), self._currency)

    def set_price(self, date_: date, price: CashAmount, *, update: bool = True) -> None:
        self._validate_date(date_)
        self._validate_price(price)
        self._price_history[date_] = price
        if update:
            self.update_values()

    def set_prices(
        self,
        date_price_tuples: Collection[tuple[date, CashAmount]],
        *,
        update: bool = True,
    ) -> None:
        for date_, price in date_price_tuples:
            self._validate_date(date_)
            self._validate_price(price)
            self._price_history[date_] = price
        if update:
            self.update_values()

    def delete_price(self, date_: date, *, update: bool = True) -> None:
        del self._price_history[date_]
        if update:
            self.update_values()

    def calculate_return(
        self, start: date | None = None, end: date | None = None
    ) -> Decimal:
        """Returns the Security return as a percentage."""
        if not hasattr(self, "_earliest_date") or self._earliest_date is None:
            return Decimal("NaN")
        if start is None:
            start = self._earliest_date
        if start < self._earliest_date:
            return Decimal("NaN")

        price_end = self.get_price(end).value_normalized
        price_start = self.get_price(start).value_normalized

        return Decimal(100 * (price_end / price_start - 1))

    def serialize(self) -> dict[str, Any]:
        date_price_pairs = [
            (
                date_.strftime("%Y-%m-%d"),
                str(price.value_normalized),
            )
            for date_, price in self.price_history_pairs
        ]
        return {
            "datatype": "Security",
            "name": self._name,
            "symbol": self._symbol,
            "type": self._type,
            "currency_code": self._currency.code,
            "shares_decimals": self._shares_decimals,
            "uuid": str(self._uuid),
            "date_price_pairs": date_price_pairs,
        }

    @staticmethod
    def deserialize(
        data: dict[str, Any],
        currencies: dict[str, Currency],
    ) -> "Security":
        name = data["name"]
        symbol = data["symbol"]
        type_ = data["type"]
        security_currency = currencies[data["currency_code"]]
        shares_decimals = data["shares_decimals"]

        obj = Security(name, symbol, type_, security_currency, shares_decimals)

        date_price_pairs: list[list[str, str]] = data["date_price_pairs"]
        for date_, price in date_price_pairs:
            obj.set_price(
                datetime.strptime(date_, "%Y-%m-%d")
                .replace(tzinfo=user_settings.settings.time_zone)
                .date(),
                CashAmount(price, obj.currency),
                update=False,
            )
        obj.update_values()
        obj._uuid = UUID(data["uuid"])  # noqa: SLF001
        return obj

    def update_values(self) -> None:
        if len(self._price_history) == 0:
            self._earliest_date = None
            self._latest_date = None
            latest_price = CashAmount(Decimal("NaN"), self._currency)
        else:
            self._earliest_date = min(date_ for date_ in self._price_history)
            self._latest_date = max(date_ for date_ in self._price_history)
            latest_price = self._price_history[self._latest_date]

        previous_latest_price = (
            self._latest_price if hasattr(self, "_latest_price") else None
        )
        self._latest_price = latest_price
        if previous_latest_price != latest_price:
            self.event_price_updated()

        self._price_decimals = max(
            (
                -price.value_normalized.as_tuple().exponent
                for price in self._price_history.values()
            ),
            default=0,
        )

        self._recalculate_price_history_pairs = True

    def _validate_date(self, date_: date) -> None:
        if not isinstance(date_, date):
            raise TypeError("Parameter 'date_' must be a date.")

    def _validate_price(self, price: CashAmount) -> None:
        if not isinstance(price, CashAmount):
            raise TypeError("Parameter 'price' must be a CashAmount.")
        if price.currency != self._currency:
            raise CurrencyError("Security.currency and price.currency must match.")


class SecurityAccount(Account):
    __slots__ = (
        "_uuid",
        "_balances",
        "_transactions",
        "_name",
        "_parent",
        "_allow_slash",
        "_allow_colon",
        "allow_update_balance",
        "event_balance_updated",
        "_securities_history",
        "_related_securities",
    )

    def __init__(self, name: str, parent: AccountGroup | None = None) -> None:
        super().__init__(name, parent)
        self._securities_history: list[tuple[datetime, dict[Security, Decimal]]] = []
        self._transactions: list[SecurityRelatedTransaction] = []
        self._related_securities: frozenset[Security] = frozenset()

        # allow_update_balance attribute is used to block updating the balance
        # when a transaction is added or removed during deserialization
        self.allow_update_balance = True

    @property
    def securities(self) -> dict[Security, Decimal]:
        if len(self._securities_history) == 0:
            return {}
        return copy.copy(self._securities_history[-1][1])

    @property
    def transactions(self) -> tuple["SecurityRelatedTransaction", ...]:
        return tuple(self._transactions)

    @property
    def currency(self) -> Currency | None:
        currencies = {security.currency for security in self._related_securities}
        if len(currencies) == 1:
            return next(iter(currencies))
        return None

    @property
    def related_securities(self) -> frozenset[Security]:
        return self._related_securities

    def get_balance(self, currency: Currency, date_: date | None = None) -> CashAmount:
        if date_ is None:
            return sum(
                (balance.convert(currency) for balance in self._balances),
                start=currency.zero_amount,
            )
        index = bisect_right(self._securities_history, date_, key=lambda x: x[0].date())
        if index:
            _, security_dict = self._securities_history[index - 1]
            balances = self._calculate_balances(security_dict, date_)
            return sum(
                (balance.convert(currency, date_) for balance in balances),
                start=currency.zero_amount,
            )
        return currency.zero_amount

    def _update_balances(self) -> None:
        if len(self._securities_history) == 0:
            self._balances = ()
            return
        self._balances = self._calculate_balances(self._securities_history[-1][1])
        self.event_balance_updated()

    @staticmethod
    def _calculate_balances(
        security_dict: dict[Security, Decimal], date_: date | None = None
    ) -> tuple[CashAmount, ...]:
        balances: dict[Currency, CashAmount] = {}
        for security, shares in security_dict.items():
            amount = security.get_price(date_) * shares
            currency = amount.currency
            if currency not in balances:
                balances[currency] = currency.zero_amount
            balances[currency] += amount
        return tuple(balances.values())

    def add_transaction(self, transaction: "SecurityRelatedTransaction") -> None:
        self._validate_transaction(transaction)
        self._transactions.append(transaction)
        if self.allow_update_balance:
            self.update_securities()

    def remove_transaction(self, transaction: "SecurityRelatedTransaction") -> None:
        self._validate_transaction(transaction)
        self._transactions.remove(transaction)
        if self.allow_update_balance:
            self.update_securities()

    def update_securities(self) -> None:
        if len(self._securities_history) != 0:
            for security in self._securities_history[-1][1]:
                if self._update_balances in security.event_price_updated:
                    security.event_price_updated.remove(self._update_balances)

        self._securities_history.clear()
        self._transactions.sort(key=lambda x: x.timestamp)
        for i, transaction in enumerate(self._transactions):
            if transaction.datetime_ == self._transactions[i - 1].datetime_ and i > 0:
                new_datetime = transaction.datetime_ + timedelta(seconds=1)
                transaction.set_attributes(
                    datetime_=new_datetime, block_account_update=True
                )

        related_securities = set()
        for transaction in self._transactions:
            security_dict = (
                defaultdict(lambda: Decimal(0))
                if len(self._securities_history) == 0
                else copy.copy(self._securities_history[-1][1])
            )
            security_dict[transaction.security] += transaction.get_shares(self)
            security_dict = defaultdict(
                lambda: Decimal(0),
                {
                    key: value
                    for key, value in security_dict.items()
                    if not value.is_zero()
                },
            )
            self._securities_history.append((transaction.datetime_, security_dict))
            related_securities.add(transaction.security)

        if len(self._securities_history) != 0:
            for security in self._securities_history[-1][1]:
                security.event_price_updated.append(self._update_balances)
        self._related_securities = frozenset(related_securities)
        self._update_balances()

    def serialize(self) -> dict[str, Any]:
        index = self._parent.children.index(self) if self._parent is not None else None
        return {
            "datatype": "SecurityAccount",
            "path": self.path,
            "index": index,
            "uuid": str(self._uuid),
        }

    @staticmethod
    def deserialize(
        data: dict[str, Any], account_group_dict: dict[str, AccountGroup]
    ) -> "SecurityAccount":
        path: str = data["path"]
        index: int | None = data["index"]
        parent_path, _, name = path.rpartition("/")

        obj = SecurityAccount(name)
        obj._uuid = UUID(data["uuid"])  # noqa: SLF001

        if parent_path:
            parent = account_group_dict[parent_path]
            parent._children_dict[index] = obj  # noqa: SLF001
            parent._update_children_tuple()  # noqa: SLF001
            obj.event_balance_updated.append(parent._update_balances)  # noqa: SLF001
            obj._parent = parent  # noqa: SLF001
        return obj

    def get_average_amount_per_share(
        self,
        security: Security,
        date_: date | None = None,  # latest date if None
        currency: Currency | None = None,  # Security.currency if None
        type_: SecurityTransactionType = SecurityTransactionType.BUY,
    ) -> CashAmount:
        if not isinstance(security, Security):
            raise TypeError("Parameter 'security' must be a Security.")
        if not isinstance(date_, (date, NoneType)):
            raise TypeError("Parameter 'date' must be a date or None.")
        if not isinstance(currency, (Currency, NoneType)):
            raise TypeError("Parameter 'currency' must be a Currency or None.")
        if date_ is None and (
            len(self._securities_history) == 0
            or security not in self._related_securities
        ):
            raise ValueError(
                f"Security {security.name} is not related to this SecurityAccount."
            )
        if date_ is not None:
            for _datetime, security_dict in reversed(self._securities_history):
                if _datetime.date() <= date_ and security in security_dict:
                    break  # OK
            else:
                raise ValueError(
                    f"Security {security.name} is not in this SecurityAccount."
                )

        if currency is None:
            currency = security.currency

        shares_price_pairs: list[tuple[int, CashAmount]] = []
        for transaction in self._transactions:
            _transaction_date = transaction.date_
            if transaction.security != security:
                continue
            if date_ is not None and _transaction_date > date_:
                continue
            if (
                isinstance(transaction, SecurityTransaction)
                and transaction.type_ == type_
            ):
                amount = transaction.amount_per_share
            elif (
                isinstance(transaction, SecurityTransfer)
                and transaction.recipient == self
            ):
                amount = transaction.sender.get_average_amount_per_share(
                    security, _transaction_date, currency
                )
            else:
                continue
            shares_price_pairs.append(
                (transaction.shares, amount.convert(currency, _transaction_date))
            )

        total_shares = 0
        total_price = currency.zero_amount
        for shares, price in shares_price_pairs:
            total_price += price * shares
            total_shares += shares

        return (
            total_price / total_shares
            if total_shares != 0
            else CashAmount("NaN", currency)
        )

    def get_shares(self, security: Security, type_: SharesType) -> Decimal:
        transactions = {t for t in self._transactions if t.security == security}
        if type_ == SharesType.TRANSFERRED:
            return sum(
                (
                    t.get_shares(self)
                    for t in transactions
                    if isinstance(t, SecurityTransfer)
                ),
                start=Decimal(0),
            )

        if type_ == SharesType.BOUGHT:
            transaction_type = SecurityTransactionType.BUY
        elif type_ == SharesType.SOLD:
            transaction_type = SecurityTransactionType.SELL
        elif type_ == SharesType.PAID_DIVIDEND:
            transaction_type = SecurityTransactionType.DIVIDEND
        else:
            raise TypeError("Parameter 'type_' must be a SharesType.")
        return sum(
            (
                t.shares
                for t in transactions
                if isinstance(t, SecurityTransaction) and t.type_ == transaction_type
            ),
            start=Decimal(0),
        )

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


class SecurityRelatedTransaction(Transaction, ABC):
    __slots__ = ()

    def __init__(
        self,
    ) -> None:
        super().__init__()
        self._security: Security
        self._shares: Decimal

    @property
    def security(self) -> Security:
        return self._security

    @property
    def shares(self) -> Decimal:
        return self._shares

    def get_shares(self, account: SecurityAccount | None = None) -> Decimal:
        """If account is SecurityAccount, returns the change in shares
        related to that SecurityAccount with the correct sign (zero for dividends).
        If account is None, returns shares with the correct sign."""

        if not isinstance(account, (SecurityAccount, NoneType)):
            raise TypeError("Parameter 'account' must be a SecurityAccount or None.")
        if account is not None and not self.is_account_related(account):
            raise UnrelatedAccountError(
                f"SecurityAccount '{account.name}' is not related to this "
                f"{self.__class__.__name__}."
            )
        return self._get_shares(account)

    def _validate_security(self, security: Security) -> None:
        if not isinstance(security, Security):
            raise TypeError(f"{self.__class__.__name__}.security must be a Security.")

    def _validate_shares(
        self, value: Decimal | int | str, shares_decimals: int
    ) -> None:
        if not isinstance(value, Decimal | int | str):
            raise TypeError(
                f"{self.__class__.__name__}.shares must be a Decimal, integer "
                "or a string containing a number."
            )
        _value = Decimal(value)
        if not _value.is_finite() or _value <= 0:
            raise ValueError(
                f"{self.__class__.__name__}.shares must be a finite positive number."
            )
        _value_decimals = -_value.as_tuple().exponent
        if _value_decimals > shares_decimals:
            raise ValueError(
                f"{self.__class__.__name__}.shares must have maximum "
                f"{shares_decimals} decimals."
            )

    @abstractmethod
    def _get_shares(self, account: SecurityAccount | None) -> Decimal:
        raise NotImplementedError


class SecurityTransaction(CashRelatedTransaction, SecurityRelatedTransaction):
    __slots__ = (
        "_uuid",
        "_type",
        "_security",
        "_shares",
        "_amount_per_share",
        "_security_account",
        "_cash_account",
        "_description",
        "_datetime",
        "_datetime_created",
        "_timestamp",
        "_tags",
        "_amount",
        "_amount_negative",
    )

    def __init__(  # noqa: PLR0913
        self,
        description: str,
        datetime_: datetime,
        type_: SecurityTransactionType,
        security: Security,
        shares: Decimal | int | str,
        amount_per_share: CashAmount,
        security_account: SecurityAccount,
        cash_account: CashAccount,
        uuid: UUID | None = None,
    ) -> None:
        super().__init__()
        if uuid is not None:
            self._uuid = uuid
        self.set_attributes(
            description=description,
            datetime_=datetime_,
            type_=type_,
            security=security,
            shares=shares,
            amount_per_share=amount_per_share,
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
    def amount_per_share(self) -> CashAmount:
        return self._amount_per_share

    @property
    def amount(self) -> CashAmount:
        return self._amount

    @property
    def currency(self) -> Currency:
        return self._cash_account.currency

    @property
    def currencies(self) -> tuple[Currency]:
        return (self._cash_account.currency,)

    def __repr__(self) -> str:
        return (
            f"SecurityTransaction({self._type.name}, "
            f"security='{self._security.symbol}', "
            f"shares={self._shares}, "
            f"{self._datetime.strftime('%Y-%m-%d')})"
        )

    def is_account_related(self, account: Account) -> bool:
        return account in {self._security_account, self._cash_account}

    def is_accounts_related(self, accounts: Collection[Account]) -> bool:
        return self._security_account in accounts or self._cash_account in accounts

    def prepare_for_deletion(self) -> None:
        self._cash_account.remove_transaction(self)
        self._security_account.remove_transaction(self)

    def serialize(self) -> dict[str, Any]:
        return {
            "datatype": "SecurityTransaction",
            "description": self._description,
            "datetime": self._datetime.replace(microsecond=0).isoformat(),
            "type": self._type.name,
            "security_name": self._security.name,
            "shares": str(self._shares),
            "amount_per_share": self._amount_per_share.serialize(),
            "security_account_path": self._security_account.path,
            "cash_account_path": self._cash_account.path,
            "datetime_created": self._datetime_created.isoformat(),
            "uuid": str(self._uuid),
        }

    @staticmethod
    def deserialize(
        data: dict[str, Any],
        accounts: dict[str, Account],
        currencies: dict[str, Currency],
        securities: dict[str, Security],
    ) -> "SecurityTransaction":
        description = data["description"]
        datetime_ = datetime.fromisoformat(data["datetime"])
        type_ = SecurityTransactionType[data["type"]]
        shares = Decimal(data["shares"])

        amount_per_share = CashAmount.deserialize(data["amount_per_share"], currencies)
        security = securities[data["security_name"]]
        cash_account = accounts[data["cash_account_path"]]
        security_account = accounts[data["security_account_path"]]

        obj = SecurityTransaction(
            description=description,
            datetime_=datetime_,
            type_=type_,
            security=security,
            shares=shares,
            amount_per_share=amount_per_share,
            security_account=security_account,
            cash_account=cash_account,
            uuid=UUID(data["uuid"]),
        )
        obj._datetime_created = datetime.fromisoformat(  # noqa: SLF001
            data["datetime_created"]
        )
        return obj

    def set_attributes(
        self,
        *,
        description: str | None = None,
        datetime_: datetime | None = None,
        type_: SecurityTransactionType | None = None,
        security: Security | None = None,
        shares: Decimal | None = None,
        amount_per_share: CashAmount | None = None,
        security_account: SecurityAccount | None = None,
        cash_account: CashAccount | None = None,
        block_account_update: bool = False,
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
        if amount_per_share is None:
            amount_per_share = self._amount_per_share
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
            amount_per_share=amount_per_share,
            security_account=security_account,
            cash_account=cash_account,
        )

        self._set_attributes(
            description=description,
            datetime_=datetime_,
            type_=type_,
            security=security,
            shares=shares,
            amount_per_share=amount_per_share,
            security_account=security_account,
            cash_account=cash_account,
            block_account_update=block_account_update,
        )

    def validate_attributes(
        self,
        *,
        description: str | None = None,
        datetime_: datetime | None = None,
        type_: SecurityTransactionType | None = None,
        security: Security | None = None,
        shares: Decimal | None = None,
        amount_per_share: CashAmount | None = None,
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
        if amount_per_share is None:
            amount_per_share = self._amount_per_share
        if security_account is None:
            security_account = self._security_account
        if cash_account is None:
            cash_account = self._cash_account

        self._validate_type(type_)
        self._validate_description(description)
        self._validate_datetime(datetime_)
        self._validate_security(security)
        self._validate_shares(shares, security.shares_decimals)
        self._validate_cash_account(cash_account, security.currency)
        self._validate_security_account(security_account)
        self._validate_amount(amount_per_share, cash_account.currency)

    def _set_attributes(
        self,
        *,
        description: str,
        datetime_: datetime,
        type_: SecurityTransactionType,
        security: Security,
        shares: Decimal,
        amount_per_share: CashAmount,
        security_account: SecurityAccount,
        cash_account: CashAccount,
        block_account_update: bool = False,
    ) -> None:
        update_cash_account = False
        update_security_account = False

        self._description = description.strip()

        if not block_account_update and hasattr(self, "_datetime"):
            update_cash_account = self._datetime != datetime_
            update_security_account = self._datetime != datetime_
        self._datetime = datetime_
        self._timestamp = datetime_.timestamp()

        if not block_account_update and hasattr(self, "_type"):
            if not update_cash_account:
                update_cash_account = self._type != type_
            if not update_security_account:
                update_security_account = self._type != type_
        self._type = type_

        if not block_account_update and hasattr(self, "_security"):
            if not update_cash_account:
                update_cash_account = self._security != security
            if not update_security_account:
                update_security_account = self._security != security
        self._security = security

        if not block_account_update and hasattr(self, "_shares"):
            if not update_cash_account:
                update_cash_account = self._shares != shares
            if not update_security_account:
                update_security_account = self._shares != shares
        self._shares = Decimal(shares).normalize()

        if (
            not block_account_update
            and hasattr(self, "_amount_per_share")
            and not update_cash_account
        ):
            update_cash_account = self._amount_per_share != amount_per_share
        self._amount_per_share = amount_per_share

        self._update_cached_data()
        self._set_accounts(
            security_account,
            cash_account,
            update_cash_account=update_cash_account,
            update_security_account=update_security_account,
        )

    def _update_cached_data(self) -> None:
        self._amount = self._shares * self._amount_per_share
        self._amount_negative = -self._amount

    def _set_accounts(
        self,
        security_account: SecurityAccount,
        cash_account: CashAccount,
        *,
        update_cash_account: bool,
        update_security_account: bool,
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
        elif update_security_account:
            self._security_account.update_securities()

        if add_cash_account:
            self._cash_account.add_transaction(self)
        elif update_cash_account:
            self._cash_account.update_balance()

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

    def _validate_cash_account(self, account: CashAccount, currency: Currency) -> None:
        if not isinstance(account, CashAccount):
            raise TypeError("SecurityTransaction.cash_account must be a CashAccount.")
        if account.currency != currency:
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

    def _get_amount(self, account: CashAccount) -> CashAmount:  # noqa: ARG002
        if self._type == SecurityTransactionType.BUY:
            return self._amount_negative
        return self._amount

    def _get_shares(self, account: SecurityAccount | None) -> Decimal:
        if self._type == SecurityTransactionType.BUY:
            return self._shares
        if self._type == SecurityTransactionType.SELL:
            return -self._shares
        if account is None:
            return self._shares
        return Decimal(0)  # for SecurityTransactionType.DIVIDEND


class SecurityTransfer(SecurityRelatedTransaction):
    __slots__ = (
        "_uuid",
        "_sender",
        "_recipient",
        "_shares",
        "_security",
        "_datetime",
        "_datetime_created",
        "_timestamp",
        "_description",
        "_tags",
    )

    def __init__(  # noqa: PLR0913
        self,
        description: str,
        datetime_: datetime,
        security: Security,
        shares: Decimal | int | str,
        sender: SecurityAccount,
        recipient: SecurityAccount,
        uuid: UUID | None = None,
    ) -> None:
        super().__init__()
        if uuid is not None:
            self._uuid = uuid
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
            f"SecurityTransfer(security='{self._security.symbol}', "
            f"shares={self._shares}, "
            f"from='{self._sender.name}', "
            f"to='{self._recipient.name}', "
            f"{self._datetime.strftime('%Y-%m-%d')})"
        )

    def is_account_related(self, account: Account) -> bool:
        return account in {self._sender, self._recipient}

    def is_accounts_related(self, accounts: Collection[Account]) -> bool:
        return self._sender in accounts or self._recipient in accounts

    def prepare_for_deletion(self) -> None:
        self._sender.remove_transaction(self)
        self._recipient.remove_transaction(self)

    def serialize(self) -> dict[str, Any]:
        return {
            "datatype": "SecurityTransfer",
            "description": self._description,
            "datetime": self._datetime.replace(microsecond=0).isoformat(),
            "security_name": self._security.name,
            "shares": str(self._shares),
            "sender_path": self._sender.path,
            "recipient_path": self._recipient.path,
            "datetime_created": self._datetime_created.isoformat(),
            "uuid": str(self._uuid),
        }

    @staticmethod
    def deserialize(
        data: dict[str, Any],
        accounts: dict[str, Account],
        securities: dict[str, Security],
    ) -> "SecurityTransfer":
        description = data["description"]
        datetime_ = datetime.fromisoformat(data["datetime"])
        shares = Decimal(data["shares"])
        security = securities[data["security_name"]]
        sender = accounts[data["sender_path"]]
        recipient = accounts[data["recipient_path"]]

        obj = SecurityTransfer(
            description=description,
            datetime_=datetime_,
            security=security,
            shares=shares,
            sender=sender,
            recipient=recipient,
            uuid=UUID(data["uuid"]),
        )
        obj._datetime_created = datetime.fromisoformat(  # noqa: SLF001
            data["datetime_created"]
        )
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
        block_account_update: bool = False,
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
            block_account_update=block_account_update,
        )

    def validate_attributes(
        self,
        *,
        description: str | None = None,
        datetime_: datetime | None = None,
        security: Security | None = None,
        shares: int | Decimal | str | None = None,
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
        self._validate_shares(shares, security.shares_decimals)
        self._validate_accounts(sender, recipient)

    def _set_attributes(
        self,
        *,
        description: str,
        datetime_: datetime,
        security: Security,
        shares: Decimal | int | str,
        sender: SecurityAccount,
        recipient: SecurityAccount,
        block_account_update: bool = False,
    ) -> None:
        update_accounts = False

        self._description = description.strip()

        if not block_account_update and hasattr(self, "_datetime"):
            update_accounts = self._datetime != datetime_
        self._datetime = datetime_
        self._timestamp = datetime_.timestamp()

        if (
            not block_account_update
            and hasattr(self, "_security")
            and not update_accounts
        ):
            update_accounts = self._security != security
        self._security = security

        if (
            not block_account_update
            and hasattr(self, "_shares")
            and not update_accounts
        ):
            update_accounts = self._shares != shares
        self._shares = Decimal(shares).normalize()

        self._set_accounts(sender, recipient, update_accounts=update_accounts)

    def _set_accounts(
        self,
        sender: SecurityAccount,
        recipient: SecurityAccount,
        *,
        update_accounts: bool,
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
        elif update_accounts:
            self._sender.update_securities()

        if add_recipient:
            self._recipient.add_transaction(self)
        elif update_accounts:
            self._recipient.update_securities()

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

    def _get_shares(self, account: SecurityAccount | None) -> Decimal:
        if account == self._sender:
            return -self._shares
        return self._shares
