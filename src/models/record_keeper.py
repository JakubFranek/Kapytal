import logging
from collections import defaultdict
from collections.abc import Callable, Collection
from datetime import datetime
from decimal import Decimal
from typing import Any, TypeVar
from uuid import UUID

from src.models.base_classes.account import Account
from src.models.base_classes.transaction import Transaction
from src.models.custom_exceptions import (
    AlreadyExistsError,
    InvalidOperationError,
    NotFoundError,
)
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


class RecordKeeper:
    __slots__ = (
        "_account_groups",
        "_accounts",
        "_base_currency",
        "_cash_accounts",
        "_cash_transactions",
        "_cash_transfers",
        "_categories",
        "_currencies",
        "_descriptions",
        "_exchange_rates",
        "_payees",
        "_refund_transactions",
        "_root_account_items",
        "_root_dual_purpose_categories",
        "_root_expense_categories",
        "_root_income_categories",
        "_securities",
        "_security_accounts",
        "_security_transactions",
        "_security_transfers",
        "_tags",
        "_transactions",
        "_transactions_uuid_dict",
    )

    def __init__(self) -> None:
        self._accounts: list[Account] = []
        self._cash_accounts: list[CashAccount] = []
        self._security_accounts: list[SecurityAccount] = []
        self._account_groups: list[AccountGroup] = []
        self._root_account_items: list[AccountGroup | Account] = []
        self._currencies: list[Currency] = []
        self._exchange_rates: list[ExchangeRate] = []
        self._securities: list[Security] = []
        self._payees: list[Attribute] = []
        self._categories: list[Category] = []
        self._root_income_categories: list[Category] = []
        self._root_expense_categories: list[Category] = []
        self._root_dual_purpose_categories: list[Category] = []
        self._tags: list[Attribute] = []
        self._transactions: list[Transaction] = []
        self._cash_transactions: list[CashTransaction] = []
        self._refund_transactions: list[RefundTransaction] = []
        self._cash_transfers: list[CashTransfer] = []
        self._security_transactions: list[SecurityTransaction] = []
        self._security_transfers: list[SecurityTransfer] = []
        self._transactions_uuid_dict: dict[UUID, Transaction] = {}
        self._descriptions: defaultdict[str, int] = defaultdict(int)
        self._base_currency: Currency | None = None

    @property
    def accounts(self) -> tuple[Account, ...]:
        return tuple(self._accounts)

    @property
    def cash_accounts(self) -> tuple[CashAccount, ...]:
        return tuple(self._cash_accounts)

    @property
    def security_accounts(self) -> tuple[SecurityAccount, ...]:
        return tuple(self._security_accounts)

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
    def root_dual_purpose_categories(self) -> tuple[Category, ...]:
        return tuple(self._root_dual_purpose_categories)

    @property
    def income_categories(self) -> tuple[Category, ...]:
        return tuple(RecordKeeper._flatten_categories(self._root_income_categories))

    @property
    def expense_categories(self) -> tuple[Category, ...]:
        return tuple(RecordKeeper._flatten_categories(self._root_expense_categories))

    @property
    def dual_purpose_categories(self) -> tuple[Category, ...]:
        return tuple(
            RecordKeeper._flatten_categories(self._root_dual_purpose_categories)
        )

    @property
    def tags(self) -> tuple[Attribute, ...]:
        return tuple(self._tags)

    @property
    def transactions(self) -> tuple[Transaction, ...]:
        return tuple(self._transactions)

    @property
    def transaction_uuid_dict(self) -> dict[UUID, Transaction]:
        return self._transactions_uuid_dict

    @property
    def cash_transactions(self) -> tuple[CashTransaction, ...]:
        return tuple(self._cash_transactions)

    @property
    def refund_transactions(self) -> tuple[RefundTransaction, ...]:
        return tuple(self._refund_transactions)

    @property
    def cash_transfers(self) -> tuple[CashTransfer, ...]:
        return tuple(self._cash_transfers)

    @property
    def security_transactions(self) -> tuple[SecurityTransaction, ...]:
        return tuple(self._security_transactions)

    @property
    def security_transfers(self) -> tuple[SecurityTransfer, ...]:
        return tuple(self._security_transfers)

    @property
    def descriptions(self) -> tuple[str, ...]:
        return tuple(self._descriptions)

    def __repr__(self) -> str:
        return "RecordKeeper"

    def add_currency(self, currency_code: str, decimals: int) -> None:
        code_upper = currency_code.upper()
        if any(currency.code == code_upper for currency in self._currencies):
            raise AlreadyExistsError(
                f"A Currency with code '{code_upper}' already exists."
            )
        currency = Currency(code_upper, decimals)
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
        exchange_rate.event_reset_currency_caches.append(self._reset_currency_caches)
        self._reset_currency_caches()

    def add_security(
        self,
        name: str,
        symbol: str,
        type_: str,
        currency_code: str,
        shares_decimals: int,
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
        security = Security(name, symbol, type_, currency, shares_decimals)
        self._securities.append(security)

    def add_category(
        self,
        path: str,
        type_: CategoryType | None = None,
        index: int | None = None,
    ) -> None:
        if any(category.path == path for category in self._categories):
            raise AlreadyExistsError(f"A Category at {path=} already exists.")

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
        parent = self.get_account_group_or_none(parent_path)
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
        parent = self.get_account_group_or_none(parent_path)
        initial_balance = CashAmount(initial_balance_value, currency)
        account = CashAccount(name, currency, initial_balance, parent)
        self._set_account_item_index(account, index)
        self._accounts.append(account)
        self._cash_accounts.append(account)
        self._cash_accounts.sort(key=lambda account: account.path.lower())

    def add_security_account(self, path: str, index: int | None = None) -> None:
        parent_path, _, name = path.rpartition("/")
        self._check_account_exists(path)
        parent = self.get_account_group_or_none(parent_path)
        account = SecurityAccount(name, parent)
        self._set_account_item_index(account, index)
        self._accounts.append(account)
        self._security_accounts.append(account)
        self._security_accounts.sort(key=lambda account: account.path.lower())

    def add_cash_transaction(
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
        self._cash_transactions.append(transaction)
        self._transactions_uuid_dict[transaction.uuid] = transaction
        self._add_description(transaction.description)

    def add_cash_transfer(
        self,
        description: str,
        datetime_: datetime,
        account_sender_path: str,
        account_recipient_path: str,
        amount_sent: Decimal | int | str,
        amount_received: Decimal | int | str,
        tag_names: Collection[str] = (),
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
        self._cash_transfers.append(transfer)
        self._transactions_uuid_dict[transfer.uuid] = transfer

        tags = [
            self.get_attribute(tag_name, AttributeType.TAG) for tag_name in tag_names
        ]
        transfer.add_tags(tags)
        self._add_description(transfer.description)

    def add_refund(
        self,
        description: str,
        datetime_: datetime,
        refunded_transaction_uuid: UUID,
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
                f"Transaction uuid='{refunded_transaction_uuid!s}' not found."
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
        self._refund_transactions.append(refund)
        self._transactions_uuid_dict[refund.uuid] = refund
        self._add_description(refund.description)

    def add_security_transaction(
        self,
        description: str,
        datetime_: datetime,
        type_: SecurityTransactionType,
        security_name: str,
        shares: Decimal | int | str,
        amount_per_share: Decimal | int | str,
        security_account_path: str,
        cash_account_path: str,
        tag_names: Collection[str] = (),
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
            amount_per_share=CashAmount(amount_per_share, cash_account.currency),
            security_account=security_account,
            cash_account=cash_account,
        )
        self._transactions.append(transaction)
        self._security_transactions.append(transaction)
        self._transactions_uuid_dict[transaction.uuid] = transaction

        tags = [
            self.get_attribute(tag_name, AttributeType.TAG) for tag_name in tag_names
        ]
        transaction.add_tags(tags)
        self._add_description(transaction.description)

    def add_security_transfer(
        self,
        description: str,
        datetime_: datetime,
        security_name: str,
        shares: Decimal | int | str,
        account_sender_path: str,
        account_recipient_path: str,
        tag_names: Collection[str] = (),
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
        self._security_transfers.append(transaction)
        self._transactions_uuid_dict[transaction.uuid] = transaction

        tags = [
            self.get_attribute(tag_name, AttributeType.TAG) for tag_name in tag_names
        ]
        transaction.add_tags(tags)
        self._add_description(transaction.description)

    def edit_cash_transactions(
        self,
        transaction_uuids: Collection[UUID],
        description: str | None = None,
        datetime_: datetime | None = None,
        transaction_type: CashTransactionType | None = None,
        account_path: str | None = None,
        payee_name: str | None = None,
        category_path_amount_pairs: Collection[tuple[str, Decimal | None]]
        | None = None,
        tag_name_amount_pairs: Collection[tuple[str, Decimal | None]] | None = None,
    ) -> None:
        transactions = self._get_transactions(transaction_uuids, CashTransaction)

        if (
            len(transactions) > 1
            and transaction_type is not None
            and not all(
                transaction.type_ == transaction_type for transaction in transactions
            )
        ):
            raise InvalidOperationError(
                "Cannot change type of multiple CashTransactions."
            )

        if account_path is not None:
            account = self.get_account(account_path, CashAccount)
        else:
            account = None

        if payee_name is not None:
            payee = self.get_attribute(payee_name, AttributeType.PAYEE)
        else:
            payee = None

        if not all(
            transaction.currency == transactions[0].currency
            for transaction in transactions
        ):
            currency = None
            if category_path_amount_pairs is not None and not all(
                amount is None for _, amount in category_path_amount_pairs
            ):
                raise ValueError(
                    "If CashTransaction of various Currencies are edited, "
                    "all Category amounts must be None."
                )
            if tag_name_amount_pairs is not None and not all(
                amount is None for _, amount in tag_name_amount_pairs
            ):
                raise ValueError(
                    "If CashTransaction of various Currencies are edited, "
                    "all Tag amounts must be None."
                )
            if account is not None:
                raise ValueError(
                    "If CashTransaction of various Currencies are edited, "
                    "'account_path' must be None."
                )
        else:
            currency = (
                account.currency if account is not None else transactions[0].currency
            )

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
            self._remove_description(transaction.description)
            transaction.set_attributes(
                description=description,
                datetime_=datetime_,
                type_=transaction_type,
                account=account,
                category_amount_pairs=category_amount_pairs,
                tag_amount_pairs=tag_amount_pairs,
                payee=payee,
            )
            self._add_description(transaction.description)

    def edit_cash_transfers(
        self,
        transaction_uuids: Collection[UUID],
        description: str | None = None,
        datetime_: datetime | None = None,
        sender_path: str | None = None,
        recipient_path: str | None = None,
        amount_sent: Decimal | None = None,
        amount_received: Decimal | None = None,
        tag_names: Collection[str] | None = None,
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
            if sender is not None:
                _amount_sent = CashAmount(amount_sent, sender.currency)
            else:
                if len({transfer.sender.currency for transfer in transfers}) != 1:
                    raise CurrencyError(
                        "If amount_sent is to be changed, all sender CashAccounts "
                        "must be of same Currency."
                    )
                _amount_sent = CashAmount(amount_sent, transfers[0].sender.currency)
        else:
            _amount_sent = None

        if amount_received is not None:
            if recipient is not None:
                _amount_received = CashAmount(amount_received, recipient.currency)
            else:
                if len({transfer.recipient.currency for transfer in transfers}) != 1:
                    raise CurrencyError(
                        "If amount_received is to be changed, "
                        "all recipient CashAccounts must be of same Currency."
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
            self._remove_description(transfer.description)
            transfer.set_attributes(
                description=description,
                datetime_=datetime_,
                amount_sent=_amount_sent,
                amount_received=_amount_received,
                sender=sender,
                recipient=recipient,
            )
            self._add_description(transfer.description)

        if tag_names is not None:
            tags = [
                self.get_attribute(tag_name, AttributeType.TAG)
                for tag_name in tag_names
            ]
            for transfer in transfers:
                transfer.clear_tags()
                transfer.add_tags(tags)

    def edit_refunds(
        self,
        transaction_uuids: Collection[UUID],
        description: str | None = None,
        datetime_: datetime | None = None,
        account_path: str | None = None,
        payee_name: str | None = None,
        category_path_amount_pairs: Collection[tuple[str, Decimal | None]]
        | None = None,
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
            category_amount_pairs = self._create_category_amount_pairs(
                category_path_amount_pairs, CategoryType.EXPENSE, currency
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
            self._remove_description(refund.description)
            refund.set_attributes(
                description=description,
                datetime_=datetime_,
                account=account,
                category_amount_pairs=category_amount_pairs,
                tag_amount_pairs=tag_amount_pairs,
                payee=payee,
            )
            self._add_description(refund.description)

    def edit_security_transactions(
        self,
        transaction_uuids: Collection[UUID],
        description: str | None = None,
        datetime_: datetime | None = None,
        transaction_type: SecurityTransactionType | None = None,
        security_name: str | None = None,
        cash_account_path: str | None = None,
        security_account_path: str | None = None,
        amount_per_share: Decimal | int | str | None = None,
        shares: Decimal | int | str | None = None,
        tag_names: Collection[str] | None = None,
    ) -> None:
        transactions = self._get_transactions(transaction_uuids, SecurityTransaction)

        if any(
            transaction.currency != transactions[0].currency
            for transaction in transactions
        ):
            if security_name is None and (
                cash_account_path is not None or amount_per_share is not None
            ):
                raise ValueError(
                    "If mixed currency SecurityTransactions are edited and "
                    "security_name is None, cash_account_path and amount_per_share must "
                    "be None too."
                )
            if security_name is not None and (
                cash_account_path is None or amount_per_share is None
            ):
                raise ValueError(
                    "If mixed currency SecurityTransactions are edited and "
                    "security_name is not None, cash_account_path and amount_per_share "
                    "must not be None too."
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

        if amount_per_share is not None:
            _amount_per_share = CashAmount(amount_per_share, currency)
        else:
            _amount_per_share = None

        if shares is not None:
            shares = Decimal(shares)

        for transaction in transactions:
            transaction.validate_attributes(
                description=description,
                datetime_=datetime_,
                type_=transaction_type,
                security=security,
                amount_per_share=_amount_per_share,
                shares=shares,
                cash_account=cash_account,
                security_account=security_account,
            )

        for transaction in transactions:
            self._remove_description(transaction.description)
            transaction.set_attributes(
                description=description,
                datetime_=datetime_,
                type_=transaction_type,
                security=security,
                amount_per_share=_amount_per_share,
                shares=shares,
                cash_account=cash_account,
                security_account=security_account,
            )
            self._add_description(transaction.description)

        if tag_names is not None:
            tags = [
                self.get_attribute(tag_name, AttributeType.TAG)
                for tag_name in tag_names
            ]
            for transaction in transactions:
                transaction.clear_tags()
                transaction.add_tags(tags)

    def edit_security_transfers(
        self,
        transaction_uuids: Collection[UUID],
        description: str | None = None,
        datetime_: datetime | None = None,
        security_name: str | None = None,
        shares: Decimal | None = None,
        sender_path: str | None = None,
        recipient_path: str | None = None,
        tag_names: Collection[str] | None = None,
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
            self._remove_description(transaction.description)
            transaction.set_attributes(
                description=description,
                datetime_=datetime_,
                sender=sender,
                recipient=recipient,
                shares=shares,
                security=security,
            )
            self._add_description(transaction.description)

        if tag_names is not None:
            tags = [
                self.get_attribute(tag_name, AttributeType.TAG)
                for tag_name in tag_names
            ]
            for transaction in transactions:
                transaction.clear_tags()
                transaction.add_tags(tags)

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
        self,
        current_name: str,
        new_name: str,
        type_: AttributeType,
        *,
        merge: bool = False,
    ) -> None:
        attributes = self._payees if type_ == AttributeType.PAYEE else self._tags

        edited_attribute = None
        existing_attribute = None
        for attribute in attributes:
            if attribute.name == current_name:
                edited_attribute = attribute
            elif attribute.name == new_name:
                existing_attribute = attribute

        if edited_attribute is None:
            raise NotFoundError(
                f"Attribute of name='{current_name}' and type_={type_} does not exist."
            )
        if not merge and existing_attribute is not None:
            raise AlreadyExistsError(
                f"Attribute of name='{new_name}' and type_={type_} already exists."
            )

        if existing_attribute is None:
            edited_attribute.name = new_name
            return
        if merge:
            if type_ == AttributeType.PAYEE:
                for transaction in self._cash_transactions + self._refund_transactions:
                    if transaction.payee == edited_attribute:
                        transaction.replace_payee(existing_attribute)
                self._payees.remove(edited_attribute)
            else:
                for transaction in self._transactions:
                    if edited_attribute in transaction.tags:
                        transaction.replace_tag(edited_attribute, existing_attribute)
                self._tags.remove(edited_attribute)

    def edit_security(
        self,
        uuid_: UUID,
        name: str | None = None,
        symbol: str | None = None,
        type_: str | None = None,
    ) -> None:
        edited_security = self.get_security_by_uuid(uuid_)
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
        new_parent = self.get_account_group_or_none(parent_path)
        edited_account.name = name
        edited_account.initial_balance = CashAmount(
            initial_balance, edited_account.currency
        )
        self._edit_account_item_parent(
            item=edited_account, new_parent=new_parent, index=index
        )
        self._cash_accounts.sort(key=lambda account: account.path.lower())

    def edit_security_account(
        self, current_path: str, new_path: str, index: int | None = None
    ) -> None:
        parent_path, _, name = new_path.rpartition("/")
        if current_path != new_path:
            self._check_account_exists(new_path)
        edited_account = self.get_account(current_path, SecurityAccount)
        new_parent = self.get_account_group_or_none(parent_path)
        edited_account.name = name
        self._edit_account_item_parent(
            item=edited_account, new_parent=new_parent, index=index
        )
        self._security_accounts.sort(key=lambda account: account.path.lower())

    def edit_account_group(
        self, current_path: str, new_path: str, index: int | None = None
    ) -> None:
        if current_path != new_path and any(
            account_group.path == new_path for account_group in self._account_groups
        ):
            raise AlreadyExistsError(
                f"An Account Group with path='{new_path}' already exists."
            )
        edited_account_group = self.get_account_group(current_path)
        parent_path, _, name = new_path.rpartition("/")
        new_parent = self.get_account_group_or_none(parent_path)
        if new_parent == edited_account_group:
            raise InvalidOperationError("An AccountGroup cannot be its own parent.")
        edited_account_group.name = name
        self._edit_account_item_parent(
            item=edited_account_group, new_parent=new_parent, index=index
        )

    def add_tags_to_transactions(
        self, transaction_uuids: Collection[UUID], tag_names: Collection[str]
    ) -> None:
        self._perform_tag_operation(
            transaction_uuids=transaction_uuids,
            tag_names=tag_names,
            method_name="add_tags",
        )

    def remove_tags_from_transactions(
        self, transaction_uuids: Collection[UUID], tag_names: Collection[str]
    ) -> None:
        self._perform_tag_operation(
            transaction_uuids=transaction_uuids,
            tag_names=tag_names,
            method_name="remove_tags",
        )

    def _perform_tag_operation(
        self,
        transaction_uuids: Collection[UUID],
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
        if isinstance(account, CashAccount):
            self._cash_accounts.remove(account)
        else:
            self._security_accounts.remove(account)
        del account

    def remove_account_group(self, account_group_path: str) -> None:
        account_group = self.get_account_group(account_group_path)
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

    def remove_transactions(self, transaction_uuids: Collection[UUID]) -> None:
        transactions = self._get_transactions(transaction_uuids, Transaction)
        for transaction in transactions:
            transaction.prepare_for_deletion()
            self._transactions.remove(transaction)
            if isinstance(transaction, CashTransaction):
                self._cash_transactions.remove(transaction)
            elif isinstance(transaction, RefundTransaction):
                self._refund_transactions.remove(transaction)
            elif isinstance(transaction, CashTransfer):
                self._cash_transfers.remove(transaction)
            elif isinstance(transaction, SecurityTransaction):
                self._security_transactions.remove(transaction)
            elif isinstance(transaction, SecurityTransfer):
                self._security_transfers.remove(transaction)
            else:
                raise TypeError(  # pragma: no cover
                    f"Unknown transaction type: {type(transaction)}"
                )

            # delete transaction from dictionary
            del self._transactions_uuid_dict[transaction.uuid]
            self._remove_description(transaction.description)

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
            account.currency == currency
            for account in self._accounts
            if isinstance(account, CashAccount)
        ):
            raise InvalidOperationError(
                "Cannot delete a Currency referenced in any CashAccount."
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
        self._reset_currency_caches()
        del removed_exchange_rate

    def remove_category(self, path: str) -> None:
        category = self.get_category(path)
        if len(category.children) != 0:
            raise InvalidOperationError("Cannot delete a Category with children.")
        if any(
            category in transaction.categories
            for transaction in (self._cash_transactions + self._refund_transactions)
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

    def get_account_group_or_none(self, path: str) -> AccountGroup | None:
        if not path:
            return None
        return self.get_account_group(path)

    def get_account_group(self, path: str) -> AccountGroup:
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

    def get_security_by_uuid(self, uuid_: UUID) -> Security:
        if not isinstance(uuid_, UUID):
            raise TypeError("Parameter 'uuid' must be a UUID.")
        for security in self._securities:
            if security.uuid == uuid_:
                return security
        raise NotFoundError(f"A Security with uuid='{uuid_!s}' does not exist.")

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

    def get_exchange_rate(self, code: str) -> ExchangeRate:
        if not isinstance(code, str):
            raise TypeError("Parameter 'code' must be a string.")
        code_upper = code.upper()
        for exchange_rate in self._exchange_rates:
            if str(exchange_rate) == code_upper:
                return exchange_rate
        raise NotFoundError(f"An ExchangeRate with code='{code_upper}' does not exist.")

    def get_category(self, path: str) -> Category:
        for category in self._categories:
            if category.path == path:
                return category
        raise NotFoundError(f"Category at {path=} does not exist.")

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
                    logging.info(f"Created Category: path={parent.path}")
                    self._save_category(parent)
            remainder_name = path.removeprefix(parent.path)[1:]
            type_ = parent.type_
            while "/" in remainder_name:
                # As long as multiple categories remain...
                new_name = remainder_name.split("/")[0]
                new_category = Category(new_name, type_, parent)
                logging.info(f"Created Category: path={new_category.path}")
                self._save_category(new_category)
                parent = new_category
                remainder_name = remainder_name.removeprefix(new_name)[1:]
        else:
            remainder_name = path
        # Reached the end - just one more category left
        final_category = Category(remainder_name, type_, parent)
        logging.info(f"Created Category: path={final_category.path}")
        self._save_category(final_category)
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
        logging.info(f"Creating {type_.name.title()}: '{name}'")
        attribute = Attribute(name, type_)
        attributes.append(attribute)
        return attribute

    def serialize(
        self,
        progress_callable: Callable[[int], None],
    ) -> dict[str, Any]:
        serialized_currencies = [currency.serialize() for currency in self._currencies]
        base_currency_code = (
            self._base_currency.code if self._base_currency is not None else None
        )

        serialized_exchange_rates = []
        no_of_exchange_rates = len(self._exchange_rates)
        step = no_of_exchange_rates // 33
        step = 1 if step == 0 else step
        for done, exchange_rate in enumerate(self._exchange_rates):
            serialized_exchange_rate = exchange_rate.serialize()
            serialized_exchange_rates.append(serialized_exchange_rate)
            if (done + 1) % step == 0:
                progress = int(done / no_of_exchange_rates * 33)
                progress_callable(progress)
            if (done + 1) == no_of_exchange_rates:
                progress_callable(33)

        serialized_securities = []
        no_of_securities = len(self._securities)
        step = no_of_securities // 33
        step = 1 if step == 0 else step
        for done, security in enumerate(self._securities):
            serialized_security = security.serialize()
            serialized_securities.append(serialized_security)
            if (done + 1) % step == 0:
                progress = int(33 + done / no_of_securities * 33)
                progress_callable(progress)
            if (done + 1) == no_of_securities:
                progress_callable(66)

        sorted_account_groups = sorted(self._account_groups, key=lambda x: x.path)
        serialized_account_groups = [
            account_group.serialize() for account_group in sorted_account_groups
        ]

        sorted_categories = sorted(self._categories, key=lambda x: x.path)
        serialized_categories = [category.serialize() for category in sorted_categories]

        sorted_accounts = sorted(self._accounts, key=lambda x: x.path)
        serialized_accounts = [account.serialize() for account in sorted_accounts]

        sorted_tags = sorted(self._tags, key=lambda x: x.name)
        serialized_tags = [tag.name for tag in sorted_tags]

        sorted_payees = sorted(self._payees, key=lambda x: x.name)
        serialized_payees = [payee.name for payee in sorted_payees]

        root_item_references = [
            {"datatype": item.__class__.__name__, "path": item.path}
            for item in self._root_account_items
        ]

        root_income_category_refs = [
            category.path for category in self._root_income_categories
        ]
        root_expense_category_refs = [
            category.path for category in self._root_expense_categories
        ]
        root_dual_purpose_category_refs = [
            category.path for category in self._root_dual_purpose_categories
        ]

        # Sorting transactions here speeds up sorting during deserialization
        sorted_transactions = sorted(self._transactions, key=lambda x: x.timestamp)
        serialized_transactions = []
        no_of_transactions = len(sorted_transactions)
        step = no_of_transactions // 34
        step = 1 if step == 0 else step
        for done, security in enumerate(sorted_transactions):
            serialized_transaction = security.serialize()
            serialized_transactions.append(serialized_transaction)
            if (done + 1) % step == 0:
                progress = int(66 + done / no_of_transactions * 34)
                progress_callable(progress)
            if (done + 1) == no_of_transactions:
                progress_callable(100)

        return {
            "datatype": "RecordKeeper",
            "currencies": serialized_currencies,
            "base_currency_code": base_currency_code,
            "exchange_rates": serialized_exchange_rates,
            "securities": serialized_securities,
            "account_groups": serialized_account_groups,
            "accounts": serialized_accounts,
            "root_account_items": root_item_references,
            "payees": serialized_payees,
            "tags": serialized_tags,
            "categories": serialized_categories,
            "root_income_categories": root_income_category_refs,
            "root_expense_categories": root_expense_category_refs,
            "root_dual_purpose_categories": root_dual_purpose_category_refs,
            "transactions": serialized_transactions,
        }

    @staticmethod
    def deserialize(
        data: dict[str, Any], progress_callable: Callable[[int], None]
    ) -> "RecordKeeper":
        obj = RecordKeeper()
        obj._currencies = data["currencies"]
        currencies: dict[str, Currency] = {
            currency.code: currency
            for currency in obj._currencies
        }
        base_currency_code = data["base_currency_code"]
        if base_currency_code is not None:
            obj._base_currency = currencies[base_currency_code]

        obj._exchange_rates = RecordKeeper._deserialize_exchange_rates(
            data["exchange_rates"], currencies, progress_callable
        )
        for exchange_rate in obj._exchange_rates:
            exchange_rate.event_reset_currency_caches.append(
                obj._reset_currency_caches
            )

        securities = RecordKeeper._deserialize_securities(
            data["securities"], currencies, progress_callable
        )
        obj._securities = list(securities.values())

        account_groups = RecordKeeper._deserialize_account_groups(
            data["account_groups"]
        )
        obj._account_groups = list(account_groups.values())

        accounts = RecordKeeper._deserialize_accounts(
            data["accounts"], account_groups, currencies
        )
        obj._accounts = list(accounts.values())
        obj._cash_accounts = [
            account for account in accounts.values() if isinstance(account, CashAccount)
        ]
        obj._security_accounts = [
            account
            for account in accounts.values()
            if isinstance(account, SecurityAccount)
        ]

        obj._root_account_items = (
            RecordKeeper._deserialize_root_account_items(
                data["root_account_items"],
                account_groups,
                accounts,
            )
        )

        obj._payees = [
            Attribute(name, AttributeType.PAYEE) for name in data["payees"]
        ]
        payees: dict[str, Attribute] = {
            payee.name: payee
            for payee in obj._payees
        }
        obj._tags = [
            Attribute(name, AttributeType.TAG) for name in data["tags"]
        ]
        tags: dict[str, Attribute] = {
            tag.name: tag
            for tag in obj._tags
        }

        categories = RecordKeeper._deserialize_categories(data["categories"])
        obj._categories = list(categories.values())

        obj._root_income_categories = (
            RecordKeeper._deserialize_root_categories(
                data["root_income_categories"], categories
            )
        )
        obj._root_expense_categories = (
            RecordKeeper._deserialize_root_categories(
                data["root_expense_categories"], categories
            )
        )
        obj._root_dual_purpose_categories = (
            RecordKeeper._deserialize_root_categories(
                data["root_dual_purpose_categories"],
                categories,
            )
        )

        obj._transactions_uuid_dict = (
            RecordKeeper._deserialize_transactions(
                data["transactions"],
                accounts,
                payees,
                tags,
                categories,
                currencies,
                securities,
                progress_callable,
            )
        )

        # Sorting transactions here is useful because front-end can assume that
        # upon load of RecordKeeper._transactions, transactions are already sorted
        # in descending order
        obj._transactions = sorted(
            obj._transactions_uuid_dict.values(),
            key=lambda x: x.timestamp,
            reverse=True,
        )

        for transaction in obj._transactions:
            if isinstance(transaction, CashTransaction):
                obj._cash_transactions.append(transaction)
            elif isinstance(transaction, RefundTransaction):
                obj._refund_transactions.append(transaction)
            elif isinstance(transaction, CashTransfer):
                obj._cash_transfers.append(transaction)
            elif isinstance(transaction, SecurityTransaction):
                obj._security_transactions.append(transaction)
            elif isinstance(transaction, SecurityTransfer):
                obj._security_transfers.append(transaction)
            else:
                raise TypeError(  # pragma: no cover
                    f"Unknown transaction type: {type(transaction)}"
                )

        for account in obj._accounts:
            account: CashAccount | SecurityAccount
            account.allow_update_balance = True
            if isinstance(account, CashAccount):
                account.update_balance()
            else:
                account.update_securities()

        # this sort is needed because updating CashAccount balance can change timestamps
        obj._transactions.sort(
            key=lambda x: x.timestamp,
            reverse=True,
        )
        obj._update_descriptions()

        return obj

    @staticmethod
    def _deserialize_exchange_rates(
        exchange_rate_dicts: Collection[dict[str, Any]],
        currencies: dict[str, Currency],
        progress_callable: Callable[[int], None],
    ) -> list[ExchangeRate]:
        exchange_rates = []
        no_of_exchange_rates = len(exchange_rate_dicts)
        step = no_of_exchange_rates // 33
        if step == 0:
            step = 1
        for done, exchange_rate_dict in enumerate(exchange_rate_dicts):
            exchange_rate = ExchangeRate.deserialize(exchange_rate_dict, currencies)
            exchange_rates.append(exchange_rate)
            if (done + 1) % step == 0:
                progress = int(done / no_of_exchange_rates * 33)
                progress_callable(progress)
            if (done + 1) == no_of_exchange_rates:
                progress_callable(33)
        return exchange_rates

    @staticmethod
    def _deserialize_securities(
        security_dicts: Collection[dict[str, Any]],
        currencies: dict[str, Currency],
        progress_callable: Callable[[int], None],
    ) -> dict[str, Security]:
        securities: dict[str, Security] = {}
        no_of_securities = len(security_dicts)
        step = no_of_securities // 33
        if step == 0:
            step = 1
        for done, security_dict in enumerate(security_dicts):
            security = Security.deserialize(security_dict, currencies)
            securities[security.name] = security
            if (done + 1) % step == 0:
                progress = int(33 + done / no_of_securities * 33)
                progress_callable(progress)
            if (done + 1) == no_of_securities:
                progress_callable(66)
        return securities

    @staticmethod
    def _deserialize_account_groups(
        account_group_dicts: Collection[dict[str, Any]],
    ) -> dict[str, AccountGroup]:
        account_groups: dict[str, AccountGroup] = {}
        for account_group_dict in account_group_dicts:
            account_group = AccountGroup.deserialize(account_group_dict, account_groups)
            account_groups[account_group.path] = account_group
        return account_groups

    @staticmethod
    def _deserialize_accounts(
        account_path_dicts: Collection[dict[str, Any]],
        account_groups: dict[str, AccountGroup],
        currencies: dict[str, Currency],
    ) -> dict[str, Account]:
        accounts: dict[str, Account] = {}
        for account_dict in account_path_dicts:
            account: Account
            if account_dict["datatype"] == "CashAccount":
                account = CashAccount.deserialize(
                    account_dict, account_groups, currencies
                )
            elif account_dict["datatype"] == "SecurityAccount":
                account = SecurityAccount.deserialize(account_dict, account_groups)
            else:
                raise ValueError("Unexpected 'datatype' value.")
            accounts[account.path] = account
            # Disable updating balance during deserialization due to performance penalty
            account.allow_update_balance = False
        return accounts

    @staticmethod
    def _deserialize_root_account_items(
        root_item_dicts: Collection[dict[str, Any]],
        account_groups: dict[str, AccountGroup],
        accounts: dict[str, Account],
    ) -> list[AccountGroup | Account]:
        root_items: list[AccountGroup | Account] = []
        for item_dict in root_item_dicts:
            datatype: str = item_dict["datatype"]
            if datatype == "AccountGroup":
                root_items.append(account_groups[item_dict["path"]])
            elif datatype.endswith("Account"):
                root_items.append(accounts[item_dict["path"]])
            else:
                raise ValueError("Unexpected 'datatype' value.")
        return root_items

    @staticmethod
    def _deserialize_categories(
        category_path_dicts: Collection[dict[str, Any]],
    ) -> dict[str, Category]:
        categories: dict[str, Category] = {}
        for category_dict in category_path_dicts:
            category = Category.deserialize(category_dict, categories)
            categories[category.path] = category
        return categories

    @staticmethod
    def _deserialize_root_categories(
        root_category_paths: Collection[str],
        categories: dict[str, Category],
    ) -> list[Category]:
        return [categories[path] for path in root_category_paths]

    @staticmethod
    def _deserialize_transactions(
        transaction_dicts: Collection[dict[str, Any]],
        accounts: dict[str, Account],
        payees: dict[str, Attribute],
        tags: dict[str, Attribute],
        categories: dict[str, Category],
        currencies: dict[str, Currency],
        securities: dict[str, Security],
        progress_callable: Callable[[int], None],
    ) -> dict[UUID, Transaction]:
        _transaction_dict: dict[UUID, Transaction] = {}
        no_of_transactions = len(transaction_dicts)
        step = no_of_transactions // 34
        if step == 0:
            step = 1
        for done, transaction_dict in enumerate(transaction_dicts):
            transaction: Transaction
            if transaction_dict["datatype"] == "CashTransaction":
                transaction = CashTransaction.deserialize(
                    transaction_dict,
                    accounts,
                    payees,
                    categories,
                    tags,
                    currencies,
                )
            elif transaction_dict["datatype"] == "CashTransfer":
                transaction = CashTransfer.deserialize(
                    transaction_dict, accounts, currencies
                )
            elif transaction_dict["datatype"] == "RefundTransaction":
                transaction = RefundTransaction.deserialize(
                    transaction_dict,
                    accounts,
                    _transaction_dict,
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
            _transaction_dict[transaction.uuid] = transaction
            if (done + 1) % step == 0:
                progress = int(66 + done / no_of_transactions * 34)
                progress_callable(progress)
            if (done + 1) == no_of_transactions:
                progress_callable(100)
        return _transaction_dict

    def _check_account_exists(self, path: str) -> None:
        if any(account.path == path for account in self._accounts):
            raise AlreadyExistsError(f"An Account with path={path} already exists.")

    def _create_category_amount_pairs(
        self,
        category_path_amount_pairs: Collection[tuple[str, Decimal | None]],
        category_type: CategoryType,
        currency: Currency | None,
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
        tag_name_amount_pairs: Collection[tuple[str, Decimal | None]],
        currency: Currency,
    ) -> list[tuple[Attribute, CashAmount | None]]:
        tag_amount_pairs: list[tuple[Attribute, CashAmount]] = []
        for tag_name, amount in tag_name_amount_pairs:
            _tag = self.get_attribute(tag_name, AttributeType.TAG)
            _amount = CashAmount(amount, currency) if amount is not None else None
            tag_amount_pairs.append((_tag, _amount))
        return tag_amount_pairs

    TransactionType = TypeVar("TransactionType", bound=Transaction)

    def _get_transactions(
        self, uuids: Collection[UUID], type_: type[TransactionType]
    ) -> list[TransactionType]:
        transactions: list[RecordKeeper.TransactionType] = []
        if any(not isinstance(uuid_, UUID) for uuid_ in uuids):
            raise TypeError("Parameter 'uuids' must be a Collection ofUUID objects.")
        for transaction in self._transactions:
            if transaction.uuid in uuids:
                if not isinstance(transaction, type_):
                    raise TypeError(
                        f"Type of Transaction at uuid='{transaction.uuid!s}' "
                        f"is not {type_.__name__}."
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
        return self._root_dual_purpose_categories

    @staticmethod
    def _flatten_account_items(
        account_items: Collection[Account | AccountGroup],
    ) -> list[Account | AccountGroup]:
        """Used to flatten the Account Item tree, preserving the order."""
        resulting_list: list[Account | AccountGroup] = []
        for account_item in account_items:
            resulting_list.append(account_item)
            if isinstance(account_item, AccountGroup):
                resulting_list = resulting_list + RecordKeeper._flatten_account_items(
                    account_item.children
                )
        return resulting_list

    @staticmethod
    def _flatten_categories(root_categories: Collection[Category]) -> list[Category]:
        """Used to flatten the Category tree, preserving the order."""
        resulting_list = []
        for category in root_categories:
            resulting_list.append(category)
            if len(category.children) > 0:
                resulting_list = resulting_list + RecordKeeper._flatten_categories(
                    category.children
                )
        return resulting_list

    def _save_category(self, category: Category) -> None:
        if category not in self._categories:
            self._categories.append(category)

        if category.parent is not None:
            return

        if (
            category.type_ == CategoryType.INCOME
            and category not in self._root_income_categories
        ):
            self._root_income_categories.append(category)
        elif (
            category.type_ == CategoryType.EXPENSE
            and category not in self._root_income_categories
        ):
            self._root_expense_categories.append(category)
        else:
            self._root_dual_purpose_categories.append(category)

    def _add_description(self, description: str) -> None:
        self._descriptions[description] += 1

    def _remove_description(self, description: str) -> None:
        self._descriptions[description] -= 1
        if self._descriptions[description] == 0:
            del self._descriptions[description]

    def _update_descriptions(self) -> None:
        self._descriptions = defaultdict(int)
        for transaction in self._transactions:
            if transaction.description:
                self._descriptions[transaction.description] += 1

    def _reset_currency_caches(self) -> None:
        for currency in self._currencies:
            currency.reset_cache()
