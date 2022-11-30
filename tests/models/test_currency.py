import string
from typing import Any

import pytest
from hypothesis import assume, example, given, strategies

from src.models.currency import Currency


@given(a=strategies.text(alphabet=string.ascii_letters, min_size=3, max_size=3))
def test_currency_code_pass(a: str):
    currency = Currency(a)
    assert currency.code == a.upper()


@given(a=strategies.text(max_size=2))
def test_currency_code_too_short(a: str):
    with pytest.raises(ValueError):
        Currency(a)


@given(a=strategies.text(min_size=4))
def test_currency_code_too_long(a: str):
    with pytest.raises(ValueError):
        Currency(a)


@given(a=strategies.text(min_size=3, max_size=3))
def test_currency_code_not_alpha(a: str):
    assume(any(char.isdigit() for char in a))
    with pytest.raises(ValueError):
        Currency(a)


@given(
    strategies.integers()
    | strategies.floats()
    | strategies.none()
    | strategies.datetimes()
    | strategies.booleans()
)
@example([])
@example({})
@example(dict())
def test_currency_code_not_string(a: Any):
    with pytest.raises(TypeError):
        Currency(a)
