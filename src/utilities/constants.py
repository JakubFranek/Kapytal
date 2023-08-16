from pathlib import Path

# Literal constants
VERSION = "0.6.0"

TIMESTAMP_FORMAT = "%Y_%m_%d_%Hh%Mm%Ss"
TIMESTAMP_EXAMPLE = "YYYY_mm_DD_HHhMMmSSs"

SETTINGS_SUFFIX = "saved_data/user_settings.json"
RECENT_FILES_SUFFIX = "saved_data/recent_files.json"
BACKUPS_FOLDER_SUFFIX = "saved_data/backups"
LOGS_FOLDER_SUFFIX = "logs"
LOGS_INFO_SUFFIX = "info"
LOGS_DEBUG_SUFFIX = "debug"

DEMO_FILE = "saved_data/demo.json"

# Runtime constants
app_root_path: Path
settings_path: Path
recent_files_path: Path
backups_folder_path: Path
logs_folder_path: Path
logs_info_path: Path
logs_debug_path: Path


def set_app_root_path(path: Path) -> None:
    global app_root_path  # noqa: PLW0603
    global settings_path  # noqa: PLW0603
    global recent_files_path  # noqa: PLW0603
    global backups_folder_path  # noqa: PLW0603
    global logs_folder_path  # noqa: PLW0603
    global logs_info_path  # noqa: PLW0603
    global logs_debug_path  # noqa: PLW0603

    app_root_path = path
    settings_path = app_root_path / SETTINGS_SUFFIX
    recent_files_path = app_root_path / RECENT_FILES_SUFFIX
    backups_folder_path = app_root_path / BACKUPS_FOLDER_SUFFIX
    logs_folder_path = app_root_path / LOGS_FOLDER_SUFFIX
    logs_info_path = app_root_path / LOGS_FOLDER_SUFFIX / LOGS_INFO_SUFFIX
    logs_debug_path = app_root_path / LOGS_FOLDER_SUFFIX / LOGS_DEBUG_SUFFIX
