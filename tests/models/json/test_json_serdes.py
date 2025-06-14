import json
from datetime import datetime, timedelta
from decimal import Decimal

import pytest
from hypothesis import assume, given
from hypothesis import strategies as st
from src.models.json.custom_json_decoder import CustomJSONDecoder
from src.models.json.custom_json_encoder import CustomJSONEncoder
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
from src.models.model_objects.currency_objects import CashAmount, Currency, ExchangeRate
from src.models.model_objects.security_objects import (
    Security,
    SecurityAccount,
    SecurityTransaction,
    SecurityTransactionType,
    SecurityTransfer,
)
from src.models.record_keeper import RecordKeeper
from src.models.user_settings import user_settings
from src.models.user_settings.user_settings_class import NumberFormat, UserSettings
from tests.models.test_assets.composites import (
    attributes,
    cash_transactions,
    cash_transfers,
    categories,
    security_transactions,
    security_transfers,
)


def test_invalid_object() -> None:
    with pytest.raises(TypeError, match="not JSON serializable"):
        json.dumps(object, cls=CustomJSONEncoder)


def test_datetime() -> None:
    dt = datetime.now(user_settings.settings.time_zone).replace(microsecond=0)
    serialized = json.dumps(dt, cls=CustomJSONEncoder).strip('"')
    decoded = datetime.fromisoformat(serialized)
    assert decoded == dt


def test_currency() -> None:
    currency = Currency("CZK", 2)
    serialized = json.dumps(currency, cls=CustomJSONEncoder)
    decoded = json.loads(serialized, cls=CustomJSONDecoder)
    assert decoded == currency


def test_exchange_rate() -> None:
    primary = Currency("EUR", 2)
    secondary = Currency("CZK", 2)
    currency_dict = {primary.code: primary, secondary.code: secondary}
    exchange_rate = ExchangeRate(primary, secondary)
    exchange_rate.set_rate(datetime.now(user_settings.settings.time_zone).date(), 1)
    serialized = json.dumps(exchange_rate, cls=CustomJSONEncoder)
    decoded = json.loads(serialized, cls=CustomJSONDecoder)
    decoded = ExchangeRate.deserialize(decoded, currency_dict)
    assert isinstance(decoded, ExchangeRate)
    assert decoded.primary_currency == exchange_rate.primary_currency
    assert decoded.secondary_currency == exchange_rate.secondary_currency
    assert decoded.latest_date == datetime.now(user_settings.settings.time_zone).date()
    assert decoded.latest_rate == 1


def test_cash_amount() -> None:
    currency = Currency("EUR", 2)
    cash_amount = CashAmount(Decimal("1.23"), currency)
    serialized = json.dumps(cash_amount, cls=CustomJSONEncoder)
    decoded = json.loads(serialized, cls=CustomJSONDecoder)
    decoded = CashAmount.deserialize(decoded, {currency.code: currency})
    assert decoded == cash_amount


@given(attribute=attributes())
def test_attribute(attribute: Attribute) -> None:
    serialized = json.dumps(attribute, cls=CustomJSONEncoder)
    decoded = json.loads(serialized, cls=CustomJSONDecoder)
    assert isinstance(decoded, Attribute)
    assert decoded.name == attribute.name
    assert decoded.type_ == attribute.type_


@given(parent=categories(), data=st.data())
def test_category(parent: Category, data: st.DataObject) -> None:
    child_1 = data.draw(categories(category_type=parent.type_))
    child_2 = data.draw(categories(category_type=parent.type_))
    assume(child_1.path != child_2.path)
    child_1.parent = parent
    child_2.parent = parent

    category_tuple = (parent, child_1, child_2)
    serialized = json.dumps(category_tuple, cls=CustomJSONEncoder)
    decoded = json.loads(serialized, cls=CustomJSONDecoder)

    category_list = []
    category_dict = {}
    for decoded_dict in decoded:
        category = Category.deserialize(decoded_dict, category_dict)
        category_list.append(category)
        category_dict[category.path] = category
    decoded = category_list[0]
    assert isinstance(decoded, Category)
    assert decoded.name == parent.name
    assert decoded.type_ == parent.type_
    assert decoded.children[0].name == child_1.name
    assert decoded.children[0].parent == decoded
    assert decoded.children[1].name == child_2.name
    assert decoded.children[1].parent == decoded


