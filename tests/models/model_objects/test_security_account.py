from hypothesis import given
from hypothesis import strategies as st

from src.models.model_objects.account_group import AccountGroup
from src.models.model_objects.security_objects import SecurityAccount
from tests.models.test_assets.composites import account_groups


@given(name=st.text(min_size=1, max_size=32), parent=st.none() | account_groups())
def test_creation(name: str, parent: AccountGroup | None) -> None:
    security_account = SecurityAccount(name, parent)
    assert security_account.name == name
    assert security_account.parent == parent
    assert security_account.balance == 0
    assert security_account.securities == {}
    assert security_account.transactions == ()
    assert security_account.__repr__() == f"SecurityAccount('{name}')"
