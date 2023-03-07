from enum import IntEnum


class AccountTreeColumn(IntEnum):
    COLUMN_NAME = 0
    COLUMN_BALANCE_NATIVE = 1
    COLUMN_BALANCE_BASE = 2
    COLUMN_SHOW = 3


class CurrencyTableColumn(IntEnum):
    COLUMN_CODE = 0
    COLUMN_PLACES = 1


class ExchangeRateTableColumn(IntEnum):
    COLUMN_CODE = 0
    COLUMN_RATE = 1
    COLUMN_LAST_DATE = 2


class PayeeTableColumn(IntEnum):
    COLUMN_NAME = 0
    COLUMN_TRANSACTIONS = 1
    COLUMN_BALANCE = 2


class TagTableColumn(IntEnum):
    COLUMN_NAME = 0
    COLUMN_TRANSACTIONS = 1
    COLUMN_BALANCE = 2


class SecurityTableColumn(IntEnum):
    COLUMN_NAME = 0
    COLUMN_SYMBOL = 1
    COLUMN_TYPE = 2
    COLUMN_PRICE = 3
    COLUMN_LAST_DATE = 4


class CategoryTreeColumn(IntEnum):
    COLUMN_NAME = 0
    COLUMN_TRANSACTIONS = 1
    COLUMN_BALANCE = 2


class TransactionTableColumn(IntEnum):
    COLUMN_DATETIME = 0
    COLUMN_DESCRIPTION = 1
    COLUMN_TYPE = 2
    COLUMN_FROM = 3
    COLUMN_TO = 4
    COLUMN_SECURITY = 5
    COLUMN_SHARES = 6
    COLUMN_AMOUNT_NATIVE = 7
    COLUMN_AMOUNT_BASE = 8
    COLUMN_AMOUNT_SENT = 9
    COLUMN_AMOUNT_RECEIVED = 10
    COLUMN_BALANCE = 11
    COLUMN_CATEGORY = 12
    COLUMN_TAG = 13
    COLUMN_UUID = 14


TRANSACTION_TABLE_COLUMN_HEADERS = {
    TransactionTableColumn.COLUMN_DATETIME: "Date",
    TransactionTableColumn.COLUMN_DESCRIPTION: "Description",
    TransactionTableColumn.COLUMN_TYPE: "Type",
    TransactionTableColumn.COLUMN_FROM: "From",
    TransactionTableColumn.COLUMN_TO: "To",
    TransactionTableColumn.COLUMN_SECURITY: "Security",
    TransactionTableColumn.COLUMN_SHARES: "Shares",
    TransactionTableColumn.COLUMN_AMOUNT_NATIVE: "Native amount",
    TransactionTableColumn.COLUMN_AMOUNT_BASE: "Base amount",
    TransactionTableColumn.COLUMN_AMOUNT_SENT: "Amount sent",
    TransactionTableColumn.COLUMN_AMOUNT_RECEIVED: "Amount received",
    TransactionTableColumn.COLUMN_BALANCE: "Balance",
    TransactionTableColumn.COLUMN_CATEGORY: "Category",
    TransactionTableColumn.COLUMN_TAG: "Tags",
    TransactionTableColumn.COLUMN_UUID: "UUID",
}
