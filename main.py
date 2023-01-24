import ctypes
import logging
import os
import sys
import traceback
from datetime import datetime
from types import TracebackType

from PyQt6.QtWidgets import QApplication

from src.models.constants import tzinfo
from src.models.record_keeper import RecordKeeper
from src.presenters.account_tree_presenter import AccountTreePresenter
from src.views.main_view import MainView


def handle_uncaught_exception(
    exc_type: type[BaseException],
    exc_value: BaseException,
    exc_traceback: TracebackType,
) -> None:
    global main_view

    # Ignore KeyboardInterrupt (special case)
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return

    stack_summary = traceback.extract_tb(exc_traceback)
    filename, line, _, _ = stack_summary.pop()
    exc_details_list = traceback.format_exception(exc_type, exc_value, exc_traceback)
    exc_details = "".join(exc_details_list)
    filename = os.path.basename(filename)
    error = "%s: %s" % (exc_type.__name__, exc_value)
    text = f"""<html>The following unexpected error has occured:<br/>
        <b>{error}</b><br/><br/>
        It occurred at <b>line {line}</b> of file <b>{filename}</b>.<br/><br/>
        The program will Quit (without saving) after closing this window.</html>"""
    logging.critical(
        "Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback)
    )
    main_view.display_error(text=text, exc_details=exc_details, critical=True)
    app.exit()


def setup_logging() -> None:
    dir_current = os.path.dirname(os.path.realpath(__file__))
    dir_logs = dir_current + r"\logs"
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


if __name__ == "__main__":

    # The following three lines are needed to make sure task bar icon works on Windows
    if os.name == "nt":
        myappid = "Jakub_Franek.Blbnicheck.v0.1"  # arbitrary string
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

    setup_logging()

    sys.excepthook = handle_uncaught_exception

    logging.info("Creating QApplication")
    app = QApplication(sys.argv)

    font = app.font()
    font.setPointSize(10)
    app.setFont(font)
    logging.info("Set QApplication font size to 10 ")

    logging.info("Creating MainWindow")
    main_view = MainView()

    logging.info("Creating RecordKeeper")
    record_keeper = RecordKeeper()
    record_keeper.add_currency("CZK", 2)
    record_keeper.add_account_group("Group A", None)
    record_keeper.add_security_account("Security Acc 1", "Group A")
    record_keeper.add_security_account("Security Acc 2", "Group A")
    record_keeper.add_account_group("Group A.A", "Group A")
    record_keeper.add_security_account("Security Acc 3", "Group A/Group A.A")
    record_keeper.add_cash_account(
        "Cash Acc 1", "CZK", 0, datetime.now(tzinfo), "Group A/Group A.A"
    )
    record_keeper.add_account_group("Group B", None)
    record_keeper.add_security_account("Security Acc 4", "Group B")

    logging.info("Creating AccountsTreePresenter")
    presenter = AccountTreePresenter(main_view, record_keeper)

    logging.info("Executing QApplication")
    app.exec()
