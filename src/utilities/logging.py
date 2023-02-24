import logging
import os
from datetime import datetime
from pathlib import Path

import src.models.user_settings.user_settings as user_settings

dir_logs_info = None
dir_logs_debug = None


class DuplicateFilter(logging.Filter):
    """Ignores subsequent identical logs."""

    def filter(self, record: logging.LogRecord) -> bool:  # noqa: A003
        current_log = (record.module, record.levelno, record.msg)
        if current_log != getattr(self, "last_log", None):
            self.last_log = current_log
            return True
        return False


def setup_logging(root_directory: Path) -> None:
    global dir_logs_info
    global dir_logs_debug

    dir_logs_info = root_directory / "logs/info"
    dir_logs_debug = root_directory / "logs/debug"
    dir_logs_info.mkdir(exist_ok=True, parents=True)
    dir_logs_debug.mkdir(exist_ok=True, parents=True)

    dt_now = datetime.now(user_settings.settings.time_zone)
    filename_info = dir_logs_info / (
        "info_" + dt_now.strftime("%Y_%m_%d_%Hh%Mm%Ss") + ".log"
    )
    filename_debug = dir_logs_debug / (
        "debug_" + dt_now.strftime("%Y_%m_%d_%Hh%Mm%Ss") + ".log"
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
        # Keep deleting logs until size limit is reached or all old logs are deleted

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

        logs_info_size = _get_directory_size(dir_logs_info)
        logs_debug_size = _get_directory_size(dir_logs_debug)
        total_size = logs_info_size + logs_debug_size

        if logs_info_number <= 1 and total_size >= size_limit:
            logging.warning(
                f"All old logs deleted, size limit of {size_limit:,} bytes "
                "could not be reached, continuing"
            )
            return

        if total_size <= size_limit:
            logging.debug(
                f"Logs size limit satisfied ({total_size:,} / {size_limit:,} bytes)"
            )
            return

        _remove_oldest_log(dir_logs_info)
        _remove_oldest_log(dir_logs_debug)


def _remove_oldest_log(directory: Path) -> None:
    log_paths = _get_log_paths(directory)
    oldest_log = min(log_paths, key=os.path.getctime)
    logging.info(f"Removing log: '{oldest_log}'")
    oldest_log.unlink()


def _get_log_paths(directory: Path) -> list[Path]:
    return [
        file_path
        for file_path in directory.iterdir()
        if file_path.is_file() and file_path.name != "README.md"
    ]


def _get_directory_size(path: Path) -> int:
    return sum(f.stat().st_size for f in path.glob("**/*") if f.is_file())
