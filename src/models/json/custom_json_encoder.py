import json
from datetime import datetime
from typing import Any

from src.models.mixins.json_serializable_mixin import JSONSerializableMixin


class CustomJSONEncoder(json.JSONEncoder):
    def __init__(self, **kwargs: Any) -> None:  # noqa: ANN401
        """Arguments indent and separators are overriden!"""

        if kwargs.get("indent") is None:
            kwargs["indent"] = 2
        if kwargs.get("separators") is None:
            kwargs["separators"] = (", ", ": ")
        super().__init__(**kwargs)

    def default(self, arg: Any) -> Any:  # noqa: ANN401
        if isinstance(arg, datetime):
            return arg.isoformat()
        if isinstance(arg, JSONSerializableMixin):
            return arg.serialize()
        return super().default(arg)  # call to raise proper TypeError
