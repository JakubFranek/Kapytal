import uuid
from typing import TYPE_CHECKING

from src.models.base_classes.account import Account
from src.models.custom_exceptions import NotFoundError
from src.models.model_objects.attributes import Attribute, Category

if TYPE_CHECKING:
    from src.models.model_objects.security_objects import Security


def find_account_by_uuid(uuid: uuid.UUID, accounts: list[Account]) -> Account:
    for account in accounts:
        if account.uuid == uuid:
            return account
    raise NotFoundError(f"Account uuid='{uuid}' not found.")


def find_security_by_uuid(uuid: uuid.UUID, securities: list["Security"]) -> "Security":
    for security in securities:
        if security.uuid == uuid:
            return security
    raise NotFoundError(f"Security uuid='{uuid}' not found.")


def find_attribute_by_name(name: str, attributes: list[Attribute]) -> Attribute:
    for attribute in attributes:
        if attribute.name == name:
            return attribute
    raise NotFoundError(f"Attribute name='{name}' not found.")


def find_category_by_path(path: str, categories: list[Category]) -> Category:
    for attribute in categories:
        if attribute.path == path:
            return attribute
    raise NotFoundError(f"Category path='{path}' not found.")
