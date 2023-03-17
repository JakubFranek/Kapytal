import json
from datetime import datetime
from decimal import Decimal
from typing import Any

from src.models.mixins.json_serializable_mixin import JSONSerializableMixin
from src.models.utilities import constants


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
            return arg.strftime(constants.DATETIME_SERDES_FMT)
        if isinstance(arg, Decimal):
            return {"datatype": "Decimal", "number": str(arg)}
        if isinstance(arg, JSONSerializableMixin):
            return arg.serialize()
        return super().default(arg)  # call to raise proper TypeError
