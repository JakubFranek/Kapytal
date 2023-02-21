import ctypes
import logging
import os
import sys

from PyQt6.QtWidgets import QApplication

import src.models.user_settings.user_settings as user_settings
from src.presenters.main_presenter import MainPresenter
from src.utilities.logging import remove_old_logs, setup_logging
from src.views.main_view import MainView
from src.views.utilities.handle_exception import handle_uncaught_exception

VERSION = "0.0.0"
SETTINGS_PATH_SUFFIX = "/saved_data/settings.json"

if __name__ == "__main__":
    # The following three lines are needed to make sure task bar icon works on Windows
    if os.name == "nt":
        myappid = f"Jakub_Franek.Kapytal.v{VERSION}"  # arbitrary string
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

    sys.excepthook = handle_uncaught_exception

    app_root_dir = os.path.dirname(os.path.realpath(__file__))  # get Kapytal root path

    setup_logging(app_root_dir)  # setup logging

    user_settings.set_path(app_root_dir + SETTINGS_PATH_SUFFIX)
    if os.path.isfile(app_root_dir + SETTINGS_PATH_SUFFIX):
        user_settings.load()
    else:
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
    main_presenter = MainPresenter(main_view, app, app_root_dir)

    logging.info("Executing QApplication, awaiting user input")
    app.exec()
