import shutil
from collections.abc import Sequence
from pathlib import Path
from typing import Any

import pytest
from hypothesis import assume, given
from hypothesis import strategies as st
from src.models.user_settings.user_settings_class import (
    NumberFormat,
    UserSettings,
    _get_number_format_for_locale,
    get_locale_code_for_number_format,
)
from src.views.constants import TransactionTableColumn
from tests.models.test_assets.composites import everything_except
from tzlocal import get_localzone_name
from zoneinfo import ZoneInfo, available_timezones

available_time_zone_keys = tuple(available_timezones())


def test_default_settings() -> None:
    settings = UserSettings()

    assert settings.__repr__() == "UserSettings"
    assert settings.time_zone == ZoneInfo(get_localzone_name())
    assert settings.backup_paths == ()
    assert settings.logs_max_size_bytes == UserSettings.LOGS_DEFAULT_MAX_SIZE
    assert settings.backups_max_size_bytes == UserSettings.BACKUPS_DEFAULT_MAX_SIZE
    assert settings.general_date_format == "%d.%m.%Y"
    assert settings.transaction_date_format == "%d.%m.%Y"
    assert settings.exchange_rate_decimals == 9
    assert settings.amount_per_share_decimals == 9


@given(time_zone_key=st.sampled_from(available_time_zone_keys))
def test_time_zone(time_zone_key: str) -> None:
    settings = UserSettings()
    tz = ZoneInfo(time_zone_key)
    settings.time_zone = tz

    assert settings.time_zone == tz

    settings.time_zone = tz

    assert settings.time_zone == tz


@given(time_zone=everything_except(ZoneInfo))
def test_time_zone_invalid_type(time_zone: Any) -> None:
    settings = UserSettings()
    with pytest.raises(TypeError, match="ZoneInfo"):
        settings.time_zone = time_zone


@given(max_size=st.integers(min_value=0))
def test_logs_max_size_bytes(max_size: int) -> None:
    settings = UserSettings()
    settings.logs_max_size_bytes = max_size

    assert settings.logs_max_size_bytes == max_size

    settings.logs_max_size_bytes = max_size

    assert settings.logs_max_size_bytes == max_size


@given(max_size=everything_except(int))
def test_logs_max_size_bytes_invalid_type(max_size: Any) -> None:
    settings = UserSettings()
    with pytest.raises(TypeError, match="int"):
        settings.logs_max_size_bytes = max_size


@given(max_size=st.integers(max_value=-1))
def test_logs_max_size_bytes_invalid_value(max_size: int) -> None:
    settings = UserSettings()
    with pytest.raises(ValueError, match="positive"):
        settings.logs_max_size_bytes = max_size


@given(max_size=st.integers(min_value=0))
def test_backups_max_size_bytes(max_size: int) -> None:
    settings = UserSettings()
    settings.backups_max_size_bytes = max_size

    assert settings.backups_max_size_bytes == max_size

    settings.backups_max_size_bytes = max_size

    assert settings.backups_max_size_bytes == max_size


@given(max_size=everything_except(int))
def test_backups_max_size_bytes_invalid_type(max_size: Any) -> None:
    settings = UserSettings()
    with pytest.raises(TypeError, match="int"):
        settings.backups_max_size_bytes = max_size


@given(max_size=st.integers(max_value=-1))
def test_backups_max_size_bytes_invalid_value(max_size: int) -> None:
    settings = UserSettings()
    with pytest.raises(ValueError, match="positive"):
        settings.backups_max_size_bytes = max_size


def test_backup_paths() -> None:
    this_dir = Path(__file__).resolve().parent
    test_dir = this_dir / "Test Directory"
    test_dir.mkdir()
    test_dir_a = test_dir / "A"
    test_dir_b = test_dir / "B"
    test_dir_c = test_dir / "C"
    test_dir_d = test_dir / "D"
    test_dir_a.mkdir()
    test_dir_b.mkdir()
    test_dir_c.mkdir()
    test_dir_d.mkdir()

    paths = [test_dir_a, test_dir_b, test_dir_c]
    settings = UserSettings()
    settings.backup_paths = paths

    assert settings.backup_paths == tuple(paths)

    paths = [test_dir_b, test_dir_c, test_dir_d]
    settings.backup_paths = paths

    assert settings.backup_paths == tuple(paths)

    shutil.rmtree(test_dir)


@given(paths=st.lists(everything_except(Path), min_size=1, max_size=5))
def test_backup_paths_invalid_type(paths: Any) -> None:
    settings = UserSettings()
    with pytest.raises(TypeError, match="Path"):
        settings.backup_paths = paths