def test_account_group() -> None:
    parent = AccountGroup("Test Name")
    child_1 = AccountGroup("Child 1", parent)
    child_2 = AccountGroup("Child 2", parent)
    account_groups = [parent, child_1, child_2]
    serialized = json.dumps(account_groups, cls=CustomJSONEncoder)
    decoded = json.loads(serialized, cls=CustomJSONDecoder)

    account_groups = []
    account_group_dict = {}
    for _account_group_dict in decoded:
        account_group = AccountGroup.deserialize(
            _account_group_dict, account_group_dict
        )
        account_groups.append(account_group)
        account_group_dict[account_group.path] = account_group
    decoded = account_groups[0]
    assert isinstance(decoded, AccountGroup)
    assert decoded.name == parent.name
    assert decoded.children[0].name == child_1.name
    assert decoded.children[0].parent == decoded
    assert decoded.children[1].name == child_2.name
    assert decoded.children[1].parent == decoded


def test_cash_account() -> None:
    currency = Currency("CZK", 2)
    cash_account = CashAccount("Test Name", currency, currency.zero_amount)
    serialized = json.dumps(cash_account, cls=CustomJSONEncoder)
    decoded = json.loads(serialized, cls=CustomJSONDecoder)
    decoded = CashAccount.deserialize(decoded, None, {currency.code: currency})
    assert isinstance(decoded, CashAccount)
    assert decoded.name == cash_account.name
    assert decoded.currency == cash_account.currency
    assert decoded.initial_balance == cash_account.initial_balance
    assert decoded.uuid == cash_account.uuid


def test_security_account() -> None:
    security_account = SecurityAccount("Test Name")
    serialized = json.dumps(security_account, cls=CustomJSONEncoder)
    decoded = json.loads(serialized, cls=CustomJSONDecoder)
    decoded = SecurityAccount.deserialize(decoded, None)
    assert isinstance(decoded, SecurityAccount)
    assert decoded.name == security_account.name
    assert decoded.uuid == security_account.uuid


def test_security() -> None:
    currency = Currency("CZK", 2)
    security = Security("Test Name", "SYMB.OL", "ETF", currency, 1)
    security.set_price(
        datetime.now(user_settings.settings.time_zone).date(),
        CashAmount("1.234567890", currency),
    )
    serialized = json.dumps(security, cls=CustomJSONEncoder)
    decoded = json.loads(serialized, cls=CustomJSONDecoder)
    decoded = Security.deserialize(decoded, {currency.code: currency})
    assert isinstance(decoded, Security)
    assert decoded.name == security.name
    assert decoded.symbol == security.symbol
    assert decoded.currency == security.currency
    assert decoded.type_ == security.type_
    assert decoded.shares_decimals == security.shares_decimals
    assert decoded.uuid == security.uuid
    assert decoded.price == security.price


def test_record_keeper_currencies_exchange_rates() -> None:
    record_keeper = RecordKeeper()
    record_keeper.add_currency("CZK", 2)
    record_keeper.add_currency("EUR", 2)
    record_keeper.add_currency("USD", 2)
    record_keeper.add_exchange_rate("EUR", "CZK")
    record_keeper.add_exchange_rate("USD", "EUR")
    serialized = record_keeper.serialize(lambda *args, **kwargs: None)  # noqa: ARG005
    serialized = json.dumps(serialized, cls=CustomJSONEncoder)
    decoded = json.loads(serialized, cls=CustomJSONDecoder)
    decoded = RecordKeeper.deserialize(
        decoded,
        lambda *args, **kwargs: None,  # noqa: ARG005
    )

    assert isinstance(decoded, RecordKeeper)
    assert decoded.currencies == decoded.currencies
    assert str(decoded.exchange_rates[0]) == str(record_keeper.exchange_rates[0])
    assert str(decoded.exchange_rates[1]) == str(record_keeper.exchange_rates[1])


