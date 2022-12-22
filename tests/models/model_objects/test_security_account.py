from typing import Any

import pytest
from hypothesis import assume, given
from hypothesis import strategies as st

from src.models.base_classes.account import UnrelatedAccountError
from src.models.model_objects.account_group import AccountGroup
from src.models.model_objects.security_objects import (
    SecurityAccount,
    SecurityTransaction,
)
from tests.models.test_assets.composites import (
    account_groups,
    everything_except,
    security_accounts,
    security_transactions,
)


@given(name=st.text(min_size=1, max_size=32), parent=st.none() | account_groups())
def test_creation(name: str, parent: AccountGroup | None) -> None:
    security_account = SecurityAccount(name, parent)
    assert security_account.name == name
    assert security_account.parent == parent
    assert security_account.balance == 0
    assert security_account.securities == {}
    assert security_account.transactions == ()
    assert security_account.__repr__() == f"SecurityAccount('{name}')"


@given(
    security_account=security_accounts(),
    transaction=everything_except(SecurityTransaction),
)
def test_validate_transaction_invalid_type(
    security_account: SecurityAccount, transaction: Any
) -> None:
    with pytest.raises(
        TypeError, match="Argument 'transaction' must be a SecurityTransaction."
    ):
        security_account._validate_transaction(transaction)


@given(
    security_account=security_accounts(),
    transaction=security_transactions(),
)
def test_validate_transaction_unrelated(
    security_account: SecurityAccount, transaction: SecurityTransaction
) -> None:
    assume(transaction.security_account != security_account)
    with pytest.raises(UnrelatedAccountError):
        security_account._validate_transaction(transaction)
