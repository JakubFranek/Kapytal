from datetime import timedelta
from decimal import Decimal

from hypothesis import given
from hypothesis import strategies as st

from src.models.model_objects.cash_objects import CashAccount
from src.models.model_objects.security_objects import (
    Security,
    SecurityAccount,
    SecurityTransaction,
    SecurityTransactionType,
)
from tests.models.test_assets.composites import (
    cash_accounts,
    securities,
    security_accounts,
)


@given(
    description=st.text(min_size=1, max_size=256),
    type_=st.just(SecurityTransactionType.BUY),
    security=securities(),
    shares=st.integers(min_value=1),
    price_per_share=st.decimals(
        min_value=0, max_value=1e10, allow_infinity=False, allow_nan=False
    ),
    fees=st.decimals(
        min_value=0, max_value=1e10, allow_infinity=False, allow_nan=False
    ),
    security_account=security_accounts(),
    cash_account=cash_accounts(),
    data=st.data(),
)
def test_buy(
    description: str,
    type_: SecurityTransactionType,
    security: Security,
    shares: int,
    price_per_share: Decimal,
    fees: Decimal,
    security_account: SecurityAccount,
    cash_account: CashAccount,
    data: st.DataObject,
) -> None:
    datetime_ = data.draw(
        st.datetimes(min_value=cash_account.initial_datetime + timedelta(days=1))
    )
    transaction = SecurityTransaction(
        description,
        datetime_,
        type_,
        security,
        shares,
        price_per_share,
        fees,
        security_account,
        cash_account,
    )
    assert transaction.price_per_share == price_per_share
    assert transaction.shares == shares
    assert transaction.security == security
    assert transaction.security_account == security_account
    assert transaction.cash_account == cash_account
    assert (
        cash_account.balance
        == cash_account.initial_balance - shares * price_per_share - fees
    )
    assert security_account.securities[security] == shares
