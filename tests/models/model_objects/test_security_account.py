from typing import Any

import pytest
from hypothesis import assume, given
from hypothesis import strategies as st

from src.models.base_classes.account import UnrelatedAccountError
from src.models.model_objects.account_group import AccountGroup
from src.models.model_objects.security_objects import (
    SecurityAccount,
    SecurityRelatedTransaction,
)
from tests.models.test_assets.composites import (
    account_groups,
    everything_except,
    security_accounts,
    security_transactions,
    security_transfers,
)


@given(name=st.text(min_size=1, max_size=32), parent=st.none() | account_groups())
def test_creation(name: str, parent: AccountGroup | None) -> None:
    security_account = SecurityAccount(name, parent)
    assert security_account.name == name
    assert security_account.parent == parent
    assert security_account.securities == {}
    assert security_account.transactions == ()
    assert security_account.__repr__() == f"SecurityAccount('{name}')"


@given(
    security_account=security_accounts(),
    transaction=everything_except(SecurityRelatedTransaction),
)
def test_validate_transaction_invalid_type(
    security_account: SecurityAccount, transaction: Any
) -> None:
    with pytest.raises(
        TypeError, match="Argument 'transaction' must be a SecurityRelatedTransaction."
    ):
        security_account._validate_transaction(transaction)


@given(
    security_account=security_accounts(),
    transaction=security_transactions() | security_transfers(),
)
def test_validate_transaction_unrelated(
    security_account: SecurityAccount, transaction: SecurityRelatedTransaction
) -> None:
    assume(not transaction.is_account_related(security_account))
    with pytest.raises(UnrelatedAccountError):
        security_account._validate_transaction(transaction)


# TODO: test this
def test_get_balance() -> None:
    pass
