import string
from datetime import datetime, timedelta
from decimal import Decimal
from types import NoneType
from typing import Any

import pytest
from hypothesis import assume, given
from hypothesis import strategies as st

from src.models.base_classes.account import Account
from src.models.constants import tzinfo
from src.models.model_objects.attributes import (
    Attribute,
    AttributeType,
    CategoryType,
    InvalidCategoryTypeError,
)
from src.models.model_objects.cash_objects import (
    CashAccount,
    CashTransaction,
    CashTransactionType,
    CashTransfer,
    RefundTransaction,
)
from src.models.model_objects.currency import CashAmount, Currency, CurrencyError
from src.models.model_objects.security_objects import (
    SecurityAccount,
    SecurityTransaction,
    SecurityTransactionType,
    SecurityTransfer,
    SecurityType,
)
from src.models.record_keeper import AlreadyExistsError, DoesNotExistError, RecordKeeper
from tests.models.test_assets.composites import (
    currencies,
    everything_except,
    valid_decimals,
)


def test_edit_category() -> None:
    record_keeper = RecordKeeper()
    record_keeper.add_category("TEST PARENT 1", None, CategoryType.EXPENSE)
    record_keeper.add_category("TEST PARENT 2", None, CategoryType.EXPENSE)
    record_keeper.add_category("TEST CAT", "TEST PARENT 1")
    record_keeper.edit_category("TEST PARENT 1/TEST CAT", "NEW NAME", "TEST PARENT 2")
    cat = record_keeper.get_category("TEST PARENT 2/NEW NAME", CategoryType.EXPENSE)
    assert cat.name == "NEW NAME"
    assert cat.path == "TEST PARENT 2/NEW NAME"


def test_edit_payee() -> None:
    record_keeper = RecordKeeper()
    record_keeper._payees.append(Attribute("TEST NAME", AttributeType.PAYEE))
    record_keeper.edit_attribute("TEST NAME", "NEW NAME", AttributeType.PAYEE)
    attribute = record_keeper.payees[0]
    assert attribute.name == "NEW NAME"


def test_edit_tag() -> None:
    record_keeper = RecordKeeper()
    record_keeper._tags.append(Attribute("TEST NAME", AttributeType.TAG))
    record_keeper.edit_attribute("TEST NAME", "NEW NAME", AttributeType.TAG)
    attribute = record_keeper.tags[0]
    assert attribute.name == "NEW NAME"
