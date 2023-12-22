from typing import Any

import pytest
from hypothesis import assume, given
from hypothesis import strategies as st
from src.models.custom_exceptions import NotFoundError
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
    type_=st.sampled_from(CategoryType),
)
def test_name_invalid_value(type_: CategoryType) -> None:
    name = "Total"
    with pytest.raises(ValueError, match="The word 'Total' is reserved for Reports."):
        Category(name, type_)


@given(
    name=st.just(""),
    type_=st.sampled_from(CategoryType),
)
def test_name_too_short(name: str, type_: CategoryType) -> None:
    with pytest.raises(NameLengthError):
        Category(name, type_)


@given(
    name=names(min_size=65),
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


@given(category=categories(), parent=categories())
def test_set_same_parent(category: Category, parent: Category) -> None:
    assume(category.type_ == parent.type_)
    category.parent = parent
    category.parent = parent
    assert category.parent == parent


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
    for i in range(length):
        category = Category(data.draw(names()), type_)
        category.parent = categories[i]
        categories.append(category)

    expected_string = ""
    for category in categories:
        expected_string += category.name + "/"

    assert categories[-1].path == expected_string[:-1]


@given(data=st.data())
def test_set_child_index(data: st.DataObject) -> None:
    parent = data.draw(categories())
    children = data.draw(
        st.lists(categories(category_type=parent.type_), min_size=5, max_size=5)
    )
    for child in children:
        child.parent = parent

    selected_index = data.draw(st.integers(min_value=0, max_value=len(children) - 1))
    new_index = data.draw(st.integers(min_value=0, max_value=len(children) - 1))

    selected_child = children[selected_index]
    parent.set_child_index(selected_child, new_index)
    assert parent.children[new_index] == selected_child


@given(data=st.data())
def test_set_child_index_specific_case(data: st.DataObject) -> None:
    parent = data.draw(categories())
    children = data.draw(
        st.lists(categories(category_type=parent.type_), min_size=10, max_size=10)
    )
    for child in children:
        child.parent = parent

    selected_index = 7
    new_index = 3

    selected_child = children[selected_index]
    parent.set_child_index(selected_child, new_index)
    assert parent.children[new_index] == selected_child


@given(data=st.data())
def test_set_child_index_same_value(data: st.DataObject) -> None:
    parent = data.draw(categories())
    children = data.draw(
        st.lists(categories(category_type=parent.type_), min_size=5, max_size=5)
    )
    for child in children:
        child.parent = parent

    selected_child = children[0]
    parent.set_child_index(selected_child, 0)
    assert parent.children[0] == selected_child


def test_set_child_index_child_does_not_exist() -> None:
    parent = Category("test", CategoryType.EXPENSE)
    with pytest.raises(NotFoundError):
        parent.set_child_index(None, 0)


def test_set_child_index_negative() -> None:
    parent = Category("test", CategoryType.EXPENSE)
    with pytest.raises(ValueError, match="negative"):
        parent.set_child_index(None, -1)


def test_is_ancestor_of() -> None:
    c1 = Category("1", CategoryType.EXPENSE)
    c2 = Category("2", CategoryType.EXPENSE, c1)
    c3 = Category("3", CategoryType.EXPENSE, c2)
    c4 = Category("3", CategoryType.EXPENSE, c3)
    assert not c1.is_ancestor_of(c1)
    assert c1.is_ancestor_of(c2)
    assert c1.is_ancestor_of(c3)
    assert c1.is_ancestor_of(c4)
    assert not c2.is_ancestor_of(c1)
    assert not c2.is_ancestor_of(c2)
    assert c2.is_ancestor_of(c3)
    assert c2.is_ancestor_of(c4)
    assert not c3.is_ancestor_of(c1)
    assert not c3.is_ancestor_of(c2)
    assert not c3.is_ancestor_of(c3)
    assert c3.is_ancestor_of(c4)
    assert not c4.is_ancestor_of(c1)
    assert not c4.is_ancestor_of(c2)
    assert not c4.is_ancestor_of(c3)
    assert not c4.is_ancestor_of(c4)


def test_is_descendant_of() -> None:
    c1 = Category("1", CategoryType.EXPENSE)
    c2 = Category("2", CategoryType.EXPENSE, c1)
    c3 = Category("3", CategoryType.EXPENSE, c2)
    c4 = Category("3", CategoryType.EXPENSE, c3)
    assert not c1.is_descendant_of(c1)
    assert not c1.is_descendant_of(c2)
    assert not c1.is_descendant_of(c3)
    assert not c1.is_descendant_of(c4)
    assert c2.is_descendant_of(c1)
    assert not c2.is_descendant_of(c2)
    assert not c2.is_descendant_of(c3)
    assert not c2.is_descendant_of(c4)
    assert c3.is_descendant_of(c1)
    assert c3.is_descendant_of(c2)
    assert not c3.is_descendant_of(c3)
    assert not c3.is_descendant_of(c4)
    assert c4.is_descendant_of(c1)
    assert c4.is_descendant_of(c2)
    assert c4.is_descendant_of(c3)
    assert not c4.is_descendant_of(c4)


def test_ancestors() -> None:
    c1 = Category("1", CategoryType.EXPENSE)
    c2 = Category("2", CategoryType.EXPENSE, c1)
    c3 = Category("3", CategoryType.EXPENSE, c2)
    c4 = Category("3", CategoryType.EXPENSE, c3)
    assert c1.ancestors == frozenset()
    assert c2.ancestors == frozenset([c1])
    assert c3.ancestors == frozenset([c1, c2])
    assert c4.ancestors == frozenset([c1, c2, c3])


def test_descendants() -> None:
    c1 = Category("1", CategoryType.EXPENSE)
    c2 = Category("2", CategoryType.EXPENSE, c1)
    c3 = Category("3", CategoryType.EXPENSE, c2)
    c4 = Category("3", CategoryType.EXPENSE, c3)
    assert c1.descendants == frozenset([c2, c3, c4])
    assert c2.descendants == frozenset([c3, c4])
    assert c3.descendants == frozenset([c4])
    assert c4.descendants == frozenset()


def test_descendants_multiple_children() -> None:
    c1 = Category("1", CategoryType.EXPENSE)
    c2a = Category("2a", CategoryType.EXPENSE, c1)
    c2b = Category("2b", CategoryType.EXPENSE, c1)
    c3aa = Category("3aa", CategoryType.EXPENSE, c2a)
    c3ab = Category("3ab", CategoryType.EXPENSE, c2a)
    c3ba = Category("3ba", CategoryType.EXPENSE, c2b)
    c3bb = Category("3bb", CategoryType.EXPENSE, c2b)
    assert c1.descendants == frozenset([c2a, c2b, c3aa, c3ab, c3ba, c3bb])
    assert c2a.descendants == frozenset([c3aa, c3ab])
    assert c2b.descendants == frozenset([c3ba, c3bb])
