import logging
import os
from datetime import datetime

from src.models.constants import tzinfo


class DuplicateFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:  # noqa: A003
        current_log = (record.module, record.levelno, record.msg)
        if current_log != getattr(self, "last_log", None):
            self.last_log = current_log
            return True
        return False


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
    logger.addFilter(DuplicateFilter())
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
