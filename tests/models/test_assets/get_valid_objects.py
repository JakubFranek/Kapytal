from datetime import datetime
from decimal import Decimal

from src.models.constants import tzinfo
from src.models.model_objects.currency import Currency
from src.models.model_objects.security_objects import Security, SecurityType
from tests.models.test_assets.concrete_abcs import (
    ConcreteAccount,
    ConcreteSecurityRelatedTransaction,
    ConcreteTransaction,
)


def get_concrete_account() -> ConcreteAccount:
    return ConcreteAccount("Valid Name")


def get_concrete_transaction() -> ConcreteTransaction:
    return ConcreteTransaction("A description", datetime.now(tzinfo))


def get_concrete_security_related_transaction() -> ConcreteSecurityRelatedTransaction:
    security = get_security()
    return ConcreteSecurityRelatedTransaction(
        "A description", datetime.now(tzinfo), Decimal("1"), security
    )


def get_security() -> Security:
    return Security(
        "Vanguard FTSE All-World UCITS ETF USD Acc",
        "VWCE.DE",
        SecurityType.ETF,
        Currency("EUR", 2),
    )
