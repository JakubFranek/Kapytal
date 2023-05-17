from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import QHeaderView, QLineEdit, QWidget
from src.views import icons
from src.views.base_classes.custom_widget import CustomWidget
from src.views.constants import PayeeTableColumn
from src.views.ui_files.forms.Ui_payee_form import Ui_PayeeForm


class PayeeForm(CustomWidget, Ui_PayeeForm):
    signal_add_payee = pyqtSignal()
    signal_rename_payee = pyqtSignal()
    signal_remove_payee = pyqtSignal()
    signal_select_payee = pyqtSignal()
    signal_search_text_changed = pyqtSignal(str)
    signal_selection_changed = pyqtSignal()

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent=parent)
        self.setupUi(self)
        self.setWindowFlag(Qt.WindowType.Window)
        self.setWindowIcon(icons.payee)

        self._initialize_actions()
        self.searchLineEdit.textChanged.connect(self.signal_search_text_changed.emit)

        self.searchLineEdit.addAction(
            icons.magnifier, QLineEdit.ActionPosition.LeadingPosition
        )

    @property
    def search_bar_text(self) -> str:
        return self.searchLineEdit.text()

    def enable_actions(
        self, *, is_payee_selected: bool, is_one_payee_selected: bool
    ) -> None:
        self.actionRename_Payee.setEnabled(is_one_payee_selected)
        self.actionRemove_Payee.setEnabled(is_payee_selected)

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

    def _initialize_actions(self) -> None:
        self.actionAdd_Payee.setIcon(icons.add)
        self.actionRename_Payee.setIcon(icons.edit)
        self.actionRemove_Payee.setIcon(icons.remove)

        self.actionAdd_Payee.triggered.connect(self.signal_add_payee.emit)
        self.actionRename_Payee.triggered.connect(self.signal_rename_payee.emit)
        self.actionRemove_Payee.triggered.connect(self.signal_remove_payee.emit)

        self.addToolButton.setDefaultAction(self.actionAdd_Payee)
        self.renameToolButton.setDefaultAction(self.actionRename_Payee)
        self.removeToolButton.setDefaultAction(self.actionRemove_Payee)
