import logging
from abc import ABC, abstractmethod
from collections.abc import Collection
from enum import Enum
from typing import Any

from src.models.base_classes.transaction import Transaction


class FilterMode(Enum):
    """Three possible filter modes: OFF, KEEP, DISCARD."""

    OFF = "No filter applied"
    KEEP = "Keep only transactions matching the filter criteria"
    DISCARD = "Discard all transactions matching the filter criteria"


class BaseTransactionFilter(ABC):
    def __init__(
        self, mode: FilterMode, *args: Any, **kwargs: Any  # noqa: ANN401
    ) -> None:
        super().__init__(*args, **kwargs)

        if not isinstance(mode, FilterMode):
            raise TypeError("Parameter 'mode' must be a FilterMode.")
        self._mode = mode

    @property
    def mode(self) -> FilterMode:
        return self._mode

    @property
    @abstractmethod
    def members(self) -> tuple[Any, ...]:
        raise NotImplementedError

    def __hash__(self) -> int:
        return hash(self.members)

    def __eq__(self, __o: object) -> bool:
        if not isinstance(__o, type(self)):
            return False
        return self.members == __o.members

    def filter_transactions(
        self, transactions: Collection[Transaction]
    ) -> tuple[Transaction]:
        if self._mode == FilterMode.OFF:
            return tuple(transactions)

        input_len = len(transactions)
        if self._mode == FilterMode.KEEP:
            output = tuple(
                transaction
                for transaction in transactions
                if self._keep_in_keep_mode(transaction)
            )
        else:
            output = tuple(
                transaction
                for transaction in transactions
                if self._keep_in_discard_mode(transaction)
            )
        if len(output) != input_len:
            logging.debug(
                f"{self.__class__.__name__}: mode={self._mode.name}, "
                f"removed={input_len - len(output)}"
            )
        return output

    @abstractmethod
    def _keep_in_keep_mode(self, transaction: Transaction) -> bool:
        """Returns True if this transaction is to be kept in KEEP mode."""
        raise NotImplementedError

    @abstractmethod
    def _keep_in_discard_mode(self, transaction: Transaction) -> bool:
        """Returns True if this transaction is to be kept in DISCARD mode."""
        raise NotImplementedError
