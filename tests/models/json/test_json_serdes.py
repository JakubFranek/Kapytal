import json
from datetime import datetime
from decimal import Decimal

import pytest
from hypothesis import given
from hypothesis import strategies as st

from src.models.constants import tzinfo
from src.models.json.custom_json_decoder import CustomJSONDecoder
from src.models.json.custom_json_encoder import CustomJSONEncoder
from src.models.model_objects.account_group import AccountGroup
from src.models.model_objects.attributes import Attribute, Category
from src.models.model_objects.cash_objects import CashAccount
from src.models.model_objects.currency import CashAmount, Currency, ExchangeRate
from src.models.model_objects.security_objects import (
    Security,
    SecurityAccount,
    SecurityType,
)
from tests.models.test_assets.composites import attributes, categories


def test_invalid_object() -> None:
    with pytest.raises(TypeError, match="not JSON serializable"):
        json.dumps(object, cls=CustomJSONEncoder)


def test_decimal() -> None:
    number = Decimal("1.234")
    serialized = json.dumps(number, cls=CustomJSONEncoder)
    decoded = json.loads(serialized, cls=CustomJSONDecoder)
    assert decoded == number


def test_datetime() -> None:
    dt = datetime.now(tzinfo)
    serialized = json.dumps(dt, cls=CustomJSONEncoder)
    decoded = json.loads(serialized, cls=CustomJSONDecoder)
    assert decoded == dt


def test_currency() -> None:
    currency = Currency("CZK", 2)
    serialized = json.dumps(currency, cls=CustomJSONEncoder)
    decoded = json.loads(serialized, cls=CustomJSONDecoder)
    assert decoded == currency


def test_exchange_rate() -> None:
    primary = Currency("EUR", 2)
    secondary = Currency("CZK", 2)
    exchange_rate = ExchangeRate(primary, secondary)
    serialized = json.dumps(exchange_rate, cls=CustomJSONEncoder)
    decoded = json.loads(serialized, cls=CustomJSONDecoder)
    assert isinstance(decoded, ExchangeRate)
    assert decoded.primary_currency == exchange_rate.primary_currency
    assert decoded.secondary_currency == exchange_rate.secondary_currency


def test_cash_amount() -> None:
    currency = Currency("EUR", 2)
    cash_amount = CashAmount(Decimal("1.23"), currency)
    serialized = json.dumps(cash_amount, cls=CustomJSONEncoder)
    decoded = json.loads(serialized, cls=CustomJSONDecoder)
    assert decoded == cash_amount


@given(attribute=attributes())
def test_attribute(attribute: Attribute) -> None:
    serialized = json.dumps(attribute, cls=CustomJSONEncoder)
    decoded = json.loads(serialized, cls=CustomJSONDecoder)
    assert isinstance(decoded, Attribute)
    assert decoded.name == attribute.name
    assert decoded.type_ == attribute.type_


@given(category=categories(), data=st.data())
def test_category(category: Category, data: st.DataObject) -> None:
    child_1 = data.draw(categories(category_type=category.type_))
    child_2 = data.draw(categories(category_type=category.type_))
    child_1.parent = category
    child_2.parent = category
    serialized = json.dumps(category, cls=CustomJSONEncoder)
    decoded = json.loads(serialized, cls=CustomJSONDecoder)
    assert isinstance(decoded, Category)
    assert decoded.name == category.name
    assert decoded.type_ == category.type_
    assert decoded.children[0].name == child_1.name
    assert decoded.children[0].parent == decoded
    assert decoded.children[1].name == child_2.name
    assert decoded.children[1].parent == decoded


def test_account_group() -> None:
    account_group = AccountGroup("Test Name")
    child_1 = AccountGroup("Child 1", account_group)
    child_2 = AccountGroup("Child 2", account_group)
    child_1.parent = account_group
    child_2.parent = account_group
    serialized = json.dumps(account_group, cls=CustomJSONEncoder)
    decoded = json.loads(serialized, cls=CustomJSONDecoder)
    assert isinstance(decoded, AccountGroup)
    assert decoded.name == account_group.name
    assert decoded.children[0].name == child_1.name
    assert decoded.children[0].parent == decoded
    assert decoded.children[1].name == child_2.name
    assert decoded.children[1].parent == decoded


def test_cash_account() -> None:
    currency = Currency("CZK", 2)
    cash_account = CashAccount(
        "Test Name", currency, CashAmount(0, currency), datetime.now(tzinfo)
    )
    serialized = json.dumps(cash_account, cls=CustomJSONEncoder)
    decoded = json.loads(serialized, cls=CustomJSONDecoder)
    assert isinstance(decoded, CashAccount)
    assert decoded.name == cash_account.name
    assert decoded.currency == cash_account.currency
    assert decoded.initial_balance == cash_account.initial_balance
    assert decoded.initial_datetime == cash_account.initial_datetime
    assert decoded.uuid == cash_account.uuid


def test_security_account() -> None:
    security_account = SecurityAccount("Test Name")
    serialized = json.dumps(security_account, cls=CustomJSONEncoder)
    decoded = json.loads(serialized, cls=CustomJSONDecoder)
    assert isinstance(decoded, SecurityAccount)
    assert decoded.name == security_account.name
    assert decoded.uuid == security_account.uuid


def test_security() -> None:
    currency = Currency("CZK", 2)
    security = Security("Test Name", "SYMB.OL", SecurityType.ETF, currency, 1)
    serialized = json.dumps(security, cls=CustomJSONEncoder)
    decoded = json.loads(serialized, cls=CustomJSONDecoder)
    assert isinstance(decoded, Security)
    assert decoded.name == security.name
    assert decoded.symbol == security.symbol
    assert decoded.currency == security.currency
    assert decoded.type_ == security.type_
    assert decoded.shares_unit == security.shares_unit
    assert decoded.price_places == security.price_places
    assert decoded.uuid == security.uuid