def test_record_keeper_account_groups() -> None:
    record_keeper = RecordKeeper()
    record_keeper.add_account_group("A1")
    record_keeper.add_account_group("A1/A2")
    record_keeper.add_account_group("A1/B2")
    record_keeper.add_account_group("A1/C2")
    record_keeper.add_account_group("A1/D2")
    record_keeper.add_account_group("A1/A2/A3")
    record_keeper.add_account_group("B1")
    record_keeper.add_account_group("C1")
    serialized = record_keeper.serialize(lambda *args, **kwargs: None)  # noqa: ARG005
    serialized = json.dumps(serialized, cls=CustomJSONEncoder)
    decoded = json.loads(serialized, cls=CustomJSONDecoder)
    decoded = RecordKeeper.deserialize(
        decoded,
        lambda *args, **kwargs: None,  # noqa: ARG005
    )
    assert isinstance(decoded, RecordKeeper)
    assert len(record_keeper.account_groups) == len(decoded.account_groups)


def test_record_keeper_accounts() -> None:
    record_keeper = RecordKeeper()
    record_keeper.add_currency("CZK", 2)
    record_keeper.add_currency("EUR", 2)
    record_keeper.add_account_group("Security Accounts", None)
    record_keeper.add_account_group("Cash Accounts", None)
    record_keeper.add_cash_account("Cash Accounts/CZK Account", "CZK", 0)
    record_keeper.add_cash_account("Cash Accounts/EUR Account", "EUR", 0)
    record_keeper.add_security_account("Security Accounts/Degiro")
    serialized = record_keeper.serialize(lambda *args, **kwargs: None)  # noqa: ARG005
    serialized = json.dumps(serialized, cls=CustomJSONEncoder)
    decoded = json.loads(serialized, cls=CustomJSONDecoder)
    decoded = RecordKeeper.deserialize(
        decoded,
        lambda *args, **kwargs: None,  # noqa: ARG005
    )
    assert isinstance(decoded, RecordKeeper)
    assert len(record_keeper.accounts) == len(decoded.accounts)


def test_record_keeper_invalid_account_datatype() -> None:
    record_keeper = RecordKeeper()
    dictionary = {"datatype": "not a valid Account sub-class"}
    with pytest.raises(ValueError, match="Unexpected 'datatype' value."):
        record_keeper._deserialize_accounts([dictionary], None, None)


def test_record_keeper_invalid_root_account_item_datatype() -> None:
    record_keeper = RecordKeeper()
    dictionary = {"datatype": "not a valid Account sub-class"}
    with pytest.raises(ValueError, match="Unexpected 'datatype' value."):
        record_keeper._deserialize_root_account_items([dictionary], None, None)


def test_record_keeper_securities() -> None:
    record_keeper = RecordKeeper()
    record_keeper.add_currency("CZK", 2)
    record_keeper.add_currency("EUR", 2)
    record_keeper.add_security("iShares MSCI All World", "IWDA.AS", "ETF", "EUR", 1)
    record_keeper.add_security(
        "ČSOB Dynamický penzijní fond", "CSOB.DYN", "Pension Fund", "CZK", 1
    )
    serialized = record_keeper.serialize(lambda *args, **kwargs: None)  # noqa: ARG005
    serialized = json.dumps(serialized, cls=CustomJSONEncoder)
    decoded = json.loads(serialized, cls=CustomJSONDecoder)
    decoded = RecordKeeper.deserialize(
        decoded,
        lambda *args, **kwargs: None,  # noqa: ARG005
    )
    assert isinstance(decoded, RecordKeeper)
    assert len(record_keeper.securities) == len(decoded.securities)


