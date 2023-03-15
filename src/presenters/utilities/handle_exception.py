from src.utilities.general import get_exception_display_info
from src.views.utilities.handle_exception import display_error_message


def handle_exception() -> None:
    """Get and display exception info via QMessageBox"""
    display_text, display_details = get_exception_display_info()
    display_error_message(display_text, display_details)
