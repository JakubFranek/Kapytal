import logging
import os
import sys
import traceback

from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QMessageBox


def get_exception_info() -> tuple[str, str] | None:
    exc_type, exc_value, exc_traceback = sys.exc_info()

    if exc_type and exc_value and exc_traceback is not None:
        # Ignore KeyboardInterrupt (special case)
        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return None

        stack_summary = traceback.extract_tb(exc_traceback)
        filename, line, _, _ = stack_summary.pop()
        exc_details_list = traceback.format_exception(
            exc_type, exc_value, exc_traceback
        )
        display_details = "".join(exc_details_list)
        filename = os.path.basename(filename)
        error = "%s: %s" % (exc_type.__name__, exc_value)

        display_text = f"""<html>The following error has occured:<br/>
            <b>{error}</b><br/><br/>
            It occurred at <b>line {line}</b> of file <b>{filename}</b>.<br/></html>"""

        logging.warning(
            "Handled exception", exc_info=(exc_type, exc_value, exc_traceback)
        )

        return display_text, display_details
    return None


def display_error_message(
    text: str,
    exc_details: str,
    critical: bool = False,
    title: str = "Error!",
) -> None:
    message_box = QMessageBox()
    if critical is True:
        message_box.setIcon(QMessageBox.Icon.Critical)
        message_box.setWindowIcon(QIcon("icons_24:cross.png"))
    else:
        message_box.setIcon(QMessageBox.Icon.Warning)
        message_box.setWindowIcon(QIcon("icons_24:exclamation.png"))
    message_box.setWindowTitle(title)
    message_box.setText(text)
    message_box.setDetailedText(exc_details)
    message_box.exec()
