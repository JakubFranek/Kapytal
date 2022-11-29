import pytest
from hypothesis import given, strategies

from src.models.currency import Currency


@given(a=strategies.text(min_size=3, max_size=3))
def test_currency_code_pass(a):
    currency = Currency(a)
    assert currency.code == a


@given(a=strategies.text(max_size=2))
def test_currency_code_too_short(a):
    with pytest.raises(ValueError):
        currency = Currency(a)


@given(a=strategies.text(min_size=4))
def test_currency_code_too_long(a):
    with pytest.raises(ValueError):
        currency = Currency(a)