def test_backup_paths_duplicates() -> None:
    this_dir = Path(__file__).resolve().parent
    test_dir = this_dir / "Test Directory"
    test_dir.mkdir()
    test_dir_a = test_dir / "A"
    test_dir_a.mkdir()

    paths = [test_dir_a, test_dir_a]
    settings = UserSettings()
    with pytest.raises(ValueError, match="duplicate"):
        settings.backup_paths = paths

    shutil.rmtree(test_dir)


def test_backup_paths_not_directory() -> None:
    this_file = Path(__file__).resolve()

    paths = [this_file]
    settings = UserSettings()
    with pytest.raises(ValueError, match="directory"):
        settings.backup_paths = paths


def test_transaction_date_format() -> None:
    settings = UserSettings()
    settings.transaction_date_format = "%Y-%m-%d"
    assert settings.transaction_date_format == "%Y-%m-%d"
    settings.transaction_date_format = "%Y-%m-%d"
    assert settings.transaction_date_format == "%Y-%m-%d"


@given(format_=everything_except(str))
def test_transaction_date_format_invalid_type(format_: Any) -> None:
    settings = UserSettings()
    with pytest.raises(TypeError, match="str"):
        settings.transaction_date_format = format_


def test_transaction_date_format_invalid_value() -> None:
    settings = UserSettings()
    with pytest.raises(ValueError, match="valid format"):
        settings.transaction_date_format = "%"


def test_general_date_format() -> None:
    settings = UserSettings()
    settings.general_date_format = "%Y-%m-%d"
    assert settings.general_date_format == "%Y-%m-%d"
    settings.general_date_format = "%Y-%m-%d"
    assert settings.general_date_format == "%Y-%m-%d"


@given(format_=everything_except(str))
def test_general_date_format_invalid_type(format_: Any) -> None:
    settings = UserSettings()
    with pytest.raises(TypeError, match="str"):
        settings.general_date_format = format_


def test_general_date_format_invalid_value() -> None:
    settings = UserSettings()
    with pytest.raises(ValueError, match="valid format"):
        settings.general_date_format = "%"


@given(decimals=st.integers(min_value=0, max_value=18))
def test_exchange_rate_decimals(decimals: int) -> None:
    settings = UserSettings()
    settings.exchange_rate_decimals = decimals
    assert settings.exchange_rate_decimals == decimals
    settings.exchange_rate_decimals = decimals
    assert settings.exchange_rate_decimals == decimals


@given(decimals=everything_except(int))
def test_exchange_rate_decimals_invalid_type(decimals: Any) -> None:
    settings = UserSettings()
    with pytest.raises(TypeError, match="integer"):
        settings.exchange_rate_decimals = decimals


@given(decimals=st.integers(max_value=-1))
def test_exchange_rate_decimals_negative_value(decimals: int) -> None:
    settings = UserSettings()
    with pytest.raises(ValueError, match="between"):
        settings.exchange_rate_decimals = decimals


@given(decimals=st.integers(min_value=19))
def test_exchange_rate_decimals_large_value(decimals: int) -> None:
    settings = UserSettings()
    with pytest.raises(ValueError, match="between"):
        settings.exchange_rate_decimals = decimals


@given(decimals=st.integers(min_value=0, max_value=18))
def test_amount_per_share_decimals(decimals: int) -> None:
    settings = UserSettings()
    settings.amount_per_share_decimals = decimals
    assert settings.amount_per_share_decimals == decimals
    settings.amount_per_share_decimals = decimals
    assert settings.amount_per_share_decimals == decimals


@given(decimals=everything_except(int))
def test_amount_per_share_decimals_invalid_type(decimals: Any) -> None:
    settings = UserSettings()
    with pytest.raises(TypeError, match="integer"):
        settings.amount_per_share_decimals = decimals


@given(decimals=st.integers(max_value=-1))
def test_amount_per_share_decimals_negative_value(decimals: int) -> None:
    settings = UserSettings()
    with pytest.raises(ValueError, match="between"):
        settings.amount_per_share_decimals = decimals


@given(decimals=st.integers(min_value=19))
def test_amount_per_share_decimals_large_value(decimals: int) -> None:
    settings = UserSettings()
    with pytest.raises(ValueError, match="between"):
        settings.amount_per_share_decimals = decimals


