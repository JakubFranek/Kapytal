from abc import ABC, abstractmethod
from typing import Any

from src.models.model_objects.currency_objects import CashAmount, Currency
from src.presenters.utilities.event import Event


class BalanceMixin(ABC):
    def __init__(self, *args: Any, **kwargs: Any) -> None:  # noqa: ANN401
        super().__init__(*args, **kwargs)
        self.event_balance_updated = Event()
        self._balances: tuple[CashAmount, ...] = ()

    @property
    def balances(self) -> tuple[CashAmount, ...]:
        """Returns a tuple of CashAmounts, one for each Currency."""
        return self._balances

    @abstractmethod
    def get_balance(self, currency: Currency) -> CashAmount:
        raise NotImplementedError
