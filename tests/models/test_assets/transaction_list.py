from datetime import datetime
from decimal import Decimal

from src.models.base_classes.transaction import Transaction
from src.models.model_objects.attributes import (
    Attribute,
    AttributeType,
    Category,
    CategoryType,
)
from src.models.model_objects.cash_objects import (
    CashAccount,
    CashTransaction,
    CashTransactionType,
    CashTransfer,
    RefundTransaction,
)
from src.models.model_objects.currency_objects import CashAmount, Currency, ExchangeRate
from src.models.model_objects.security_objects import (
    Security,
    SecurityAccount,
    SecurityTransaction,
    SecurityTransactionType,
    SecurityTransfer,
)
from src.models.user_settings import user_settings

CZK = Currency("CZK", 2)
USD = Currency("USD", 2)
czk_usd_exchange_rate = ExchangeRate(CZK, USD)
czk_usd_exchange_rate.set_rate(
    date_=datetime(2023, 1, 1, tzinfo=user_settings.settings.time_zone).date(),
    rate=Decimal("0.04"),
)
USD.add_exchange_rate(czk_usd_exchange_rate)

security = Security("Apple", "AAPL", "Stock", USD, 1)

security_account_1 = SecurityAccount("DEGIRO")
security_account_2 = SecurityAccount("Interactive Brokers")

cash_account_1 = CashAccount("Wallet", CZK, CashAmount(0, CZK))
cash_account_2 = CashAccount("Savings", CZK, CashAmount(0, CZK))
cash_account_3 = CashAccount("DEGIRO USD", USD, CashAmount(0, USD))

category_food = Category("Food", CategoryType.EXPENSE)
category_household = Category("Household", CategoryType.EXPENSE)

tag = Attribute("Tag", AttributeType.TAG)

payee_tesco = Attribute("Tesco", AttributeType.PAYEE)
payee_alza = Attribute("Alza", AttributeType.PAYEE)


transaction_list: list[Transaction] = []
transaction_list.append(
    CashTransaction(
        "Groceries",
        datetime(2023, 1, 1, tzinfo=user_settings.settings.time_zone),
        CashTransactionType.EXPENSE,
        cash_account_1,
        payee_tesco,
        ((category_food, CashAmount(100, CZK)),),
        ((tag, CashAmount(100, CZK)),),
    )
)
transaction_list.append(
    CashTransaction(
        "Electronics",
        datetime(2023, 2, 1, tzinfo=user_settings.settings.time_zone),
        CashTransactionType.EXPENSE,
        cash_account_1,
        payee_alza,
        ((category_food, CashAmount(15000, CZK)),),
        ((tag, CashAmount(15000, CZK)),),
    )
)
transaction_list.append(
    CashTransaction(
        "Groceries and household items",
        datetime(2023, 3, 1, tzinfo=user_settings.settings.time_zone),
        CashTransactionType.EXPENSE,
        cash_account_1,
        payee_tesco,
        (
            (category_food, CashAmount(1000, CZK)),
            (category_household, CashAmount(500, CZK)),
        ),
        ((tag, CashAmount(1000, CZK)),),
    )
)
transaction_list.append(
    RefundTransaction(
        "Refund of Electronics",
        datetime(2023, 2, 15, tzinfo=user_settings.settings.time_zone),
        cash_account_1,
        transaction_list[1],
        payee_alza,
        ((category_food, CashAmount(15000, CZK)),),
        ((tag, CashAmount(15000, CZK)),),
    )
)
transaction_list.append(
    CashTransfer(
        "Transfer from Savings to DEGIRO USD",
        datetime(2023, 3, 1, tzinfo=user_settings.settings.time_zone),
        cash_account_2,
        cash_account_3,
        CashAmount(10000, CZK),
        CashAmount(400, USD),
    )
)
transaction_list.append(
    SecurityTransaction(
        "Buy AAPL",
        datetime(2023, 3, 5, tzinfo=user_settings.settings.time_zone),
        SecurityTransactionType.BUY,
        security,
        10,
        CashAmount(125, USD),
        security_account_1,
        cash_account_3,
    )
)
transaction_list.append(
    SecurityTransaction(
        "Sell AAPL",
        datetime(2023, 3, 10, tzinfo=user_settings.settings.time_zone),
        SecurityTransactionType.SELL,
        security,
        5,
        CashAmount(150, USD),
        security_account_1,
        cash_account_3,
    )
)
transaction_list.append(
    SecurityTransfer(
        "Transfer AAPL",
        datetime(2023, 3, 15, tzinfo=user_settings.settings.time_zone),
        security,
        10,
        security_account_1,
        security_account_2,
    )
)

earliest_datetime = min([t.datetime_ for t in transaction_list])
latest_datetime = max([t.datetime_ for t in transaction_list])
