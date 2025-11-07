import json
from datetime import datetime, timedelta

import pytest
from hypothesis import given
from hypothesis import strategies as st
from src.models.json.custom_json_decoder import CustomJSONDecoder
from src.models.json.custom_json_encoder import CustomJSONEncoder
from src.models.model_objects.attributes import (
    Attribute,
    AttributeType,
    CategoryType,
)
from src.models.model_objects.cash_objects import (
    CashTransactionType,
)
from src.models.model_objects.currency_objects import Currency
from src.models.model_objects.security_objects import (
    SecurityTransactionType,
)
from src.models.record_keeper import RecordKeeper
from src.models.user_settings import user_settings
from src.models.user_settings.user_settings_class import NumberFormat, UserSettings
from tests.models.test_assets.composites import (
    attributes,
)
from tests.utilities.constants import IBANS_VALID


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
    record_keeper.add_cash_account(
        "Cash Accounts/CZK Account", "CZK", 0, IBANS_VALID[0]
    )
    record_keeper.add_cash_account(
        "Cash Accounts/EUR Account", "EUR", 0, IBANS_VALID[1]
    )
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


def test_record_keeper_transactions() -> None:
    record_keeper = RecordKeeper()
    record_keeper.add_currency("CZK", 2)
    record_keeper.add_currency("EUR", 2)
    record_keeper.add_exchange_rate("EUR", "CZK")
    record_keeper.add_security(
        "ČSOB Dynamický penzijní fond", "CSOB.DYN", "Pension Fund", "CZK", 0
    )
    record_keeper.add_account_group("Bank Accounts", None)
    record_keeper.add_cash_account(
        "Bank Accounts/Raiffeisen", "CZK", 15000, IBANS_VALID[0]
    )
    record_keeper.add_cash_account("Bank Accounts/Moneta", "CZK", 0, IBANS_VALID[1])
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
