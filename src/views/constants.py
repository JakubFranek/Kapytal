from enum import IntEnum


class AccountTreeColumns(IntEnum):
    COLUMN_NAME = 0
    COLUMN_BALANCE_NATIVE = 1
    COLUMN_BALANCE_BASE = 2
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


class TransactionTableColumns(IntEnum):
    COLUMN_DATETIME = 0
    COLUMN_DESCRIPTION = 1
    COLUMN_TYPE = 2
    COLUMN_ACCOUNT = 3
    COLUMN_SENDER = 4
    COLUMN_RECIPIENT = 5
    COLUMN_PAYEE = 6
    COLUMN_SECURITY = 7
    COLUMN_SHARES = 8
    COLUMN_AMOUNT_NATIVE = 9
    COLUMN_AMOUNT_BASE = 10
    COLUMN_AMOUNT_SENT = 11
    COLUMN_AMOUNT_RECEIVED = 12
    COLUMN_BALANCE = 13
    COLUMN_CATEGORY = 14
    COLUMN_TAG = 15
    COLUMN_UUID = 16


TRANSACTION_TABLE_COLUMN_HEADERS = {
    TransactionTableColumns.COLUMN_DATETIME: "Date & time",
    TransactionTableColumns.COLUMN_DESCRIPTION: "Description",
    TransactionTableColumns.COLUMN_TYPE: "Type",
    TransactionTableColumns.COLUMN_ACCOUNT: "Account",
    TransactionTableColumns.COLUMN_SENDER: "Sender",
    TransactionTableColumns.COLUMN_RECIPIENT: "Recipient",
    TransactionTableColumns.COLUMN_PAYEE: "Payee",
    TransactionTableColumns.COLUMN_SECURITY: "Security",
    TransactionTableColumns.COLUMN_SHARES: "Shares",
    TransactionTableColumns.COLUMN_AMOUNT_NATIVE: "Native amount",
    TransactionTableColumns.COLUMN_AMOUNT_BASE: "Base amount",
    TransactionTableColumns.COLUMN_AMOUNT_SENT: "Amount sent",
    TransactionTableColumns.COLUMN_AMOUNT_RECEIVED: "Amount received",
    TransactionTableColumns.COLUMN_BALANCE: "Balance",
    TransactionTableColumns.COLUMN_CATEGORY: "Category",
    TransactionTableColumns.COLUMN_TAG: "Tags",
    TransactionTableColumns.COLUMN_UUID: "UUID",
}
