import logging

from src.utilities.general import get_exception_display_info
from src.views.utilities.handle_exception import display_error_message


def handle_exception(exception: Exception) -> None:
    """Log exception and display its info via QMessageBox"""

    logging.error(
        "Handling exception:",
        exc_info=(type(exception), exception, exception.__traceback__),
    )
    display_text, display_details = get_exception_display_info(exception)
    display_error_message(display_text, display_details, log=False)
