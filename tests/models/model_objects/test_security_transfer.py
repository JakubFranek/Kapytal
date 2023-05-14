from datetime import datetime
from types import NoneType
from typing import Any

import pytest
from hypothesis import given
from hypothesis import strategies as st
from src.models.custom_exceptions import TransferSameAccountError
from src.models.model_objects.security_objects import (
    Security,
    SecurityAccount,
    SecurityTransfer,
)
from src.models.user_settings import user_settings
from tests.models.test_assets.composites import (
    everything_except,
    securities,
    security_accounts,
    security_transfers,
    share_decimals,
)


@given(
    description=st.text(min_size=1, max_size=256),
    datetime_=st.datetimes(timezones=st.just(user_settings.settings.time_zone)),
    security=securities(),
    account_sender=security_accounts(),
    account_recipient=security_accounts(),
    data=st.data(),
)
def test_creation(  # noqa: PLR0913
    description: str,
    datetime_: datetime,
    security: Security,
    account_sender: SecurityAccount,
    account_recipient: SecurityAccount,
    data: st.DataObject,
) -> None:
    shares = data.draw(share_decimals(security.shares_unit))
    transfer = SecurityTransfer(
        description, datetime_, security, shares, account_sender, account_recipient
    )
    assert transfer.shares == shares
    assert transfer.security == security
    assert transfer.__repr__() == (
        f"SecurityTransfer(security='{transfer.security.symbol}', "
        f"shares={transfer.shares}, "
        f"from='{transfer.sender.name}', "
        f"to='{transfer.recipient.name}', "
        f"{transfer.datetime_.strftime('%Y-%m-%d')})"
    )
    assert transfer in account_sender.transactions
    assert transfer in account_recipient.transactions
    assert account_sender.securities[security] == -shares
    assert account_recipient.securities[security] == +shares


@given(
    description=st.text(min_size=1, max_size=256),
    datetime_=st.datetimes(timezones=st.just(user_settings.settings.time_zone)),
    security=securities(),
    account_sender=everything_except((SecurityAccount, NoneType)),
    account_recipient=security_accounts(),
    data=st.data(),
)
def test_invalid_account_sender_type(  # noqa: PLR0913
    description: str,
    datetime_: datetime,
    security: Security,
    account_sender: Any,
    account_recipient: SecurityAccount,
    data: st.DataObject,
) -> None:
    shares = data.draw(share_decimals(shares_unit=security.shares_unit))
    with pytest.raises(
        TypeError, match="SecurityTransfer.sender must be a SecurityAccount."
    ):
        SecurityTransfer(
            description, datetime_, security, shares, account_sender, account_recipient
        )


@given(
    description=st.text(min_size=1, max_size=256),
    datetime_=st.datetimes(timezones=st.just(user_settings.settings.time_zone)),
    security=securities(),
    account_recipient=everything_except((SecurityAccount, NoneType)),
    account_sender=security_accounts(),
    data=st.data(),
)
def test_invalid_account_recipient_type(  # noqa: PLR0913
    description: str,
    datetime_: datetime,
    security: Security,
    account_sender: SecurityAccount,
    account_recipient: Any,
    data: st.DataObject,
) -> None:
    shares = data.draw(share_decimals(shares_unit=security.shares_unit))
    with pytest.raises(
        TypeError,
        match="SecurityTransfer.recipient must be a SecurityAccount.",
    ):
        SecurityTransfer(
            description, datetime_, security, shares, account_sender, account_recipient
        )


@given(
    transfer=security_transfers(),
    new_sender=security_accounts(),
    new_recipient=security_accounts(),
)
def test_change_accounts(
    transfer: SecurityTransfer,
    new_sender: SecurityAccount,
    new_recipient: SecurityAccount,
) -> None:
    security = transfer.security
    shares = transfer.shares
    old_sender = transfer.sender
    old_recipient = transfer.recipient

    transfer.set_attributes(sender=new_sender, recipient=new_recipient)

    assert transfer not in old_sender.transactions
    assert transfer not in old_recipient.transactions
    assert transfer in new_sender.transactions
    assert transfer in new_recipient.transactions
    assert old_sender.securities[security] == 0
    assert old_recipient.securities[security] == 0
    assert new_sender.securities[security] == -shares
    assert new_recipient.securities[security] == +shares


@given(transfer=security_transfers())
def test_validate_attribues_same_values(transfer: SecurityTransfer) -> None:
    transfer.validate_attributes()


@given(transfer=security_transfers())
def test_set_attribues_same_values(transfer: SecurityTransfer) -> None:
    transfer.set_attributes()


@given(transfer=security_transfers())
def test_set_attribues_same_accounts(transfer: SecurityTransfer) -> None:
    with pytest.raises(TransferSameAccountError):
        transfer.set_attributes(recipient=transfer.sender)


@given(transaction=security_transfers(), unrelated_account=security_accounts())
def test_is_accounts_related(
    transaction: SecurityTransfer, unrelated_account: SecurityAccount
) -> None:
    related_accounts = (transaction.sender, unrelated_account)
    assert transaction.is_accounts_related(related_accounts)
    related_accounts = (transaction.recipient, unrelated_account)
    assert transaction.is_accounts_related(related_accounts)
    related_accounts = (transaction.sender, transaction.recipient, unrelated_account)
    assert transaction.is_accounts_related(related_accounts)
    unrelated_accounts = (unrelated_account,)
    assert not transaction.is_accounts_related(unrelated_accounts)
