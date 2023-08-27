from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QTableView, QWidget
from src.views import icons
from src.views.base_classes.custom_widget import CustomWidget
from src.views.ui_files.forms.Ui_table_view_form import Ui_TableViewForm


class TransactionTableForm(CustomWidget, Ui_TableViewForm):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent=parent)
        self.setupUi(self)
        self.setWindowFlag(Qt.WindowType.Window)
        self.setWindowIcon(icons.table)

    @property
    def table_view(self) -> QTableView:
        return self.tableView

    def set_window_title(self, window_title: str) -> None:
        self.setWindowTitle(window_title)
