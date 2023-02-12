from enum import IntEnum


class AccountTreeColumns(IntEnum):
    COLUMN_NAME = 0
    COLUMN_BALANCE_NATIVE = 2
    COLUMN_BALANCE_BASE = 1
    COLUMN_SHOW = 3


class CurrencyTableColumns(IntEnum):
    COLUMN_CODE = 0
    COLUMN_PLACES = 1


class ExchangeRateTableColumns(IntEnum):
    COLUMN_CODE = 0
    COLUMN_RATE = 1
    COLUMN_LAST_DATE = 2


class PayeeTableColumns(IntEnum):
    COLUMN_NAME = 0
    COLUMN_TRANSACTIONS = 1
    COLUMN_BALANCE = 2


class TagTableColumns(IntEnum):
    COLUMN_NAME = 0
    COLUMN_TRANSACTIONS = 1
    COLUMN_BALANCE = 2


class SecurityTableColumns(IntEnum):
    COLUMN_NAME = 0
    COLUMN_SYMBOL = 1
    COLUMN_TYPE = 2
    COLUMN_PRICE = 3
    COLUMN_LAST_DATE = 4


class CategoryTreeColumns(IntEnum):
    COLUMN_NAME = 0
    COLUMN_TRANSACTIONS = 1
    COLUMN_BALANCE = 2
