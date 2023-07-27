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


class Security(CopyableMixin, NameMixin, UUIDMixin, JSONSerializableMixin):
    __slots__ = (
        "_uuid",
        "_name",
        "_symbol",
        "_type",
        "_currency",
        "_shares_unit",
        "_price_history",
        "_price_history_pairs",
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

    def __init__(  # noqa: PLR0913
        self,
        name: str,
        symbol: str,
        type_: str,
        currency: Currency,
        shares_unit: Decimal | int | str,
    ) -> None:
        super().__init__(name=name, allow_slash=True)
        self.symbol = symbol
        self.type_ = type_

        if not isinstance(currency, Currency):
            raise TypeError("Security.currency must be a Currency.")
        self._currency = currency

        if not isinstance(shares_unit, Decimal | int | str):
            raise TypeError(
                "Security.shares_unit must be a Decimal, integer or a string "
                "containing a number."
            )
        _shares_unit = Decimal(shares_unit)
        if not _shares_unit.is_finite() or _shares_unit <= 0:
            raise ValueError("Security.shares_unit must be finite and positive.")
        if _shares_unit.log10() % 1 != 0:
            raise ValueError("Security.shares_unit must be a power of 10.")
        self._shares_unit = _shares_unit

        self._price_history: dict[date, CashAmount] = {}
        self._price_history_pairs: tuple[tuple[date, CashAmount], ...] = ()
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
    def latest_date(self) -> date | None:
        if hasattr(self, "_latest_date"):
            return self._latest_date
        return None

    # TODO: review whether the following property is really needed
    @property
    def price_history(self) -> dict[date, CashAmount]:
        return self._price_history

    @property
    def price_history_pairs(self) -> tuple[tuple[date, CashAmount], ...]:
        if self._recalculate_price_history_pairs:
            pairs = [(date_, price) for date_, price in self._price_history.items()]
            pairs.sort()
            self._price_history_pairs = tuple(pairs)
            self._recalculate_price_history_pairs = False
        return self._price_history_pairs

    # TODO: review whether the following property is really needed
    @property
    def decimal_price_history_pairs(self) -> tuple[tuple[date, Decimal]]:
        return tuple(
            (date_, price.value_normalized) for date_, price in self.price_history_pairs
        )

    @property
    def shares_unit(self) -> Decimal:
        return self._shares_unit

    def __repr__(self) -> str:
        return f"Security('{self._name}')"

    def __str__(self) -> str:
        return self._name

    def get_price(self, date_: date | None) -> CashAmount:
        if date_ is None:
            return self.price
        try:
            return self._price_history[date_]
        except KeyError:
            i = bisect_right(self.price_history_pairs, date_, key=lambda x: x[0])
            if i:
                _, price = self.price_history_pairs[i - 1]
                return price
            logging.warning(
                f"{self!s}: no earlier price found for {date_}, returning 'NaN'"
            )
            return CashAmount(Decimal("NaN"), self._currency)

    def set_price(self, date_: date, price: CashAmount) -> None:
        self._validate_date(date_)
        self._validate_price(price)
        self._price_history[date_] = price
        self._update_values()

    def set_prices(
        self, date_price_tuples: Collection[tuple[date, CashAmount]]
    ) -> None:
        for date_, price in date_price_tuples:
            self._validate_date(date_)
            self._validate_price(price)
            self._price_history[date_] = price
        self._update_values()

    def delete_price(self, date_: date) -> None:
        del self._price_history[date_]
        self._update_values()

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
            "shares_unit": str(self._shares_unit.normalize()),
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

        shares_unit = Decimal(data["shares_unit"])

        obj = Security(name, symbol, type_, security_currency, shares_unit)

        date_price_pairs: list[list[str, str]] = data["date_price_pairs"]
        for date_, price in date_price_pairs:
            obj.set_price(
                datetime.strptime(date_, "%Y-%m-%d")
                .replace(tzinfo=user_settings.settings.time_zone)
                .date(),
                CashAmount(price, obj.currency),
            )

        obj._uuid = UUID(data["uuid"])  # noqa: SLF001
        return obj

    def _update_values(self) -> None:
        if len(self._price_history) == 0:
            self._latest_date = None
            latest_price = CashAmount(Decimal("NaN"), self._currency)
        else:
            self._latest_date = max(date_ for date_ in self._price_history)
            latest_price = self._price_history[self._latest_date]
        if hasattr(self, "_latest_price"):
            previous_latest_price = self._latest_price
        else:
            previous_latest_price = None

        self._latest_price = latest_price
        if previous_latest_price != latest_price:
            self.event_price_updated()

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
    )

    def __init__(self, name: str, parent: AccountGroup | None = None) -> None:
        super().__init__(name, parent)
        self._securities_history: list[tuple[datetime, dict[Security, Decimal]]] = []
        self._transactions: list[SecurityRelatedTransaction] = []

        # allow_update_balance attribute is used to block updating the balance
        # when a transaction is added or removed during deserialization
        self.allow_update_balance = True

    @property
    def securities(self) -> dict[Security, Decimal]:
        if len(self._securities_history) == 0:
            return {}
        return self._securities_history[-1][1]

    @property
    def transactions(self) -> tuple["SecurityRelatedTransaction", ...]:
        return tuple(self._transactions)

    def get_balance(self, currency: Currency, date_: date | None = None) -> CashAmount:
        if date_ is None:
            return sum(
                (balance.convert(currency) for balance in self._balances),
                start=currency.zero_amount,
            )
        i = bisect_right(self._securities_history, date_, key=lambda x: x[0].date())
        if i:
            _datetime, security_dict = self._securities_history[i - 1]
            _date = _datetime.date()
            if i == 1 and date_ != _datetime.date():
                logging.warning(
                    f"{self!s}: no Security history found for "
                    f"{date_.strftime('%Y-%m-%d')}, "
                    f"using the earliest available Security history for "
                    f"{_date.strftime('%Y-%m-%d')}"
                )
            balances = self._calculate_balances(security_dict, date_)
            return sum(
                (balance.convert(currency) for balance in balances),
                start=currency.zero_amount,
            )
        logging.warning(
            f"{self!s}: no earlier Security history found for {date_}, "
            f"returning 0 {currency.code}"
        )
        return CashAmount(0, currency)

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
            security_amount = security.get_price(date_) * shares
            if security_amount.is_nan():
                continue
            if security_amount.currency in balances:
                balances[security_amount.currency] += security_amount
            else:
                balances[security_amount.currency] = security_amount
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
            if i > 0 and transaction.datetime_ == self._transactions[i - 1].datetime_:
                new_datetime = transaction.datetime_ + timedelta(seconds=1)
                transaction.set_attributes(datetime_=new_datetime)

        for transaction in self._transactions:
            security_dict = (
                defaultdict(lambda: Decimal(0))
                if len(self._securities_history) == 0
                else copy.copy(self._securities_history[-1][1])
            )
            security_dict[transaction.security] += transaction.get_shares(self)
            security_dict = defaultdict(
                lambda: Decimal(0),
                {key: value for key, value in security_dict.items() if value != 0},
            )
            self._securities_history.append((transaction.datetime_, security_dict))

        if len(self._securities_history) != 0:
            for security in self._securities_history[-1][1]:
                security.event_price_updated.append(self._update_balances)
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
        if _value % shares_unit != 0:
            raise ValueError(
                f"{self.__class__.__name__}.shares must be a multiple of "
                f"{shares_unit}."
            )

    @abstractmethod
    def _get_shares(self, account: SecurityAccount) -> Decimal:
        raise NotImplementedError


