import json
from datetime import datetime
from decimal import Decimal

from hypothesis import given

from src.models.constants import tzinfo
from src.models.json.custom_json_decoder import CustomJSONDecoder
from src.models.json.custom_json_encoder import CustomJSONEncoder
from src.models.model_objects.attributes import Attribute
from src.models.model_objects.currency import CashAmount, Currency, ExchangeRate
from tests.models.test_assets.composites import attributes


def test_decimal() -> None:
    data_dict = {"datatype": "Decimal", "number": "1.234"}
    data = json.dumps(data_dict, cls=CustomJSONEncoder)
    result = json.loads(data, cls=CustomJSONDecoder)
    assert isinstance(result, Decimal)
    assert str(result) == "1.234"


def test_datetime() -> None:
    dt = datetime.now(tzinfo)
    data_dict = {"datatype": "datetime", "datetime": dt.isoformat()}
    data = json.dumps(data_dict, cls=CustomJSONEncoder)
    result = json.loads(data, cls=CustomJSONDecoder)
    assert isinstance(result, datetime)
    assert dt == result


def test_currency() -> None:
    data_dict = {
        "datatype": "Currency",
        "code": "CZK",
        "places": 2,
    }
    data = json.dumps(data_dict, cls=CustomJSONEncoder)
    result = json.loads(data, cls=CustomJSONDecoder)
    assert isinstance(result, Currency)
    assert result.code == "CZK"
    assert result.places == 2


def test_exchange_rate() -> None:
    primary = Currency("EUR", 2)
    secondary = Currency("CZK", 2)
    data_dict = {
        "datatype": "ExchangeRate",
        "primary_currency": primary.to_dict(),
        "secondary_currency": secondary.to_dict(),
    }
    data = json.dumps(data_dict, cls=CustomJSONEncoder)
    result = json.loads(data, cls=CustomJSONDecoder)
    assert isinstance(result, ExchangeRate)
    assert result.primary_currency == primary
    assert result.secondary_currency == secondary


def test_cash_amount() -> None:
    currency = Currency("EUR", 2)
    data_dict = {
        "datatype": "CashAmount",
        "value": Decimal("1.23"),
        "currency": currency,
    }
    data = json.dumps(data_dict, cls=CustomJSONEncoder)
    result = json.loads(data, cls=CustomJSONDecoder)
    assert isinstance(result, CashAmount)
    assert result.value == Decimal("1.23")
    assert result.currency == currency


@given(attribute=attributes())
def test_attribute(attribute: Attribute) -> None:
    data_dict = {
        "datatype": "Attribute",
        "name": attribute.name,
        "type_": attribute.type_.name,
    }
    data = json.dumps(data_dict, cls=CustomJSONEncoder)
    result = json.loads(data, cls=CustomJSONDecoder)
    assert isinstance(result, Attribute)
    assert result.name == attribute.name
    assert result.type_ == attribute.type_
