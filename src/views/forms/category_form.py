import logging

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QCloseEvent, QIcon
from PyQt6.QtWidgets import QHeaderView, QLineEdit, QWidget

from src.views.constants import CategoryTreeColumns
from src.views.ui_files.Ui_category_form import Ui_CategoryForm


class CategoryForm(QWidget, Ui_CategoryForm):
    signal_add_category = pyqtSignal()
    signal_rename_category = pyqtSignal()
    signal_remove_category = pyqtSignal()
    signal_select_category = pyqtSignal()
    signal_search_text_changed = pyqtSignal()
    signal_selection_changed = pyqtSignal()

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent=parent)
        self.setupUi(self)
        self.setWindowFlag(Qt.WindowType.Window)
        self.setWindowIcon(QIcon("icons_16:category.png"))

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

    def set_buttons(self, is_category_selected: bool) -> None:
        self.removeToolButton.setEnabled(is_category_selected)
        self.editToolButton.setEnabled(is_category_selected)

    def finalize_setup(self) -> None:
        self.treeView.header().setSectionResizeMode(
            CategoryTreeColumns.COLUMN_NAME,
            QHeaderView.ResizeMode.ResizeToContents,
        )
        self.treeView.header().setSectionResizeMode(
            CategoryTreeColumns.COLUMN_TRANSACTIONS,
            QHeaderView.ResizeMode.ResizeToContents,
        )
        self.treeView.selectionModel().selectionChanged.connect(
            self.signal_selection_changed.emit
        )
