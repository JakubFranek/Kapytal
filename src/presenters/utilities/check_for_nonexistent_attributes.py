import logging
from collections.abc import Collection

from PyQt6.QtWidgets import QWidget
from src.models.model_objects.attributes import Attribute, Category, CategoryType
from src.models.model_objects.cash_objects import CashTransactionType
from src.views.utilities.message_box_functions import ask_yes_no_question


def check_for_nonexistent_attributes(
    attribute_names: Collection[str],
    attributes: Collection[Attribute],
    parent: QWidget,
    attr_type: str,
) -> bool:
    """Check whether any name in 'attribute_names' is not found in 'attributes'.
    If so, ask the user if they want to create new Attributes or not.
    Returns True if the dialog can proceed, False if abort."""

    nonexistent_attributes = []
    for attribute_name in attribute_names:
        if attribute_name and attribute_name not in (
            attribute.name for attribute in attributes
        ):
            nonexistent_attributes.append(attribute_name)
    if nonexistent_attributes:
        nonexistent_attributes_str = ", ".join(nonexistent_attributes)
        logging.info(
            f"Nonexistent {attr_type} names entered, asking user whether to proceed"
        )
        return ask_yes_no_question(
            parent,
            (
                f"<html>The following {attr_type}s do not exist:<br/>"
                f"<b><i>{nonexistent_attributes_str}</i></b><br/><br/>"
                f"Create new {attr_type}s and proceed?</html>"
            ),
            title=f"Create new {attr_type}s?",
        )
    return True


def check_for_nonexistent_categories(
    category_names: Collection[str],
    type_: CashTransactionType,
    categories: Collection[Category],
    parent: QWidget,
) -> bool:
    """Check whether any Category in category_names does not exist. If so,
    ask the user if they want to create new Categories or not.
    Returns True if the dialog can proceed, False if abort."""

    nonexistent_categories = []
    for category in category_names:
        if category and category not in (category_.path for category_ in categories):
            nonexistent_categories.append(category)
    if nonexistent_categories:
        nonexistent_categories_str = ", ".join(nonexistent_categories)
        category_type = (
            CategoryType.INCOME
            if type_ == CashTransactionType.INCOME
            else CategoryType.EXPENSE
        )
        logging.info(
            "Nonexistent Category paths entered, asking user whether to proceed"
        )
        return ask_yes_no_question(
            parent,
            (
                "<html>The following Categories do not "
                "exist:<br/>"
                f"<b><i>{nonexistent_categories_str}</i></b><br/><br/>"
                f"Create new {category_type.name.title()} Categories "
                "and proceed?</html>"
            ),
            title="Create new Categories?",
        )
    return True
