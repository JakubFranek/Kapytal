from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QAction, QContextMenuEvent, QCursor
from PyQt6.QtWidgets import QMenu, QTableView, QWidget
from src.views import icons
from src.views.base_classes.custom_widget import CustomWidget
from src.views.ui_files.forms.Ui_table_view_form import Ui_TableViewForm


class TransactionTableForm(CustomWidget, Ui_TableViewForm):
    signal_edit = pyqtSignal()

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent=parent)
        self.setupUi(self)
        self.setWindowFlag(Qt.WindowType.Window)
        self.setWindowIcon(icons.table)
        self.tableView.contextMenuEvent = self._create_context_menu

        self.actionEdit = QAction("Edit", self)
        self.actionEdit.setIcon(icons.edit)
        self.actionEdit.triggered.connect(self.signal_edit.emit)

        self.tableView.doubleClicked.connect(self.signal_edit.emit)

    @property
    def table_view(self) -> QTableView:
        return self.tableView

    def set_window_title(self, window_title: str) -> None:
        self.setWindowTitle(window_title)

    def _create_context_menu(self, event: QContextMenuEvent) -> None:  # noqa: ARG002
        self.menu = QMenu(self)
        self.menu.addAction(self.actionEdit)
        self.menu.popup(QCursor.pos())
