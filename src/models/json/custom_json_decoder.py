import json
from datetime import datetime
from decimal import Decimal
from typing import Any

from src.models.model_objects.attributes import Attribute, Category
from src.models.model_objects.currency import CashAmount, Currency
from src.models.model_objects.security_objects import Security
from src.models.record_keeper import RecordKeeper


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
                case "RecordKeeper":
                    return RecordKeeper.from_dict(obj)
                case "Currency":
                    return Currency.from_dict(obj)
                case "CashAmount":
                    return CashAmount.from_dict(obj)
                case "Attribute":
                    return Attribute.from_dict(obj)
                case "Category":
                    return Category.from_dict(obj)
                case "Security":
                    return Security.from_dict(obj)
                case _:
                    return obj
        raise NotImplementedError
