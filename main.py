import ctypes
import logging
import os
import sys

from PyQt6.QtWidgets import QApplication

from src.presenters.main_presenter import MainPresenter
from src.utilities.logging import setup_logging
from src.views.main_view import MainView
from src.views.utilities.handle_exception import handle_uncaught_exception

VERSION = "0.0.0"

if __name__ == "__main__":
    # The following three lines are needed to make sure task bar icon works on Windows
    if os.name == "nt":
        myappid = f"Jakub_Franek.Kapytal.v{VERSION}"  # arbitrary string
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

    app_root_dir = os.path.dirname(os.path.realpath(__file__))
    setup_logging(app_root_dir)

    sys.excepthook = handle_uncaught_exception

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
