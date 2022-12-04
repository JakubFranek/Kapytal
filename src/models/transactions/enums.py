from enum import Enum, auto


class CashTransactionType(Enum):
    INCOME = auto()
    EXPENSE = auto()


class SecurityTransactionType(Enum):
    BUY = auto()
    SELL = auto()


class CategoryType(Enum):
    INCOME = auto()
    EXPENSE = auto()
    INCOME_AND_EXPENSE = auto()
