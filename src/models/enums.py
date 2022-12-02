from enum import Enum, auto


class CashTransactionType(Enum):
    INCOME = auto()
    EXPENSE = auto()


class SecurityTransactionType(Enum):
    BUY = auto()
    SELL = auto()
