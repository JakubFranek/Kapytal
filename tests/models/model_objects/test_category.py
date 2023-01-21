from typing import Any

import pytest
from hypothesis import assume, given
from hypothesis import strategies as st

from src.models.mixins.name_mixin import NameLengthError
from src.models.model_objects.attributes import Category, CategoryType
from tests.models.test_assets.composites import categories, everything_except, names


@given(name=names(), category_type=st.sampled_from(CategoryType))
def test_creation(name: str, category_type: CategoryType) -> None:
    category = Category(name, category_type)

    assert category.name == name
    assert category.type_ == category_type
    assert category.parent is None
    assert category.children == ()


@given(
    name=st.just(""),
    type_=st.sampled_from(CategoryType),
)
def test_name_too_short(name: str, type_: CategoryType) -> None:
    with pytest.raises(NameLengthError):
        Category(name, type_)


@given(
    name=names(min_size=33),
    type_=st.sampled_from(CategoryType),
)
def test_name_too_long(name: str, type_: CategoryType) -> None:
    with pytest.raises(NameLengthError):
        Category(name, type_)


@given(category=categories(), parent=categories())
def test_add_and_remove_parent(category: Category, parent: Category) -> None:
    assume(category.type_ == parent.type_)
    assert category.parent is None
    assert category not in parent.children
    category.parent = parent
    assert category.parent == parent
    assert category in parent.children
    category.parent = None
    assert category.parent is None
    assert category not in parent.children


@given(category=categories(), parent=everything_except((Category, type(None))))
def test_parent_invalid_type(category: Category, parent: Any) -> None:
    with pytest.raises(
        TypeError, match="Category.parent must be a Category or a None."
    ):
        category.parent = parent


@given(
    name=names(),
    category_type=everything_except(CategoryType),
)
def test_type_invalid_type(name: str, category_type: Any) -> None:
    with pytest.raises(TypeError, match="Category.type_ must be a CategoryType."):
        Category(name, category_type)


@given(category=categories(), parent=categories())
def test_invalid_parent_type(category: Category, parent: Category) -> None:
    assume(category.type_ != parent.type_)
    with pytest.raises(
        ValueError,
        match="The type_ of parent Category must match the type_ of this Category.",
    ):
        category.parent = parent


@given(first_category=categories(), length=st.integers(1, 5), data=st.data())
def test_path(first_category: Category, length: int, data: st.DataObject) -> None:
    type_ = first_category.type_
    categories = [first_category]
    for i in range(0, length):
        category = Category(data.draw(names()), type_)
        category.parent = categories[i]
        categories.append(category)

    expected_string = ""
    for category in categories:
        expected_string += category.name + "/"

    assert categories[-1].path == expected_string[:-1]
