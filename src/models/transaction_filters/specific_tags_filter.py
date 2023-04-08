from collections.abc import Collection

from src.models.base_classes.transaction import Transaction
from src.models.model_objects.attributes import (
    Attribute,
    AttributeType,
    InvalidAttributeError,
)
from src.models.transaction_filters.filter_mode_mixin import FilterMode, FilterModeMixin


class SpecificTagsFilter(FilterModeMixin):
    """Filters transactions based on whether they have specific tags.
    Leaves Tag-less transactions alone.

    KEEP: Keeps only Transactions with the specified Tags (or no Tags).
    DISCARD: Discards Transactions with the specified Tags."""

    def __init__(self, tags: Collection[Attribute], mode: FilterMode) -> None:
        super().__init__(mode=mode)

        if any(not isinstance(tag, Attribute) for tag in tags):
            raise TypeError("Parameter 'tags' must be a collection of Attributes.")
        if any(tag.type_ != AttributeType.TAG for tag in tags):
            raise InvalidAttributeError(
                "Parameter 'tags' must contain only Attributes with type_=TAG."
            )
        self._tags = frozenset(tags)

    @property
    def tags(self) -> frozenset[Attribute]:
        return self._tags

    @property
    def members(self) -> tuple[frozenset[Attribute], FilterMode]:
        return (self._tags, self._mode)

    def __repr__(self) -> str:
        return f"SpecificTagsFilter(tags={self._tags}, mode={self._mode.name})"

    def __hash__(self) -> int:
        return hash(self.members)

    def __eq__(self, __o: object) -> bool:
        if not isinstance(__o, SpecificTagsFilter):
            return False
        return self.members == __o.members

    def filter_transactions(
        self, transactions: Collection[Transaction]
    ) -> tuple[Transaction]:
        if self._mode == FilterMode.OFF:
            return tuple(transactions)
        if self._mode == FilterMode.KEEP:
            return tuple(
                transaction
                for transaction in transactions
                if any(tag in self._tags for tag in transaction.tags)
                or len(transaction.tags) == 0
            )
        if self._mode == FilterMode.DISCARD:
            return tuple(
                transaction
                for transaction in transactions
                if not any(tag in self._tags for tag in transaction.tags)
                or len(transaction.tags) == 0
            )
        raise ValueError("Invalid FilterMode value.")  # pragma: no cover
