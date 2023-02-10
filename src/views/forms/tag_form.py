import logging

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QCloseEvent, QIcon
from PyQt6.QtWidgets import QHeaderView, QLineEdit, QWidget

from src.views.constants import TagTableColumns
from src.views.ui_files.Ui_tag_form import Ui_TagForm


class TagForm(QWidget, Ui_TagForm):
    signal_add_tag = pyqtSignal()
    signal_rename_tag = pyqtSignal()
    signal_remove_tag = pyqtSignal()
    signal_select_tag = pyqtSignal()
    signal_search_text_changed = pyqtSignal()
    signal_selection_changed = pyqtSignal()

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent=parent)
        self.setupUi(self)
        self.setWindowFlag(Qt.WindowType.Window)
        self.setWindowIcon(QIcon("icons_16:tag.png"))

        self.addButton.clicked.connect(self.signal_add_tag.emit)
        self.removeButton.clicked.connect(self.signal_remove_tag.emit)
        self.renameButton.clicked.connect(self.signal_rename_tag.emit)
        self.selectButton.clicked.connect(self.signal_select_tag.emit)

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

    def set_buttons(self, is_tag_selected: bool) -> None:
        self.removeButton.setEnabled(is_tag_selected)
        self.renameButton.setEnabled(is_tag_selected)
        self.selectButton.setEnabled(is_tag_selected)

    def finalize_setup(self) -> None:
        self.tableView.horizontalHeader().setSectionResizeMode(
            TagTableColumns.COLUMN_NAME,
            QHeaderView.ResizeMode.ResizeToContents,
        )
        self.tableView.horizontalHeader().setSectionResizeMode(
            TagTableColumns.COLUMN_TRANSACTIONS,
            QHeaderView.ResizeMode.ResizeToContents,
        )
        self.tableView.selectionModel().selectionChanged.connect(
            self.signal_selection_changed.emit
        )
        self.tableView.sortByColumn(0, Qt.SortOrder.AscendingOrder)
