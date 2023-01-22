import os

from PyQt6.QtCore import QDir
from PyQt6.QtWidgets import QHeaderView, QMainWindow

from src.views.constants import AccountTreeColumns
from src.views.ui_files.Ui_mainwindow import Ui_MainWindow

# TODO: set up error display


class MainView(QMainWindow, Ui_MainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.initial_setup()

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

    def finalize_setup(self) -> None:
        self.accountsTree.header().setSectionResizeMode(
            AccountTreeColumns.COLUMN_NAME, QHeaderView.ResizeMode.Stretch
        )
        self.accountsTree.header().setSectionResizeMode(
            AccountTreeColumns.COLUMN_BALANCE, QHeaderView.ResizeMode.ResizeToContents
        )
        self.accountsTree.header().setSectionResizeMode(
            AccountTreeColumns.COLUMN_BALANCE_BASE,
            QHeaderView.ResizeMode.ResizeToContents,
        )
        self.accountsTree.header().setSectionResizeMode(
            AccountTreeColumns.COLUMN_SHOW, QHeaderView.ResizeMode.ResizeToContents
        )
