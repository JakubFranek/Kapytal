import json
from datetime import datetime
from decimal import Decimal
from typing import Any

from src.models.model_objects.attributes import Attribute
from src.models.model_objects.currency_objects import Currency
from src.models.record_keeper import RecordKeeper
from src.models.user_settings.user_settings_class import UserSettings


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
                    return RecordKeeper.deserialize(obj)
                case "Currency":
                    return Currency.deserialize(obj)
                case "Attribute":
                    return Attribute.deserialize(obj)
                case "UserSettings":
                    return UserSettings.deserialize(obj)
                case _:
                    return obj
        raise NotImplementedError
