from collections.abc import Collection
from uuid import UUID

from src.models.base_classes.transaction import Transaction
from src.models.transaction_filters.base_transaction_filter import (
    BaseTransactionFilter,
    FilterMode,
)


class UUIDFilter(BaseTransactionFilter):
    __slots__ = ("_uuids", "_mode", "_uuids_set")

    def __init__(self, uuids: Collection[UUID], mode: FilterMode) -> None:
        super().__init__(mode=mode)
        for _uuid in uuids:
            if not isinstance(_uuid, UUID):
                raise TypeError("Parameter 'uuids' must be a Collection of Accounts.")
        self._uuids = tuple(uuids)
        self._uuids_set = frozenset(uuids)

    @property
    def uuids(self) -> tuple[UUID, ...]:
        return self._uuids

    @property
    def uuids_set(self) -> frozenset[UUID]:
        return self._uuids_set

    @property
    def members(self) -> tuple[tuple[UUID, ...], FilterMode]:
        return (self._uuids_set, self._mode)

    def __repr__(self) -> str:
        return f"UUIDFilter(uuids={self._uuids}, mode={self._mode.name})"

    def _keep_in_keep_mode(self, transaction: Transaction) -> bool:
        return transaction.uuid in self._uuids_set

    def _keep_in_discard_mode(self, transaction: Transaction) -> bool:
        return transaction.uuid not in self._uuids_set
