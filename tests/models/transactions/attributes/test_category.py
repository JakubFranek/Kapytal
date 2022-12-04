from collections.abc import Callable
from datetime import datetime
from random import randint
from typing import Any

import pytest
from hypothesis import assume, given
from hypothesis import strategies as st

from src.models.constants import tzinfo
from src.models.transactions.attributes.category import Category
from src.models.transactions.enums import CategoryType


@st.composite
def categories(
    draw: Callable[[st.SearchStrategy[str | CategoryType]], str | CategoryType]
) -> Category:
    name = draw(st.text(min_size=1, max_size=32))
    category_type = draw(st.sampled_from(CategoryType))
    return Category(name, category_type)


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


@given(
    name=st.text(min_size=1, max_size=32), category_type=st.sampled_from(CategoryType)
)
def test_creation_pass(name: str, category_type: CategoryType) -> None:
    dt_start = datetime.now(tzinfo)
    category = Category(name, category_type)

    dt_created_diff = category.datetime_created - dt_start

    assert category.name == name
    assert category.type_ == category_type
    assert category.parent is None
    assert category.children == ()
    assert dt_created_diff.seconds < 1


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


@given(
    name=st.text(min_size=1, max_size=32),
    category_type=st.integers()
    | st.floats()
    | st.none()
    | st.datetimes()
    | st.booleans()
    | st.sampled_from([[], (), {}, set()]),
)
def test_type_invalid_type(name: str, category_type: Any) -> None:
    with pytest.raises(TypeError, match="Category type must be a CategoryType."):
        Category(name, category_type)
