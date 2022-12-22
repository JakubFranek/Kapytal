import pytest
from hypothesis import given
from hypothesis import strategies as st

from src.models.mixins.name_mixin import NameLengthError
from src.models.model_objects.security_objects import Security, SecurityType


@given(
    name=st.text(min_size=1, max_size=64),
    symbol=st.text(alphabet=Security.SYMBOL_ALLOWED_CHARS, min_size=1, max_size=8),
    type_=st.sampled_from(SecurityType),
)
def test_creation(name: str, symbol: str, type_: SecurityType) -> None:
    security = Security(name, symbol, type_)
    assert security.name == name
    assert security.symbol == symbol.upper()
    assert security.type_ == type_


@given(
    name=st.just(""),
    symbol=st.just("Test"),
    type_=st.just(SecurityType.ETF),
)
def test_name_too_short(name: str, symbol: str, type_: SecurityType) -> None:
    with pytest.raises(NameLengthError):
        Security(name, symbol, type_)


@given(
    name=st.text(min_size=65),
    symbol=st.just("Test"),
    type_=st.just(SecurityType.ETF),
)
def test_name_too_long(name: str, symbol: str, type_: SecurityType) -> None:
    with pytest.raises(NameLengthError):
        Security(name, symbol, type_)
