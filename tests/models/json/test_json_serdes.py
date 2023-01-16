import json
from datetime import datetime
from decimal import Decimal

import pytest
from hypothesis import given

from src.models.constants import tzinfo
from src.models.json.custom_json_decoder import CustomJSONDecoder
from src.models.json.custom_json_encoder import CustomJSONEncoder
from src.models.model_objects.attributes import Attribute
from src.models.model_objects.currency import CashAmount, Currency, ExchangeRate
from tests.models.test_assets.composites import attributes


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
