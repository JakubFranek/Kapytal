from pathlib import Path

# Literal constants
VERSION = "1.2.1"

GITHUB_URL = "https://github.com/JakubFranek/Kapytal"
GITHUB_API_URL = "https://api.github.com/repos/JakubFranek/Kapytal"
GITHUB_DOCS_URL = "https://github.com/JakubFranek/Kapytal/blob/master/docs/index.md"

TIMESTAMP_FORMAT = "%Y_%m_%d_%Hh%Mm%Ss"
TIMESTAMP_EXAMPLE = "YYYY_mm_DD_HHhMMmSSs"

SETTINGS_SUFFIX = "saved_data/user_settings.json"
RECENT_FILES_SUFFIX = "saved_data/recent_files.json"
BACKUPS_FOLDER_SUFFIX = "saved_data/backups"
LOGS_FOLDER_SUFFIX = "logs"

DEMO_BASIC_FILE_SUFFIX = "saved_data/demo_basic.json"
DEMO_MORTGAGE_FILE_SUFFIX = "saved_data/demo_mortgage.json"
TEMPLATE_CATEGORY_EN_FILE_SUFFIX = "saved_data/template_category_en.json"
TEMPLATE_CATEGORY_CZ_FILE_SUFFIX = "saved_data/template_category_cz.json"

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
backups_folder_path: Path
logs_folder_path: Path
logs_path: Path
demo_basic_file_path: Path
demo_mortgage_file_path: Path
template_category_en_file_path: Path
template_category_cz_file_path: Path


def set_app_root_path(path: Path) -> None:
    global app_root_path  # noqa: PLW0603
    global settings_path  # noqa: PLW0603
    global recent_files_path  # noqa: PLW0603
    global backups_folder_path  # noqa: PLW0603
    global logs_folder_path  # noqa: PLW0603
    global logs_path  # noqa: PLW0603
    global demo_basic_file_path  # noqa: PLW0603
    global demo_mortgage_file_path  # noqa: PLW0603
    global template_category_en_file_path  # noqa: PLW0603
    global template_category_cz_file_path  # noqa: PLW0603

    app_root_path = path
    settings_path = app_root_path / SETTINGS_SUFFIX
    recent_files_path = app_root_path / RECENT_FILES_SUFFIX
    backups_folder_path = app_root_path / BACKUPS_FOLDER_SUFFIX
    logs_folder_path = app_root_path / LOGS_FOLDER_SUFFIX
    logs_path = app_root_path / LOGS_FOLDER_SUFFIX
    demo_basic_file_path = app_root_path / DEMO_BASIC_FILE_SUFFIX
    demo_mortgage_file_path = app_root_path / DEMO_MORTGAGE_FILE_SUFFIX
    template_category_en_file_path = app_root_path / TEMPLATE_CATEGORY_EN_FILE_SUFFIX
    template_category_cz_file_path = app_root_path / TEMPLATE_CATEGORY_CZ_FILE_SUFFIX