@given(
    tags=st.lists(attributes(AttributeType.TAG), min_size=1, max_size=5),
    payees=st.lists(attributes(AttributeType.PAYEE), min_size=1, max_size=5),
)
def test_record_keeper_tags_and_payees(
    tags: list[Attribute], payees: list[Attribute]
) -> None:
    record_keeper = RecordKeeper()
    record_keeper._tags = tags
    record_keeper._payees = payees
    serialized = record_keeper.serialize(lambda *args, **kwargs: None)  # noqa: ARG005
    serialized = json.dumps(serialized, cls=CustomJSONEncoder)
    decoded = json.loads(serialized, cls=CustomJSONDecoder)
    decoded = RecordKeeper.deserialize(
        decoded,
        lambda *args, **kwargs: None,  # noqa: ARG005
    )
    assert isinstance(decoded, RecordKeeper)
    assert len(record_keeper.tags) == len(decoded.tags)
    assert len(record_keeper.payees) == len(decoded.payees)


def test_record_keeper_categories() -> None:
    record_keeper = RecordKeeper()
    record_keeper.add_category("Salary", CategoryType.INCOME)
    record_keeper.add_category("Food", CategoryType.EXPENSE)
    record_keeper.add_category("Food/Groceries")
    record_keeper.add_category("Food/Eating out")
    record_keeper.add_category("Housing", CategoryType.EXPENSE)
    record_keeper.add_category("Housing/Rent")
    record_keeper.add_category("Housing/Electricity")
    record_keeper.add_category("Housing/Water")
    record_keeper.add_category("Food/Work lunch")
    record_keeper.add_category("Splitting costs", CategoryType.DUAL_PURPOSE)
    serialized = record_keeper.serialize(lambda *args, **kwargs: None)  # noqa: ARG005
    serialized = json.dumps(serialized, cls=CustomJSONEncoder)
    decoded = json.loads(serialized, cls=CustomJSONDecoder)
    decoded = RecordKeeper.deserialize(
        decoded,
        lambda *args, **kwargs: None,  # noqa: ARG005
    )
    assert isinstance(decoded, RecordKeeper)
    assert len(record_keeper.categories) == len(decoded.categories)
    assert len(record_keeper.root_income_categories) == len(
        decoded.root_income_categories
    )
    assert len(record_keeper.root_expense_categories) == len(
        decoded.root_expense_categories
    )
    assert len(record_keeper.root_dual_purpose_categories) == len(
        decoded.root_dual_purpose_categories
    )


@given(transaction=cash_transactions())
def test_cash_transaction(transaction: CashTransaction) -> None:
    category_dict = {category.path: category for category in transaction.categories}
    tag_dict = {tag.name: tag for tag in transaction.tags}

    serialized = json.dumps(transaction, cls=CustomJSONEncoder)
    transaction.account.remove_transaction(transaction)
    decoded = json.loads(serialized, cls=CustomJSONDecoder)
    decoded = CashTransaction.deserialize(
        decoded,
        {transaction.account.path: transaction.account},
        {transaction.payee.name: transaction.payee},
        category_dict,
        tag_dict,
        {transaction.currency.code: transaction.currency},
    )
    assert isinstance(decoded, CashTransaction)
    assert decoded.uuid == transaction.uuid
    assert decoded.description == transaction.description
    assert decoded.datetime_ == transaction.datetime_.replace(microsecond=0)
    assert decoded.datetime_created == transaction.datetime_created.replace(
        microsecond=0
    )
    assert decoded.type_ == transaction.type_
    assert decoded.account == transaction.account
    assert transaction.payee == transaction.payee
    assert transaction.category_amount_pairs == transaction.category_amount_pairs
    assert transaction.tag_amount_pairs == transaction.tag_amount_pairs


