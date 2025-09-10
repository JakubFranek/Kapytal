import logging
from abc import ABC, abstractmethod
from collections.abc import Collection
from enum import Enum
from typing import Any, ParamSpec

from src.models.base_classes.transaction import Transaction

P = ParamSpec("P")


class FilterMode(Enum):
    """Three possible filter modes: OFF, KEEP, DISCARD."""

    OFF = "No filter applied"
    KEEP = "Keep only transactions matching the filter criteria"
    DISCARD = "Discard all transactions matching the filter criteria"


class BaseTransactionFilter(ABC):
    __slots__ = ()

    def __init__(
        self,
        mode: FilterMode,
        *args: P.args,
        **kwargs: P.kwargs,
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

    @property
    def is_all_pass(self) -> bool:
        return self._mode == FilterMode.OFF

    def __hash__(self) -> int:
        return hash(self.members)

    def __eq__(self, /, __o: object) -> bool:
        """Filters are considered equal if they are of the same type and
        both are OFF or their members are equal."""

        if not isinstance(__o, type(self)):
            return False
        if self._mode == FilterMode.OFF and __o.mode == FilterMode.OFF:
            return True
        return self.members == __o.members

    def validate_transaction(self, transaction: Transaction) -> bool:
        if self._mode == FilterMode.OFF:
            return True
        if self._mode == FilterMode.KEEP:
            return self._keep_in_keep_mode(transaction)
        return self._keep_in_discard_mode(transaction)

    def filter_transactions(
        self, transactions: Collection[Transaction]
    ) -> tuple[Transaction, ...]:
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
                f"discarded={input_len - len(output)}"
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
