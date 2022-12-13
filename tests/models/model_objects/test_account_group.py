from datetime import datetime
from decimal import Decimal
from typing import Any

import pytest
from hypothesis import assume, given
from hypothesis import strategies as st

from src.models.constants import tzinfo
from src.models.model_objects.account_group import AccountGroup
from src.models.model_objects.cash_objects import CashAccount
from tests.models.test_assets.composites import account_groups, cash_accounts


@given(name=st.text(min_size=1, max_size=32))
def test_creation(name: str) -> None:
    dt_start = datetime.now(tzinfo)
    account_group = AccountGroup(name)

    dt_created_diff = account_group.datetime_created - dt_start

    assert account_group.name == name
    assert account_group.parent is None
    assert dt_created_diff.seconds < 1
    assert account_group.balance == Decimal(0)


@given(account_group=account_groups(), parent=account_groups())
def test_add_and_remove_parent(
    account_group: AccountGroup, parent: AccountGroup
) -> None:
    assert account_group.parent is None
    assert account_group.children == ()
    account_group.parent = parent
    assert account_group.parent == parent
    assert account_group in parent.children
    account_group.parent = None
    assert account_group.parent is None
    assert account_group not in parent.children


@given(
    account_group=account_groups(),
    parent=st.integers()
    | st.floats()
    | st.none()
    | st.datetimes()
    | st.booleans()
    | st.sampled_from([[], (), {}, set()]),
)
def test_invalid_parent_type(account_group: AccountGroup, parent: Any) -> None:
    assume(parent is not None)
    with pytest.raises(
        TypeError, match="AccountGroup.parent must be an AccountGroup or a None."
    ):
        account_group.parent = parent


@given(
    account_group=account_groups(),
    accounts=st.lists(cash_accounts(), min_size=1, max_size=5),
)
def test_balance(account_group: AccountGroup, accounts: list[CashAccount]) -> None:
    for account in accounts:
        account.parent = account_group

    expected_sum = sum(account.balance for account in accounts)
    assert account_group.balance == expected_sum
