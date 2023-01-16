import json
from datetime import datetime
from decimal import Decimal
from typing import Any

from src.models.model_objects.currency import CashAmount, Currency, ExchangeRate


class CustomJSONDecoder(json.JSONDecoder):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(object_hook=self.object_hook, *args, **kwargs)

    def object_hook(self, obj: Any) -> Any:
        if "datatype" in obj:
            match obj["datatype"]:
                case "datetime":
                    return datetime.fromisoformat(obj["datetime"])
                case "Decimal":
                    return Decimal(obj["number"])
                case "Currency":
                    return Currency.from_dict(obj)
                case "ExchangeRate":
                    return ExchangeRate.from_dict(obj)
                case "CashAmount":
                    return CashAmount.from_dict(obj)
        raise NotImplementedError
