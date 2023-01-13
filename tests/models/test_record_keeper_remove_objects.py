from datetime import datetime
from decimal import Decimal

import pytest

from src.models.constants import tzinfo
from src.models.custom_exceptions import InvalidOperationError
from src.models.model_objects.security_objects import SecurityType
from src.models.record_keeper import DoesNotExistError, RecordKeeper


def test_remove_account() -> None:
    record_keeper = RecordKeeper()
    record_keeper.add_account_group("PARENT", None)
    parent = record_keeper.account_groups[0]

    record_keeper.add_security_account("TEST NAME", "PARENT")
    assert len(parent.children) != 0
    assert len(record_keeper.accounts) != 0

    record_keeper.remove_account("PARENT/TEST NAME")
    assert parent.children == ()
    assert record_keeper.accounts == ()


def test_remove_account_does_not_exist() -> None:
    record_keeper = RecordKeeper()
    with pytest.raises(DoesNotExistError):
        record_keeper.remove_account("")


def test_remove_account_has_children() -> None:
    record_keeper = RecordKeeper()
    record_keeper.add_account_group("PARENT", None)
    parent = record_keeper.account_groups[0]

    record_keeper.add_security_account("TEST SENDER", "PARENT")
    record_keeper.add_security_account("TEST RECIPIENT", "PARENT")
    assert len(parent.children) != 0
    assert len(record_keeper.accounts) != 0

    record_keeper.add_currency("CZK", 2)
    record_keeper.add_security("NAME", "SYMB", SecurityType.ETF, "CZK", 1)
    sender_path = "PARENT/TEST SENDER"
    recipient_path = "PARENT/TEST RECIPIENT"
    record_keeper.add_security_transfer(
        "", datetime.now(tzinfo), "SYMB", Decimal(1), sender_path, recipient_path
    )

    with pytest.raises(InvalidOperationError):
        record_keeper.remove_account("PARENT/TEST SENDER")


def test_remove_account_group() -> None:
    record_keeper = RecordKeeper()
    record_keeper.add_account_group("PARENT", None)
    parent = record_keeper.account_groups[0]

    record_keeper.add_account_group("TEST NAME", "PARENT")
    assert len(parent.children) != 0
    assert len(record_keeper.account_groups) != 0

    record_keeper.remove_account_group("PARENT/TEST NAME")
    assert parent.children == ()
    assert record_keeper.account_groups == (parent,)


def test_remove_account_group_does_not_exist() -> None:
    record_keeper = RecordKeeper()
    with pytest.raises(DoesNotExistError):
        record_keeper.remove_account_group("")


def test_remove_account_group_has_children() -> None:
    record_keeper = RecordKeeper()
    record_keeper.add_account_group("PARENT", None)
    parent = record_keeper.account_groups[0]

    record_keeper.add_account_group("TEST NAME", "PARENT")
    assert len(parent.children) != 0
    assert len(record_keeper.account_groups) != 0

    record_keeper.add_account_group("TEST CHILD", "PARENT/TEST NAME")

    with pytest.raises(InvalidOperationError):
        record_keeper.remove_account_group("PARENT/TEST NAME")
