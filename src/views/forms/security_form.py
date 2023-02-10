import logging

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QCloseEvent, QIcon
from PyQt6.QtWidgets import QHeaderView, QLineEdit, QWidget

from src.views.constants import SecurityTableColumns
from src.views.ui_files.Ui_security_form import Ui_SecurityForm


# TODO: add some way to view and edit price history
class SecurityForm(QWidget, Ui_SecurityForm):
    signal_add_security = pyqtSignal()
    signal_edit_security = pyqtSignal()
    signal_set_security_price = pyqtSignal()
    signal_remove_security = pyqtSignal()
    signal_select_security = pyqtSignal()
    signal_search_text_changed = pyqtSignal()
    signal_selection_changed = pyqtSignal()

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent=parent)
        self.setupUi(self)
        self.setWindowFlag(Qt.WindowType.Window)
        self.setWindowIcon(QIcon("icons_16:certificate.png"))

        self.addButton.clicked.connect(self.signal_add_security.emit)
        self.removeButton.clicked.connect(self.signal_remove_security.emit)
        self.editButton.clicked.connect(self.signal_edit_security.emit)
        self.setPriceButton.clicked.connect(self.signal_set_security_price.emit)
        self.selectButton.clicked.connect(self.signal_select_security.emit)

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

    def set_buttons(self, is_security_selected: bool) -> None:
        self.removeButton.setEnabled(is_security_selected)
        self.editButton.setEnabled(is_security_selected)
        self.setPriceButton.setEnabled(is_security_selected)
        self.selectButton.setEnabled(is_security_selected)

    def finalize_setup(self) -> None:
        self.tableView.horizontalHeader().setSectionResizeMode(
            SecurityTableColumns.COLUMN_NAME,
            QHeaderView.ResizeMode.ResizeToContents,
        )
        self.tableView.horizontalHeader().setSectionResizeMode(
            SecurityTableColumns.COLUMN_SYMBOL,
            QHeaderView.ResizeMode.ResizeToContents,
        )
        self.tableView.horizontalHeader().setSectionResizeMode(
            SecurityTableColumns.COLUMN_TYPE,
            QHeaderView.ResizeMode.ResizeToContents,
        )
        self.tableView.horizontalHeader().setSectionResizeMode(
            SecurityTableColumns.COLUMN_PRICE,
            QHeaderView.ResizeMode.ResizeToContents,
        )
        self.tableView.selectionModel().selectionChanged.connect(
            self.signal_selection_changed.emit
        )
        self.tableView.sortByColumn(0, Qt.SortOrder.AscendingOrder)
