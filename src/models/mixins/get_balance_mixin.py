from abc import ABC, abstractmethod

from src.models.model_objects.currency_objects import CashAmount, Currency


class GetBalanceMixin(ABC):
    @abstractmethod
    def get_balance(self, currency: Currency) -> CashAmount:
        raise NotImplementedError
