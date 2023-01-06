from datetime import datetime
from typing import Any

import pytest
from hypothesis import given
from hypothesis import strategies as st

from src.models.constants import tzinfo
from src.models.model_objects.security_objects import (
    Security,
    SecurityAccount,
    SecurityTransfer,
)
from tests.models.test_assets.composites import (
    everything_except,
    securities,
    security_accounts,
    security_transfers,
    valid_decimals,
)


@given(
    description=st.text(min_size=1, max_size=256),
    datetime_=st.datetimes(timezones=st.just(tzinfo)),
    security=securities(),
    shares=valid_decimals(min_value=0.01),
    account_sender=security_accounts(),
    account_recipient=security_accounts(),
)
def test_creation(
    description: str,
    datetime_: datetime,
    security: Security,
    shares: int,
    account_sender: SecurityAccount,
    account_recipient: SecurityAccount,
) -> None:
    transfer = SecurityTransfer(
        description, datetime_, security, shares, account_sender, account_recipient
    )
    assert transfer.shares == shares
    assert transfer.security == security
    assert transfer.__repr__() == (
        f"SecurityTransfer(security='{transfer.security.symbol}', "
        f"shares={transfer.shares}, "
        f"from='{transfer.account_sender.name}', "
        f"to='{transfer.account_recipient.name}', "
        f"{transfer.datetime_.strftime('%Y-%m-%d')})"
    )
    assert transfer in account_sender.transactions
    assert transfer in account_recipient.transactions
    assert account_sender.securities[security] == -shares
    assert account_recipient.securities[security] == +shares


@given(
    description=st.text(min_size=1, max_size=256),
    datetime_=st.datetimes(timezones=st.just(tzinfo)),
    security=securities(),
    shares=valid_decimals(min_value=0.01),
    account_sender=everything_except(SecurityAccount),
    account_recipient=security_accounts(),
)
def test_invalid_account_sender_type(
    description: str,
    datetime_: datetime,
    security: Security,
    shares: int,
    account_sender: Any,
    account_recipient: SecurityAccount,
) -> None:
    with pytest.raises(
        TypeError, match="SecurityTransaction.account_sender must be a SecurityAccount."
    ):
        SecurityTransfer(
            description, datetime_, security, shares, account_sender, account_recipient
        )


@given(
    description=st.text(min_size=1, max_size=256),
    datetime_=st.datetimes(timezones=st.just(tzinfo)),
    security=securities(),
    shares=valid_decimals(min_value=0.01),
    account_recipient=everything_except(SecurityAccount),
    account_sender=security_accounts(),
)
def test_invalid_account_recipient_type(
    description: str,
    datetime_: datetime,
    security: Security,
    shares: int,
    account_sender: SecurityAccount,
    account_recipient: Any,
) -> None:
    with pytest.raises(
        TypeError,
        match="SecurityTransaction.account_recipient must be a SecurityAccount.",
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
    old_sender = transfer.account_sender
    old_recipient = transfer.account_recipient

    transfer.account_sender = new_sender
    transfer.account_recipient = new_recipient

    assert transfer not in old_sender.transactions
    assert transfer not in old_recipient.transactions
    assert transfer in new_sender.transactions
    assert transfer in new_recipient.transactions
    assert old_sender.securities[security] == 0
    assert old_recipient.securities[security] == 0
    assert new_sender.securities[security] == -shares
    assert new_recipient.securities[security] == +shares
