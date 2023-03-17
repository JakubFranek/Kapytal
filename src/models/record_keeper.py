# FIXME: this file belongs somewhere else...

from collections.abc import Collection
from datetime import date, datetime
from decimal import Decimal
from typing import Any, TypeVar

from src.models.base_classes.account import Account
from src.models.base_classes.transaction import Transaction
from src.models.custom_exceptions import (
    AlreadyExistsError,
    InvalidOperationError,
    NotFoundError,
)
from src.models.mixins.copyable_mixin import CopyableMixin
from src.models.mixins.json_serializable_mixin import JSONSerializableMixin
from src.models.model_objects.account_group import AccountGroup
from src.models.model_objects.attributes import (
    Attribute,
    AttributeType,
    Category,
    CategoryType,
)
from src.models.model_objects.cash_objects import (
    CashAccount,
    CashRelatedTransaction,
    CashTransaction,
    CashTransactionType,
    CashTransfer,
    RefundTransaction,
)
from src.models.model_objects.currency_objects import (
    CashAmount,
    Currency,
    CurrencyError,
    ExchangeRate,
)
from src.models.model_objects.security_objects import (
    Security,
    SecurityAccount,
    SecurityRelatedTransaction,
    SecurityTransaction,
    SecurityTransactionType,
    SecurityTransfer,
)

# IDEA: split RecordKeeper into smaller object keepers
# such as CategoryKeeper, AccountItem keeper etc.


