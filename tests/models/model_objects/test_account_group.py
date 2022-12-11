from datetime import datetime
from typing import Any

import pytest
from hypothesis import assume, given
from hypothesis import strategies as st

from src.models.constants import tzinfo
from src.models.model_objects.account_group import AccountGroup
from tests.models.composites import account_groups


@given(name=st.text(min_size=1, max_size=32))
def test_creation(name: str) -> None:
    dt_start = datetime.now(tzinfo)
    account_group = AccountGroup(name)

    dt_created_diff = account_group.datetime_created - dt_start

    assert account_group.name == name
    assert account_group.parent is None
    assert dt_created_diff.seconds < 1


@given(name=st.text(min_size=1, max_size=32), parent=account_groups())
def test_add_and_remove_parent(name: str, parent: AccountGroup) -> None:
    account_group = AccountGroup(name)
    assert account_group.parent is None
    assert account_group.children == ()
    account_group.parent = parent
    assert account_group.parent == parent
    assert account_group in parent.children
    account_group.parent = None
    assert account_group.parent is None
    assert account_group not in parent.children


@given(
    name=st.text(min_size=1, max_size=32),
    parent=st.integers()
    | st.floats()
    | st.none()
    | st.datetimes()
    | st.booleans()
    | st.sampled_from([[], (), {}, set()]),
)
def test_invalid_parent_type(name: str, parent: Any) -> None:
    assume(parent is not None)
    account = AccountGroup(name)
    with pytest.raises(
        TypeError, match="AccountGroup.parent must be an AccountGroup or a None."
    ):
        account.parent = parent
