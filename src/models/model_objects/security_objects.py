import copy
import string
from datetime import date
from decimal import Decimal
from enum import Enum, auto

from src.models.base_classes.account import Account
from src.models.mixins.datetime_created_mixin import DatetimeCreatedMixin
from src.models.mixins.name_mixin import NameMixin
from src.models.mixins.uuid_mixin import UUIDMixin
from src.models.model_objects.account_group import AccountGroup


class InvalidCharacterError(ValueError):
    """Raised when invalid character is passed."""


class SecurityType(Enum):
    ETF = auto()
    MUTUAL_FUND = auto()


class Security(NameMixin, DatetimeCreatedMixin, UUIDMixin):
    NAME_MIN_LENGTH = 1
    NAME_MAX_LENGTH = 64
    SYMBOL_MIN_LENGTH = 1
    SYMBOL_MAX_LENGTH = 8
    SYMBOL_ALLOWED_CHARS = string.ascii_letters + string.digits + "."

    def __init__(self, name: str, symbol: str, type_: SecurityType) -> None:
        super().__init__(name=name)
        self.symbol = symbol.upper()

        if not isinstance(type_, SecurityType):
            raise TypeError("Security.type_ must be a SecurityType.")
        self._type = type_
        self._price_history: dict[date, Decimal] = {}

    @property
    def type_(self) -> SecurityType:
        return self._type

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
        self._symbol = value

    @property
    def price(self) -> Decimal:
        latest_date = max(date_ for date_ in self._price_history)
        return self._price_history[latest_date]

    @property
    def price_history(self) -> dict[date, Decimal]:
        return copy.deepcopy(self._price_history)

    def __repr__(self) -> str:
        return f"Security(symbol='{self.symbol}', type={self.type_.name})"

    def __hash__(self) -> int:
        return hash(self.uuid)

    def set_price(self, date_: date, price: Decimal) -> None:
        if not isinstance(date_, date):
            raise TypeError("Argument 'date_' must be a date.")
        if not isinstance(price, Decimal):
            raise TypeError("Argument 'price' must be a Decimal.")
        if not price.is_finite() or price < 0:
            raise ValueError("Argument 'price' must be a finite, non-negative Decimal.")
        self._price_history[date_] = price


class SecurityAccount(Account):
    def __init__(self, name: str, parent: AccountGroup | None = None) -> None:
        super().__init__(name, parent)
        self._securities: dict[Security, int] = {}
