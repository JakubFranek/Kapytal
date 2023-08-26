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


class ValueTableColumn(IntEnum):
    DATE = 0
    VALUE = 1


class PayeeTableColumn(IntEnum):
    NAME = 0
    TRANSACTIONS = 1
    BALANCE = 2


class AttributeTableColumn(IntEnum):
    NAME = 0
    TRANSACTIONS = 1
    BALANCE = 2


class SecurityTableColumn(IntEnum):
    NAME = 0
    SYMBOL = 1
    TYPE = 2
    PRICE = 3
    LAST_DATE = 4


class SecurityAccountTableColumn(IntEnum):
    SECURITY_NAME = 0
    SYMBOL = 1
    TYPE = 2
    SHARES = 3
    PRICE = 4
    AMOUNT_NATIVE = 5
    AMOUNT_BASE = 6


class OwnedSecuritiesTreeColumn(IntEnum):
    NAME = 0
    SHARES = 1
    AMOUNT_NATIVE = 2
    AMOUNT_BASE = 3


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
    PRICE_PER_SHARE = 7
    AMOUNT_NATIVE = 8
    AMOUNT_BASE = 9
    AMOUNT_SENT = 10
    AMOUNT_RECEIVED = 11
    BALANCE = 12
    CATEGORY = 13
    TAG = 14
    UUID = 15
    DATETIME_CREATED = 16


TRANSACTION_TABLE_COLUMN_HEADERS = {
    TransactionTableColumn.DATETIME: "Date",
    TransactionTableColumn.DESCRIPTION: "Description",
    TransactionTableColumn.TYPE: "Type",
    TransactionTableColumn.FROM: "From",
    TransactionTableColumn.TO: "To",
    TransactionTableColumn.SECURITY: "Security",
    TransactionTableColumn.SHARES: "Shares",
    TransactionTableColumn.PRICE_PER_SHARE: "Price per share",
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


class CashFlowTableColumn(IntEnum):
    INCOME = 0
    INWARD_TRANSFERS = 1
    REFUNDS = 2
    INITIAL_BALANCES = 3
    TOTAL_INFLOW = 4
    EXPENSES = 5
    OUTWARD_TRANSFERS = 6
    TOTAL_OUTFLOW = 7
    DELTA_NEUTRAL = 8
    DELTA_PERFORMANCE_SECURITIES = 9
    DELTA_PERFORMANCE_CURRENCIES = 10
    DELTA_PERFORMANCE = 11
    DELTA_TOTAL = 12
    SAVINGS_RATE = 13


class AssetTypeTreeColumn(IntEnum):
    NAME = 0
    BALANCE_NATIVE = 1
    BALANCE_BASE = 2
