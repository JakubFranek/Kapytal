import logging
import os
from datetime import datetime

import src.models.user_settings.user_settings as user_settings
from src.models.constants import tzinfo

dir_logs_info = ""
dir_logs_debug = ""


class DuplicateFilter(logging.Filter):
    """Ignores subsequent identical logs."""

    def filter(self, record: logging.LogRecord) -> bool:  # noqa: A003
        current_log = (record.module, record.levelno, record.msg)
        if current_log != getattr(self, "last_log", None):
            self.last_log = current_log
            return True
        return False


def setup_logging(root_directory: str) -> None:
    global dir_logs_info
    global dir_logs_debug

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
    logger.addFilter(DuplicateFilter())
    logger.setLevel(logging.DEBUG)
    logger.addHandler(handler_debug)
    logger.addHandler(handler_info)
    logging.debug("Logging setup complete")


def remove_old_logs() -> None:
    size_limit = user_settings.settings.logs_max_size_bytes

    while True:
        # Keep deleting logs until size limit is reached or all logs are deleted

        while True:
            # Ensure there is the same number of INFO and DEBUG logs

            logs_info_number = len(_get_log_paths(dir_logs_info))
            logs_debug_number = len(_get_log_paths(dir_logs_debug))

            if logs_info_number == logs_debug_number:
                break

            logging.warning(
                "Log number mismatch: "
                f"{logs_info_number} info logs != {logs_debug_number} debug logs"
            )
            if logs_info_number > logs_debug_number:
                _remove_oldest_log(dir_logs_info)
            elif logs_info_number < logs_debug_number:
                _remove_oldest_log(dir_logs_debug)

        if logs_info_number <= 1:
            logging.warning(
                f"All old logs deleted, size limit of {size_limit:,} bytes "
                "could not be reached, continuing"
            )
            return  # only the current log is left

        logs_info_size = _get_directory_size(dir_logs_info)
        logs_debug_size = _get_directory_size(dir_logs_debug)
        total_size = logs_info_size + logs_debug_size

        if total_size <= size_limit:
            logging.debug(
                f"Logs size limit reached ({total_size:,} / {size_limit:,} bytes)"
            )
            return  # logs are within size limit

        _remove_oldest_log(dir_logs_info)
        _remove_oldest_log(dir_logs_debug)


def _remove_oldest_log(directory: str) -> None:
    log_paths = _get_log_paths(directory)
    oldest_log = min(log_paths, key=os.path.getctime)
    logging.info(f"Removing log: '{oldest_log}'")
    os.remove(oldest_log)


def _get_log_paths(directory: str) -> list[str]:
    listdir = os.listdir(directory)
    return [
        os.path.join(directory, file_name)
        for file_name in listdir
        if os.path.isfile(os.path.join(directory, file_name))
        and file_name != "README.md"
    ]


def _get_directory_size(directory_path: str) -> int:
    """Calculates directory size recursively."""

    total_size = 0
    for dir_path, _, file_names in os.walk(directory_path):
        for file_name in file_names:
            file_path = os.path.join(dir_path, file_name)
            # skip if it is symbolic link
            if not os.path.islink(file_path):
                total_size += os.path.getsize(file_path)

    return total_size
