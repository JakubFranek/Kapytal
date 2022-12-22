import copy
import string
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


# TODO: maybe put all generic Errors into one module?
class InvalidCharacterError(ValueError):
    """Raised when invalid character is passed."""


class SecurityType(Enum):
    ETF = auto()
    MUTUAL_FUND = auto()


class SecurityTransactionType(Enum):
    BUY = auto()
    SELL = auto()


class Security(NameMixin, DatetimeCreatedMixin, UUIDMixin):
    NAME_MIN_LENGTH = 1
    NAME_MAX_LENGTH = 64
    SYMBOL_MIN_LENGTH = 1
    SYMBOL_MAX_LENGTH = 8
    SYMBOL_ALLOWED_CHARS = string.ascii_letters + string.digits + "."

    def __init__(self, name: str, symbol: str, type_: SecurityType) -> None:
        super().__init__(name=name)
        self.symbol = symbol

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
        self._symbol = value.upper()

    @property
    def price(self) -> Decimal:
        if len(self._price_history) == 0:
            return Decimal(0)
        latest_date = max(date_ for date_ in self._price_history)
        return self._price_history[latest_date]

    @property
    def price_history(self) -> dict[date, Decimal]:
        return copy.deepcopy(self._price_history)

    def __repr__(self) -> str:
        return f"Security(symbol='{self.symbol}', type={self.type_.name})"

    def __hash__(self) -> int:
        return hash(self.uuid)

    def __eq__(self, __o: object) -> bool:
        if not isinstance(__o, Security):
            return False
        return self.uuid == __o.uuid

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
        self._securities: defaultdict[Security, int] = defaultdict(int)
        self._transactions: list[SecurityTransaction] = []

    @property
    def securities(self) -> dict[Security, int]:
        return copy.deepcopy(self._securities)

    @property
    def balance(self) -> Decimal:
        return Decimal(
            sum(
                security.price * shares for security, shares in self._securities.items()
            )
        )

    @property
    def transactions(self) -> tuple["SecurityTransaction", ...]:
        return tuple(self._transactions)

    def __repr__(self) -> str:
        return f"SecurityAccount('{self.name}')"

    def add_transaction(self, transaction: "SecurityTransaction") -> None:
        self._validate_transaction(transaction)
        if transaction.type_ == SecurityTransactionType.SELL:
            self._securities[transaction.security] -= transaction.shares
        else:
            self._securities[transaction.security] += transaction.shares
        self._transactions.append(transaction)

    def remove_transaction(self, transaction: "SecurityTransaction") -> None:
        self._validate_transaction(transaction)
        if transaction.type_ == SecurityTransactionType.SELL:
            self._securities[transaction.security] += transaction.shares
        else:
            self._securities[transaction.security] -= transaction.shares
        self._transactions.remove(transaction)

    def _validate_transaction(self, transaction: "SecurityTransaction") -> None:
        if not isinstance(transaction, SecurityTransaction):
            raise TypeError("Argument 'transaction' must be a SecurityTransaction.")
        if not transaction.is_account_related(self):
            raise UnrelatedAccountError(
                "This SecurityAccount is not related to the provided "
                "SecurityTransaction."
            )
        return


class SecurityTransaction(CashRelatedTransaction):
    def __init__(
        self,
        description: str,
        datetime_: datetime,
        type_: SecurityTransactionType,
        security: Security,
        shares: int,
        price_per_share: Decimal,
        fees: Decimal,
        security_account: SecurityAccount,
        cash_account: CashAccount,
    ) -> None:
        super().__init__(description, datetime_)

        if not isinstance(type_, SecurityTransactionType):
            raise TypeError(
                "SecurityTransaction.type_ must be a SecurityTransactionType."
            )
        self._type = type_

        if not isinstance(security, Security):
            raise TypeError("SecurityTransaction.security must be a Security.")
        self._security = security

        self.shares = shares
        self.price_per_share = price_per_share
        self.fees = fees

        if not isinstance(cash_account, CashAccount):
            raise TypeError("SecurityTransaction.cash_account must be a CashAccount.")
        self.cash_account = cash_account

        self.security_account = security_account

    @property
    def type_(self) -> SecurityTransactionType:
        return self._type

    @property
    def security(self) -> Security:
        return self._security

    @property
    def shares(self) -> int:
        return self._shares

    @shares.setter
    def shares(self, value: int) -> None:
        if not isinstance(value, int):
            raise TypeError("SecurityTransaction.shares must be an int.")
        if value < 1:
            raise ValueError("SecurityTransaction.shares must be at least 1.")
        self._shares = value

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
            self._security_account

        self._security_account = new_account
        self._security_account.add_transaction(self)

    @property
    def cash_account(self) -> CashAccount:
        return self._cash_account

    @cash_account.setter
    def cash_account(self, new_account: CashAccount) -> None:
        if not isinstance(new_account, CashAccount):
            raise TypeError("SecurityTransaction.cash_account must be a CashAccount.")

        if hasattr(self, "_cash_account"):
            self._cash_account

        self._cash_account = new_account
        self._cash_account.add_transaction(self)

    def get_amount_for_account(self, account: CashAccount) -> Decimal:
        if not isinstance(account, CashAccount):
            raise TypeError("Argument 'account' must be a CashAccount.")
        if not self.is_account_related(account):
            raise UnrelatedAccountError(
                "Provided CashAccount is unrelated to this SecurityTransaction."
            )
        if self.type_ == SecurityTransactionType.BUY:
            return -self._shares * self.price_per_share - self.fees
        return self._shares * self.price_per_share - self.fees

    def is_account_related(self, account: Account) -> bool:
        return account == self.cash_account or account == self.security_account


class SecurityTransfer(Transaction):
    def __init__(
        self,
        description: str,
        datetime_: datetime,
        account_sender: SecurityAccount,
        account_recipient: SecurityAccount,
        security: Security,
        shares: int,
    ) -> None:
        super().__init__(description, datetime_)
        # TODO: implement this class
