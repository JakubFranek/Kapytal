import logging

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QCloseEvent, QIcon
from PyQt6.QtWidgets import QWidget

from src.views.ui_files.Ui_payee_form import Ui_PayeeForm


class PayeeForm(QWidget, Ui_PayeeForm):
    signal_add_payee = pyqtSignal()
    signal_rename_payee = pyqtSignal()
    signal_remove_payee = pyqtSignal()
    signal_select_payee = pyqtSignal()

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent=parent)
        self.setupUi(self)
        self.setWindowFlag(Qt.WindowType.Window)
        self.setWindowIcon(QIcon("icons_16:user-silhouette.png"))

        self.addButton.clicked.connect(self.signal_add_payee.emit)
        self.removeButton.clicked.connect(self.signal_remove_payee.emit)
        self.renameButton.clicked.connect(self.signal_rename_payee.emit)
        self.selectButton.clicked.connect(self.signal_select_payee.emit)

    def show_form(self) -> None:
        logging.debug(f"Showing {self.__class__.__name__}")
        self.show()

    def closeEvent(self, a0: QCloseEvent) -> None:
        logging.debug(f"Closing {self.__class__.__name__}")
        return super().closeEvent(a0)
