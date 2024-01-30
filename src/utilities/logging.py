import logging
from datetime import datetime
from pathlib import Path

from src.models.user_settings import user_settings
from src.utilities import constants
from src.utilities.general import contains_timestamp, get_datetime_from_file_path


class MyFormatter(logging.Formatter):
    converter = datetime.fromtimestamp

    def formatTime(  # noqa: N802
        self, record: logging.LogRecord, datefmt: str | None = None
    ) -> str:
        dt: datetime = self.converter(record.created)
        if datefmt:
            return dt.strftime(datefmt)
        dt_as_str = dt.strftime("%Y-%m-%d %H:%M:%S")
        return "%s.%03d" % (dt_as_str, record.msecs)


class DuplicateFilter(logging.Filter):
    """Ignores subsequent identical logs, if time interval < 100 ms."""

    DELAY_US = 100_000

    def __init__(self, formatter: logging.Formatter, name: str = "") -> None:
        super().__init__(name)
        self.formatter = formatter

    def filter(self, record: logging.LogRecord) -> bool:
        self.formatter.format(record)
        current_log = (record.module, record.levelno, record.msg)
        current_dt = datetime.strptime(  # noqa: DTZ007
            record.asctime, "%Y-%m-%d %H:%M:%S.%f"
        )

        if current_log != getattr(self, "last_log", None):
            # New record
            self.last_log = current_log
            self.last_dt = current_dt
            return True

        # Same record
        if hasattr(self, "last_dt"):
            time_delta = current_dt - self.last_dt
            if time_delta.microseconds > DuplicateFilter.DELAY_US:
                # Same record with at least 100 ms interval
                self.last_log = current_log
                self.last_dt = current_dt
                return True
        return False


def setup_logging() -> None:
    constants.logs_path.mkdir(exist_ok=True, parents=True)

    dt_now = datetime.now(user_settings.settings.time_zone)
    filename_debug = constants.logs_path / (
        "debug_" + dt_now.strftime(constants.TIMESTAMP_FORMAT) + ".log"
    )
    formatter = MyFormatter(
        fmt=("%(asctime)s %(levelname)-8s {%(module)s} [%(funcName)s] %(message)s"),
        datefmt="%Y-%m-%d %H:%M:%S.%f",
    )

    handler_debug = logging.FileHandler(
        filename=filename_debug, mode="w+", encoding="utf-8"
    )
    handler_debug.setLevel(logging.DEBUG)

    handler_debug.setFormatter(formatter)

    root_logger = logging.getLogger()  # this is the root logger
    logging.getLogger("yfinance").disabled = True
    logging.getLogger("urllib3.connectionpool").disabled = True
    root_logger.addFilter(DuplicateFilter(formatter))
    root_logger.setLevel(logging.DEBUG)
    root_logger.addHandler(handler_debug)
    logging.logThreads = False
    logging.logProcesses = False
    logging.logMultiprocessing = False
    logging.debug(f"Kapytal v{constants.VERSION}: logging setup complete")


def remove_old_logs() -> None:
    size_limit = user_settings.settings.logs_max_size_bytes

    while True:
        # Keep deleting logs until size limit is reached or all old logs are deleted

        logs_number = len(_get_log_paths(constants.logs_path))
        logs_size = _get_directory_size(constants.logs_path)

        if logs_number <= 1 and logs_size >= size_limit:
            logging.warning(
                f"All old logs deleted, size limit of {size_limit:,} bytes "
                "could not be reached, continuing"
            )
            return

        if logs_size <= size_limit:
            logging.debug(
                f"Logs size limit satisfied ({logs_size:,}/{size_limit:,} bytes)"
            )
            return

        _remove_oldest_log(constants.logs_path)


def _remove_oldest_log(directory: Path) -> None:
    log_paths = _get_log_paths(directory)
    oldest_log = min(log_paths, key=get_datetime_from_file_path)
    logging.info(f"Removing log: {oldest_log}")
    oldest_log.unlink()


def _get_log_paths(directory: Path) -> list[Path]:
    return [
        file_path
        for file_path in directory.iterdir()
        if file_path.is_file()
        and file_path.suffix == ".log"
        and contains_timestamp(file_path)
    ]


def _get_directory_size(path: Path) -> int:
    return sum(f.stat().st_size for f in path.glob("**/*") if f.is_file())
