from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QHeaderView, QTableView, QWidget
from src.views import icons
from src.views.base_classes.custom_widget import CustomWidget
from src.views.constants import SecurityAccountTableColumn
from src.views.ui_files.forms.Ui_table_view_form import Ui_TableViewForm


class SecurityAccountForm(CustomWidget, Ui_TableViewForm):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent=parent)
        self.setupUi(self)
        self.setWindowFlag(Qt.WindowType.Window)
        self.setWindowIcon(icons.security_account)

    @property
    def table_view(self) -> QTableView:
        return self.tableView

    def set_account_path(self, account_path: str) -> None:
        self.setWindowTitle(account_path)

    def finalize_setup(self) -> None:
        self.tableView.horizontalHeader().setStretchLastSection(False)
        self.tableView.horizontalHeader().setSectionResizeMode(
            SecurityAccountTableColumn.SECURITY_NAME,
            QHeaderView.ResizeMode.ResizeToContents,
        )
        self.tableView.horizontalHeader().setSectionResizeMode(
            SecurityAccountTableColumn.SYMBOL,
            QHeaderView.ResizeMode.ResizeToContents,
        )
        self.tableView.horizontalHeader().setSectionResizeMode(
            SecurityAccountTableColumn.TYPE,
            QHeaderView.ResizeMode.ResizeToContents,
        )
        self.tableView.horizontalHeader().setSectionResizeMode(
            SecurityAccountTableColumn.SHARES,
            QHeaderView.ResizeMode.ResizeToContents,
        )
        self.tableView.horizontalHeader().setSectionResizeMode(
            SecurityAccountTableColumn.PRICE,
            QHeaderView.ResizeMode.ResizeToContents,
        )
        self.tableView.horizontalHeader().setSectionResizeMode(
            SecurityAccountTableColumn.AMOUNT_NATIVE,
            QHeaderView.ResizeMode.Stretch,
        )
        self.tableView.horizontalHeader().setSectionResizeMode(
            SecurityAccountTableColumn.AMOUNT_BASE,
            QHeaderView.ResizeMode.Stretch,
        )

        style = self.style()
        last_section_text = self.tableView.model().headerData(
            SecurityAccountTableColumn.AMOUNT_BASE,
            Qt.Orientation.Horizontal,
            Qt.ItemDataRole.DisplayRole,
        )
        self.tableView.horizontalHeader().setMinimumSectionSize(
            style.pixelMetric(style.PixelMetric.PM_HeaderMarkSize)
            + style.pixelMetric(style.PixelMetric.PM_HeaderGripMargin) * 2
            + self.fontMetrics().horizontalAdvance(last_section_text)
        )
