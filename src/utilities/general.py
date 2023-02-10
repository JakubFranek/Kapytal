import logging
import os
import shutil
import sys
import traceback
from datetime import datetime
from decimal import Decimal
from types import TracebackType

from src.models.constants import tzinfo


def backup_json_file(file_path: str, backup_directories: list[str]) -> None:
    dt_now = datetime.now(tzinfo)
    file_name = os.path.basename(file_path).removesuffix(".json")
    backup_name = (
        file_name + "_backup_" + dt_now.strftime("%Y_%m_%d_%Hh%Mm%Ss") + ".json"
    )
    for backup_directory in backup_directories:
        if not os.path.exists(backup_directory):
            os.makedirs(backup_directory)

        backup_path = os.path.join(backup_directory, backup_name)
        shutil.copyfile(file_path, backup_path)
        logging.info(f"Backed up {file_path} to {backup_path}")

        listdir = os.listdir(backup_directory)
        old_backup_paths = [
            os.path.join(backup_directory, file_name)
            for file_name in listdir
            if os.path.isfile(os.path.join(backup_directory, file_name))
            and file_name != "README.md"
        ]
        no_of_backups = len(old_backup_paths)
        _ = sum(os.path.getsize(backup) for backup in old_backup_paths)  # size in bytes
        if no_of_backups > 10:  # NOTE: will be determined by size in release
            oldest_backup = min(old_backup_paths, key=os.path.getctime)
            logging.info(f"Removing oldest backup: {oldest_backup}")
            os.remove(oldest_backup)


def setup_logging(root_directory: str) -> None:
    dir_logs_info = root_directory + r"\logs\info"
    dir_logs_debug = root_directory + r"\logs\debug"
    if not os.path.exists(dir_logs_info):
        os.makedirs(dir_logs_info)
    if not os.path.exists(dir_logs_debug):
        os.makedirs(dir_logs_debug)

    dt_now = datetime.now(tzinfo)
    filename_info = (
        dir_logs_info + r"\info_" + dt_now.strftime("%Y_%m_%d_%Hh%Mm%Ss") + ".log"
    )
    filename_debug = (
        dir_logs_debug + r"\debug_" + dt_now.strftime("%Y_%m_%d_%Hh%Mm%Ss") + ".log"
    )
    formatter = logging.Formatter(
        fmt=(
            "%(asctime)s.%(msecs)03d %(levelname)-8s "
            "{%(module)s} [%(funcName)s] %(message)s"
        ),
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    handler_info = logging.FileHandler(
        filename=filename_info, mode="w+", encoding="utf-8"
    )
    handler_info.setLevel(logging.INFO)
    handler_debug = logging.FileHandler(
        filename=filename_debug, mode="w+", encoding="utf-8"
    )
    handler_debug.setLevel(logging.DEBUG)

    handler_debug.setFormatter(formatter)
    handler_info.setFormatter(formatter)

    logger = logging.getLogger()  # this is the root logger
    logger.setLevel(logging.DEBUG)
    logger.addHandler(handler_debug)
    logger.addHandler(handler_info)
    logging.debug("Logging setup complete")

    _remove_old_logs(dir_logs_info)
    _remove_old_logs(dir_logs_debug)


def _remove_old_logs(directory: str) -> None:
    while True:
        listdir = os.listdir(directory)
        log_paths = [
            os.path.join(directory, file_name)
            for file_name in listdir
            if os.path.isfile(os.path.join(directory, file_name))
            and file_name != "README.md"
        ]
        _ = sum(os.path.getsize(log) for log in log_paths)  # size in bytes
        if len(log_paths) > 10:  # NOTE: will be determined by size in release
            oldest_log = min(log_paths, key=os.path.getctime)
            logging.info(f"Removing log: {oldest_log}")
            os.remove(oldest_log)
        else:
            break


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
    filename, line, _, _ = stack_summary.pop()
    exc_details_list = traceback.format_exception(exc_type, exc_value, exc_traceback)
    exc_details = "".join(exc_details_list)
    filename = os.path.basename(filename)

    return filename, line, exc_details


def normalize_decimal_to_min_places(value: Decimal, min_places: int) -> Decimal:
    """Returns a Decimal which has at least 'min_places' decimal places,
    but has no trailing zeroes beyond that limit."""

    normalized = value.normalize()
    _, _, exponent = normalized.as_tuple()
    if isinstance(exponent, int) and -exponent < min_places:
        return normalized.quantize(Decimal(f"1e-{min_places}"))
    return normalized
