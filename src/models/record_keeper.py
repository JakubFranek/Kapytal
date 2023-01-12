# TODO: this file belongs somewhere else...

from collections.abc import Collection
from datetime import date, datetime
from decimal import Decimal
from typing import overload

from src.models.base_classes.account import Account
from src.models.base_classes.transaction import Transaction
from src.models.custom_exceptions import AlreadyExistsError
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
    RefundTransaction,
)
from src.models.model_objects.currency import (
    CashAmount,
    Currency,
    CurrencyError,
    ExchangeRate,
)
from src.models.model_objects.security_objects import (
    Security,
    SecurityAccount,
    SecurityTransaction,
    SecurityTransactionType,
    SecurityTransfer,
    SecurityType,
)


class DoesNotExistError(ValueError):
    """Raised when a search for an object finds nothing."""


class RecordKeeper:
    def __init__(self) -> None:
        self._accounts: list[Account] = []
        self._account_groups: list[AccountGroup] = []
        self._currencies: list[Currency] = []
        self._exchange_rates: list[ExchangeRate] = []
        self._securities: list[Security] = []
        self._payees: list[Attribute] = []
        self._categories: list[Category] = []
        self._tags: list[Attribute] = []
        self._transactions: list[Transaction] = []

    @property
    def accounts(self) -> tuple[Account, ...]:
        return tuple(self._accounts)

    @property
    def account_groups(self) -> tuple[AccountGroup, ...]:
        return tuple(self._account_groups)

    @property
    def currencies(self) -> tuple[Currency, ...]:
        return tuple(self._currencies)

    @property
    def exchange_rates(self) -> tuple[ExchangeRate, ...]:
        return tuple(self._exchange_rates)

    @property
    def securities(self) -> tuple[Security, ...]:
        return tuple(self._securities)

    @property
    def payees(self) -> tuple[Attribute, ...]:
        return tuple(self._payees)

    @property
    def categories(self) -> tuple[Category, ...]:
        return tuple(self._categories)

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
        self._currencies.append(currency)

    def add_exchange_rate(
        self, primary_currency_code: str, secondary_currency_code: str
    ) -> None:
        exchange_rate_str = f"{primary_currency_code}/{secondary_currency_code}"
        for exchange_rate in self._exchange_rates:
            if str(exchange_rate) == exchange_rate_str:
                raise AlreadyExistsError(
                    f"ExchangeRate '{exchange_rate_str} already exists.'"
                )
        primary_currency = self.get_currency(primary_currency_code)
        secondary_currency = self.get_currency(secondary_currency_code)
        exchange_rate = ExchangeRate(primary_currency, secondary_currency)
        self._exchange_rates.append(exchange_rate)

    def add_security(
        self,
        name: str,
        symbol: str,
        type_: SecurityType,
        currency_code: str,
        unit: Decimal | int | str,
    ) -> None:
        symbol_upper = symbol.upper()
        if any(security.symbol == symbol_upper for security in self._securities):
            raise AlreadyExistsError(
                f"A Security with symbol '{symbol_upper}' already exists."
            )
        currency = self.get_currency(currency_code)
        security = Security(name, symbol, type_, currency, unit)
        self._securities.append(security)

    def add_category(
        self, name: str, parent_path: str | None, type_: CategoryType | None = None
    ) -> Category:
        if parent_path is not None:
            for category in self._categories:
                if category.path == parent_path:
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
                    "If parameter 'parent_path' is None, "
                    "'type_' must be a CategoryType."
                )
            category_type = type_

        path = parent.path + "/" + name if parent else name
        for category in self._categories:
            if category.path == path:
                raise AlreadyExistsError(f"A Category at path '{path}' already exists.")

        category = Category(name, category_type, parent)
        self._categories.append(category)
        return category

    def add_account_group(self, name: str, parent_path: str | None) -> None:
        parent = self.get_account_parent(parent_path)
        if parent is not None:
            target_path = parent.path + "/" + name
        else:
            target_path = name
            parent = None
        if any(acc_group.path == target_path for acc_group in self._account_groups):
            raise AlreadyExistsError(
                f"An AccountGroup with path '{target_path}' already exists."
            )
        account_group = AccountGroup(name, parent)
        self._account_groups.append(account_group)

    def add_cash_account(
        self,
        name: str,
        currency_code: str,
        initial_balance_value: Decimal | int | str,
        initial_datetime: datetime,
        parent_path: str | None,
    ) -> None:
        self._check_account_exists(name, parent_path)
        currency = self.get_currency(currency_code)
        parent = self.get_account_parent(parent_path)
        initial_balance = CashAmount(initial_balance_value, currency)
        account = CashAccount(name, currency, initial_balance, initial_datetime, parent)
        self._accounts.append(account)

    def add_security_account(self, name: str, parent_path: str | None) -> None:
        self._check_account_exists(name, parent_path)
        parent = self.get_account_parent(parent_path)
        account = SecurityAccount(name, parent)
        self._accounts.append(account)

    def add_cash_transaction(  # noqa: CFQ002, TMN001
        self,
        description: str,
        datetime_: datetime,
        transaction_type: CashTransactionType,
        account_path: str,
        category_path_amount_pairs: Collection[tuple[str, Decimal]],
        payee_name: str,
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

    def add_cash_transfer(  # noqa: CFQ002, TMN001
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

    def add_refund(
        self,
        description: str,
        datetime_: datetime,
        refunded_transaction_uuid_string: int,
        refunded_account_path: str,
        category_path_amount_pairs: Collection[tuple[str, Decimal]],
        tag_name_amount_pairs: Collection[tuple[str, Decimal]],
        payee_name: str,
    ) -> None:
        for transaction in self._transactions:
            if str(transaction.uuid) == refunded_transaction_uuid_string:
                refunded_transaction = transaction
                break
        else:
            raise ValueError(
                f"Transaction with UUID '{refunded_transaction_uuid_string}' not found."
            )

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

    def add_security_transaction(
        self,
        description: str,
        datetime_: datetime,
        type_: SecurityTransactionType,
        security_symbol: str,
        shares: Decimal | int | str,
        price_per_share: Decimal | int | str,
        fees: Decimal | int | str,
        security_account_path: str,
        cash_account_path: str,
    ) -> None:
        security = self.get_security(security_symbol)
        cash_account = self.get_account(cash_account_path, CashAccount)
        security_account = self.get_account(security_account_path, SecurityAccount)

        transaction = SecurityTransaction(
            description=description,
            datetime_=datetime_,
            type_=type_,
            security=security,
            shares=shares,
            price_per_share=CashAmount(price_per_share, cash_account.currency),
            fees=CashAmount(fees, cash_account.currency),
            security_account=security_account,
            cash_account=cash_account,
        )
        self._transactions.append(transaction)

    def add_security_transfer(
        self,
        description: str,
        datetime_: datetime,
        security_symbol: str,
        shares: Decimal | int | str,
        account_sender_path: str,
        account_recipient_path: str,
    ) -> None:
        security = self.get_security(security_symbol)
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

    def edit_cash_transactions(
        self,
        transaction_uuid_strings: Collection[str],
        description: str | None = None,
        datetime_: datetime | None = None,
        transaction_type: CashTransactionType | None = None,
        account_path: str | None = None,
        category_path_amount_pairs: Collection[tuple[str, Decimal | None]]
        | None = None,
        payee_name: str | None = None,
        tag_name_amount_pairs: Collection[tuple[str, Decimal]] | None = None,
    ) -> None:
        transactions: list[CashTransaction] = [
            transaction
            for transaction in self._transactions
            if str(transaction.uuid) in transaction_uuid_strings
        ]

        if not all(
            isinstance(transaction, CashTransaction) for transaction in transactions
        ):
            raise TypeError("All edited transactions must be CashTransactions.")

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

    def edit_cash_transfers(
        self,
        transaction_uuid_strings: Collection[str],
        description: str | None = None,
        datetime_: datetime | None = None,
        sender_path: str | None = None,
        recipient_path: str | None = None,
        amount_sent: Decimal | None = None,
        amount_received: Decimal | None = None,
    ) -> None:
        transfers: list[CashTransfer] = [
            transaction
            for transaction in self._transactions
            if str(transaction.uuid) in transaction_uuid_strings
        ]

        if not all(isinstance(transaction, CashTransfer) for transaction in transfers):
            raise TypeError("All edited transactions must be CashTransfers.")

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
            amount_sent = CashAmount(amount_sent, transfers[0].sender.currency)

        if amount_received is not None:
            if not all(
                transfer.recipient.currency == transfers[0].recipient.currency
                for transfer in transfers
            ):
                raise CurrencyError(
                    "If amount_received is to be changed, all recipient CashAccounts "
                    "must be of same Currency."
                )
            amount_received = CashAmount(
                amount_received, transfers[0].recipient.currency
            )

        for transfer in transfers:
            transfer.validate_attributes(
                description=description,
                datetime_=datetime_,
                amount_sent=amount_sent,
                amount_received=amount_received,
                sender=sender,
                recipient=recipient,
            )

        for transfer in transfers:
            transfer.set_attributes(
                description=description,
                datetime_=datetime_,
                amount_sent=amount_sent,
                amount_received=amount_received,
                sender=sender,
                recipient=recipient,
            )

    def edit_refunds(
        self,
        transaction_uuid_strings: Collection[str],
        description: str | None = None,
        datetime_: datetime | None = None,
        transaction_type: CashTransactionType | None = None,
        account_path: str | None = None,
        category_path_amount_pairs: Collection[tuple[str, Decimal | None]]
        | None = None,
        payee_name: str | None = None,
        tag_name_amount_pairs: Collection[tuple[str, Decimal]] | None = None,
    ) -> None:
        refunds: list[RefundTransaction] = [
            transaction
            for transaction in self._transactions
            if str(transaction.uuid) in transaction_uuid_strings
        ]

        if not all(isinstance(refund, RefundTransaction) for refund in refunds):
            raise TypeError("All edited transactions must be RefundTransactions.")

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

    def edit_security_transactions(
        self,
        transaction_uuid_strings: Collection[str],
        description: str | None = None,
        datetime_: datetime | None = None,
        transaction_type: SecurityTransactionType | None = None,
        security_symbol: str | None = None,
        cash_account_path: str | None = None,
        security_account_path: str | None = None,
        price_per_share: Decimal | int | str | None = None,
        fees: Decimal | int | str | None = None,
        shares: Decimal | int | str | None = None,
    ) -> None:
        transactions: list[SecurityTransaction] = [
            transaction
            for transaction in self._transactions
            if str(transaction.uuid) in transaction_uuid_strings
        ]

        if not all(
            isinstance(transaction, SecurityTransaction) for transaction in transactions
        ):
            raise TypeError("All edited transactions must be SecurityTransactions.")

        if not all(
            transaction.currency == transactions[0].currency
            for transaction in transactions
        ):
            raise CurrencyError(
                "Edited SecurityTransactions must have the same currency."
            )

        if security_symbol is not None:
            security = self.get_security(security_symbol)
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
            price_per_share = CashAmount(price_per_share, currency)

        if fees is not None:
            fees = CashAmount(fees, currency)

        if shares is not None:
            shares = Decimal(shares)

        for transaction in transactions:
            transaction.validate_attributes(
                description=description,
                datetime_=datetime_,
                type_=transaction_type,
                security=security,
                price_per_share=price_per_share,
                fees=fees,
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
                price_per_share=price_per_share,
                fees=fees,
                shares=shares,
                cash_account=cash_account,
                security_account=security_account,
            )

    def edit_security_transfers(
        self,
        transaction_uuid_strings: Collection[str],
        description: str | None = None,
        datetime_: datetime | None = None,
        security_symbol: str | None = None,
        shares: Decimal | None = None,
        sender_path: str | None = None,
        recipient_path: str | None = None,
    ) -> None:
        transactions: list[SecurityTransfer] = [
            transaction
            for transaction in self._transactions
            if str(transaction.uuid) in transaction_uuid_strings
        ]

        if not all(
            isinstance(transaction, SecurityTransfer) for transaction in transactions
        ):
            raise TypeError("All edited transactions must be SecurityTransfers.")

        if security_symbol is not None:
            security = self.get_security(security_symbol)
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
        self,
        current_path: str,
        new_name: str | None = None,
        new_parent_path: str | None = None,
    ) -> None:
        for category in self._categories:
            if category.path == current_path:
                current_path = category
                break
        else:
            raise DoesNotExistError(
                f"Category at path='{current_path}' does not exist."
            )
        if new_name is not None:
            category.name = new_name
        if new_parent_path is not None:
            new_parent = self.get_category(new_parent_path, category.type_)
            category.parent = new_parent

    def edit_attribute(
        self, current_name: str, new_name: str, type_: AttributeType
    ) -> None:
        if type_ == AttributeType.PAYEE:
            attributes = self._payees
        else:
            attributes = self._tags

        for attribute in attributes:
            if attribute.name == current_name:
                edited_attribute = attribute
                break
        else:
            raise DoesNotExistError(
                f"Attribute of name='{current_name}' and type_={type_} does not exist."
            )
        edited_attribute.name = new_name

    def edit_security(
        self,
        current_symbol: str,
        new_symbol: str | None = None,
        new_name: str | None = None,
    ) -> None:
        for security in self._securities:
            if security.symbol == current_symbol.upper():
                edited_security = security
                break
        else:
            raise DoesNotExistError(
                f"Security with symbol='{current_symbol}' does not exist."
            )
        if new_symbol is not None:
            edited_security.symbol = new_symbol
        if new_name is not None:
            edited_security.name = new_name

    def edit_account(
        self,
        current_path: str,
        new_name: str | None = None,
        new_parent_path: str | None = None,
    ) -> None:
        for account in self._accounts:
            if account.path == current_path:
                edited_account = account
                break
        else:
            raise DoesNotExistError(f"Account at path='{current_path}' does not exist.")
        if new_name is not None:
            edited_account.name = new_name
        if new_parent_path is not None:
            parent = self.get_account_parent(new_parent_path)
            edited_account.parent = parent

    def edit_account_group(
        self,
        current_path: str,
        new_name: str | None = None,
        new_parent_path: str | None = None,
    ) -> None:
        for account_group in self._account_groups:
            if account_group.path == current_path:
                edited_account_group = account_group
                break
        else:
            raise DoesNotExistError(
                f"AccountGroup at path='{current_path}' does not exist."
            )
        if new_name is not None:
            edited_account_group.name = new_name
        if new_parent_path is not None:
            parent = self.get_account_parent(new_parent_path)
            edited_account_group.parent = parent

    def add_tags_to_transactions(
        self, transaction_uuid_strings: Collection[str], tag_names: Collection[str]
    ) -> None:
        self._perform_tag_operation(
            transaction_uuid_strings=transaction_uuid_strings,
            tag_names=tag_names,
            method_name="add_tags",
        )

    def remove_tags_from_transactions(
        self, transaction_uuid_strings: Collection[str], tag_names: Collection[str]
    ) -> None:
        self._perform_tag_operation(
            transaction_uuid_strings=transaction_uuid_strings,
            tag_names=tag_names,
            method_name="remove_tags",
        )

    def _perform_tag_operation(
        self,
        transaction_uuid_strings: Collection[str],
        tag_names: Collection[str],
        method_name: str,
    ) -> None:
        transactions: list[Transaction] = [
            transaction
            for transaction in self._transactions
            if str(transaction.uuid) in transaction_uuid_strings
        ]

        tags = [
            self.get_attribute(tag_name, AttributeType.TAG) for tag_name in tag_names
        ]
        for transaction in transactions:
            method = getattr(transaction, method_name)
            method(tags)

    def get_account_parent(self, path: str | None) -> AccountGroup | None:
        if path:
            for account_group in self._account_groups:
                if account_group.path == path:
                    return account_group
            raise DoesNotExistError(
                f"An AccountGroup with path='{path}' does not exist."
            )
        return None

    @overload
    def get_account(
        self, path: str, type_: type[CashAccount]  # noqa: U100
    ) -> CashAccount:
        ...

    @overload
    def get_account(
        self, path: str, type_: type[SecurityAccount]  # noqa: U100
    ) -> SecurityAccount:
        ...

    def get_account(
        self,
        path: str,
        type_: type[Account],
    ) -> Account:
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
        raise DoesNotExistError(f"An Account with path='{path}' does not exist.")

    def get_security(self, symbol: str) -> Security:
        if not isinstance(symbol, str):
            raise TypeError("Parameter 'symbol' must be a string.")
        symbol_upper = symbol.upper()
        for security in self._securities:
            if security.symbol == symbol_upper:
                return security
        raise DoesNotExistError(
            f"A Security with symbol='{symbol_upper}' does not exist."
        )

    def get_currency(self, code: str) -> Currency:
        if not isinstance(code, str):
            raise TypeError("Parameter 'code' must be a string.")
        code_upper = code.upper()
        for currency in self._currencies:
            if currency.code == code_upper:
                return currency
        raise DoesNotExistError(f"A Currency with code='{code_upper}' does not exist.")

    # TODO: having to specify type for existing Category is annoying
    def get_category(self, path: str, type_: CategoryType) -> Category:
        """Returns Category at path. If it does not exist, creates a new Category
        at path with given type_."""

        if not isinstance(path, str):
            raise TypeError("Parameter 'path' must be a string.")
        if not isinstance(type_, CategoryType):
            raise TypeError("Parameter 'type_' must be a CategoryType.")
        for category in self._categories:
            if category.path == path:
                return category
        # Category with path not found... searching for parents.
        current_path = path
        parent = None
        if "/" in current_path:
            while "/" in current_path:
                current_path = current_path[: current_path.rfind("/")]
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
        self, exchange_rate_str: str, rate: Decimal, date_: date
    ) -> None:
        if not isinstance(exchange_rate_str, str):
            raise TypeError("Parameter 'exchange_rate_str' must be a string.")

        for exchange_rate in self._exchange_rates:
            if str(exchange_rate) == exchange_rate_str:
                exchange_rate.set_rate(date_, rate)
                return
        raise DoesNotExistError(f"Exchange rate '{exchange_rate_str} not found.'")

    def _check_account_exists(self, name: str, parent_path: str | None) -> None:
        if not isinstance(name, str):
            raise TypeError("Parameter 'name' must be a string.")
        if not isinstance(parent_path, str) and parent_path is not None:
            raise TypeError("Parameter 'parent_path' must be a string or a None.")
        target_path = parent_path + "/" + name if parent_path is not None else name
        if any(account.path == target_path for account in self._accounts):
            raise AlreadyExistsError(
                f"An Account with path={target_path} already exists."
            )

    def _create_category_amount_pairs(
        self,
        category_path_amount_pairs: Collection[tuple[str, Decimal | None]],
        category_type: CategoryType,
        currency: Currency,
    ) -> list[tuple[Category, CashAmount | None]]:
        category_amount_pairs: list[tuple[Category, CashAmount | None]] = []
        for category_path, amount in category_path_amount_pairs:
            valid_amount = CashAmount(amount, currency) if amount is not None else None
            category = self.get_category(category_path, category_type)  # noqa: NEW100
            pair = (category, valid_amount)
            category_amount_pairs.append(pair)
        return category_amount_pairs

    def _create_tag_amount_pairs(
        self,
        tag_name_amount_pairs: Collection[tuple[str, Decimal]],
        currency: Currency,
    ) -> list[tuple[Category, CashAmount]]:
        tag_amount_pairs: list[tuple[Attribute, CashAmount]] = []
        for tag_name, amount in tag_name_amount_pairs:
            tag_amount_pairs.append(
                (
                    self.get_attribute(tag_name, AttributeType.TAG),
                    CashAmount(amount, currency),
                )
            )
        return tag_amount_pairs