class RecordKeeper(CopyableMixin, JSONSerializableMixin):
    def __init__(self) -> None:
        self._accounts: list[Account] = []
        self._account_groups: list[AccountGroup] = []
        self._root_account_items: list[AccountGroup | Account] = []
        self._currencies: list[Currency] = []
        self._exchange_rates: list[ExchangeRate] = []
        self._securities: list[Security] = []
        self._payees: list[Attribute] = []
        self._categories: list[Category] = []
        self._root_income_categories: list[Category] = []
        self._root_expense_categories: list[Category] = []
        self._root_income_and_expense_categories: list[Category] = []
        self._tags: list[Attribute] = []
        self._transactions: list[Transaction] = []
        self._base_currency: Currency | None = None

    @property
    def accounts(self) -> tuple[Account, ...]:
        return tuple(RecordKeeper._flatten_accounts(self._root_account_items))

    @property
    def account_groups(self) -> tuple[AccountGroup, ...]:
        return tuple(self._account_groups)

    @property
    def account_items(self) -> tuple[Account | AccountGroup, ...]:
        return tuple(RecordKeeper._flatten_account_items(self._root_account_items))

    @property
    def root_account_items(self) -> tuple[Account | AccountGroup, ...]:
        return tuple(self._root_account_items)

    @property
    def currencies(self) -> tuple[Currency, ...]:
        return tuple(self._currencies)

    @property
    def base_currency(self) -> Currency | None:
        return self._base_currency

    @property
    def exchange_rates(self) -> tuple[ExchangeRate, ...]:
        return tuple(self._exchange_rates)

    @property
    def securities(self) -> tuple[Security, ...]:
        return tuple(self._securities)

    @property
    def payees(self) -> tuple[Attribute, ...]:
        self._payees.sort(key=lambda payee: payee.name)
        return tuple(self._payees)

    @property
    def categories(self) -> tuple[Category, ...]:
        return tuple(self._categories)

    @property
    def root_income_categories(self) -> tuple[Category, ...]:
        return tuple(self._root_income_categories)

    @property
    def root_expense_categories(self) -> tuple[Category, ...]:
        return tuple(self._root_expense_categories)

    @property
    def root_income_and_expense_categories(self) -> tuple[Category, ...]:
        return tuple(self._root_income_and_expense_categories)

    @property
    def income_categories(self) -> tuple[Category, ...]:
        return tuple(
            category
            for category in self._categories
            if category.type_ == CategoryType.INCOME
        )

    @property
    def expense_categories(self) -> tuple[Category, ...]:
        return tuple(
            category
            for category in self._categories
            if category.type_ == CategoryType.EXPENSE
        )

    @property
    def income_and_expense_categories(self) -> tuple[Category, ...]:
        return tuple(
            category
            for category in self._categories
            if category.type_ == CategoryType.INCOME_AND_EXPENSE
        )

    @property
    def tags(self) -> tuple[Attribute, ...]:
        return tuple(self._tags)

    @property
    def transactions(self) -> tuple[Transaction, ...]:
        return tuple(self._transactions)

    def __repr__(self) -> str:
        return "RecordKeeper"

    def add_currency(self, currency_code: str, places: int) -> None:
        code_upper = currency_code.upper()
        if any(currency.code == code_upper for currency in self._currencies):
            raise AlreadyExistsError(
                f"A Currency with code '{code_upper}' already exists."
            )
        currency = Currency(code_upper, places)
        if len(self._currencies) == 0:
            self._base_currency = currency
        self._currencies.append(currency)

    def add_payee(self, name: str) -> None:
        if any(payee.name == name for payee in self._payees):
            raise AlreadyExistsError(f"A Payee {name=} already exists.")
        payee = Attribute(name, AttributeType.PAYEE)
        self._payees.append(payee)

    def add_tag(self, name: str) -> None:
        if any(tag.name == name for tag in self._tags):
            raise AlreadyExistsError(f"A Tag {name=} already exists.")
        tag = Attribute(name, AttributeType.TAG)
        self._tags.append(tag)

    def add_exchange_rate(
        self, primary_currency_code: str, secondary_currency_code: str
    ) -> None:
        exchange_rate_str = f"{primary_currency_code}/{secondary_currency_code}"
        exchange_rate_str_reverse = f"{secondary_currency_code}/{primary_currency_code}"
        for exchange_rate in self._exchange_rates:
            if (
                str(exchange_rate) == exchange_rate_str
                or str(exchange_rate) == exchange_rate_str_reverse
            ):
                raise AlreadyExistsError(
                    f"An ExchangeRate between {primary_currency_code} "
                    f"and {secondary_currency_code} already exists."
                )
        primary_currency = self.get_currency(primary_currency_code)
        secondary_currency = self.get_currency(secondary_currency_code)
        exchange_rate = ExchangeRate(primary_currency, secondary_currency)
        self._exchange_rates.append(exchange_rate)

    def add_security(  # noqa: PLR0913
        self,
        name: str,
        symbol: str,
        type_: str,
        currency_code: str,
        unit: Decimal | int | str,
    ) -> None:
        if any(security.name == name for security in self._securities):
            raise AlreadyExistsError(f"A Security with name='{name}' already exists.")
        symbol_upper = symbol.upper()
        if len(symbol_upper) != 0 and any(
            security.symbol == symbol_upper for security in self._securities
        ):
            raise AlreadyExistsError(
                f"A Security with symbol='{symbol_upper}' already exists."
            )

        currency = self.get_currency(currency_code)
        security = Security(name, symbol, type_, currency, unit)
        self._securities.append(security)

    def add_category(
        self, path: str, type_: CategoryType | None = None, index: int | None = None
    ) -> None:
        for category in self._categories:
            if category.path == path:
                raise AlreadyExistsError(f"A Category at path '{path}' already exists.")

        if "/" in path:
            parent_path, _, name = path.rpartition("/")
            parent = self.get_category(parent_path)
            category_type = parent.type_
        else:
            if not isinstance(type_, CategoryType):
                raise TypeError(
                    "If Category to-be-added has no parent, "
                    "parameter 'type_' must be a CategoryType."
                )
            name = path
            parent = None
            category_type = type_

        category = Category(name, category_type, parent)
        self._set_category_index(category, index)
        self._categories.append(category)

    def add_account_group(self, path: str, index: int | None = None) -> None:
        parent_path, _, name = path.rpartition("/")
        parent = self.get_account_parent_or_none(parent_path)
        if any(acc_group.path == path for acc_group in self._account_groups):
            raise AlreadyExistsError(
                f"An AccountGroup with path '{path}' already exists."
            )
        account_group = AccountGroup(name, parent)
        self._set_account_item_index(account_group, index)
        self._account_groups.append(account_group)

    def add_cash_account(
        self,
        path: str,
        currency_code: str,
        initial_balance_value: Decimal | int | str,
        index: int | None = None,
    ) -> None:
        parent_path, _, name = path.rpartition("/")
        self._check_account_exists(path)
        currency = self.get_currency(currency_code)
        parent = self.get_account_parent_or_none(parent_path)
        initial_balance = CashAmount(initial_balance_value, currency)
        account = CashAccount(name, currency, initial_balance, parent)
        self._set_account_item_index(account, index)
        self._accounts.append(account)

    def add_security_account(self, path: str, index: int | None = None) -> None:
        parent_path, _, name = path.rpartition("/")
        self._check_account_exists(path)
        parent = self.get_account_parent_or_none(parent_path)
        account = SecurityAccount(name, parent)
        self._set_account_item_index(account, index)
        self._accounts.append(account)

    def add_cash_transaction(  # noqa: PLR0913
        self,
        description: str,
        datetime_: datetime,
        transaction_type: CashTransactionType,
        account_path: str,
        payee_name: str,
        category_path_amount_pairs: Collection[tuple[str, Decimal]],
        tag_name_amount_pairs: Collection[tuple[str, Decimal]],
    ) -> None:
        account = self.get_account(account_path, CashAccount)
        payee = self.get_attribute(payee_name, AttributeType.PAYEE)

        tag_amount_pairs = self._create_tag_amount_pairs(
            tag_name_amount_pairs, account.currency
        )
        category_type = (
            CategoryType.INCOME
            if transaction_type == CashTransactionType.INCOME
            else CategoryType.EXPENSE
        )
        category_amount_pairs = self._create_category_amount_pairs(
            category_path_amount_pairs, category_type, account.currency
        )

        transaction = CashTransaction(
            description=description,
            datetime_=datetime_,
            type_=transaction_type,
            account=account,
            payee=payee,
            category_amount_pairs=category_amount_pairs,
            tag_amount_pairs=tag_amount_pairs,
        )
        self._transactions.append(transaction)

    def add_cash_transfer(  # noqa: PLR0913
        self,
        description: str,
        datetime_: datetime,
        account_sender_path: str,
        account_recipient_path: str,
        amount_sent: Decimal | int | str,
        amount_received: Decimal | int | str,
    ) -> None:
        account_sender = self.get_account(account_sender_path, CashAccount)
        account_recipient = self.get_account(account_recipient_path, CashAccount)

        transfer = CashTransfer(
            description=description,
            datetime_=datetime_,
            sender=account_sender,
            recipient=account_recipient,
            amount_sent=CashAmount(amount_sent, account_sender.currency),
            amount_received=CashAmount(amount_received, account_recipient.currency),
        )
        self._transactions.append(transfer)

    def add_refund(  # noqa: PLR0913
        self,
        description: str,
        datetime_: datetime,
        refunded_transaction_uuid: str,
        refunded_account_path: str,
        payee_name: str,
        category_path_amount_pairs: Collection[tuple[str, Decimal]],
        tag_name_amount_pairs: Collection[tuple[str, Decimal]],
    ) -> None:
        refunded_transactions = self._get_transactions(
            [refunded_transaction_uuid], CashTransaction
        )
        if len(refunded_transactions) == 0:
            raise ValueError(
                f"Transaction with UUID '{refunded_transaction_uuid}' not found."
            )
        refunded_transaction = refunded_transactions[0]

        refunded_account = self.get_account(refunded_account_path, CashAccount)

        category_type = CategoryType.EXPENSE
        category_amount_pairs = self._create_category_amount_pairs(
            category_path_amount_pairs, category_type, refunded_account.currency
        )

        tag_amount_pairs = self._create_tag_amount_pairs(
            tag_name_amount_pairs, refunded_account.currency
        )

        payee = self.get_attribute(payee_name, AttributeType.PAYEE)

        refund = RefundTransaction(
            description=description,
            datetime_=datetime_,
            account=refunded_account,
            refunded_transaction=refunded_transaction,
            category_amount_pairs=category_amount_pairs,
            tag_amount_pairs=tag_amount_pairs,
            payee=payee,
        )
        self._transactions.append(refund)

    def add_security_transaction(  # noqa: PLR0913
        self,
        description: str,
        datetime_: datetime,
        type_: SecurityTransactionType,
        security_name: str,
        shares: Decimal | int | str,
        price_per_share: Decimal | int | str,
        security_account_path: str,
        cash_account_path: str,
    ) -> None:
        security = self.get_security_by_name(security_name)
        cash_account = self.get_account(cash_account_path, CashAccount)
        security_account = self.get_account(security_account_path, SecurityAccount)

        transaction = SecurityTransaction(
            description=description,
            datetime_=datetime_,
            type_=type_,
            security=security,
            shares=shares,
            price_per_share=CashAmount(price_per_share, cash_account.currency),
            security_account=security_account,
            cash_account=cash_account,
        )
        self._transactions.append(transaction)

    def add_security_transfer(  # noqa: PLR0913
        self,
        description: str,
        datetime_: datetime,
        security_name: str,
        shares: Decimal | int | str,
        account_sender_path: str,
        account_recipient_path: str,
    ) -> None:
        security = self.get_security_by_name(security_name)
        account_sender = self.get_account(account_sender_path, SecurityAccount)
        account_recipient = self.get_account(account_recipient_path, SecurityAccount)
        transaction = SecurityTransfer(
            description=description,
            datetime_=datetime_,
            security=security,
            shares=shares,
            sender=account_sender,
            recipient=account_recipient,
        )
        self._transactions.append(transaction)

    def edit_cash_transactions(  # noqa: PLR0913
        self,
        transaction_uuids: Collection[str],
        description: str | None = None,
        datetime_: datetime | None = None,
        transaction_type: CashTransactionType | None = None,
        account_path: str | None = None,
        category_path_amount_pairs: Collection[tuple[str, Decimal | None]]
        | None = None,
        payee_name: str | None = None,
        tag_name_amount_pairs: Collection[tuple[str, Decimal]] | None = None,
    ) -> None:
        transactions = self._get_transactions(transaction_uuids, CashTransaction)

        if not all(
            transaction.currency == transactions[0].currency
            for transaction in transactions
        ):
            raise CurrencyError("Edited CashTransactions must have the same currency.")

        if account_path is not None:
            account = self.get_account(account_path, CashAccount)
        else:
            account = None

        if payee_name is not None:
            payee = self.get_attribute(payee_name, AttributeType.PAYEE)
        else:
            payee = None

        currency = account.currency if account is not None else transactions[0].currency

        if category_path_amount_pairs is not None:
            category_type = (
                CategoryType.INCOME
                if transaction_type == CashTransactionType.INCOME
                else CategoryType.EXPENSE
            )
            category_amount_pairs = self._create_category_amount_pairs(
                category_path_amount_pairs, category_type, currency
            )
        else:
            category_amount_pairs = None

        if tag_name_amount_pairs is not None:
            tag_amount_pairs = self._create_tag_amount_pairs(
                tag_name_amount_pairs, currency
            )
        else:
            tag_amount_pairs = None

        for transaction in transactions:
            transaction.validate_attributes(
                description=description,
                datetime_=datetime_,
                type_=transaction_type,
                account=account,
                category_amount_pairs=category_amount_pairs,
                tag_amount_pairs=tag_amount_pairs,
                payee=payee,
            )

        for transaction in transactions:
            transaction.set_attributes(
                description=description,
                datetime_=datetime_,
                type_=transaction_type,
                account=account,
                category_amount_pairs=category_amount_pairs,
                tag_amount_pairs=tag_amount_pairs,
                payee=payee,
            )

    def edit_cash_transfers(  # noqa: PLR0913
        self,
        transaction_uuids: Collection[str],
        description: str | None = None,
        datetime_: datetime | None = None,
        sender_path: str | None = None,
        recipient_path: str | None = None,
        amount_sent: Decimal | None = None,
        amount_received: Decimal | None = None,
    ) -> None:
        transfers = self._get_transactions(transaction_uuids, CashTransfer)

        if sender_path is not None:
            sender = self.get_account(sender_path, CashAccount)
        else:
            sender = None

        if recipient_path is not None:
            recipient = self.get_account(recipient_path, CashAccount)
        else:
            recipient = None

        if amount_sent is not None:
            if not all(
                transfer.sender.currency == transfers[0].sender.currency
                for transfer in transfers
            ):
                raise CurrencyError(
                    "If amount_sent is to be changed, all sender CashAccounts "
                    "must be of same Currency."
                )
            _amount_sent = CashAmount(amount_sent, transfers[0].sender.currency)
        else:
            _amount_sent = None

        if amount_received is not None:
            if not all(
                transfer.recipient.currency == transfers[0].recipient.currency
                for transfer in transfers
            ):
                raise CurrencyError(
                    "If amount_received is to be changed, all recipient CashAccounts "
                    "must be of same Currency."
                )
            _amount_received = CashAmount(
                amount_received, transfers[0].recipient.currency
            )
        else:
            _amount_received = None

        for transfer in transfers:
            transfer.validate_attributes(
                description=description,
                datetime_=datetime_,
                amount_sent=_amount_sent,
                amount_received=_amount_received,
                sender=sender,
                recipient=recipient,
            )

        for transfer in transfers:
            transfer.set_attributes(
                description=description,
                datetime_=datetime_,
                amount_sent=_amount_sent,
                amount_received=_amount_received,
                sender=sender,
                recipient=recipient,
            )

    def edit_refunds(  # noqa: PLR0913
        self,
        transaction_uuids: Collection[str],
        description: str | None = None,
        datetime_: datetime | None = None,
        transaction_type: CashTransactionType | None = None,
        account_path: str | None = None,
        category_path_amount_pairs: Collection[tuple[str, Decimal | None]]
        | None = None,
        payee_name: str | None = None,
        tag_name_amount_pairs: Collection[tuple[str, Decimal]] | None = None,
    ) -> None:
        refunds = self._get_transactions(transaction_uuids, RefundTransaction)

        if not all(refund.currency == refunds[0].currency for refund in refunds):
            raise CurrencyError(
                "Edited RefundTransactions must have the same currency."
            )

        if account_path is not None:
            account = self.get_account(account_path, CashAccount)
        else:
            account = None

        if payee_name is not None:
            payee = self.get_attribute(payee_name, AttributeType.PAYEE)
        else:
            payee = None

        currency = account.currency if account is not None else refunds[0].currency

        if category_path_amount_pairs is not None:
            category_type = (
                CategoryType.INCOME
                if transaction_type == CashTransactionType.INCOME
                else CategoryType.EXPENSE
            )
            category_amount_pairs = self._create_category_amount_pairs(
                category_path_amount_pairs, category_type, currency
            )
        else:
            category_amount_pairs = None

        if tag_name_amount_pairs is not None:
            tag_amount_pairs = self._create_tag_amount_pairs(
                tag_name_amount_pairs, currency
            )
        else:
            tag_amount_pairs = None

        for refund in refunds:
            refund.validate_attributes(
                description=description,
                datetime_=datetime_,
                account=account,
                category_amount_pairs=category_amount_pairs,
                tag_amount_pairs=tag_amount_pairs,
                payee=payee,
            )

        for refund in refunds:
            refund.set_attributes(
                description=description,
                datetime_=datetime_,
                account=account,
                category_amount_pairs=category_amount_pairs,
                tag_amount_pairs=tag_amount_pairs,
                payee=payee,
            )

    def edit_security_transactions(  # noqa: PLR0913
        self,
        transaction_uuids: Collection[str],
        description: str | None = None,
        datetime_: datetime | None = None,
        transaction_type: SecurityTransactionType | None = None,
        security_name: str | None = None,
        cash_account_path: str | None = None,
        security_account_path: str | None = None,
        price_per_share: Decimal | int | str | None = None,
        shares: Decimal | int | str | None = None,
    ) -> None:
        transactions = self._get_transactions(transaction_uuids, SecurityTransaction)

        if not all(
            transaction.currency == transactions[0].currency
            for transaction in transactions
        ):
            raise CurrencyError(
                "Edited SecurityTransactions must have the same currency."
            )

        if security_name is not None:
            security = self.get_security_by_name(security_name)
        else:
            security = None

        if cash_account_path is not None:
            cash_account = self.get_account(cash_account_path, CashAccount)
        else:
            cash_account = None

        if security_account_path is not None:
            security_account = self.get_account(security_account_path, SecurityAccount)
        else:
            security_account = None

        currency = (
            cash_account.currency
            if cash_account is not None
            else transactions[0].currency
        )

        if price_per_share is not None:
            _price_per_share = CashAmount(price_per_share, currency)
        else:
            _price_per_share = None

        if shares is not None:
            shares = Decimal(shares)

        for transaction in transactions:
            transaction.validate_attributes(
                description=description,
                datetime_=datetime_,
                type_=transaction_type,
                security=security,
                price_per_share=_price_per_share,
                shares=shares,
                cash_account=cash_account,
                security_account=security_account,
            )

        for transaction in transactions:
            transaction.set_attributes(
                description=description,
                datetime_=datetime_,
                type_=transaction_type,
                security=security,
                price_per_share=_price_per_share,
                shares=shares,
                cash_account=cash_account,
                security_account=security_account,
            )

    def edit_security_transfers(  # noqa: PLR0913
        self,
        transaction_uuids: Collection[str],
        description: str | None = None,
        datetime_: datetime | None = None,
        security_name: str | None = None,
        shares: Decimal | None = None,
        sender_path: str | None = None,
        recipient_path: str | None = None,
    ) -> None:
        transactions = self._get_transactions(transaction_uuids, SecurityTransfer)

        if security_name is not None:
            security = self.get_security_by_name(security_name)
        else:
            security = None

        if sender_path is not None:
            sender = self.get_account(sender_path, SecurityAccount)
        else:
            sender = None

        if recipient_path is not None:
            recipient = self.get_account(recipient_path, SecurityAccount)
        else:
            recipient = None

        for transaction in transactions:
            transaction.validate_attributes(
                description=description,
                datetime_=datetime_,
                sender=sender,
                recipient=recipient,
                shares=shares,
                security=security,
            )

        for transaction in transactions:
            transaction.set_attributes(
                description=description,
                datetime_=datetime_,
                sender=sender,
                recipient=recipient,
                shares=shares,
                security=security,
            )

    def edit_category(
        self, current_path: str, new_path: str, index: int | None = None
    ) -> None:
        if current_path != new_path and any(
            category.path == new_path for category in self._categories
        ):
            raise AlreadyExistsError(
                f"A Category with path='{new_path}' already exists."
            )

        edited_category = self.get_category(current_path)

        if "/" in new_path:
            parent_path, _, name = new_path.rpartition("/")
            new_parent = self.get_category(parent_path)
        else:
            name = new_path
            new_parent = None

        if new_parent == edited_category:
            raise InvalidOperationError("A Category cannot be its own parent.")

        edited_category.name = name
        self._edit_category_parent(
            category=edited_category, new_parent=new_parent, index=index
        )

    def edit_attribute(
        self, current_name: str, new_name: str, type_: AttributeType
    ) -> None:
        attributes = self._payees if type_ == AttributeType.PAYEE else self._tags

        for attribute in attributes:
            if attribute.name == current_name:
                edited_attribute = attribute
                break
        else:
            raise NotFoundError(
                f"Attribute of name='{current_name}' and type_={type_} does not exist."
            )
        edited_attribute.name = new_name

    def edit_security(
        self,
        uuid: str,
        name: str | None = None,
        symbol: str | None = None,
        type_: str | None = None,
    ) -> None:
        edited_security = self.get_security_by_uuid(uuid)
        if name is not None:
            edited_security.name = name
        if symbol is not None:
            edited_security.symbol = symbol
        if type_ is not None:
            edited_security.type_ = type_

    def edit_cash_account(
        self,
        current_path: str,
        new_path: str,
        initial_balance: Decimal | int | str,
        index: int | None = None,
    ) -> None:
        parent_path, _, name = new_path.rpartition("/")
        if current_path != new_path:
            self._check_account_exists(new_path)
        edited_account = self.get_account(current_path, CashAccount)
        new_parent = self.get_account_parent_or_none(parent_path)
        edited_account.name = name
        edited_account.initial_balance = CashAmount(
            initial_balance, edited_account.currency
        )
        self._edit_account_item_parent(
            item=edited_account, new_parent=new_parent, index=index
        )

    def edit_security_account(
        self, current_path: str, new_path: str, index: int | None = None
    ) -> None:
        parent_path, _, name = new_path.rpartition("/")
        if current_path != new_path:
            self._check_account_exists(new_path)
        edited_account = self.get_account(current_path, SecurityAccount)
        new_parent = self.get_account_parent_or_none(parent_path)
        edited_account.name = name
        self._edit_account_item_parent(
            item=edited_account, new_parent=new_parent, index=index
        )

    # REFACTOR: this method should be simplified somehow (similar to edit_account)
    def edit_account_group(
        self, current_path: str, new_path: str, index: int | None = None
    ) -> None:
        if current_path != new_path and any(
            account_group.path == new_path for account_group in self._account_groups
        ):
            raise AlreadyExistsError(
                f"An Account Group with path='{new_path}' already exists."
            )
        edited_account_group = self.get_account_parent(current_path)
        parent_path, _, name = new_path.rpartition("/")
        new_parent = self.get_account_parent_or_none(parent_path)
        if new_parent == edited_account_group:
            raise InvalidOperationError("An AccountGroup cannot be its own parent.")
        edited_account_group.name = name
        self._edit_account_item_parent(
            item=edited_account_group, new_parent=new_parent, index=index
        )

    def add_tags_to_transactions(
        self, transaction_uuids: Collection[str], tag_names: Collection[str]
    ) -> None:
        self._perform_tag_operation(
            transaction_uuids=transaction_uuids,
            tag_names=tag_names,
            method_name="add_tags",
        )

    def remove_tags_from_transactions(
        self, transaction_uuids: Collection[str], tag_names: Collection[str]
    ) -> None:
        self._perform_tag_operation(
            transaction_uuids=transaction_uuids,
            tag_names=tag_names,
            method_name="remove_tags",
        )

    def _perform_tag_operation(
        self,
        transaction_uuids: Collection[str],
        tag_names: Collection[str],
        method_name: str,
    ) -> None:
        transactions = self._get_transactions(transaction_uuids, Transaction)

        tags = [
            self.get_attribute(tag_name, AttributeType.TAG) for tag_name in tag_names
        ]
        for transaction in transactions:
            method = getattr(transaction, method_name)
            method(tags)

    def remove_account(self, path: str) -> None:
        account = self.get_account(path, Account)
        if len(account.transactions) != 0:
            raise InvalidOperationError(
                "Cannot delete an Account which is still used in some transactions."
            )
        if account.parent is None:
            self._root_account_items.remove(account)
        else:
            account.parent = None
        self._accounts.remove(account)
        del account

    def remove_account_group(self, account_group_path: str) -> None:
        account_group = self.get_account_parent(account_group_path)
        if len(account_group.children) != 0:
            raise InvalidOperationError(
                "Cannot delete an AccountGroup which has children."
            )
        if account_group.parent is None:
            self._root_account_items.remove(account_group)
        else:
            account_group.parent = None
        self._account_groups.remove(account_group)
        del account_group

    def remove_transactions(self, transaction_uuids: Collection[str]) -> None:
        transactions = self._get_transactions(transaction_uuids, Transaction)
        for transaction in transactions:
            transaction.prepare_for_deletion()
            self._transactions.remove(transaction)

    def remove_security(self, uuid: str) -> None:
        security = self.get_security_by_uuid(uuid)
        if any(
            transaction.security == security
            for transaction in self._transactions
            if isinstance(transaction, SecurityRelatedTransaction)
        ):
            raise InvalidOperationError(
                "Cannot delete a Security referenced in any transaction."
            )
        self._securities.remove(security)
        del security

    def remove_currency(self, code: str) -> None:
        currency = self.get_currency(code)
        if any(
            currency in exchange_rate.currencies
            for exchange_rate in self._exchange_rates
        ):
            raise InvalidOperationError(
                "Cannot delete a Currency referenced in any ExchangeRate."
            )
        if any(
            currency in transaction.currencies
            for transaction in self._transactions
            if isinstance(transaction, CashRelatedTransaction)
        ):
            raise InvalidOperationError(
                "Cannot delete a Currency referenced in any CashRelatedTransaction."
            )
        if any(currency == security.currency for security in self._securities):
            raise InvalidOperationError(
                "Cannot delete a Currency referenced in any Security."
            )
        self._currencies.remove(currency)
        if currency == self._base_currency:
            self._base_currency = (
                self._currencies[0] if len(self._currencies) > 0 else None
            )
        del currency

    def remove_exchange_rate(self, exchange_rate_code: str) -> None:
        for exchange_rate in self._exchange_rates:
            if str(exchange_rate) == exchange_rate_code:
                removed_exchange_rate = exchange_rate
                break
        else:
            raise NotFoundError(f"ExchangeRate '{exchange_rate_code}' does not exist.")

        removed_exchange_rate.prepare_for_deletion()
        self._exchange_rates.remove(removed_exchange_rate)
        del removed_exchange_rate

    def remove_category(self, path: str) -> None:
        category = self.get_category(path)
        if len(category.children) != 0:
            raise InvalidOperationError("Cannot delete a Category with children.")
        if any(
            category in transaction.categories
            for transaction in self._transactions
            if isinstance(transaction, CashTransaction | RefundTransaction)
        ):
            raise InvalidOperationError(
                "Cannot delete a Category referenced in any CashTransaction "
                "or RefundTransaction."
            )
        self._categories.remove(category)
        if category.parent is None:
            list_ref = self._get_root_category_list(category)
            list_ref.remove(category)
        else:
            category.parent = None
        del category

    def remove_tag(self, name: str) -> None:
        tag = self.get_attribute(name, AttributeType.TAG)
        if any(tag in transaction.tags for transaction in self._transactions):
            raise InvalidOperationError(
                "Cannot delete a tag referenced in any Transaction."
            )
        self._tags.remove(tag)
        del tag

    def remove_payee(self, name: str) -> None:
        payee = self.get_attribute(name, AttributeType.PAYEE)
        if any(
            payee == transaction.payee
            for transaction in self._transactions
            if isinstance(transaction, CashTransaction | RefundTransaction)
        ):
            raise InvalidOperationError(
                "Cannot delete a payee referenced in any CashTransaction "
                "or RefundTransaction."
            )
        self._payees.remove(payee)
        del payee

    def set_base_currency(self, code: str) -> None:
        currency = self.get_currency(code)
        self._base_currency = currency

    def get_account_parent_or_none(self, path: str | None) -> AccountGroup | None:
        if not path:
            return None
        return self.get_account_parent(path)

    def get_account_parent(self, path: str) -> AccountGroup:
        for account_group in self._account_groups:
            if account_group.path == path:
                return account_group
        raise NotFoundError(f"An AccountGroup with path='{path}' does not exist.")

    AccountType = TypeVar("AccountType", CashAccount, SecurityAccount, Account)

    def get_account(
        self,
        path: str,
        type_: type[AccountType],
    ) -> AccountType:
        if not isinstance(path, str):
            raise TypeError("Parameter 'path' must be a string.")
        if not isinstance(type_, type(Account)):
            raise TypeError("Parameter type_ must be type(Account).")
        for account in self._accounts:
            if account.path == path:
                if not isinstance(account, type_):
                    raise TypeError(
                        f"Type of Account at path='{path}' is not {type_.__name__}."
                    )
                return account
        raise NotFoundError(f"An Account with path='{path}' does not exist.")

    def get_security_by_uuid(self, uuid: str) -> Security:
        if not isinstance(uuid, str):
            raise TypeError("Parameter 'uuid' must be a string.")
        for security in self._securities:
            if str(security.uuid) == uuid:
                return security
        raise NotFoundError(f"A Security with uuid='{uuid}' does not exist.")

    def get_security_by_name(self, name: str) -> Security:
        if not isinstance(name, str):
            raise TypeError("Parameter 'name' must be a string.")
        for security in self._securities:
            if security.name == name:
                return security
        raise NotFoundError(f"A Security with name='{name}' does not exist.")

    def get_currency(self, code: str) -> Currency:
        if not isinstance(code, str):
            raise TypeError("Parameter 'code' must be a string.")
        code_upper = code.upper()
        for currency in self._currencies:
            if currency.code == code_upper:
                return currency
        raise NotFoundError(f"A Currency with code='{code_upper}' does not exist.")

    def get_category(self, path: str) -> Category:
        for category in self._categories:
            if category.path == path:
                return category
        raise NotFoundError(f"Category at path='{path}' does not exist.")

    def get_or_make_category(self, path: str, type_: CategoryType) -> Category:
        """Returns Category at path. If it does not exist, creates a new Category
        at path with given type_."""

        if not isinstance(path, str):
            raise TypeError("Parameter 'path' must be a string.")
        if not isinstance(type_, CategoryType):
            raise TypeError("Parameter 'type_' must be a CategoryType.")
        for category in self._categories:
            if category.path == path:
                return category

        # Category with path not found... making it (along with any parents).
        return self._make_category_leaf(path, type_)

    def _make_category_leaf(self, path: str, type_: CategoryType) -> Category:
        current_path = path
        parent = None
        if "/" in current_path:
            while "/" in current_path:
                # Searching for any existing parent in path.
                current_path, _, _ = current_path.rpartition("/")
                for category in self._categories:
                    if category.path == current_path:
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
            remainder_name = path.removeprefix(parent.path)[1:]
            while "/" in remainder_name:
                # As long as multiple categories remain...
                new_name = remainder_name.split("/")[0]
                new_category = Category(new_name, type_, parent)
                self._categories.append(new_category)
                parent = new_category
                remainder_name = remainder_name.removeprefix(new_name)[1:]
        else:
            remainder_name = path
        # Reached the end - just one more category left
        final_category = Category(remainder_name, type_, parent)
        self._categories.append(final_category)
        return final_category

    def get_attribute(self, name: str, type_: AttributeType) -> Attribute:
        if not isinstance(name, str):
            raise TypeError("Parameter 'name' must be a string.")
        if not isinstance(type_, AttributeType):
            raise TypeError("Parameter 'type_' must be an AttributeType.")
        attributes = self._payees if type_ == AttributeType.PAYEE else self._tags
        for attribute in attributes:
            if attribute.name == name:
                return attribute
        # Attribute not found! Making a new one.
        attribute = Attribute(name, type_)
        attributes.append(attribute)
        return attribute

    def set_exchange_rate(
        self, exchange_rate_code: str, rate: Decimal, date_: date
    ) -> None:
        if not isinstance(exchange_rate_code, str):
            raise TypeError("Parameter 'exchange_rate_str' must be a string.")

        for exchange_rate in self._exchange_rates:
            if str(exchange_rate) == exchange_rate_code:
                exchange_rate.set_rate(date_, rate)
                return
        raise NotFoundError(f"Exchange rate '{exchange_rate_code} not found.'")

    def set_security_price(self, uuid: str, value: Decimal, date_: date) -> None:
        security = self.get_security_by_uuid(uuid)
        price = CashAmount(value, security.currency)
        security.set_price(date_, price)

    def serialize(self) -> dict[str, Any]:
        sorted_account_groups = sorted(self._account_groups, key=lambda x: str(x))
        sorted_categories = sorted(self._categories, key=lambda x: str(x))

        root_item_references = []
        for item in self._root_account_items:
            if isinstance(item, AccountGroup):
                root_item_references.append(
                    {"datatype": "AccountGroup", "path": item.path}
                )
            else:
                root_item_references.append(
                    {"datatype": "Account", "uuid": str(item.uuid)}
                )
        base_currency_code = (
            self._base_currency.code if self._base_currency is not None else None
        )

        root_income_category_refs = []
        for category in self._root_income_categories:
            root_income_category_refs.append(category.path)
        root_expense_category_refs = []
        for category in self._root_expense_categories:
            root_expense_category_refs.append(category.path)
        root_income_and_expense_category_refs = []
        for category in self._root_income_and_expense_categories:
            root_income_and_expense_category_refs.append(category.path)

        return {
            "datatype": "RecordKeeper",
            "currencies": self._currencies,
            "base_currency_code": base_currency_code,
            "exchange_rates": self._exchange_rates,
            "securities": self._securities,
            "account_groups": sorted_account_groups,
            "accounts": self._accounts,
            "root_account_items": root_item_references,
            "payees": self._payees,
            "tags": self._tags,
            "categories": sorted_categories,
            "root_income_categories": root_income_category_refs,
            "root_expense_categories": root_expense_category_refs,
            "root_income_and_expense_categories": root_income_and_expense_category_refs,
            "transactions": self._transactions,
        }

    # TODO: do I need to use private setters in deserializers?
    @staticmethod
    def deserialize(data: dict[str, Any]) -> "RecordKeeper":
        obj = RecordKeeper()
        obj._currencies = data["currencies"]  # noqa: SLF001
        base_currency_code = data["base_currency_code"]
        if base_currency_code is not None:
            obj.set_base_currency(base_currency_code)

        exchange_rates_dicts = data["exchange_rates"]
        obj._exchange_rates = RecordKeeper._deserialize_exchange_rates(  # noqa: SLF001
            exchange_rates_dicts, obj._currencies  # noqa: SLF001
        )

        security_dicts = data["securities"]
        obj._securities = RecordKeeper._deserialize_securities(  # noqa: SLF001
            security_dicts, obj._currencies  # noqa: SLF001
        )

        obj._account_groups = RecordKeeper._deserialize_account_groups(  # noqa: SLF001
            data["account_groups"]
        )

        account_dicts = data["accounts"]
        obj._accounts = RecordKeeper._deserialize_accounts(  # noqa: SLF001
            account_dicts, obj._account_groups, obj._currencies  # noqa: SLF001
        )

        obj._root_account_items = (  # noqa: SLF001
            RecordKeeper._deserialize_root_account_items(
                data["root_account_items"],
                obj._account_groups,  # noqa: SLF001
                obj._accounts,  # noqa: SLF001
            )
        )

        obj._payees = data["payees"]  # noqa: SLF001
        obj._tags = data["tags"]  # noqa: SLF001

        obj._categories = RecordKeeper._deserialize_categories(  # noqa: SLF001
            data["categories"]
        )
        obj._root_income_categories = (  # noqa: SLF001
            RecordKeeper._deserialize_root_categories(
                data["root_income_categories"], obj._categories  # noqa: SLF001
            )
        )
        obj._root_expense_categories = (  # noqa: SLF001
            RecordKeeper._deserialize_root_categories(
                data["root_expense_categories"], obj._categories  # noqa: SLF001
            )
        )
        obj._root_income_and_expense_categories = (  # noqa: SLF001
            RecordKeeper._deserialize_root_categories(
                data["root_income_and_expense_categories"],
                obj._categories,  # noqa: SLF001
            )
        )

        obj._transactions = RecordKeeper._deserialize_transactions(  # noqa: SLF001
            data["transactions"],
            obj._accounts,  # noqa: SLF001
            obj._payees,  # noqa: SLF001
            obj._tags,  # noqa: SLF001
            obj._categories,  # noqa: SLF001
            obj._currencies,  # noqa: SLF001
            obj._securities,  # noqa: SLF001
        )

        return obj

    @staticmethod
    def _deserialize_exchange_rates(
        exchange_rate_dicts: Collection[dict[str, Any]],
        currencies: Collection[Currency],
    ) -> list[ExchangeRate]:
        exchange_rates = []
        for exchange_rate_dict in exchange_rate_dicts:
            exchange_rate = ExchangeRate.deserialize(exchange_rate_dict, currencies)
            exchange_rates.append(exchange_rate)
        return exchange_rates

    @staticmethod
    def _deserialize_securities(
        security_dicts: Collection[dict[str, Any]],
        currencies: Collection[Currency],
    ) -> list[Security]:
        securities = []
        for security_dict in security_dicts:
            security = Security.deserialize(security_dict, currencies)
            securities.append(security)
        return securities

    @staticmethod
    def _deserialize_account_groups(
        account_group_dicts: Collection[dict[str, Any]]
    ) -> list[AccountGroup]:
        account_groups: list[AccountGroup] = []
        for account_group_dict in account_group_dicts:
            account_group = AccountGroup.deserialize(account_group_dict, account_groups)
            account_groups.append(account_group)
        return account_groups

    @staticmethod
    def _deserialize_accounts(
        account_dicts: Collection[dict[str, Any]],
        account_groups: Collection[AccountGroup],
        currencies: Collection[Currency],
    ) -> list[Account]:
        accounts: list[Account] = []
        for account_dict in account_dicts:
            account: Account
            if account_dict["datatype"] == "CashAccount":
                account = CashAccount.deserialize(
                    account_dict, account_groups, currencies
                )
            elif account_dict["datatype"] == "SecurityAccount":
                account = SecurityAccount.deserialize(account_dict, account_groups)
            else:
                raise ValueError("Unexpected 'datatype' value.")
            accounts.append(account)
        return accounts

    @staticmethod
    def _deserialize_root_account_items(
        root_item_dicts: Collection[dict[str, Any]],
        account_groups: Collection[AccountGroup],
        accounts: Collection[Account],
    ) -> list[AccountGroup | Account]:
        root_items: list[AccountGroup | Account] = []
        for item_dict in root_item_dicts:
            if item_dict["datatype"] == "AccountGroup":
                for account_group in account_groups:
                    if account_group.path == item_dict["path"]:
                        root_items.append(account_group)
                        break
            elif item_dict["datatype"] == "Account":
                for account in accounts:
                    if str(account.uuid) == item_dict["uuid"]:
                        root_items.append(account)
                        break
            else:
                raise ValueError("Unexpected 'datatype' value.")
        return root_items

    @staticmethod
    def _deserialize_categories(
        category_dicts: Collection[dict[str, Any]]
    ) -> list[Category]:
        categories: list[Category] = []
        for category_dict in category_dicts:
            category = Category.deserialize(category_dict, categories)
            categories.append(category)
        return categories

    @staticmethod
    def _deserialize_root_categories(
        root_category_paths: Collection[str],
        categories: Collection[Category],
    ) -> list[Category]:
        root_categories = []
        for path in root_category_paths:
            for category in categories:
                if category.path == path:
                    root_categories.append(category)
                    break
        return root_categories

    @staticmethod
    def _deserialize_transactions(  # noqa: PLR0913
        transaction_dicts: Collection[dict[str, Any]],
        accounts: Collection[Account],
        payees: Collection[Attribute],
        tags: Collection[Attribute],
        categories: Collection[Category],
        currencies: Collection[Currency],
        securities: Collection[Security],
    ) -> list[Transaction]:
        transactions: list[Transaction] = []
        for transaction_dict in transaction_dicts:
            transaction: Transaction
            if transaction_dict["datatype"] == "CashTransaction":
                transaction = CashTransaction.deserialize(
                    transaction_dict, accounts, payees, categories, tags, currencies
                )
            elif transaction_dict["datatype"] == "CashTransfer":
                transaction = CashTransfer.deserialize(
                    transaction_dict, accounts, currencies
                )
            elif transaction_dict["datatype"] == "RefundTransaction":
                transaction = RefundTransaction.deserialize(
                    transaction_dict,
                    accounts,
                    transactions,
                    payees,
                    categories,
                    tags,
                    currencies,
                )
            elif transaction_dict["datatype"] == "SecurityTransaction":
                transaction = SecurityTransaction.deserialize(
                    transaction_dict, accounts, currencies, securities
                )
            elif transaction_dict["datatype"] == "SecurityTransfer":
                transaction = SecurityTransfer.deserialize(
                    transaction_dict, accounts, securities
                )
            else:
                raise ValueError("Unexpected 'datatype' value.")
            transactions.append(transaction)
        return transactions

    def _check_account_exists(self, path: str) -> None:
        if any(account.path == path for account in self._accounts):
            raise AlreadyExistsError(f"An Account with path={path} already exists.")

    def _create_category_amount_pairs(
        self,
        category_path_amount_pairs: Collection[tuple[str, Decimal | None]],
        category_type: CategoryType,
        currency: Currency,
    ) -> list[tuple[Category, CashAmount | None]]:
        category_amount_pairs = []
        for category_path, amount in category_path_amount_pairs:
            valid_amount = CashAmount(amount, currency) if amount is not None else None
            category = self.get_or_make_category(category_path, category_type)
            pair = (category, valid_amount)
            category_amount_pairs.append(pair)
        return category_amount_pairs

    def _create_tag_amount_pairs(
        self,
        tag_name_amount_pairs: Collection[tuple[str, Decimal]],
        currency: Currency,
    ) -> list[tuple[Attribute, CashAmount]]:
        tag_amount_pairs: list[tuple[Attribute, CashAmount]] = []
        for tag_name, amount in tag_name_amount_pairs:
            tag_amount_pairs.append(
                (
                    self.get_attribute(tag_name, AttributeType.TAG),
                    CashAmount(amount, currency),
                )
            )
        return tag_amount_pairs

    TransactionType = TypeVar("TransactionType", bound=Transaction)

    def _get_transactions(
        self, uuid_strings: Collection[str], type_: type[TransactionType]
    ) -> list[TransactionType]:
        transactions: list[RecordKeeper.TransactionType] = []
        for transaction in self._transactions:
            uuid = str(transaction.uuid)
            if uuid in uuid_strings:
                if not isinstance(transaction, type_):
                    raise TypeError(
                        f"Type of Transaction at uuid='{uuid}' is not {type_.__name__}."
                    )
                transactions.append(transaction)
        return transactions

    def _set_account_item_index(
        self, item: Account | AccountGroup, index: int | None
    ) -> None:
        parent = item.parent
        if parent is None:
            if index is not None:
                self._root_account_items.insert(index, item)
            else:
                self._root_account_items.append(item)
        elif index is not None:
            parent.set_child_index(item, index)

    def _set_category_index(self, category: Category, index: int | None) -> None:
        parent = category.parent
        if parent is None:
            list_ref = self._get_root_category_list(category)

            if index is not None:
                list_ref.insert(index, category)
            else:
                list_ref.append(category)
        elif index is not None:
            parent.set_child_index(category, index)

    def _edit_account_item_parent(
        self,
        item: Account | AccountGroup,
        new_parent: AccountGroup | None,
        index: int | None,
    ) -> None:
        current_parent = item.parent
        if current_parent != new_parent:
            item.parent = new_parent
            if current_parent is None and new_parent is not None:
                self._root_account_items.remove(item)
            if current_parent is not None and new_parent is None:
                self._root_account_items.append(item)
        if index is None:
            return
        if new_parent is None:
            self._root_account_items.remove(item)
            self._root_account_items.insert(index, item)
        else:
            new_parent.set_child_index(item, index)

    def _edit_category_parent(
        self,
        category: Category,
        new_parent: Category | None,
        index: int | None,
    ) -> None:
        current_parent = category.parent
        if current_parent != new_parent:
            category.parent = new_parent
            list_ref = self._get_root_category_list(category)
            if current_parent is None and new_parent is not None:
                list_ref.remove(category)
            if current_parent is not None and new_parent is None:
                list_ref.append(category)
        if index is None:
            return
        if new_parent is None:
            list_ref = self._get_root_category_list(category)
            list_ref.remove(category)
            list_ref.insert(index, category)
        else:
            new_parent.set_child_index(category, index)

    def _get_root_category_list(self, category: Category) -> list[Category]:
        if category.type_ == CategoryType.INCOME:
            return self._root_income_categories
        if category.type_ == CategoryType.EXPENSE:
            return self._root_expense_categories
        return self._root_income_and_expense_categories

    @staticmethod
    def _flatten_accounts(
        account_items: Collection[Account | AccountGroup],
    ) -> list[Account]:
        resulting_list = []
        for account_item in account_items:
            if isinstance(account_item, Account):
                resulting_list.append(account_item)
            else:
                resulting_list = resulting_list + RecordKeeper._flatten_accounts(
                    account_item.children
                )
        return resulting_list

    @staticmethod
    def _flatten_account_items(
        account_items: Collection[Account | AccountGroup],
    ) -> list[Account | AccountGroup]:
        resulting_list: list[Account | AccountGroup] = []
        for account_item in account_items:
            resulting_list.append(account_item)
            if isinstance(account_item, AccountGroup):
                resulting_list = resulting_list + RecordKeeper._flatten_account_items(
                    account_item.children
                )
        return resulting_list
