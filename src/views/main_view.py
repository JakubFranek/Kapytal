import os

from PyQt6.QtCore import QDir
from PyQt6.QtGui import QIcon
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

        # Stopping AccountTree stretching
        # self.splitter.setStretchFactor(0, 0)
        # self.splitter.setStretchFactor(1, 1)

        self.actionExpand_All.setIcon(QIcon("icons_16:arrow-out.png"))
        self.actionCollapse_All.setIcon(QIcon("icons_16:arrow-in.png"))

        self.actionExpand_All.triggered.connect(self.accountsTree.expandAll)
        self.actionCollapse_All.triggered.connect(self.accountsTree.collapseAll)

        self.toolButton_expandAll.setDefaultAction(self.actionExpand_All)
        self.toolButton_collapseAll.setDefaultAction(self.actionCollapse_All)

    def finalize_setup(self) -> None:
        self.accountsTree.header().setSectionResizeMode(
            AccountTreeColumns.COLUMN_NAME.value,
            QHeaderView.ResizeMode.ResizeToContents,
        )
        self.accountsTree.header().setSectionResizeMode(
            AccountTreeColumns.COLUMN_BALANCE.value,
            QHeaderView.ResizeMode.ResizeToContents,
        )
        self.accountsTree.header().setSectionResizeMode(
            AccountTreeColumns.COLUMN_BALANCE_BASE.value,
            QHeaderView.ResizeMode.ResizeToContents,
        )
        self.accountsTree.header().setSectionResizeMode(
            AccountTreeColumns.COLUMN_SHOW.value,
            QHeaderView.ResizeMode.ResizeToContents,
        )
