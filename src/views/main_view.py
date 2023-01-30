import os

from PyQt6.QtCore import QDir, pyqtSignal
from PyQt6.QtWidgets import QMainWindow

from src.views.account_tree import AccountTree
from src.views.ui_files.Ui_main_window import Ui_MainWindow


class MainView(QMainWindow, Ui_MainWindow):

    signal_open_currency_form = pyqtSignal()

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
        self.account_tree = AccountTree(self)
        self.verticalLayoutTree.addWidget(self.account_tree)

        self.actionCurrencies_and_Exchange_Rates.triggered.connect(
            self.signal_open_currency_form.emit
        )

        self.toolButton_expandAll.setDefaultAction(self.account_tree.actionExpand_All)
        self.toolButton_collapseAll.setDefaultAction(
            self.account_tree.actionCollapse_All
        )
