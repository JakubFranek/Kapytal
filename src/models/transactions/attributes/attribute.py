from datetime import datetime

from src.models.constants import tzinfo


class TransactionAttribute:
    NAME_MIN_LENGTH = 1
    NAME_MAX_LENGTH = 32

    def __init__(self, name: str) -> None:
        self.name = name
        self._date_created = datetime.now(tzinfo)
        self._date_last_edited = self.date_created

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, value: str) -> None:
        if not isinstance(value, str):
            raise TypeError("TransactionAttribute name must be a string.")

        if not hasattr(self, "_name") or (
            hasattr(self, "_name") and self._name != value
        ):
            if (
                len(value) < TransactionAttribute.NAME_MIN_LENGTH
                or len(value) > TransactionAttribute.NAME_MAX_LENGTH
            ):
                raise ValueError(
                    f"""TransactionAttribute name length must be between
                    {TransactionAttribute.NAME_MIN_LENGTH} and
                    {TransactionAttribute.NAME_MAX_LENGTH} characters."""
                )
            self._name = value
            self._date_last_edited = datetime.now(tzinfo)

    @property
    def date_created(self) -> datetime:
        return self._date_created

    @property
    def date_last_edited(self) -> datetime:
        return self._date_last_edited
