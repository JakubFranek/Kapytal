import ctypes
import logging
import os
import sys
from pathlib import Path

from PyQt6.QtWidgets import QApplication

import src.models.user_settings.user_settings as user_settings
from src.models.json.custom_json_decoder import CustomJSONDecoder
from src.models.json.custom_json_encoder import CustomJSONEncoder
from src.presenters.main_presenter import MainPresenter
from src.utilities.logging import remove_old_logs, setup_logging
from src.views.main_view import MainView
from src.views.utilities.handle_exception import handle_uncaught_exception

VERSION = "0.0.0"
SETTINGS_PATH_SUFFIX = "saved_data/user_settings.json"
BACKUPS_PATH_SUFFIX = "saved_data/backups"

if __name__ == "__main__":
    # The following three lines are needed to make sure task bar icon works on Windows
    if os.name == "nt":
        myappid = f"Jakub_Franek.Kapytal.v{VERSION}"  # arbitrary string
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

    sys.excepthook = handle_uncaught_exception

    app_root_path = Path(__file__).resolve().parent  # get Kapytal root path

    setup_logging(app_root_path)

    user_settings.set_path(app_root_path / SETTINGS_PATH_SUFFIX)
    user_settings.set_json_decoder(CustomJSONDecoder)
    user_settings.set_json_encoder(CustomJSONEncoder)
    if Path(app_root_path / SETTINGS_PATH_SUFFIX).exists():
        user_settings.load()
    else:
        user_settings.settings.backup_paths = [
            Path(app_root_path / BACKUPS_PATH_SUFFIX)
        ]
        user_settings.save()

    remove_old_logs()  # remove logs once settings are initialized

    logging.debug("Creating QApplication")
    app = QApplication(sys.argv)
    app.setApplicationName("Kapytal")
    app.setApplicationVersion(VERSION)

    logging.debug("Setting QApplication font size to 10 pts")
    font = app.font()
    font.setPointSize(10)
    app.setFont(font)

    logging.debug("Creating MainWindow")
    main_view = MainView()

    logging.debug("Creating MainPresenter")
    main_presenter = MainPresenter(main_view, app, app_root_path)

    logging.info("Executing QApplication, awaiting user input")
    app.exec()
