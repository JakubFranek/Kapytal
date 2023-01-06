import copy
import string
from abc import ABC, abstractmethod
from collections import defaultdict
from datetime import date, datetime
from decimal import Decimal
from enum import Enum, auto

from src.models.base_classes.account import Account, UnrelatedAccountError
from src.models.base_classes.transaction import Transaction
from src.models.mixins.datetime_created_mixin import DatetimeCreatedMixin
from src.models.mixins.name_mixin import NameMixin
from src.models.mixins.uuid_mixin import UUIDMixin
from src.models.model_objects.account_group import AccountGroup
from src.models.model_objects.cash_objects import CashAccount, CashRelatedTransaction
from src.models.model_objects.currency import CashAmount, Currency, CurrencyError


# TODO: maybe put all generic Errors into one module?
class InvalidCharacterError(ValueError):
    """Raised when invalid character is passed."""


class PriceNotFoundError(ValueError):
    """Raised when Security price does not exist."""


class SecurityType(Enum):
    ETF = auto()
    MUTUAL_FUND = auto()


class SecurityTransactionType(Enum):
    BUY = auto()
    SELL = auto()


# TODO: add smallest unit to Security
class Security(NameMixin, DatetimeCreatedMixin, UUIDMixin):
    NAME_MIN_LENGTH = 1
    NAME_MAX_LENGTH = 64
    SYMBOL_MIN_LENGTH = 1
    SYMBOL_MAX_LENGTH = 8
    SYMBOL_ALLOWED_CHARS = string.ascii_letters + string.digits + "."

    def __init__(
        self,
        name: str,
        symbol: str,
        type_: SecurityType,
        currency: Currency,
        shares_unit: Decimal | int | str,
        price_places: int | None = None,
    ) -> None:
        super().__init__(name=name)
        self.symbol = symbol

        if not isinstance(type_, SecurityType):
            raise TypeError("Security.type_ must be a SecurityType.")
        self._type = type_

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
    def type_(self) -> SecurityType:
        return self._type

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
        latest_date = max(date_ for date_ in self._price_history)
        return self._price_history[latest_date]

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
        return f"Security(symbol='{self.symbol}', type={self.type_.name})"

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


# TODO: maybe add shares / balance history
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
        return f"SecurityAccount('{self.name}')"

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
        self, description: str, datetime_: datetime, shares: Decimal, security: Security
    ) -> None:
        super().__init__(description, datetime_)
        if not isinstance(security, Security):
            raise TypeError(f"{self.__class__.__name__}.security must be a Security.")
        self._security = security
        self.shares = shares

    @property
    def security(self) -> Security:
        return self._security

    @property
    def shares(self) -> Decimal:
        return self._shares

    @shares.setter
    def shares(self, value: Decimal) -> None:
        if not isinstance(value, Decimal):
            raise TypeError(f"{self.__class__.__name__}.shares must be a Decimal.")
        if not value.is_finite() or value <= 0:
            raise ValueError(
                f"{self.__class__.__name__}.shares must be a finite positive number."
            )
        if value % self._security.shares_unit != 0:
            raise ValueError(
                f"{self.__class__.__name__}.shares must be a multiple of "
                f"{self._security.shares_unit}."
            )
        self._shares = value

    def get_shares(self, account: SecurityAccount) -> Decimal:
        if not isinstance(account, SecurityAccount):
            raise TypeError("Parameter 'account' must be a SecurityAccount.")
        if not self.is_account_related(account):
            raise UnrelatedAccountError(
                f"SecurityAccount '{account.name}' is not related to this "
                f"{self.__class__.__name__}."
            )
        return self._get_shares(account)

    @abstractmethod
    def _get_shares(self, account: SecurityAccount) -> Decimal:
        raise NotImplementedError("Not implemented")


