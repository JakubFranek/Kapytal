from datetime import datetime

from src.models.constants import tzinfo
from tests.models.test_assets.concrete_abcs import ConcreteAccount, ConcreteTransaction


def get_concrete_account() -> ConcreteAccount:
    return ConcreteAccount("Valid Name")


def get_concrete_transaction() -> ConcreteTransaction:
    return ConcreteTransaction("A description", datetime.now(tzinfo))
