from collections.abc import Callable
from datetime import datetime, timedelta, timezone
from random import randint
from typing import Any

import pytest
from hypothesis import assume, given
from hypothesis import strategies as st

from src.models.transactions.attributes.category import Category

timezone_offset = +1.0  # Central European Time (CET = UTC+01:00)
tzinfo = timezone(timedelta(hours=timezone_offset))


@st.composite
def categories(draw: Callable[[st.SearchStrategy[str]], str]) -> Category:
    name = draw(st.text(min_size=1, max_size=32))
    return Category(name)


@st.composite
def list_of_categories(
    draw: Callable[[st.SearchStrategy[Category]], Category]
) -> list[Category]:
    list_of_categories = []
    size = randint(1, 10)
    for _ in range(size):
        category = draw(categories())
        list_of_categories.append(category)
    return list_of_categories


@given(name=st.text(min_size=1, max_size=32))
def test_creation_pass(name: str) -> None:
    dt_start = datetime.now(tzinfo)
    category = Category(name)

    dt_created_diff = category.date_created - dt_start
    dt_edited_diff = category.date_last_edited - dt_start

    assert category.name == name
    assert category.parent is None
    assert category.children == ()
    assert dt_created_diff.seconds < 1
    assert dt_created_diff == dt_edited_diff


@given(category=categories(), parent=categories())
def test_add_and_remove_parent(category: Category, parent: Category) -> None:
    assert category.parent is None
    category.parent = parent
    assert category.parent == parent
    category.parent = None
    assert category.parent is None


@given(
    category=categories(),
    parent=st.integers()
    | st.floats()
    | st.none()
    | st.datetimes()
    | st.booleans()
    | st.sampled_from([[], (), {}, set()]),
)
def test_parent_invalid_type(category: Category, parent: Any) -> None:
    assume(parent is not None)
    with pytest.raises(
        TypeError, match="Category parent can only be a Category or a None."
    ):
        category.parent = parent