class SecurityTransaction(CashRelatedTransaction, SecurityRelatedTransaction):
    def __init__(
        self,
        description: str,
        datetime_: datetime,
        type_: SecurityTransactionType,
        security: Security,
        shares: Decimal,
        price_per_share: CashAmount,
        fees: CashAmount,
        security_account: SecurityAccount,
        cash_account: CashAccount,
    ) -> None:
        super().__init__(
            description=description,
            datetime_=datetime_,
            shares=shares,
            security=security,
        )

        if not isinstance(type_, SecurityTransactionType):
            raise TypeError(
                "SecurityTransaction.type_ must be a SecurityTransactionType."
            )
        self._type = type_

        self.price_per_share = price_per_share
        self.fees = fees

        self.cash_account = cash_account
        self.security_account = security_account

    @property
    def type_(self) -> SecurityTransactionType:
        return self._type

    @property
    def security_account(self) -> SecurityAccount:
        return self._security_account

    @security_account.setter
    def security_account(self, new_account: SecurityAccount) -> None:
        if not isinstance(new_account, SecurityAccount):
            raise TypeError(
                "SecurityTransaction.security_account must be a SecurityAccount."
            )

        if hasattr(self, "_security_account"):
            self._security_account.remove_transaction(self)

        self._security_account = new_account
        self._security_account.add_transaction(self)

    @property
    def cash_account(self) -> CashAccount:
        return self._cash_account

    @cash_account.setter
    def cash_account(self, new_account: CashAccount) -> None:
        if not isinstance(new_account, CashAccount):
            raise TypeError("SecurityTransaction.cash_account must be a CashAccount.")
        if new_account.currency != self._security.currency:
            raise CurrencyError(
                "The currencies of SecurityTransaction.security and "
                "SecurityTransaction.cash_account must match."
            )

        if hasattr(self, "_cash_account"):
            self._cash_account.remove_transaction(self)

        self._cash_account = new_account
        self._cash_account.add_transaction(self)

    @property
    def price_per_share(self) -> CashAmount:
        return self._price_per_share

    @price_per_share.setter
    def price_per_share(self, value: CashAmount) -> None:
        if not isinstance(value, CashAmount):
            raise TypeError("SecurityTransaction.price_per_share must be a CashAmount.")
        self._price_per_share = value

    @property
    def fees(self) -> CashAmount:
        return self._fees

    @fees.setter
    def fees(self, value: CashAmount) -> None:
        if not isinstance(value, CashAmount):
            raise TypeError("SecurityTransaction.fees must be a CashAmount.")
        self._fees = value

    def __repr__(self) -> str:
        return (
            f"SecurityTransaction({self.type_.name}, "
            f"security='{self.security.symbol}', "
            f"shares={self.shares}, "
            f"{self.datetime_.strftime('%Y-%m-%d')})"
        )

    def _get_amount(self, account: CashAccount) -> CashAmount:  # noqa: U100
        if self.type_ == SecurityTransactionType.BUY:
            return -self._shares * self.price_per_share - self.fees
        return self._shares * self.price_per_share - self.fees

    def _get_shares(self, account: SecurityAccount) -> Decimal:  # noqa: U100
        if self.type_ == SecurityTransactionType.BUY:
            return self.shares
        return -self.shares

    def is_account_related(self, account: Account) -> bool:
        return account == self._cash_account or account == self._security_account


class SecurityTransfer(SecurityRelatedTransaction):
    def __init__(
        self,
        description: str,
        datetime_: datetime,
        security: Security,
        shares: Decimal,
        account_sender: SecurityAccount,
        account_recipient: SecurityAccount,
    ) -> None:
        super().__init__(
            description=description,
            datetime_=datetime_,
            security=security,
            shares=shares,
        )
        self.account_sender = account_sender
        self.account_recipient = account_recipient

    def __repr__(self) -> str:
        return (
            f"SecurityTransfer(security='{self.security.symbol}', "
            f"shares={self.shares}, "
            f"from='{self.account_sender.name}', "
            f"to='{self.account_recipient.name}', "
            f"{self.datetime_.strftime('%Y-%m-%d')})"
        )

    @property
    def account_sender(self) -> SecurityAccount:
        return self._account_sender

    @account_sender.setter
    def account_sender(self, new_account: SecurityAccount) -> None:
        if not isinstance(new_account, SecurityAccount):
            raise TypeError(
                "SecurityTransaction.account_sender must be a SecurityAccount."
            )

        if hasattr(self, "_account_sender"):
            self._account_sender.remove_transaction(self)

        self._account_sender = new_account
        self._account_sender.add_transaction(self)

    @property
    def account_recipient(self) -> SecurityAccount:
        return self._account_recipient

    @account_recipient.setter
    def account_recipient(self, new_account: SecurityAccount) -> None:
        if not isinstance(new_account, SecurityAccount):
            raise TypeError(
                "SecurityTransaction.account_recipient must be a SecurityAccount."
            )

        if hasattr(self, "_account_recipient"):
            self._account_recipient.remove_transaction(self)

        self._account_recipient = new_account
        self._account_recipient.add_transaction(self)

    def _get_shares(self, account: SecurityAccount) -> Decimal:
        if account == self._account_sender:
            return -self.shares
        return self.shares

    def is_account_related(self, account: Account) -> bool:
        return account == self.account_sender or account == self.account_recipient