@given(transaction=cash_transfers())
def test_cash_transfer(transaction: CashTransfer) -> None:
    currency_dict = {currency.code: currency for currency in transaction.currencies}
    account_dict = {
        transaction.sender.path: transaction.sender,
        transaction.recipient.path: transaction.recipient,
    }

    serialized = json.dumps(transaction, cls=CustomJSONEncoder)
    transaction.sender.remove_transaction(transaction)
    transaction.recipient.remove_transaction(transaction)
    decoded = json.loads(serialized, cls=CustomJSONDecoder)
    decoded = CashTransfer.deserialize(
        decoded,
        account_dict,
        currency_dict,
    )
    assert isinstance(decoded, CashTransfer)
    assert decoded.uuid == transaction.uuid
    assert decoded.description == transaction.description

    decoded_iso = decoded.datetime_.isoformat()
    original_iso = transaction.datetime_.replace(microsecond=0).isoformat()
    assert decoded_iso == original_iso

    assert decoded.datetime_ == transaction.datetime_.replace(microsecond=0).astimezone(
        decoded.datetime_.tzinfo
    )
    assert decoded.datetime_created == transaction.datetime_created.replace(
        microsecond=0
    )
    assert decoded.sender == transaction.sender
    assert decoded.recipient == transaction.recipient
    assert decoded.amount_sent == transaction.amount_sent
    assert decoded.amount_received == transaction.amount_received


@given(transaction=cash_transactions(type_=CashTransactionType.EXPENSE))
def test_refund_transaction(transaction: CashTransaction) -> None:
    transaction.set_attributes(
        tag_amount_pairs=[
            (Attribute("test tag", AttributeType.TAG), transaction.amount)
        ]
    )

    currency_dict = {currency.code: currency for currency in transaction.currencies}
    tag_dict = {tag.name: tag for tag in transaction.tags}
    category_dict = {category.path: category for category in transaction.categories}
    payee_dict = {transaction.payee.name: transaction.payee}
    account_dict = {transaction.account.path: transaction.account}
    transaction_dict = {transaction.uuid: transaction}

    refund = RefundTransaction(
        "A short description",
        transaction.datetime_ + timedelta(days=1),
        transaction.account,
        transaction,
        transaction.payee,
        transaction.category_amount_pairs,
        transaction.tag_amount_pairs,
    )
    transaction.remove_refund(refund)
    serialized = json.dumps(refund, cls=CustomJSONEncoder)
    refund.account.remove_transaction(refund)
    decoded = json.loads(serialized, cls=CustomJSONDecoder)
    decoded = RefundTransaction.deserialize(
        decoded,
        account_dict,
        transaction_dict,
        payee_dict,
        category_dict,
        tag_dict,
        currency_dict,
    )
    assert isinstance(decoded, RefundTransaction)
    assert decoded.uuid == refund.uuid
    assert decoded.description == refund.description
    assert decoded.datetime_ == refund.datetime_.replace(microsecond=0)
    assert decoded.datetime_created == refund.datetime_created.replace(microsecond=0)
    assert decoded.account == refund.account
    assert decoded.refunded_transaction.uuid == transaction.uuid
    assert decoded.payee == refund.payee
    assert decoded.category_amount_pairs == refund.category_amount_pairs
    assert decoded.tag_amount_pairs == refund.tag_amount_pairs


@given(transaction=security_transactions())
def test_security_transaction(transaction: SecurityTransaction) -> None:
    serialized = json.dumps(transaction, cls=CustomJSONEncoder)
    transaction.cash_account.remove_transaction(transaction)
    transaction.security_account.remove_transaction(transaction)
    decoded = json.loads(serialized, cls=CustomJSONDecoder)
    decoded = SecurityTransaction.deserialize(
        decoded,
        {
            transaction.cash_account.path: transaction.cash_account,
            transaction.security_account.path: transaction.security_account,
        },
        {transaction.currency.code: transaction.currency},
        {transaction.security.name: transaction.security},
    )
    assert isinstance(decoded, SecurityTransaction)
    assert decoded.uuid == transaction.uuid
    assert decoded.description == transaction.description
    assert decoded.datetime_ == transaction.datetime_.replace(microsecond=0).astimezone(
        decoded.datetime_.tzinfo
    )
    assert decoded.datetime_created == transaction.datetime_created.replace(
        microsecond=0
    )
    assert decoded.type_ == transaction.type_
    assert decoded.security == transaction.security
    assert decoded.amount_per_share == transaction.amount_per_share
    assert decoded.cash_account == transaction.cash_account
    assert decoded.security_account == transaction.security_account