@given(check=st.sampled_from([True, False]))
def test_check_for_updates_on_startup(check: bool) -> None:
    settings = UserSettings()
    assert settings.check_for_updates_on_startup is True
    settings.check_for_updates_on_startup = check
    assert settings.check_for_updates_on_startup == check


@given(check=everything_except(bool))
def test_check_for_updates_on_startup_invalid_type(check: Any) -> None:
    settings = UserSettings()
    with pytest.raises(TypeError, match="bool"):
        settings.check_for_updates_on_startup = check


@given(
    columns=st.lists(
        st.sampled_from(TransactionTableColumn),
        unique=True,
        min_size=len(TransactionTableColumn),
        max_size=len(TransactionTableColumn),
    ),
)
def test_transaction_table_column_order(columns: list[TransactionTableColumn]) -> None:
    settings = UserSettings()
    assert settings.transaction_table_column_order == ()
    settings.transaction_table_column_order = columns
    assert settings.transaction_table_column_order == tuple(columns)
    settings.transaction_table_column_order = columns
    assert settings.transaction_table_column_order == tuple(columns)


@given(columns=everything_except(Sequence))
def test_transaction_table_column_order_invalid_type(columns: Any) -> None:
    settings = UserSettings()
    with pytest.raises(TypeError, match="Sequence"):
        settings.transaction_table_column_order = columns


def test_transaction_table_column_order_invalid_member_type() -> None:
    settings = UserSettings()
    columns = [True, (), {}, 1.0]
    with pytest.raises(TypeError, match="TransactionTableColumn"):
        settings.transaction_table_column_order = columns


@given(
    columns=st.lists(
        st.sampled_from(TransactionTableColumn),
        unique=False,
        min_size=len(TransactionTableColumn),
        max_size=len(TransactionTableColumn),
    )
)
def test_transaction_table_column_order_duplicates(
    columns: list[TransactionTableColumn],
) -> None:
    assume(len(columns) != len(set(columns)))
    settings = UserSettings()
    with pytest.raises(ValueError, match="duplicate"):
        settings.transaction_table_column_order = columns


@given(
    columns=st.lists(st.sampled_from(TransactionTableColumn), unique=True, min_size=1)
)
def test_transaction_table_column_order_invalid_length(
    columns: list[TransactionTableColumn],
) -> None:
    assume(len(columns) != len(TransactionTableColumn))
    settings = UserSettings()
    with pytest.raises(ValueError, match="exactly"):
        settings.transaction_table_column_order = columns


@given(format_=st.sampled_from(NumberFormat))
def test_number_format(format_: NumberFormat) -> None:
    settings = UserSettings()
    settings.number_format = format_
    assert settings.number_format == format_
    settings.number_format = format_
    assert settings.number_format == format_


@given(format_=everything_except(NumberFormat))
def test_number_format_invalid_type(format_: Any) -> None:
    settings = UserSettings()
    with pytest.raises(TypeError, match="NumberFormat"):
        settings.number_format = format_


locale_data_set = {
    "en_US": NumberFormat.SEP_COMMA_DECIMAL_POINT,
    "cs_CZ": NumberFormat.SEP_SPACE_DECIMAL_COMMA,
    "xh_ZA": NumberFormat.SEP_SPACE_DECIMAL_POINT,
    "nl_NL": NumberFormat.SEP_POINT_DECIMAL_COMMA,
    "C": NumberFormat.SEP_NONE_DECIMAL_POINT,
}


@pytest.mark.parametrize("test_data", locale_data_set.items())
def test_get_number_format_for_locale(test_data: tuple[str, NumberFormat]) -> None:
    import locale

    locale.setlocale(locale.LC_NUMERIC, test_data[0])
    assert _get_number_format_for_locale() == test_data[1]


def test_get_number_format_for_locale_no_locale_set() -> None:
    assert _get_number_format_for_locale() == NumberFormat.SEP_NONE_DECIMAL_POINT


def test_get_number_format_for_locale_unsupported() -> None:
    import locale

    locale.setlocale(locale.LC_NUMERIC, "fa_IR")
    assert _get_number_format_for_locale() == NumberFormat.SEP_NONE_DECIMAL_POINT


@pytest.mark.parametrize("test_data", locale_data_set.items())
def test_get_locale_code_for_number_format(test_data: tuple[str, NumberFormat]) -> None:
    assert get_locale_code_for_number_format(test_data[1]) == test_data[0]


@given(format_=everything_except(NumberFormat))
def test_get_locale_code_for_number_format_invalid_value(format_: Any) -> None:
    with pytest.raises(ValueError, match="Unknown number format"):
        get_locale_code_for_number_format(format_)
