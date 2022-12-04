from enum import Enum, auto


class CategoryType(Enum):
    INCOME = auto()
    EXPENSE = auto()
    INCOME_AND_EXPENSE = auto()
