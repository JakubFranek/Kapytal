import logging
import shutil
import sys
import traceback
from datetime import datetime
from decimal import Decimal
from pathlib import Path
from types import TracebackType

import src.models.user_settings.user_settings as user_settings
import src.utilities.constants as constants


def backup_json_file(file_path: Path) -> None:
    dt_now = datetime.now(user_settings.settings.time_zone)
    size_limit = user_settings.settings.backups_max_size_bytes

    backup_name = (
        file_path.stem + "_" + dt_now.strftime(constants.TIMESTAMP_FORMAT) + ".json"
    )

    for backup_directory in user_settings.settings.backup_paths:
        backup_directory.mkdir(exist_ok=True, parents=True)
        backup_directory_readme = backup_directory / "README.md"
        if not backup_directory_readme.exists():
            readme_path = constants.backups_folder_path / "README.md"
            shutil.copyfile(readme_path, backup_directory_readme)

        backup_path = backup_directory / backup_name
        shutil.copyfile(file_path, backup_path)
        logging.info(f"Backed up {file_path} to {backup_path}")

        while True:
            # Keep deleting backups until size limit is satisfied

            old_backup_paths = [
                file_path
                for file_path in backup_directory.iterdir()
                if file_path.is_file()
                and file_path.suffix == ".json"
                and contains_timestamp(file_path)
            ]
            total_size = sum(f.stat().st_size for f in old_backup_paths if f.is_file())

            if len(old_backup_paths) == 1 and total_size > size_limit:
                logging.warning(
                    f"Only the latest backup is left, size limit of "
                    f"{size_limit:,} bytes could not be reached: {backup_directory}"
                )
                break

            if total_size <= size_limit:
                logging.debug(
                    f"Backup size limit satisfied ({total_size:,} / "
                    f"{size_limit:,} bytes): {backup_directory}"
                )
                break

            if total_size > size_limit:
                oldest_backup = min(old_backup_paths, key=get_datetime_from_file_path)
                logging.info(f"Removing oldest backup: {oldest_backup}")
                oldest_backup.unlink()


def contains_timestamp(path: Path) -> bool:
    """Return True if the Path contains a '%Y_%m_%d_%Hh%Mm%Ss' timestamp
    at the end of its stem."""

    stem = path.stem
    timestamp = stem[-len(constants.TIMESTAMP_EXAMPLE) :]  # noqa: E203
    try:
        datetime.strptime(timestamp, constants.TIMESTAMP_FORMAT)  # noqa: DTZ007
        return True
    except ValueError:
        return False


def get_datetime_from_file_path(path: Path) -> datetime:
    """Return datetime from a Path containing a '%Y_%m_%d_%Hh%Mm%Ss' timestamp
    at the end of the stem."""

    stem = path.stem
    timestamp = stem[-len(constants.TIMESTAMP_EXAMPLE) :]  # noqa: E203
    return datetime.strptime(timestamp, constants.TIMESTAMP_FORMAT).replace(
        tzinfo=user_settings.settings.time_zone
    )


def get_exception_display_info() -> tuple[str, str] | None:
    exc_type, exc_value, exc_traceback = sys.exc_info()

    if exc_type is not None and exc_value is not None and exc_traceback is not None:
        # Ignore KeyboardInterrupt (special case)
        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return None

        filename, line, exc_details = get_exception_info(
            exc_type, exc_value, exc_traceback
        )

        error = "%s: %s" % (exc_type.__name__, exc_value)
        display_text = f"""<html>The following error has occured:<br/>
            <b>{error}</b><br/><br/>
            It occurred at <b>line {line}</b> of file <b>{filename}</b>.<br/></html>"""

        logging.error(
            "Handled exception", exc_info=(exc_type, exc_value, exc_traceback)
        )

        return display_text, exc_details
    return None


def get_exception_info(
    exc_type: type[BaseException],
    exc_value: BaseException,
    exc_traceback: TracebackType,
) -> tuple[str, str, str,]:
    stack_summary = traceback.extract_tb(exc_traceback)
    file_name, line, _, _ = stack_summary.pop()
    exc_details_list = traceback.format_exception(exc_type, exc_value, exc_traceback)
    exc_details = "".join(exc_details_list)
    file_name = Path(file_name).name

    return file_name, line, exc_details


def normalize_decimal_to_min_places(value: Decimal, min_places: int) -> Decimal:
    """Returns a Decimal which has at least 'min_places' decimal places,
    but has no trailing zeroes beyond that limit."""

    normalized = value.normalize()
    _, _, exponent = normalized.as_tuple()
    if isinstance(exponent, int) and -exponent < min_places:
        return normalized.quantize(Decimal(f"1e-{min_places}"))
    return normalized
