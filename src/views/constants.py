from enum import IntEnum

from PyQt6.QtGui import QFont

monospace_font = QFont("Consolas")


class AccountTreeColumn(IntEnum):
    NAME = 0
    BALANCE_NATIVE = 1
    BALANCE_BASE = 2
    SHOW = 3


class CurrencyTableColumn(IntEnum):
    CODE = 0
    PLACES = 1


class ExchangeRateTableColumn(IntEnum):
    CODE = 0
    RATE = 1
    LAST_DATE = 2


class PayeeTableColumn(IntEnum):
    NAME = 0
    TRANSACTIONS = 1
    BALANCE = 2


class TagTableColumn(IntEnum):
    NAME = 0
    TRANSACTIONS = 1
    BALANCE = 2


class SecurityTableColumn(IntEnum):
    NAME = 0
    SYMBOL = 1
    TYPE = 2
    PRICE = 3
    LAST_DATE = 4


class CategoryTreeColumn(IntEnum):
    NAME = 0
    TRANSACTIONS = 1
    BALANCE = 2


class TransactionTableColumn(IntEnum):
    DATETIME = 0
    DESCRIPTION = 1
    TYPE = 2
    FROM = 3
    TO = 4
    SECURITY = 5
    SHARES = 6
    AMOUNT_NATIVE = 7
    AMOUNT_BASE = 8
    AMOUNT_SENT = 9
    AMOUNT_RECEIVED = 10
    BALANCE = 11
    CATEGORY = 12
    TAG = 13
    UUID = 14
    DATETIME_CREATED = 15


TRANSACTION_TABLE_COLUMN_HEADERS = {
    TransactionTableColumn.DATETIME: "Date",
    TransactionTableColumn.DESCRIPTION: "Description",
    TransactionTableColumn.TYPE: "Type",
    TransactionTableColumn.FROM: "From",
    TransactionTableColumn.TO: "To",
    TransactionTableColumn.SECURITY: "Security",
    TransactionTableColumn.SHARES: "Shares",
    TransactionTableColumn.AMOUNT_NATIVE: "Native amount",
    TransactionTableColumn.AMOUNT_BASE: "Base amount",
    TransactionTableColumn.AMOUNT_SENT: "Amount sent",
    TransactionTableColumn.AMOUNT_RECEIVED: "Amount received",
    TransactionTableColumn.BALANCE: "Balance",
    TransactionTableColumn.CATEGORY: "Category",
    TransactionTableColumn.TAG: "Tags",
    TransactionTableColumn.UUID: "UUID",
    TransactionTableColumn.DATETIME_CREATED: "Date & time created",
}
