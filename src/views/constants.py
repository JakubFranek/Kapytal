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
    DECIMALS = 1


class ExchangeRateTableColumn(IntEnum):
    CODE = 0
    RATE = 1
    LAST_DATE = 2
    D1 = 3
    D7 = 4
    M1 = 5
    M3 = 6
    M6 = 7
    Y1 = 8
    Y2 = 9
    Y3 = 10
    Y5 = 11
    Y7 = 12
    Y10 = 13
    YTD = 14
    TOTAL = 15
    TOTAL_ANNUALIZED = 16


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
    D1 = 5
    D7 = 6
    M1 = 7
    M3 = 8
    M6 = 9
    Y1 = 10
    Y2 = 11
    Y3 = 12
    Y5 = 13
    Y7 = 14
    Y10 = 15
    YTD = 16
    TOTAL = 17
    TOTAL_ANNUALIZED = 18


class SecurityAccountTableColumn(IntEnum):
    SECURITY_NAME = 0
    SYMBOL = 1
    TYPE = 2
    SHARES = 3
    PRICE = 4
    AMOUNT_NATIVE = 5
    AMOUNT_BASE = 6


class SecuritiesOverviewTreeColumn(IntEnum):
    NAME = 0

    SHARES_OWNED = 1
    SHARES_BOUGHT = 2
    SHARES_SOLD = 3
    SHARES_TRANSFERRED = 4

    AMOUNT_OWNED_NATIVE = 5
    AMOUNT_OWNED_BASE = 6
    AMOUNT_BOUGHT_NATIVE = 7
    AMOUNT_BOUGHT_BASE = 8
    AMOUNT_SOLD_NATIVE = 9
    AMOUNT_SOLD_BASE = 10

    PRICE_MARKET_NATIVE = 11
    PRICE_MARKET_BASE = 12
    PRICE_AVERAGE_BUY_NATIVE = 13
    PRICE_AVERAGE_BUY_BASE = 14
    PRICE_AVERAGE_SELL_NATIVE = 15
    PRICE_AVERAGE_SELL_BASE = 16
    DIVIDEND_AVERAGE_NATIVE = 17
    DIVIDEND_AVERAGE_BASE = 18

    GAIN_PER_SHARE_TOTAL_NATIVE = 19
    GAIN_PER_SHARE_TOTAL_BASE = 20
    GAIN_TOTAL_NATIVE = 21
    GAIN_TOTAL_BASE = 22
    GAIN_TOTAL_CURRENCY_BASE = 23
    RETURN_TOTAL_NATIVE = 24
    RETURN_TOTAL_BASE = 25
    IRR_TOTAL_NATIVE = 26
    IRR_TOTAL_BASE = 27

    GAIN_REALIZED_NATIVE = 28
    GAIN_REALIZED_BASE = 29
    GAIN_DIVIDEND_NATIVE = 30
    GAIN_DIVIDEND_BASE = 31
    RETURN_REALIZED_NATIVE = 32
    RETURN_REALIZED_BASE = 33

    GAIN_UNREALIZED_NATIVE = 34
    GAIN_UNREALIZED_BASE = 35
    RETURN_UNREALIZED_NATIVE = 36
    RETURN_UNREALIZED_BASE = 37


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
    AMOUNT_NATIVE = 5
    AMOUNT_BASE = 6
    AMOUNT_SENT = 7
    AMOUNT_RECEIVED = 8
    SECURITY = 9
    SHARES = 10
    AMOUNT_PER_SHARE = 11
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
    TransactionTableColumn.AMOUNT_PER_SHARE: "Amount per Share",
    TransactionTableColumn.AMOUNT_NATIVE: "Native Amount",
    TransactionTableColumn.AMOUNT_BASE: "Base Amount",
    TransactionTableColumn.AMOUNT_SENT: "Amount Sent",
    TransactionTableColumn.AMOUNT_RECEIVED: "Amount Received",
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


class QuotesUpdateTableColumn(IntEnum):
    ITEM = 0
    LATEST_DATE = 2
    LATEST_QUOTE = 1
