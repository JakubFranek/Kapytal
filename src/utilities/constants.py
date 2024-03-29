from pathlib import Path

# Literal constants
VERSION = "1.0.0"

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
