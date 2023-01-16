import json
from datetime import datetime
from decimal import Decimal
from typing import Any

from src.models.mixins.json_serializable_mixin import JSONSerializableMixin


class CustomJSONEncoder(json.JSONEncoder):
    def __init__(self, *args: Any, **kwargs: Any) -> None:  # noqa: U100
        super().__init__(indent=2, separators=(", ", ": "))

    def default(self, arg: Any) -> Any:
        if isinstance(arg, datetime):
            return {"datatype": "datetime", "datetime": arg.isoformat()}
        if isinstance(arg, Decimal):
            return {"datatype": "Decimal", "number": str(arg)}
        if isinstance(arg, JSONSerializableMixin):
            return arg.to_dict()
        return super().default(arg)  # call to raise proper TypeError
