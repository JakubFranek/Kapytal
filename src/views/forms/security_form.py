from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import QHeaderView, QLineEdit, QWidget
from src.views import icons
from src.views.base_classes.custom_widget import CustomWidget
from src.views.constants import OwnedSecuritiesTreeColumn, SecurityTableColumn
from src.views.ui_files.forms.Ui_security_form import Ui_SecurityForm

# TODO: add some way to view and edit price history
# TODO: add search bar, expand and collapse controls to Overview tab


class SecurityForm(CustomWidget, Ui_SecurityForm):
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

        self.addToolButton.setDefaultAction(self.actionAdd_Security)
        self.removeToolButton.setDefaultAction(self.actionRemove_Security)
        self.editToolButton.setDefaultAction(self.actionEdit_Security)
        self.setPriceToolButton.setDefaultAction(self.actionSet_Security_Price)

        self.actionAdd_Security.triggered.connect(self.signal_add_security.emit)
        self.actionRemove_Security.triggered.connect(self.signal_remove_security.emit)
        self.actionEdit_Security.triggered.connect(self.signal_edit_security.emit)
        self.actionSet_Security_Price.triggered.connect(
            self.signal_set_security_price.emit
        )

        self.actionAdd_Security.setIcon(icons.add)
        self.actionRemove_Security.setIcon(icons.remove)
        self.actionEdit_Security.setIcon(icons.edit)
        self.actionSet_Security_Price.setIcon(icons.set_security_price)

        self.searchLineEdit.addAction(
            icons.magnifier, QLineEdit.ActionPosition.LeadingPosition
        )
        self.searchLineEdit.textChanged.connect(self.signal_search_text_changed.emit)

    @property
    def search_bar_text(self) -> str:
        return self.searchLineEdit.text()

    def enable_actions(self, *, is_security_selected: bool) -> None:
        self.actionRemove_Security.setEnabled(is_security_selected)
        self.actionEdit_Security.setEnabled(is_security_selected)
        self.actionSet_Security_Price.setEnabled(is_security_selected)

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

        self.treeView.header().setStretchLastSection(False)
        self.treeView.header().setSectionResizeMode(
            OwnedSecuritiesTreeColumn.NAME,
            QHeaderView.ResizeMode.Stretch,
        )
        self.treeView.header().setSectionResizeMode(
            OwnedSecuritiesTreeColumn.SHARES,
            QHeaderView.ResizeMode.ResizeToContents,
        )
        self.treeView.header().setSectionResizeMode(
            OwnedSecuritiesTreeColumn.AMOUNT_NATIVE,
            QHeaderView.ResizeMode.ResizeToContents,
        )
        self.treeView.header().setSectionResizeMode(
            OwnedSecuritiesTreeColumn.AMOUNT_BASE,
            QHeaderView.ResizeMode.ResizeToContents,
        )

    def refresh_tree_view(self) -> None:
        self.treeView.expandAll()
        for column in OwnedSecuritiesTreeColumn:
            self.treeView.resizeColumnToContents(column)
