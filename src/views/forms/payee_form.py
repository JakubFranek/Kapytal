import logging

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QAction, QCloseEvent, QIcon
from PyQt6.QtWidgets import QLineEdit, QWidget

from src.views.ui_files.Ui_payee_form import Ui_PayeeForm


class PayeeForm(QWidget, Ui_PayeeForm):
    signal_add_payee = pyqtSignal()
    signal_rename_payee = pyqtSignal()
    signal_remove_payee = pyqtSignal()
    signal_select_payee = pyqtSignal()
    signal_sort_ascending = pyqtSignal()
    signal_sort_descending = pyqtSignal()
    signal_search_text_changed = pyqtSignal()

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent=parent)
        self.setupUi(self)
        self.setWindowFlag(Qt.WindowType.Window)
        self.setWindowIcon(QIcon("icons_16:user-silhouette.png"))

        self.addButton.clicked.connect(self.signal_add_payee.emit)
        self.removeButton.clicked.connect(self.signal_remove_payee.emit)
        self.renameButton.clicked.connect(self.signal_rename_payee.emit)
        self.selectButton.clicked.connect(self.signal_select_payee.emit)

        self.actionSortAscending = QAction(self)
        self.actionSortDescending = QAction(self)
        self.actionSortAscending.setIcon(QIcon("icons_16:sort-alphabet.png"))
        self.actionSortDescending.setIcon(
            QIcon("icons_16:sort-alphabet-descending.png")
        )

        self.sortAscendingButton.setDefaultAction(self.actionSortAscending)
        self.sortDescendingButton.setDefaultAction(self.actionSortDescending)

        self.actionSortAscending.triggered.connect(self.signal_sort_ascending.emit)
        self.actionSortDescending.triggered.connect(self.signal_sort_descending.emit)

        self.searchLineEdit.addAction(
            QIcon("icons_16:magnifier.png"), QLineEdit.ActionPosition.LeadingPosition
        )
        self.searchLineEdit.textChanged.connect(self.signal_search_text_changed.emit)
        self.searchLineEdit.setToolTip(
            (
                "Special characters:\n"
                "* matches zero or more of any characters\n"
                "? matches any single character\n"
                "[...] matches any character within square brackets"
            )
        )

    @property
    def search_bar_text(self) -> str:
        return self.searchLineEdit.text()

    def show_form(self) -> None:
        logging.debug(f"Showing {self.__class__.__name__}")
        self.show()

    def closeEvent(self, a0: QCloseEvent) -> None:
        logging.debug(f"Closing {self.__class__.__name__}")
        return super().closeEvent(a0)