@given(transaction=security_transfers())
def test_security_transfer(transaction: SecurityTransfer) -> None:
    serialized = json.dumps(transaction, cls=CustomJSONEncoder)
    transaction.sender.remove_transaction(transaction)
    transaction.recipient.remove_transaction(transaction)

    decoded = json.loads(serialized, cls=CustomJSONDecoder)
    decoded = SecurityTransfer.deserialize(
        decoded,
        {
            transaction.sender.path: transaction.sender,
            transaction.recipient.path: transaction.recipient,
        },
        {transaction.security.name: transaction.security},
    )
    assert isinstance(decoded, SecurityTransfer)
    assert decoded.uuid == transaction.uuid
    assert decoded.description == transaction.description
    assert decoded.datetime_ == transaction.datetime_.replace(microsecond=0)
    assert decoded.datetime_created == transaction.datetime_created.replace(
        microsecond=0
    )
    assert decoded.security == transaction.security
    assert decoded.sender == transaction.sender
    assert decoded.recipient == transaction.recipient


def test_record_keeper_transactions() -> None:
    record_keeper = RecordKeeper()
    record_keeper.add_currency("CZK", 2)
    record_keeper.add_currency("EUR", 2)
    record_keeper.add_exchange_rate("EUR", "CZK")
    record_keeper.add_security(
        "ČSOB Dynamický penzijní fond", "CSOB.DYN", "Pension Fund", "CZK", 0
    )
    record_keeper.add_account_group("Bank Accounts", None)
    record_keeper.add_cash_account("Bank Accounts/Raiffeisen", "CZK", 15000)
    record_keeper.add_cash_account("Bank Accounts/Moneta", "CZK", 0)
    record_keeper.add_security_account("ČSOB penzijní účet", None)
    record_keeper.add_security_account("ČSOB penzijní účet 2", None)
    record_keeper.add_cash_transaction(
        "chili con carne ingredients",
        datetime.now(user_settings.settings.time_zone),
        CashTransactionType.EXPENSE,
        "Bank Accounts/Raiffeisen",
        "Albert",
        [("Food/Groceries", 1000)],
        [("Split", 500)],
    )
    record_keeper.add_cash_transaction(
        "some stupid electronic device",
        datetime.now(user_settings.settings.time_zone),
        CashTransactionType.EXPENSE,
        "Bank Accounts/Raiffeisen",
        "Alza",
        [("Electronics", 10000)],
        [],
    )
    record_keeper.add_refund(
        "refunding stupid electronic device",
        datetime.now(user_settings.settings.time_zone) + timedelta(days=1),
        record_keeper.transactions[1].uuid,
        "Bank Accounts/Raiffeisen",
        "Alza",
        [("Electronics", 10000)],
        [],
    )
    record_keeper.add_cash_transfer(
        "sending money to Moneta",
        datetime.now(user_settings.settings.time_zone),
        "Bank Accounts/Raiffeisen",
        "Bank Accounts/Moneta",
        1000,
        1000,
    )
    record_keeper.add_security_transaction(
        "buying ČSOB DPS shares",
        datetime.now(user_settings.settings.time_zone),
        SecurityTransactionType.BUY,
        "ČSOB Dynamický penzijní fond",
        1000,
        "1.7",
        "ČSOB penzijní účet",
        "Bank Accounts/Raiffeisen",
    )
    record_keeper.add_security_transfer(
        "transfering DPS shares",
        datetime.now(user_settings.settings.time_zone),
        "ČSOB Dynamický penzijní fond",
        10,
        "ČSOB penzijní účet",
        "ČSOB penzijní účet 2",
    )

    serialized = record_keeper.serialize(lambda *args, **kwargs: None)  # noqa: ARG005
    serialized = json.dumps(serialized, cls=CustomJSONEncoder)
    decoded = json.loads(serialized, cls=CustomJSONDecoder)
    decoded = RecordKeeper.deserialize(
        decoded,
        lambda *args, **kwargs: None,  # noqa: ARG005
    )
    assert isinstance(decoded, RecordKeeper)
    assert decoded.currencies == record_keeper.currencies
    assert len(decoded.exchange_rates) == len(record_keeper.exchange_rates)
    assert decoded.securities == record_keeper.securities
    assert len(decoded.tags) == len(record_keeper.tags)
    assert len(decoded.payees) == len(record_keeper.payees)
    assert len(decoded.account_groups) == len(record_keeper.account_groups)
    assert len(decoded.accounts) == len(record_keeper.accounts)
    assert len(decoded.transactions) == len(record_keeper.transactions)


