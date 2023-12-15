import logging
import webbrowser

import packaging.version
import requests
from PyQt6.QtWidgets import QApplication
from src.utilities import constants
from src.views.dialogs.busy_dialog import create_simple_busy_indicator
from src.views.main_view import MainView
from src.views.utilities.handle_exception import display_error_message
from src.views.utilities.message_box_functions import ask_yes_no_question, show_info_box

API_STATUS_SUCCESS = 200


class UpdatePresenter:
    def __init__(self, view: MainView) -> None:
        self._view = view

    def check_for_updates(self, *, silent: bool, timeout: int = 5) -> None:
        self._busy_dialog = create_simple_busy_indicator(
            self._view, "Checking for updates, please wait..."
        )
        self._busy_dialog.open()
        QApplication.processEvents()
        try:
            self._check_for_updates(silent=silent, timeout=timeout)
        except:  # noqa: TRY302
            raise
        finally:
            self._busy_dialog.close()

    def _check_for_updates(self, *, silent: bool, timeout: int = 5) -> None:
        logging.debug(f"Checking for updates: {silent=}")
        try:
            response = requests.get(
                constants.GITHUB_API_URL + "/releases",
                timeout=timeout,
            )
        except requests.exceptions.Timeout:
            logging.warning("Timeout while checking for updates")
            if not silent:
                display_error_message(
                    text=(
                        "Timeout while checking for updates. Please make sure you "
                        "have an internet connection and try again."
                    ),
                    title="No response from GitHub",
                )
            return
        except ConnectionError:
            logging.warning("Connection error while checking for updates")
            if not silent:
                display_error_message(
                    text=(
                        "Connection error occured while checking for updates. Please "
                        "make sure you have an internet connection and try again."
                    ),
                    title="No response from GitHub",
                )
            return

        response_json = response.json()
        if response.status_code != API_STATUS_SUCCESS:
            logging.warning(f"Unexpected response from GitHub: {response.status_code}")
            if not silent:
                display_error_message(
                    text=(
                        "Unexpected response from GitHub. Please make sure you have an "
                        "internet connection and try again."
                    ),
                    exc_details=response.text,
                    title="No response from GitHub",
                )
            return

        latest_release_name = response_json[0]["name"]
        latest_version = packaging.version.parse(
            latest_release_name[1:]  # ignore first letter 'v'
        )
        current_version = packaging.version.parse(constants.VERSION)
        if latest_version > current_version:
            logging.info(f"New version available: {latest_release_name}")
            if not ask_yes_no_question(
                parent=self._view,
                question=(
                    f"Current version: v{constants.VERSION}\n"
                    f"Latest version: {latest_release_name}\n\n"
                    "Open latest release in internet browser?"
                ),
                title="New version available",
            ):
                logging.info("User rejected opening latest release web page")
                return

            logging.info("User accepted opening latest release web page")
            webbrowser.open(response_json[0]["html_url"])
        elif not silent:
            show_info_box(
                parent=self._view,
                title="Up to date",
                text=(
                    "No updates available. "
                    f"Kapytal v{constants.VERSION} is the latest release."
                ),
            )
