import logging
import shutil
import sys
import traceback
from collections.abc import Collection
from datetime import datetime
from pathlib import Path
from types import TracebackType
from typing import Protocol, Self, TypeVar

from src.models.user_settings import user_settings
from src.utilities import constants


def backup_json_file(file_path: Path) -> None:
    dt_now = datetime.now(user_settings.settings.time_zone)
    size_limit = user_settings.settings.backups_max_size_bytes

    if file_path.name.endswith(".json.enc"):
        file_suffix = ".json.enc"
    elif file_path.name.endswith(".json"):
        file_suffix = ".json"
    else:
        raise ValueError(f"File {file_path} does not end with .json or .json.enc")

    file_name_stem = file_path.name.removesuffix(file_suffix)

    backup_name = (
        file_name_stem + "_" + dt_now.strftime(constants.TIMESTAMP_FORMAT) + file_suffix
    )

    for backup_directory in user_settings.settings.backup_paths:
        backup_directory.mkdir(exist_ok=True, parents=True)

        backup_directory_readme = backup_directory / "README.md"
        if not backup_directory_readme.exists():
            readme_path = constants.app_root_path / "saved_data/backups/README.md"
            if readme_path.exists():
                shutil.copyfile(readme_path, backup_directory_readme)
            else:
                logging.warning(
                    f"README.md not found in neither {constants.app_root_path} "
                    f"nor {backup_directory}"
                )

        backup_path = backup_directory / backup_name
        shutil.copyfile(file_path, backup_path)
        logging.info(f"Backed up {file_path} to {backup_path}")

        while True:
            # Keep deleting backups until size limit is satisfied

            old_backup_paths = [
                file_path
                for file_path in backup_directory.iterdir()
                if file_path.is_file()
                and "".join(file_path.suffixes) in {".json", ".json.enc"}
                and contains_timestamp(file_path, file_suffix)
            ]
            total_size = sum(f.stat().st_size for f in old_backup_paths if f.is_file())

            if len(old_backup_paths) == 1 and total_size > size_limit:
                logging.warning(
                    f"Only the latest backup is left, size limit of "
                    f"{size_limit} bytes could not be reached: {backup_directory}"
                )
                break

            if total_size <= size_limit:
                logging.debug(
                    f"Backup size limit satisfied ({total_size} / "
                    f"{size_limit} bytes): {backup_directory}"
                )
                break

            if total_size > size_limit:
                oldest_backup = min(old_backup_paths, key=get_datetime_from_file_path)
                logging.info(f"Removing oldest backup: {oldest_backup}")
                oldest_backup.unlink()


def contains_timestamp(path: Path, suffix: str) -> bool:
    """Return True if the Path contains a '%Y_%m_%d_%Hh%Mm%Ss' timestamp
    at the end of its stem."""

    stem = str(path).removesuffix(suffix)
    timestamp = stem[-len(constants.TIMESTAMP_EXAMPLE) :]
    try:
        datetime.strptime(timestamp, constants.TIMESTAMP_FORMAT)  # noqa: DTZ007
    except ValueError:
        return False
    else:
        return True


def get_datetime_from_file_path(path: Path) -> datetime:
    """Return datetime from a Path containing a '%Y_%m_%d_%Hh%Mm%Ss' timestamp
    at the end of the stem."""

    if path.name.endswith(".json.enc"):
        suffix = ".json.enc"
    elif path.name.endswith(".json"):
        suffix = ".json"
    else:
        raise ValueError(f"File {path} does not end with .json or .json.enc")

    stem = str(path).removesuffix(suffix)
    timestamp = stem[-len(constants.TIMESTAMP_EXAMPLE) :]
    return datetime.strptime(timestamp, constants.TIMESTAMP_FORMAT).replace(
        tzinfo=user_settings.settings.time_zone
    )


def get_exception_display_info(exception: Exception) -> tuple[str, str] | None:
    exc_traceback = exception.__traceback__
    exc_type = type(exception)
    exc_value = exception

    if exc_traceback is None:
        raise ValueError("Exception traceback is None.")

    # Ignore KeyboardInterrupt (special case)
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return None

    filename, line, exc_details = get_exception_info(exc_type, exc_value, exc_traceback)

    error = f"{exc_type.__name__}: {exc_value}"
    display_text = f"""<html>The following error has occured:<br/>
        <b>{error}</b><br/><br/>
        It occurred at <b>line {line}</b> of file <b>{filename}</b>.<br/></html>"""

    return display_text, exc_details


def get_exception_info(
    exc_type: type[BaseException],
    exc_value: BaseException,
    exc_traceback: TracebackType,
) -> tuple[
    str,
    str,
    str,
]:
    stack_summary = traceback.extract_tb(exc_traceback)
    file_name, line, _, _ = stack_summary.pop()
    exc_details_list = traceback.format_exception(exc_type, exc_value, exc_traceback)
    exc_details = "".join(exc_details_list)
    file_name = Path(file_name).name

    return file_name, line, exc_details


class TreeItem(Protocol):
    @property
    def children(self) -> Collection[Self]: ...

    @property
    def parent(self) -> Self | None: ...


TreeItemType = TypeVar("TreeItemType", bound=TreeItem)


def flatten_tree(root_items: Collection[TreeItemType]) -> list[TreeItemType]:
    """Flattens any tree, as long as the root items have a children property."""
    flat_stats: list[TreeItemType] = []
    for stats in root_items:
        flat_stats.append(stats)
        if len(stats.children) > 0:
            flat_stats = flat_stats + flatten_tree(stats.children)
    return flat_stats
