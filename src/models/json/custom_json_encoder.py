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

    def default(self, o: Any) -> Any:  # noqa: ANN401
        if isinstance(o, datetime):
            return o.isoformat()
        if isinstance(o, JSONSerializableMixin):
            return o.serialize()
        return super().default(o)  # call to raise proper TypeError
