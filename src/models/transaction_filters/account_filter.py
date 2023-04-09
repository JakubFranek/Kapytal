from collections.abc import Collection

from src.models.base_classes.account import Account
from src.models.base_classes.transaction import Transaction
from src.models.transaction_filters.base_transaction_filter import (
    BaseTransactionFilter,
    FilterMode,
)


class AccountFilter(BaseTransactionFilter):
    def __init__(self, accounts: Collection[Account], mode: FilterMode) -> None:
        super().__init__(mode=mode)
        if any(not isinstance(account, Account) for account in accounts):
            raise TypeError("Parameter 'accounts' must be a Collection ofAccounts.")
        self._accounts = tuple(accounts)

    @property
    def accounts(self) -> tuple[Account, ...]:
        return self._accounts

    @property
    def members(self) -> tuple[tuple[Account, ...], FilterMode]:
        return (self._accounts, self._mode)

    def __repr__(self) -> str:
        return f"AccountFilter(accounts={self._accounts}, mode={self._mode.name})"

    def _keep_in_keep_mode(self, transaction: Transaction) -> bool:
        return transaction.is_accounts_related(self._accounts)

    def _keep_in_discard_mode(self, transaction: Transaction) -> bool:
        return not self._keep_in_keep_mode(transaction)
