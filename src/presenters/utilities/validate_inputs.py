import logging
from datetime import datetime

from PyQt6.QtWidgets import QWidget
from src.models.user_settings import user_settings
from src.views.utilities.message_box_functions import ask_yes_no_question


def validate_datetime(datetime_: datetime, parent: QWidget) -> bool:
    """If the datetime is in the future, ask the user if they want to proceed."""
    date_now = datetime.now(tz=user_settings.settings.time_zone).date()
    if date_now < datetime_.date():
        logging.warning(
            f"Entered date is in the future ({date_now}), "
            "asking user whether to proceed"
        )
        answer = ask_yes_no_question(
            parent=parent,
            question="The entered date is in the future. Proceed anyway?",
            title="Are you sure?",
        )
        logging.info(f"User answer: proceed={answer}")
        return answer
    return True