def test_record_keeper_transactions_invalid_datatype() -> None:
    record_keeper = RecordKeeper()
    transaction_dict = {"datatype": "invalid type!"}
    with pytest.raises(ValueError, match="Unexpected 'datatype' value."):
        record_keeper._deserialize_transactions(
            [transaction_dict],
            None,
            None,
            None,
            None,
            None,
            None,
            lambda *args, **kwargs: None,  # noqa: ARG005
        )


def test_user_settings() -> None:
    settings = UserSettings()
    serialized = json.dumps(settings, cls=CustomJSONEncoder)
    decoded = json.loads(serialized, cls=CustomJSONDecoder)
    assert isinstance(decoded, UserSettings)
    assert decoded.time_zone == settings.time_zone
    assert decoded.backup_paths == settings.backup_paths
    assert decoded.logs_max_size_bytes == settings.logs_max_size_bytes
    assert decoded.backups_max_size_bytes == settings.backups_max_size_bytes
    assert decoded.general_date_format == settings.general_date_format
    assert decoded.transaction_date_format == settings.transaction_date_format
    assert decoded.exchange_rate_decimals == settings.exchange_rate_decimals
    assert decoded.amount_per_share_decimals == settings.amount_per_share_decimals
    assert decoded.number_format == settings.number_format
    assert decoded.check_for_updates_on_startup == settings.check_for_updates_on_startup


settings_json = r"""{
  "datatype": "UserSettings",
  "time_zone": "Europe/Prague",
  "logs_max_size_bytes": 1000000,
  "backups_max_size_bytes": 100000000,
  "backup_paths": [
    "D:\\Coding\\Kapytal\\saved_data\\backups"
  ]
}"""


def test_user_settings_missing_keys() -> None:
    decoded = json.loads(settings_json, cls=CustomJSONDecoder)
    assert isinstance(decoded, UserSettings)
    assert decoded.general_date_format == "%d.%m.%Y"
    assert decoded.transaction_date_format == "%d.%m.%Y"
    assert decoded.exchange_rate_decimals == 9
    assert decoded.amount_per_share_decimals == 9
    assert decoded.number_format == NumberFormat.SEP_NONE_DECIMAL_POINT
    assert decoded.check_for_updates_on_startup is True


def test_record_keeper_with_extra_data() -> None:
    record_keeper = RecordKeeper()
    serialized = record_keeper.serialize(lambda *args, **kwargs: None)  # noqa: ARG005
    data = {
        "version": "0.0.0",
        "datetime_saved": datetime.now(user_settings.settings.time_zone),
        "data": record_keeper.serialize(lambda *args, **kwargs: None),  # noqa: ARG005
    }
    serialized = json.dumps(data, cls=CustomJSONEncoder)
    decoded = json.loads(serialized, cls=CustomJSONDecoder)
    decoded = RecordKeeper.deserialize(
        decoded["data"],
        lambda *args, **kwargs: None,  # noqa: ARG005
    )

    assert isinstance(decoded, RecordKeeper)
