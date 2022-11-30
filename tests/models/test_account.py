import string
from typing import Any, Callable

import pytest
from hypothesis import given, strategies

from src.models.account import Account
from src.models.currency import Currency


@strategies.composite
def currencies(draw: Callable[[strategies.SearchStrategy[str]], str]) -> Currency:
    name = draw(strategies.text(alphabet=string.ascii_letters, min_size=3, max_size=3))
    return Currency(name)


@given(
    name=strategies.text(min_size=1, max_size=32),
    currency=currencies(),
)
def test_account_creation_pass(name: str, currency: Currency):
    account = Account(name, currency)
    assert account.name == name
    assert account.currency == currency


@given(name=strategies.just(""), currency=currencies())
def test_account_name_too_short(name: str, currency: Currency):
    with pytest.raises(ValueError):
        Account(name, currency)


@given(name=strategies.text(min_size=33), currency=currencies())
def test_account_name_too_long(name: str, currency: Currency):
    with pytest.raises(ValueError):
        Account(name, currency)


@given(
    name=strategies.integers()
    | strategies.floats()
    | strategies.none()
    | strategies.datetimes()
    | strategies.booleans()
    | strategies.sampled_from([[], (), {}, dict()]),
    currency=currencies(),
)
def test_account_name_not_string(name: Any, currency: Currency):
    with pytest.raises(TypeError):
        Account(name, currency)