class SecurityTransaction(CashRelatedTransaction, SecurityRelatedTransaction):
    __slots__ = (
        "_uuid",
        "_type",
        "_security",
        "_shares",
        "_price_per_share",
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
        price_per_share: CashAmount,
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
        return account == self._cash_account or account == self._security_account

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
            "price_per_share": self._price_per_share.serialize(),
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
        price_per_share = CashAmount.deserialize(data["price_per_share"], currencies)
        security = securities[data["security_name"]]
        cash_account = accounts[data["cash_account_path"]]
        security_account = accounts[data["security_account_path"]]

        obj = SecurityTransaction(
            description=description,
            datetime_=datetime_,
            type_=type_,
            security=security,
            shares=shares,
            price_per_share=price_per_share,
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
        update_cash_account = False
        update_security_account = False

        self._description = description

        if hasattr(self, "_datetime"):
            update_cash_account = self._datetime != datetime_
            update_security_account = self._datetime != datetime_
        self._datetime = datetime_
        self._timestamp = datetime_.timestamp()

        if hasattr(self, "_type"):
            if not update_cash_account:
                update_cash_account = self._type != type_
            if not update_security_account:
                update_security_account = self._type != type_
        self._type = type_

        if hasattr(self, "_security"):
            if not update_cash_account:
                update_cash_account = self._security != security
            if not update_security_account:
                update_security_account = self._security != security
        self._security = security

        if hasattr(self, "_shares"):
            if not update_cash_account:
                update_cash_account = self._shares != shares
            if not update_security_account:
                update_security_account = self._shares != shares
        self._shares = Decimal(shares).normalize()

        if hasattr(self, "_price_per_share") and not update_cash_account:
            update_cash_account = self._price_per_share != price_per_share
        self._price_per_share = price_per_share

        self._update_cached_data()
        self._set_accounts(
            security_account,
            cash_account,
            update_cash_account=update_cash_account,
            update_security_account=update_security_account,
        )

    def _update_cached_data(self) -> None:
        self._amount = self._shares * self._price_per_share
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

    def _get_amount(self, account: CashAccount) -> CashAmount:
        del account
        if self._type == SecurityTransactionType.BUY:
            return self._amount_negative
        return self._amount

    def _get_shares(self, account: SecurityAccount) -> Decimal:
        del account
        if self._type == SecurityTransactionType.BUY:
            return self._shares
        return -self._shares


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
        return account == self._sender or account == self._recipient

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
        update_accounts = False

        self._description = description

        if hasattr(self._datetime):
            update_accounts = self._datetime != datetime_
        self._datetime = datetime_
        self._timestamp = datetime_.timestamp()

        if hasattr(self._security) and not update_accounts:
            update_accounts = self._security != security
        self._security = security

        if hasattr(self._shares) and not update_accounts:
            update_accounts = self._shares != shares
        self._shares = shares.normalize()

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

    def _get_shares(self, account: SecurityAccount) -> Decimal:
        if account == self._sender:
            return -self._shares
        return self._shares
