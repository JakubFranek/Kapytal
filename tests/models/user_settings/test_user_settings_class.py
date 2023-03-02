import shutil
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo, available_timezones

import pytest
from hypothesis import given
from hypothesis import strategies as st
from tzlocal import get_localzone_name

from src.models.user_settings.user_settings_class import UserSettings
from tests.models.test_assets.composites import everything_except

available_time_zone_keys = tuple(available_timezones())


def test_user_settings_default_settings() -> None:
    settings = UserSettings()

    assert settings.__repr__() == "UserSettings"
    assert settings.time_zone == ZoneInfo(get_localzone_name())
    assert settings.backup_paths == ()
    assert settings.logs_max_size_bytes == 1_000_000
    assert settings.backups_max_size_bytes == 10_000_000


@given(time_zone_key=st.sampled_from(available_time_zone_keys))
def test_user_settings_time_zone(time_zone_key: str) -> None:
    settings = UserSettings()
    tz = ZoneInfo(time_zone_key)
    settings.time_zone = tz

    assert settings.time_zone == tz

    settings.time_zone = tz

    assert settings.time_zone == tz


@given(time_zone=everything_except(ZoneInfo))
def test_user_settings_time_zone_invalid_type(time_zone: Any) -> None:
    settings = UserSettings()
    with pytest.raises(TypeError, match="ZoneInfo"):
        settings.time_zone = time_zone


@given(max_size=st.integers(min_value=0))
def test_user_settings_logs_max_size_bytes(max_size: int) -> None:
    settings = UserSettings()
    settings.logs_max_size_bytes = max_size

    assert settings.logs_max_size_bytes == max_size

    settings.logs_max_size_bytes = max_size

    assert settings.logs_max_size_bytes == max_size


@given(max_size=everything_except(int))
def test_user_settings_logs_max_size_bytes_invalid_type(max_size: Any) -> None:
    settings = UserSettings()
    with pytest.raises(TypeError, match="int"):
        settings.logs_max_size_bytes = max_size


@given(max_size=st.integers(max_value=-1))
def test_user_settings_logs_max_size_bytes_invalid_value(max_size: int) -> None:
    settings = UserSettings()
    with pytest.raises(ValueError, match="positive"):
        settings.logs_max_size_bytes = max_size


@given(max_size=st.integers(min_value=0))
def test_user_settings_backups_max_size_bytes(max_size: int) -> None:
    settings = UserSettings()
    settings.backups_max_size_bytes = max_size

    assert settings.backups_max_size_bytes == max_size

    settings.backups_max_size_bytes = max_size

    assert settings.backups_max_size_bytes == max_size


@given(max_size=everything_except(int))
def test_user_settings_backups_max_size_bytes_invalid_type(max_size: Any) -> None:
    settings = UserSettings()
    with pytest.raises(TypeError, match="int"):
        settings.backups_max_size_bytes = max_size


@given(max_size=st.integers(max_value=-1))
def test_user_settings_backups_max_size_bytes_invalid_value(max_size: int) -> None:
    settings = UserSettings()
    with pytest.raises(ValueError, match="positive"):
        settings.backups_max_size_bytes = max_size


def test_user_settings_backup_paths() -> None:
    this_dir = Path(__file__).resolve().parent
    test_dir = this_dir / "Test Directory"
    test_dir.mkdir()
    test_dir_A = test_dir / "A"
    test_dir_B = test_dir / "B"
    test_dir_C = test_dir / "C"
    test_dir_D = test_dir / "D"
    test_dir_A.mkdir()
    test_dir_B.mkdir()
    test_dir_C.mkdir()
    test_dir_D.mkdir()

    paths = [test_dir_A, test_dir_B, test_dir_C]
    settings = UserSettings()
    settings.backup_paths = paths

    assert settings.backup_paths == tuple(paths)

    paths = [test_dir_B, test_dir_C, test_dir_D]
    settings.backup_paths = paths

    assert settings.backup_paths == tuple(paths)

    shutil.rmtree(test_dir)


@given(paths=st.lists(everything_except(Path), min_size=1, max_size=5))
def test_user_settings_backup_paths_invalid_type(paths: Any) -> None:
    settings = UserSettings()
    with pytest.raises(TypeError, match="Path"):
        settings.backup_paths = paths


def test_user_settings_backup_paths_duplicates() -> None:
    this_dir = Path(__file__).resolve().parent
    test_dir = this_dir / "Test Directory"
    test_dir.mkdir()
    test_dir_A = test_dir / "A"
    test_dir_A.mkdir()

    paths = [test_dir_A, test_dir_A]
    settings = UserSettings()
    with pytest.raises(ValueError, match="duplicate"):
        settings.backup_paths = paths

    shutil.rmtree(test_dir)


def test_user_settings_backup_paths_not_directory() -> None:
    this_file = Path(__file__).resolve()

    paths = [this_file]
    settings = UserSettings()
    with pytest.raises(ValueError, match="directory"):
        settings.backup_paths = paths
