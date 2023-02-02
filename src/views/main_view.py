import os

from PyQt6.QtCore import QDir, pyqtSignal
from PyQt6.QtGui import QCloseEvent, QIcon
from PyQt6.QtWidgets import QApplication, QFileDialog, QMainWindow, QMessageBox

from src.views.account_tree import AccountTree
from src.views.ui_files.Ui_main_window import Ui_MainWindow


class MainView(QMainWindow, Ui_MainWindow):
    signal_exit = pyqtSignal()
    signal_open_currency_form = pyqtSignal()
    signal_save = pyqtSignal()
    signal_save_as = pyqtSignal()
    signal_open = pyqtSignal()

    def __init__(self) -> None:
        super().__init__()
        self.initial_setup()

    def get_save_path(self) -> str:
        return QFileDialog.getSaveFileName(self, filter="JSON file (*.json)")[0]

    def get_open_path(self) -> str:
        return QFileDialog.getOpenFileName(self, filter="JSON file (*.json)")[0]

    def ask_save_before_close(self) -> bool | None:
        reply = QMessageBox.question(
            self,
            "Save changes before quitting?",
            (
                "Unsaved changes have been made.\n"
                "Do you want to save them before quitting?"
            ),
            (
                QMessageBox.StandardButton.Yes
                | QMessageBox.StandardButton.No
                | QMessageBox.StandardButton.Cancel
            ),
            QMessageBox.StandardButton.Cancel,
        )
        if reply == QMessageBox.StandardButton.Yes:
            return True
        if reply == QMessageBox.StandardButton.No:
            return False
        return None

    def set_save_status(
        self, current_file_path: str | None, unsaved_changes: bool
    ) -> None:
        if unsaved_changes is True:
            self.actionSave.setIcon(QIcon("icons_16:disk--exclamation.png"))
            star_str = "*"
        else:
            self.actionSave.setIcon(QIcon("icons_16:disk.png"))
            star_str = ""

        app = QApplication.instance()
        version = app.applicationVersion()

        if current_file_path is None:
            self.actionSave.setEnabled(False)
            self.setWindowTitle(f"Kapytal v{version}")
        else:
            self.actionSave.setEnabled(True)
            self.setWindowTitle(f"Kapytal v{version} - " + current_file_path + star_str)

    def closeEvent(self, event: QCloseEvent) -> None:
        self.signal_exit.emit()
        event.ignore()

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

        self.actionOpen_File.setIcon(QIcon("icons_16:folder-open-document.png"))
        self.actionSave.setIcon(QIcon("icons_16:disk.png"))
        self.actionSave_As.setIcon(QIcon("icons_16:disks.png"))
        self.actionCurrencies_and_Exchange_Rates.setIcon(QIcon("icons_16:currency.png"))

        self.actionCurrencies_and_Exchange_Rates.triggered.connect(
            self.signal_open_currency_form.emit
        )
        self.actionSave.triggered.connect(self.signal_save.emit)
        self.actionSave_As.triggered.connect(self.signal_save_as.emit)
        self.actionOpen_File.triggered.connect(self.signal_open.emit)

        self.toolButton_expandAll.setDefaultAction(self.account_tree.actionExpand_All)
        self.toolButton_collapseAll.setDefaultAction(
            self.account_tree.actionCollapse_All
        )
