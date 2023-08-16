import logging
from collections.abc import Collection

from PyQt6.QtWidgets import QWidget
from src.models.model_objects.attributes import Attribute, Category
from src.views.utilities.message_box_functions import ask_yes_no_question


def check_for_nonexistent_attributes(
    attribute_names: Collection[str],
    attributes: Collection[Attribute],
    parent: QWidget,
) -> bool:
    """Check whether any name in 'attribute_names' is not found in 'attributes'.
    If so, ask the user if they want to create new Attributes or not.
    Returns True if the dialog can proceed, False if abort."""

    nonexistent_names: list[str] = []
    existing_names = {attribute.name for attribute in attributes}
    nonexistent_names = [
        attribute_name
        for attribute_name in attribute_names
        if attribute_name and attribute_name not in existing_names
    ]

    if nonexistent_names:
        attr_type = next(iter(attributes)).type_.name.title()
        logging.info(
            f"Nonexistent {attr_type} names entered, asking user whether to proceed"
        )

        existing_names_dict: dict[str, set[str]] = {}
        for name in existing_names:
            name_lower = name.lower()
            if name_lower in existing_names_dict:
                existing_names_dict[name_lower].add(name)
            else:
                existing_names_dict[name_lower] = {name}

        _nonexistent_names = nonexistent_names.copy()
        for name in nonexistent_names:
            name_lower = name.lower()
            if name_lower in existing_names_dict:
                bullet_points = [
                    f"- <b><i>{name}</b></i><br/>"
                    for name in existing_names_dict[name_lower]
                ]
                bullet_points = "".join(bullet_points)
                if not ask_yes_no_question(
                    parent,
                    (
                        f"<html>{attr_type} <b><i>{name}</i></b> does not exist, but "
                        f"the following {attr_type}s are similar:<br/>"
                        f"{bullet_points}<br/>"
                        f"Create {attr_type} <b><i>{name}</i></b> anyway?<br/></html>"
                    ),
                    title=f"Create new {attr_type}?",
                ):
                    logging.debug(f"User cancelled {attr_type} creation for '{name}'")
                    return False
                _nonexistent_names.remove(name)

        if not _nonexistent_names:
            return True

        nonexistent_attributes_str = ", ".join(_nonexistent_names)
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
    categories: Collection[Category],
    parent: QWidget,
) -> bool:
    """Check whether any Category in category_names does not exist. If so,
    ask the user if they want to create new Categories or not.
    Returns True if the dialog can proceed, False if abort."""

    nonexistent_paths = []
    for category in category_names:
        if category and category not in (category_.path for category_ in categories):
            nonexistent_paths.append(category)
    if nonexistent_paths:
        nonexistent_categories_str = ", ".join(nonexistent_paths)
        logging.info(
            "Nonexistent Category paths entered, asking user whether to proceed"
        )
        return ask_yes_no_question(
            parent,
            (
                "<html>The following Categories do not "
                "exist:<br/>"
                f"<b><i>{nonexistent_categories_str}</i></b><br/><br/>"
                f"Create new Categories and proceed?</html>"
            ),
            title="Create new Categories?",
        )
    return True
