import logging

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QCloseEvent
from PyQt6.QtWidgets import QHeaderView, QLineEdit, QWidget
from src.views import icons
from src.views.constants import PayeeTableColumn
from src.views.ui_files.forms.Ui_payee_form import Ui_PayeeForm

# TODO: change visual style from side buttons to tool buttons and context menu


class PayeeForm(QWidget, Ui_PayeeForm):
    signal_add_payee = pyqtSignal()
    signal_rename_payee = pyqtSignal()
    signal_remove_payee = pyqtSignal()
    signal_select_payee = pyqtSignal()
    signal_search_text_changed = pyqtSignal()
    signal_selection_changed = pyqtSignal()

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent=parent)
        self.setupUi(self)
        self.setWindowFlag(Qt.WindowType.Window)
        self.setWindowIcon(icons.payee)

        self.addButton.clicked.connect(self.signal_add_payee.emit)
        self.removeButton.clicked.connect(self.signal_remove_payee.emit)
        self.renameButton.clicked.connect(self.signal_rename_payee.emit)
        self.selectButton.clicked.connect(self.signal_select_payee.emit)
        self.searchLineEdit.textChanged.connect(self.signal_search_text_changed.emit)

        self.searchLineEdit.addAction(
            icons.magnifier, QLineEdit.ActionPosition.LeadingPosition
        )

    @property
    def search_bar_text(self) -> str:
        return self.searchLineEdit.text()

    def show_form(self) -> None:
        logging.debug(f"Showing {self.__class__.__name__}")
        self.show()

    def closeEvent(self, a0: QCloseEvent) -> None:  # noqa: N802
        logging.debug(f"Closing {self.__class__.__name__}")
        return super().closeEvent(a0)

    def set_buttons(self, *, is_payee_selected: bool) -> None:
        self.removeButton.setEnabled(is_payee_selected)
        self.renameButton.setEnabled(is_payee_selected)
        self.selectButton.setEnabled(is_payee_selected)

    def finalize_setup(self) -> None:
        self.tableView.horizontalHeader().setStretchLastSection(False)
        self.tableView.horizontalHeader().setSectionResizeMode(
            PayeeTableColumn.NAME,
            QHeaderView.ResizeMode.ResizeToContents,
        )
        self.tableView.horizontalHeader().setSectionResizeMode(
            PayeeTableColumn.TRANSACTIONS,
            QHeaderView.ResizeMode.ResizeToContents,
        )
        self.tableView.horizontalHeader().setSectionResizeMode(
            PayeeTableColumn.BALANCE,
            QHeaderView.ResizeMode.Stretch,
        )

        style = self.style()
        last_section_text = self.tableView.model().headerData(
            PayeeTableColumn.BALANCE,
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
