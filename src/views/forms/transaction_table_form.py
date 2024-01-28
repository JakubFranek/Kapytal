from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QAction, QContextMenuEvent, QCursor
from PyQt6.QtWidgets import QLineEdit, QMenu, QTableView, QWidget
from src.views import icons
from src.views.base_classes.custom_widget import CustomWidget
from src.views.ui_files.forms.Ui_transaction_table_form import Ui_TransactionTableForm


class TransactionTableForm(CustomWidget, Ui_TransactionTableForm):
    signal_edit = pyqtSignal()
    signal_add_tags = pyqtSignal()
    signal_remove_tags = pyqtSignal()
    signal_search_text_changed = pyqtSignal(str)
    signal_selection_changed = pyqtSignal()

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent=parent)
        self.setupUi(self)
        self.setWindowFlag(Qt.WindowType.Window)
        self.setWindowIcon(icons.table)

        self.resize(800, 500)

        self.tableView.contextMenuEvent = self._create_context_menu

        self.actionEdit = QAction("Edit", self)
        self.actionEdit.setIcon(icons.edit)
        self.actionEdit.triggered.connect(self.signal_edit.emit)

        self.actionAddTags = QAction("Add Tags", self)
        self.actionAddTags.setIcon(icons.add_tag)
        self.actionAddTags.triggered.connect(self.signal_add_tags.emit)

        self.actionRemoveTags = QAction("Remove Tags", self)
        self.actionRemoveTags.setIcon(icons.remove_tag)
        self.actionRemoveTags.triggered.connect(self.signal_remove_tags.emit)

        self.searchLineEdit.addAction(
            icons.magnifier, QLineEdit.ActionPosition.LeadingPosition
        )
        self.searchLineEdit.setPlaceholderText("Search Transactions")
        self.searchLineEdit.textChanged.connect(self.signal_search_text_changed.emit)

        self.tableView.doubleClicked.connect(self.signal_edit.emit)

    def finalize_setup(self) -> None:
        self.tableView.selectionModel().selectionChanged.connect(
            self.signal_selection_changed.emit
        )

    @property
    def table_view(self) -> QTableView:
        return self.tableView

    def set_window_title(self, window_title: str) -> None:
        self.setWindowTitle(window_title)

    def set_shown_transactions(self, shown: int, total: int) -> None:
        self.shownTransactionsLabel.setText(
            f"Showing Transactions: {shown:n} / {total:n}"
        )

    def set_selected_amount(self, amount: str) -> None:
        self.selectedTransactionsTotalLabel.setText(
            f"Selected Transactions Total: {amount}"
        )

    def _create_context_menu(self, event: QContextMenuEvent) -> None:  # noqa: ARG002
        self.menu = QMenu(self)
        self.menu.addAction(self.actionEdit)
        self.menu.addAction(self.actionAddTags)
        self.menu.addAction(self.actionRemoveTags)
        self.menu.popup(QCursor.pos())
