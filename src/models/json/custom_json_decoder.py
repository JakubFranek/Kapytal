import json
from typing import Any

from src.models.model_objects.currency_objects import Currency
from src.models.user_settings.user_settings_class import UserSettings


class CustomJSONDecoder(json.JSONDecoder):
    def __init__(self, *args: Any, **kwargs: Any) -> None:  # noqa: ANN401
        super().__init__(*args, **kwargs, object_hook=self._object_hook)

    @staticmethod
    def _object_hook(obj: dict[str, Any]) -> Any:  # noqa: ANN401
        if "datatype" in obj:
            match obj["datatype"]:
                case "Currency":
                    return Currency.deserialize(obj)
                case "UserSettings":
                    return UserSettings.deserialize(obj)
                case _:
                    return obj
        if "data" in obj:
            return obj
        raise NotImplementedError
