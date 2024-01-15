import ctypes
import logging
import os
import sys
from pathlib import Path

from PyQt6.QtWidgets import QApplication, QStyleFactory
from src.models.json.custom_json_decoder import CustomJSONDecoder
from src.models.json.custom_json_encoder import CustomJSONEncoder
from src.models.user_settings import user_settings
from src.presenters.main_presenter import MainPresenter
from src.utilities import constants
from src.utilities.logging import remove_old_logs, setup_logging
from src.views import colors
from src.views.main_view import MainView
from src.views.utilities.handle_exception import handle_uncaught_exception


def main() -> None:
    # The following three lines are needed to make sure task bar icon works on Windows
    if os.name == "nt":
        myappid = f"Jakub_Franek.Kapytal.v{constants.VERSION}"  # arbitrary string
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

    sys.excepthook = handle_uncaught_exception

    app_root_path = Path(__file__).resolve().parent  # get Kapytal root path
    constants.set_app_root_path(app_root_path)

    setup_logging()

    user_settings.set_json_decoder(CustomJSONDecoder)
    user_settings.set_json_encoder(CustomJSONEncoder)
    if constants.settings_path.exists():
        user_settings.load()
    else:
        Path.mkdir(constants.backups_folder_path, parents=True, exist_ok=True)
        user_settings.settings.backup_paths = [constants.backups_folder_path]
        user_settings.save()

    remove_old_logs()  # remove logs once settings are initialized

    logging.debug("Creating QApplication")
    app = QApplication(sys.argv)
    app.setApplicationName("Kapytal")
    app.setApplicationVersion(constants.VERSION)

    logging.debug("Setting QApplication font size to 10 pts")
    app.setStyleSheet("QWidget{font-size: 10pt;}")

    logging.debug("Setting Fusion style")
    app.setStyle(QStyleFactory.create("Fusion"))

    color_scheme = app.styleHints().colorScheme()
    colors.color_scheme = color_scheme
    logging.debug(f"QApplication color scheme: '{color_scheme.name}'")

    logging.debug("Creating MainWindow")
    main_view = MainView()

    logging.debug("Creating MainPresenter")
    main_presenter = MainPresenter(main_view, app)

    logging.debug("Showing MainView")
    main_view.showMaximized()

    app.processEvents()  # draw MainView so WelcomeDialog can be properly centered

    if user_settings.settings.check_for_updates_on_startup:
        logging.debug("Checking for updates")
        main_presenter.check_for_updates()

    logging.debug("Showing Welcome dialog")
    main_presenter.show_welcome_dialog()

    logging.info("Executing QApplication, awaiting user input")
    app.exec()


if __name__ == "__main__":
    main()
