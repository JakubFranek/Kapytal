import os
import sys
from pathlib import Path


# Helper function to get XDG directories
def _get_xdg_dir(env_var: str, default: str) -> Path:
    """Get XDG directory with fallback to default."""
    path_str = os.getenv(env_var)
    if path_str:
        return Path(path_str)
    return Path(default).expanduser()


# Literal constants
APP_NAME = "Kapytal"
VERSION = "1.2.2"

GITHUB_URL = "https://github.com/JakubFranek/Kapytal"
GITHUB_API_URL = "https://api.github.com/repos/JakubFranek/Kapytal"
GITHUB_DOCS_URL = "https://github.com/JakubFranek/Kapytal/blob/master/docs/index.md"

TIMESTAMP_FORMAT = "%Y_%m_%d_%Hh%Mm%Ss"
TIMESTAMP_EXAMPLE = "YYYY_mm_DD_HHhMMmSSs"

WINDOWS_SAVED_DATA_FOLDER_NAME = "saved_data"

# XDG Base Directory paths (Linux)
LINUX_CONFIG_FOLDER_PATH = _get_xdg_dir("XDG_CONFIG_HOME", "~/.config")
LINUX_DATA_FOLDER_PATH = _get_xdg_dir("XDG_DATA_HOME", "~/.local/share")
LINUX_STATE_FOLDER_PATH = _get_xdg_dir("XDG_STATE_HOME", "~/.local/state")

SETTINGS_FILE_NAME = "user_settings.json"
RECENT_FILES_FILE_NAME = "recent_files.json"
BACKUPS_FOLDER_NAME = "backups"
LOGS_FOLDER_NAME = "logs"

DEMO_BASIC_FILE_NAME = "demo_basic.json"
DEMO_MORTGAGE_FILE_NAME = "demo_mortgage.json"
TEMPLATE_CATEGORY_EN_FILE_NAME = "template_category_en.json"
TEMPLATE_CATEGORY_CZ_FILE_NAME = "template_category_cz.json"

PASSWORD_MIN_LENGTH = 8

IBAN_LENGTHS = {  # from https://gist.github.com/dkdndes/578c579a86f7a19c646d5db9a4f9a845
    "AL": 28,
    "AD": 24,
    "AT": 20,
    "AZ": 28,
    "BH": 22,
    "BY": 28,
    "BE": 16,
    "BA": 20,
    "BR": 29,
    "BG": 22,
    "CR": 22,
    "HR": 21,
    "CY": 28,
    "CZ": 24,
    "DK": 18,
    "DO": 28,
    "EG": 29,
    "SV": 28,
    "EE": 20,
    "FO": 18,
    "FI": 18,
    "FR": 27,
    "GE": 22,
    "DE": 22,
    "GI": 23,
    "GR": 27,
    "GL": 18,
    "GT": 28,
    "VA": 22,
    "HU": 28,
    "IS": 26,
    "IQ": 23,
    "IE": 22,
    "IL": 23,
    "IT": 27,
    "JO": 30,
    "KZ": 20,
    "XK": 20,
    "KW": 30,
    "LV": 21,
    "LB": 28,
    "LY": 25,
    "LI": 21,
    "LT": 20,
    "LU": 20,
    "MT": 31,
    "MR": 27,
    "MU": 30,
    "MD": 24,
    "MC": 27,
    "ME": 22,
    "NL": 18,
    "MK": 19,
    "NO": 15,
    "PK": 24,
    "PS": 29,
    "PL": 28,
    "PT": 25,
    "QA": 29,
    "RO": 24,
    "LC": 32,
    "SM": 27,
    "ST": 25,
    "SA": 24,
    "RS": 22,
    "SC": 31,
    "SK": 24,
    "SI": 19,
    "ES": 24,
    "SD": 18,
    "SE": 24,
    "CH": 21,
    "TL": 23,
    "TN": 24,
    "TR": 26,
    "UA": 29,
    "AE": 23,
    "GB": 22,
    "VG": 24,
}

# Runtime constants
app_root_path: Path
settings_path: Path
recent_files_path: Path
backups_directory: Path
logs_directory: Path
demo_basic_file_path: Path
demo_mortgage_file_path: Path
template_category_en_file_path: Path
template_category_cz_file_path: Path


def set_app_root_path(path: Path) -> None:
    global app_root_path  # noqa: PLW0603
    global settings_path  # noqa: PLW0603
    global recent_files_path  # noqa: PLW0603
    global backups_directory  # noqa: PLW0603
    global logs_directory  # noqa: PLW0603
    global demo_basic_file_path  # noqa: PLW0603
    global demo_mortgage_file_path  # noqa: PLW0603
    global template_category_en_file_path  # noqa: PLW0603
    global template_category_cz_file_path  # noqa: PLW0603

    app_root_path = path

    if sys.platform == "win32":
        saved_data_dir = app_root_path / WINDOWS_SAVED_DATA_FOLDER_NAME

        backups_directory = saved_data_dir / BACKUPS_FOLDER_NAME
        logs_directory = app_root_path / LOGS_FOLDER_NAME

        settings_path = saved_data_dir / SETTINGS_FILE_NAME
        recent_files_path = saved_data_dir / RECENT_FILES_FILE_NAME
        demo_basic_file_path = saved_data_dir / DEMO_BASIC_FILE_NAME
        demo_mortgage_file_path = saved_data_dir / DEMO_MORTGAGE_FILE_NAME
        template_category_en_file_path = saved_data_dir / TEMPLATE_CATEGORY_EN_FILE_NAME
        template_category_cz_file_path = saved_data_dir / TEMPLATE_CATEGORY_CZ_FILE_NAME
    else:
        settings_path = LINUX_CONFIG_FOLDER_PATH / APP_NAME / SETTINGS_FILE_NAME
        logs_directory = LINUX_STATE_FOLDER_PATH / APP_NAME / LOGS_FOLDER_NAME

        data_dir = LINUX_DATA_FOLDER_PATH / APP_NAME

        backups_directory = data_dir / BACKUPS_FOLDER_NAME
        recent_files_path = data_dir / RECENT_FILES_FILE_NAME
        demo_basic_file_path = data_dir / DEMO_BASIC_FILE_NAME
        demo_mortgage_file_path = data_dir / DEMO_MORTGAGE_FILE_NAME
        template_category_en_file_path = data_dir / TEMPLATE_CATEGORY_EN_FILE_NAME
        template_category_cz_file_path = data_dir / TEMPLATE_CATEGORY_CZ_FILE_NAME
