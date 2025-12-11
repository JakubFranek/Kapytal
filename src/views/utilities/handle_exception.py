import logging
import sys
from types import TracebackType

from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QApplication, QMessageBox
from src.utilities.general import get_exception_info


def handle_uncaught_exception(
    exc_type: type[BaseException],
    exc_value: BaseException,
    exc_traceback: TracebackType,
) -> None:
    # Ignore KeyboardInterrupt (special case)
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return

    filename, line, exc_details = get_exception_info(exc_type, exc_value, exc_traceback)

    error = f"{exc_type.__name__}: {exc_value}"
    text = f"""<html>The following unexpected error has occured:<br/>
        <b>{error}</b><br/><br/>
        It occurred at <b>line {line}</b> of file <b>{filename}</b>.<br/><br/>
        The program will Quit (without saving) after closing this window.</html>"""
    logging.critical(
        "Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback)
    )

    # BUG: this sometimes does not quit the app!
    display_error_message(text=text, exc_details=exc_details, critical=True)
    app = QApplication.instance()
    sys.exit(app.quit())  # app.quit or exit?


def display_error_message(
    text: str,
    exc_details: str = "",
    *,
    critical: bool = False,
    title: str = "Error",
    log: bool = True,
) -> None:
    message_box = QMessageBox()
    if critical is True:
        message_box.setIcon(QMessageBox.Icon.Critical)
        message_box.setWindowIcon(
            QIcon(QMessageBox.standardIcon(QMessageBox.Icon.Critical))
        )
    else:
        message_box.setIcon(QMessageBox.Icon.Warning)
        message_box.setWindowIcon(
            QIcon(QMessageBox.standardIcon(QMessageBox.Icon.Warning))
        )
    message_box.setWindowTitle(title)
    message_box.setText(text)
    if exc_details:
        message_box.setDetailedText(exc_details)

    if log:
        logging.warning(f"Displaying {title}: {text}")

    message_box.exec()
