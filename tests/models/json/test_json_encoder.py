import json
from datetime import datetime
from decimal import Decimal

import pytest
from hypothesis import given

from src.models.constants import tzinfo
from src.models.json.custom_json_encoder import CustomJSONEncoder
from src.models.model_objects.attributes import Attribute
from src.models.model_objects.currency import CashAmount, Currency, ExchangeRate
from tests.models.test_assets.composites import attributes


def test_invalid_object() -> None:
    with pytest.raises(TypeError, match="not JSON serializable"):
        json.dumps(object, cls=CustomJSONEncoder)


def test_decimal() -> None:
    obj = Decimal("1.234")
    result = json.dumps(obj, cls=CustomJSONEncoder)
    expected_dict = {"datatype": "Decimal", "number": "1.234"}
    expected_string = json.dumps(expected_dict, cls=CustomJSONEncoder)
    assert result == expected_string


def test_datetime() -> None:
    obj = datetime.now(tzinfo)
    result = json.dumps(obj, cls=CustomJSONEncoder)
    expected_dict = {"datatype": "datetime", "datetime": obj.isoformat()}
    expected_string = json.dumps(expected_dict, cls=CustomJSONEncoder)
    assert result == expected_string


def test_currency() -> None:
    currency = Currency("CZK", 2)
    result = json.dumps(currency, cls=CustomJSONEncoder)
    expected_dict = {
        "datatype": "Currency",
        "code": currency.code,
        "places": currency.places,
    }
    expected_string = json.dumps(expected_dict, cls=CustomJSONEncoder)
    assert result == expected_string


def test_exchange_rate() -> None:
    primary = Currency("EUR", 2)
    secondary = Currency("CZK", 2)
    exchange_rate = ExchangeRate(primary, secondary)
    result = json.dumps(exchange_rate, cls=CustomJSONEncoder)
    expected_dict = {
        "datatype": "ExchangeRate",
        "primary_currency": primary,
        "secondary_currency": secondary,
    }
    expected_string = json.dumps(expected_dict, cls=CustomJSONEncoder)
    assert result == expected_string


def test_cash_amount() -> None:
    amount = CashAmount(Decimal("1.23"), Currency("CZK", 2))
    result = json.dumps(amount, cls=CustomJSONEncoder)
    expected_dict = {
        "datatype": "CashAmount",
        "value": Decimal("1.23"),
        "currency": Currency("CZK", 2),
    }
    expected_string = json.dumps(expected_dict, cls=CustomJSONEncoder)
    assert result == expected_string


@given(attribute=attributes())
def test_attribute(attribute: Attribute) -> None:
    result = json.dumps(attribute, cls=CustomJSONEncoder)
    expected_dict = {
        "datatype": "Attribute",
        "name": attribute.name,
        "type_": attribute.type_.name,
    }
    expected_string = json.dumps(expected_dict, cls=CustomJSONEncoder)
    assert result == expected_string
