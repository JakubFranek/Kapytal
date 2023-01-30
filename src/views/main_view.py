import os

from PyQt6.QtCore import QDir, pyqtSignal
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QMainWindow, QMessageBox

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

    # IDEA: place this in some utility module?
    def display_error(
        self,
        text: str,
        exc_details: str,
        critical: bool = False,
        title: str = "Error!",
    ) -> None:
        message_box = QMessageBox()
        if critical is True:
            message_box.setIcon(QMessageBox.Icon.Critical)
            message_box.setWindowIcon(QIcon("icons_24:cross.png"))
        else:
            message_box.setIcon(QMessageBox.Icon.Warning)
            message_box.setWindowIcon(QIcon("icons_24:exclamation.png"))
        message_box.setWindowTitle(title)
        message_box.setText(text)
        message_box.setDetailedText(exc_details)
        message_box.exec()
