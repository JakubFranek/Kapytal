import logging
import os
import sys
import traceback
from datetime import datetime
from types import TracebackType

from src.models.constants import tzinfo


def setup_logging(root_directory: str) -> None:
    dir_logs = root_directory + r"\logs"
    if not os.path.exists(dir_logs):
        os.makedirs(dir_logs)

    listdir = os.listdir(dir_logs)
    logs_paths = [
        os.path.join(dir_logs, log)
        for log in listdir
        if os.path.isfile(os.path.join(dir_logs, log))
    ]
    no_of_logs = len(logs_paths)
    _ = sum(os.path.getsize(log) for log in logs_paths)  # size in bytes
    if no_of_logs > 10:  # TODO: will be determined by size in release
        oldest_log = min(logs_paths, key=os.path.getctime)
        os.remove(oldest_log)

    start_dt = datetime.now(tzinfo)
    file_name = dir_logs + r"\debug_" + start_dt.strftime("%Y_%m_%d_%Hh%Mm%Ss") + ".log"
    log_format = (
        "%(asctime)s.%(msecs)03d %(levelname)s {%(module)s} [%(funcName)s] %(message)s"
    )
    logging.basicConfig(
        filename=file_name,
        level=logging.DEBUG,
        datefmt="%Y-%m-%d %H:%M:%S",
        format=log_format,
        filemode="w+",
        encoding="utf-8",
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

        logging.warning(
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
