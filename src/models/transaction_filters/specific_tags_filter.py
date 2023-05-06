import unicodedata
from collections.abc import Collection

from src.models.base_classes.transaction import Transaction
from src.models.model_objects.attributes import (
    Attribute,
    AttributeType,
    InvalidAttributeError,
)
from src.models.transaction_filters.base_transaction_filter import (
    BaseTransactionFilter,
    FilterMode,
)


class SpecificTagsFilter(BaseTransactionFilter):
    """Filters transactions based on whether they have specific Tags.
    Ignores Tag-less transactions.

    KEEP: Keeps only Transactions with the specified Tags (or no Tags).
    DISCARD: Discards Transactions with the specified Tags."""

    def __init__(self, tags: Collection[Attribute], mode: FilterMode) -> None:
        super().__init__(mode=mode)

        if any(not isinstance(tag, Attribute) for tag in tags):
            raise TypeError("Parameter 'tags' must be a Collection of Attributes.")
        if any(tag.type_ != AttributeType.TAG for tag in tags):
            raise InvalidAttributeError(
                "Parameter 'tags' must contain only Attributes with type_=TAG."
            )
        self._tags = frozenset(tags)

    @property
    def tags(self) -> frozenset[Attribute]:
        return self._tags

    @property
    def tag_names(self) -> tuple[str]:
        return tuple(
            sorted(
                (tag.name for tag in self._tags),
                key=lambda name: unicodedata.normalize("NFD", name.lower()),
            )
        )

    @property
    def members(self) -> tuple[frozenset[Attribute], FilterMode]:
        return (self._tags, self._mode)

    def __repr__(self) -> str:
        return f"SpecificTagsFilter(tags={self.tag_names}, mode={self._mode.name})"

    def _keep_in_keep_mode(self, transaction: Transaction) -> bool:
        return len(transaction.tags) == 0 or any(
            tag in self._tags for tag in transaction.tags
        )

    def _keep_in_discard_mode(self, transaction: Transaction) -> bool:
        return len(transaction.tags) == 0 or not any(
            tag in self._tags for tag in transaction.tags
        )
