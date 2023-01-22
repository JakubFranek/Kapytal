import os

from PyQt6.QtCore import QDir
from PyQt6.QtWidgets import QMainWindow

from src.views.ui_files.Ui_mainwindow import Ui_MainWindow

# TODO: set up AccountTree column resizing policy
# TODO: set up error display
# TODO: set up icons


class MainView(QMainWindow, Ui_MainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.initial_setup()

        # TODO: this will be moved to MainPresenter or something
        self.show()

    def initial_setup(self) -> None:
        QDir.addSearchPath(
            "icons_24",
            os.path.join(QDir.currentPath(), "resources/icons/icons-24"),
        )
        QDir.addSearchPath(
            "icons_16",
            os.path.join(QDir.currentPath(), "resources/icons/icons-16"),
        )
        QDir.addSearchPath(
            "icons_custom",
            os.path.join(QDir.currentPath(), "resources/icons/icons-custom"),
        )

        self.setupUi(self)
