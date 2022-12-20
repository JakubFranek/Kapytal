from collections.abc import Collection
from datetime import datetime
from decimal import Decimal

from src.models.base_classes.account import Account
from src.models.base_classes.transaction import Transaction
from src.models.model_objects.account_group import AccountGroup
from src.models.model_objects.attributes import (
    Attribute,
    AttributeType,
    Category,
    CategoryType,
)
from src.models.model_objects.cash_objects import (
    CashAccount,
    CashTransaction,
    CashTransactionType,
    CashTransfer,
)
from src.models.model_objects.currency import Currency


class AlreadyExistsError(ValueError):
    """Raised when an attempt is made to create an object which already exists."""


class DoesNotExistError(ValueError):
    """Raised when a search for an object finds nothing."""


class RecordKeeper:
    def __init__(self) -> None:
        self._accounts: list[Account] = []
        self._account_groups: list[AccountGroup] = []
        self._currencies: list[Currency] = []
        self._payees: list[Attribute] = []
        self._categories: list[Category] = []
        self._tags: list[Attribute] = []
        self._transactions: list[Transaction] = []

    @property
    def accounts(self) -> tuple[CashAccount]:
        return tuple(self._accounts)

    @property
    def account_groups(self) -> tuple[AccountGroup]:
        return tuple(self._account_groups)

    @property
    def currencies(self) -> tuple[Currency]:
        return tuple(self._currencies)

    @property
    def payees(self) -> tuple[Attribute]:
        return tuple(self._payees)

    @property
    def categories(self) -> tuple[Category]:
        return tuple(self._categories)

    @property
    def tags(self) -> tuple[Attribute]:
        return tuple(self._tags)

    @property
    def transactions(self) -> tuple[Transaction]:
        return tuple(self._transactions)

    def add_currency(self, currency_code: str) -> None:
        code_upper = currency_code.upper()
        if any(currency.code == code_upper for currency in self._currencies):
            raise AlreadyExistsError(
                f"A Currency with code {code_upper} already exists."
            )
        currency = Currency(code_upper)
        self._currencies.append(currency)

    def add_category(
        self, name: str, parent_path: str | None, type_: CategoryType | None = None
    ) -> Category:
        if parent_path:
            for category in self._categories:
                if str(category) == parent_path:
                    parent = category
                    category_type = category.type_
                    break
            else:
                raise DoesNotExistError(
                    f"The parent Category (path '{parent_path}') does not exist."
                )
        else:
            parent = None
            if not isinstance(type_, CategoryType):
                raise TypeError(
                    "If argument 'parent_path' is not provided, 'type_' must be"
                    " a CategoryType."
                )
            category_type = type_

        path = str(parent) + "/" + name if parent else name
        for category in self._categories:
            if str(category) == path:
                raise AlreadyExistsError(f"A Category at path '{path}' already exists.")

        category = Category(name, category_type, parent)
        self._categories.append(category)
        return category

    def add_account_group(self, name: str, parent_name: str | None) -> None:
        if any(acc_group.name == name for acc_group in self._account_groups):
            raise AlreadyExistsError(f"An AccountGroup named {name} already exists.")
        parent = self.get_account_parent(parent_name)
        account_group = AccountGroup(name)
        account_group.parent = parent
        self._account_groups.append(account_group)

    def add_cash_account(
        self,
        name: str,
        currency_code: str,
        initial_balance: Decimal,
        initial_datetime: datetime,
        parent_name: str | None,
    ) -> None:
        if any(name == account.name for account in self._accounts):
            raise AlreadyExistsError(f"An Account named {name} already exists.")
        currency = self.get_currency(currency_code)
        parent = self.get_account_parent(parent_name)
        account = CashAccount(name, currency, initial_balance, initial_datetime)
        account.parent = parent
        self._accounts.append(account)

    def add_cash_transaction(  # noqa: CFQ002, TMN001
        self,
        description: str,
        datetime_: datetime,
        transaction_type: str,
        account_name: str,
        category_path_amount_pairs: Collection[tuple[str, Decimal]],
        payee_name: str,
        tag_names: Collection[str],
    ) -> None:
        account = self.get_account(account_name)
        type_ = RecordKeeper.get_cash_transaction_type(transaction_type)
        payee = self.get_attribute(payee_name, AttributeType.PAYEE)

        tags: list[Attribute] = []
        for tag_name in tag_names:
            tags.append(self.get_attribute(tag_name, AttributeType.TAG))

        category_amount_pairs: list[tuple[Category, Decimal]] = []
        category_type = (
            CategoryType.INCOME
            if type_ == CashTransactionType.INCOME
            else CategoryType.EXPENSE
        )
        for category_path, amount in category_path_amount_pairs:
            pair = (self.get_category(category_path, category_type), amount)
            category_amount_pairs.append(pair)

        transaction = CashTransaction(
            description,
            datetime_,
            type_,
            account,
            category_amount_pairs,
            payee,
            tags,
        )
        self._transactions.append(transaction)

    def add_cash_transfer(  # noqa: CFQ002, TMN001
        self,
        description: str,
        datetime_: datetime,
        account_sender_name: CashAccount,
        account_recipient_name: CashAccount,
        amount_sent: Decimal,
        amount_received: Decimal,
    ) -> None:
        account_sender = self.get_account(account_sender_name)
        account_recipient = self.get_account(account_recipient_name)

        transfer = CashTransfer(
            description,
            datetime_,
            account_sender,
            account_recipient,
            amount_sent,
            amount_received,
        )
        self._transactions.append(transfer)

    def get_account_parent(self, parent_name: str | None) -> AccountGroup | None:
        if parent_name:
            for account_group in self._account_groups:
                if account_group.name == parent_name:
                    return account_group
            raise DoesNotExistError(
                f"An AccountGroup named {parent_name} does not exist."
            )
        return None

    def get_account(self, name: str) -> Account:
        for account in self._accounts:
            if account.name == name:
                return account
        raise DoesNotExistError(f"An Account named {name} does not exist.")

    def get_currency(self, code: str) -> Currency:
        code_upper = code.upper()
        for currency in self._currencies:
            if currency.code == code_upper:
                return currency
        raise DoesNotExistError(f"A Currency with code {code_upper} does not exist.")

    def get_category(self, path: str, type_: CategoryType) -> Category:
        for category in self._categories:
            if str(category) == path:
                return category
        # Category with full_name not found... searching for parents.
        current_path = path
        parent = None
        while "/" in current_path:
            current_path = current_path[: current_path.rfind("/")]
            for category in self._categories:
                if str(category) == current_path:
                    parent = category
                    break
            if parent:
                break
        else:
            if parent is None:
                # No parent Category found - we need to make one.
                root_name = path.split("/")[0]
                parent = Category(root_name, type_)
                self._categories.append(parent)
        remainder_name = path.removeprefix(str(parent))[1:]
        while "/" in remainder_name:
            # As long as multiple categories remain...
            new_name = remainder_name.split("/")[0]
            new_category = Category(new_name, type_, parent)
            self._categories.append(new_category)
            parent = new_category
            remainder_name = remainder_name.removeprefix(new_name)[1:]
        # Reached the end - just one more category left
        final_category = Category(remainder_name, type_, parent)
        self._categories.append(final_category)
        return final_category

    def get_attribute(self, name: str, type_: AttributeType) -> Attribute:
        attributes = self._payees if type_ == AttributeType.PAYEE else self._tags
        for attribute in attributes:
            if attribute.name == name:
                return attribute
        # Attribute not found! Making a new one.
        attribute = Attribute(name, type_)
        attributes.append(attribute)
        return attribute

    @staticmethod
    def get_cash_transaction_type(type_: str) -> CashTransactionType:
        if not isinstance(type_, str):
            raise TypeError(
                "Argument 'type_' must be a string (either 'income' or 'expense')."
            )
        type_lower = type_.lower()
        if type_lower == "income":
            return CashTransactionType.INCOME
        if type_lower == "expense":
            return CashTransactionType.EXPENSE
        raise ValueError(
            "A CashTransactionType can be only 'income' or 'expense',"
            f" not {type_lower}."
        )
