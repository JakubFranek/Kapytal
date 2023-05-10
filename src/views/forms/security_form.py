import logging

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QCloseEvent
from PyQt6.QtWidgets import QHeaderView, QLineEdit, QWidget
from src.views import icons
from src.views.constants import OwnedSecuritiesTreeColumn, SecurityTableColumn
from src.views.ui_files.forms.Ui_security_form import Ui_SecurityForm

# TODO: add some way to view and edit price history
# TODO: change visual style from side buttons to tool buttons and context menu


class SecurityForm(QWidget, Ui_SecurityForm):
    signal_add_security = pyqtSignal()
    signal_edit_security = pyqtSignal()
    signal_set_security_price = pyqtSignal()
    signal_remove_security = pyqtSignal()
    signal_select_security = pyqtSignal()
    signal_search_text_changed = pyqtSignal(str)
    signal_selection_changed = pyqtSignal()

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent=parent)
        self.setupUi(self)
        self.setWindowFlag(Qt.WindowType.Window)
        self.setWindowIcon(icons.security)

        self.addButton.clicked.connect(self.signal_add_security.emit)
        self.removeButton.clicked.connect(self.signal_remove_security.emit)
        self.editButton.clicked.connect(self.signal_edit_security.emit)
        self.setPriceButton.clicked.connect(self.signal_set_security_price.emit)

        self.searchLineEdit.addAction(
            icons.magnifier, QLineEdit.ActionPosition.LeadingPosition
        )
        self.searchLineEdit.textChanged.connect(self.signal_search_text_changed.emit)

    @property
    def search_bar_text(self) -> str:
        return self.searchLineEdit.text()

    def show_form(self) -> None:
        logging.debug(f"Showing {self.__class__.__name__}")
        self.show()

    def closeEvent(self, a0: QCloseEvent) -> None:  # noqa: N802
        logging.debug(f"Closing {self.__class__.__name__}")
        return super().closeEvent(a0)

    def set_buttons(self, *, is_security_selected: bool) -> None:
        self.removeButton.setEnabled(is_security_selected)
        self.editButton.setEnabled(is_security_selected)
        self.setPriceButton.setEnabled(is_security_selected)

    def finalize_setup(self) -> None:
        self.tableView.horizontalHeader().setStretchLastSection(False)
        self.tableView.horizontalHeader().setSectionResizeMode(
            SecurityTableColumn.NAME,
            QHeaderView.ResizeMode.ResizeToContents,
        )
        self.tableView.horizontalHeader().setSectionResizeMode(
            SecurityTableColumn.SYMBOL,
            QHeaderView.ResizeMode.ResizeToContents,
        )
        self.tableView.horizontalHeader().setSectionResizeMode(
            SecurityTableColumn.TYPE,
            QHeaderView.ResizeMode.ResizeToContents,
        )
        self.tableView.horizontalHeader().setSectionResizeMode(
            SecurityTableColumn.PRICE,
            QHeaderView.ResizeMode.ResizeToContents,
        )
        self.tableView.horizontalHeader().setSectionResizeMode(
            SecurityTableColumn.LAST_DATE,
            QHeaderView.ResizeMode.Stretch,
        )

        style = self.style()
        last_section_text = self.tableView.model().headerData(
            SecurityTableColumn.LAST_DATE,
            Qt.Orientation.Horizontal,
            Qt.ItemDataRole.DisplayRole,
        )
        self.tableView.horizontalHeader().setMinimumSectionSize(
            style.pixelMetric(style.PixelMetric.PM_HeaderMarkSize)
            + style.pixelMetric(style.PixelMetric.PM_HeaderGripMargin) * 2
            + self.fontMetrics().horizontalAdvance(last_section_text)
        )

        self.tableView.selectionModel().selectionChanged.connect(
            self.signal_selection_changed.emit
        )
        self.tableView.sortByColumn(0, Qt.SortOrder.AscendingOrder)

    def refresh_tree_view(self) -> None:
        self.treeView.expandAll()
        for column in OwnedSecuritiesTreeColumn:
            self.treeView.resizeColumnToContents(column)
