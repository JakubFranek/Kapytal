from collections.abc import Collection

from src.models.base_classes.account import Account
from src.models.base_classes.transaction import Transaction
from src.models.transaction_filters.filter_mode_mixin import FilterMode, FilterModeMixin


class AccountFilter(FilterModeMixin):
    def __init__(self, accounts: Collection[Account], mode: FilterMode) -> None:
        super().__init__(mode=mode)
        if any(not isinstance(account, Account) for account in accounts):
            raise TypeError("Parameter 'accounts' must be a collection of Accounts.")
        self._accounts = tuple(accounts)

    @property
    def accounts(self) -> tuple[Account]:
        return self._accounts

    @property
    def members(self) -> tuple[tuple[Account], FilterMode]:
        return (self._accounts, self._mode)

    def __repr__(self) -> str:
        return f"AccountFilter(accounts={self._accounts}, mode={self._mode.name})"

    def __hash__(self) -> int:
        return hash(self.members)

    def __eq__(self, __o: object) -> bool:
        if not isinstance(__o, AccountFilter):
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
                if transaction.is_accounts_related(self._accounts)
            )
        if self._mode == FilterMode.DISCARD:
            return tuple(
                transaction
                for transaction in transactions
                if not transaction.is_accounts_related(self._accounts)
            )
        raise ValueError("Invalid FilterMode value.")  # pragma: no cover
