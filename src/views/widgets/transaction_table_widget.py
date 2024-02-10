import logging
from collections.abc import Sequence

from PyQt6.QtCore import QEvent, QObject, Qt, pyqtSignal
from PyQt6.QtGui import QAction, QContextMenuEvent, QCursor, QKeyEvent
from PyQt6.QtWidgets import (
    QApplication,
    QHeaderView,
    QLineEdit,
    QMenu,
    QTableView,
    QWidget,
)
from src.views import icons
from src.views.constants import TRANSACTION_TABLE_COLUMN_HEADERS, TransactionTableColumn
from src.views.dialogs.busy_dialog import create_simple_busy_indicator
from src.views.ui_files.widgets.Ui_transaction_table_widget import (
    Ui_TransactionTableWidget,
)


class EventFilter(QObject):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.table = QTableView(parent)  # dummy QTableView to test events on

    def eventFilter(self, source: QObject, event: QEvent) -> bool:  # noqa: ARG002
        if isinstance(event, QKeyEvent):
            text_cleared_event = QKeyEvent(
                event.type(),
                event.key(),
                event.modifiers(),
                event.nativeScanCode(),
                event.nativeVirtualKey(),
                event.nativeModifiers(),
                "",
                event.isAutoRepeat(),
                event.count(),
                event.device(),
            )
            original_event = QKeyEvent(
                event.type(),
                event.key(),
                event.modifiers(),
                event.nativeScanCode(),
                event.nativeVirtualKey(),
                event.nativeModifiers(),
                event.text(),
                event.isAutoRepeat(),
                event.count(),
                event.device(),
            )
            self.table.keyPressEvent(text_cleared_event)
            self.table.keyPressEvent(original_event)
            res_cleared = text_cleared_event.isAccepted()
            res_original = original_event.isAccepted()
            if res_original and not res_cleared:
                return True
            return False
        return False


class TransactionTableWidget(QWidget, Ui_TransactionTableWidget):
    signal_search_text_changed = pyqtSignal(str)
    signal_filter_transactions = pyqtSignal()
    signal_reset_columns = pyqtSignal()
    signal_save_column_order = pyqtSignal()
    signal_load_column_order = pyqtSignal()

    signal_income = pyqtSignal()
    signal_expense = pyqtSignal()
    signal_refund = pyqtSignal()
    signal_cash_transfer = pyqtSignal()
    signal_buy = pyqtSignal()
    signal_sell = pyqtSignal()
    signal_dividend = pyqtSignal()
    signal_security_transfer = pyqtSignal()

    signal_find_related = pyqtSignal()

    signal_delete = pyqtSignal()
    signal_edit = pyqtSignal()
    signal_duplicate = pyqtSignal()

    signal_add_tags = pyqtSignal()
    signal_remove_tags = pyqtSignal()
    signal_selection_changed = pyqtSignal()

    signal_copy_uuids = pyqtSignal()

    def __init__(self, parent: QWidget | None) -> None:
        super().__init__(parent)
        self.setupUi(self)
        self.tableView.horizontalHeader().setResizeContentsPrecision(100)
        self.tableView.setSortingEnabled(True)
        self._create_column_actions()
        self._set_icons()
        self._connect_actions()
        self._initialize_signals()
        self._setup_header()
        self._setup_table()

        # this is necessary to make action shortcuts work
        self.tableView.addAction(self.actionDelete)
        self.tableView.addAction(self.actionDuplicate)
        self.tableView.addAction(self.actionRefund)

        # this filter disables keyboard search in QTableView
        self.filter_ = EventFilter(parent=None)
        self.tableView.installEventFilter(self.filter_)

    @property
    def search_bar_text(self) -> str:
        return self.searchLineEdit.text()

    @search_bar_text.setter
    def search_bar_text(self, text: str) -> None:
        self.searchLineEdit.setText(text)

    @property
    def auto_column_visibility(self) -> bool:
        return self.actionAuto_Column_Mode.isChecked()

    @auto_column_visibility.setter
    def auto_column_visibility(self, value: bool) -> None:
        self.actionAuto_Column_Mode.setChecked(value)
        if value:
            self.actionAuto_Column_Mode.setEnabled(False)

    def set_filter_tooltip(self, active_filters: str) -> None:
        text = "Filter Transactions"
        if active_filters:
            text += "\n\nActive Filters:"
            for filter_ in active_filters:
                text += f"\n-{filter_}"
        self.actionFilter_Transactions.setToolTip(text)

    def finalize_setup(self) -> None:
        self.tableView.selectionModel().selectionChanged.connect(
            self.signal_selection_changed.emit
        )
        self.signal_selection_changed.emit()

    def set_shown_transactions(self, shown: int, total: int) -> None:
        self.shownTransactionsLabel.setText(
            f"Showing Transactions: {shown:n} / {total:n}"
        )

    def set_selected_amount(self, amount: str) -> None:
        self.selectedTransactionsTotalLabel.setText(
            f"Selected Transactions Total: {amount}"
        )

    def resize_table_to_contents(self) -> None:
        self.tableView.horizontalHeader().setStretchLastSection(False)
        self.tableView.resizeColumnsToContents()
        self.tableView.horizontalHeader().setStretchLastSection(True)

    def set_column_visibility(
        self,
        column: TransactionTableColumn,
        *,
        show: bool,
        resize: bool = False,
        turn_off_auto_column_visibility: bool = False,
    ) -> None:
        if turn_off_auto_column_visibility:
            self.actionAuto_Column_Mode.setChecked(False)
            self.actionAuto_Column_Mode.setEnabled(True)

        if show != self.tableView.isColumnHidden(column):
            return

        columns = TRANSACTION_TABLE_COLUMN_HEADERS.keys()
        # If all other columns are hidden, this column must stay shown
        if not any(
            not self.tableView.isColumnHidden(column_)
            for column_ in columns
            if column_ != column
        ):
            return

        self.tableView.setColumnHidden(column, not show)
        if show and resize:
            self.resize_table_to_contents()
            self.tableView.viewport().update()

    def set_all_columns_visibility(self, *, show: bool) -> None:
        for column in TRANSACTION_TABLE_COLUMN_HEADERS:
            self.set_column_visibility(
                column, show=show, turn_off_auto_column_visibility=True
            )
        self.resize_table_to_contents()

    def set_actions(
        self, *, enable_duplicate: bool, enable_refund: bool, enable_find_related: bool
    ) -> None:
        selected_indexes = self.tableView.selectionModel().selectedIndexes()
        selected_rows = [index for index in selected_indexes if index.column() == 0]

        is_any_selected = len(selected_rows) > 0
        is_one_selected = len(selected_rows) == 1

        self.actionEdit.setEnabled(is_any_selected)
        self.actionDuplicate.setEnabled(is_one_selected and enable_duplicate)
        self.actionDelete.setEnabled(is_any_selected)
        self.actionCopy_UUIDs.setEnabled(is_any_selected)
        self.actionAdd_Tags.setEnabled(is_any_selected)
        self.actionRemove_Tags.setEnabled(is_any_selected)
        self.actionRefund.setEnabled(enable_refund)
        self.actionFind_Related.setEnabled(enable_find_related)

    def set_filter_active(self, *, active: bool) -> None:
        if not active:
            self.actionFilter_Transactions.setIcon(icons.filter_)
            self.filterToolButton.setToolButtonStyle(
                Qt.ToolButtonStyle.ToolButtonIconOnly
            )
            self.actionFilter_Transactions.setText("Filter Transactions")
        else:
            self.actionFilter_Transactions.setIcon(icons.filter_warning)
            self.filterToolButton.setToolButtonStyle(
                Qt.ToolButtonStyle.ToolButtonTextBesideIcon
            )
            self.actionFilter_Transactions.setText("Filter active")

    def _create_column_actions(self) -> None:
        self.column_actions: list[QAction] = []
        for column, text in TRANSACTION_TABLE_COLUMN_HEADERS.items():
            action = QAction(parent=self)
            _text = text.replace("&", "&&")
            action.setText(_text)
            action.setData(column)
            action.setCheckable(True)
            action.triggered.connect(
                lambda checked, column=column: self.set_column_visibility(
                    column=column,
                    show=checked,
                    resize=True,
                    turn_off_auto_column_visibility=True,
                )
            )
            self.column_actions.append(action)

    def _create_header_context_menu(self, _: QContextMenuEvent) -> None:
        self.header_menu = QMenu(self)
        self.header_menu.addAction(self.actionAuto_Column_Mode)
        self.header_menu.addSeparator()
        self.header_menu.addAction(self.actionShow_All_Columns)
        self.header_menu.addAction(self.actionHide_All_Columns)
        self.header_menu.addSeparator()
        self.header_menu.addAction(self.actionSave_Column_Order)
        self.header_menu.addAction(self.actionLoad_Column_Order)
        self.header_menu.addSeparator()
        self.header_menu.addAction(self.actionResize_Columns_to_Fit)
        self.header_menu.addAction(self.actionReset_Columns)
        self.header_menu.addSeparator()
        for action in self.column_actions:
            column = action.data()
            if self.tableView.isColumnHidden(column):
                action.setChecked(False)
            else:
                action.setChecked(True)
            self.header_menu.addAction(action)
        self.header_menu.popup(QCursor.pos())

    def _create_table_context_menu(self, _: QContextMenuEvent) -> None:
        self.table_menu = QMenu(self)
        self.table_menu.setToolTipsVisible(True)
        self.table_menu.addAction(self.actionEdit)
        self.table_menu.addAction(self.actionDuplicate)
        self.table_menu.addAction(self.actionDelete)
        self.table_menu.addAction(self.actionCopy_UUIDs)
        self.table_menu.addSeparator()
        self.table_menu.addAction(self.actionAdd_Tags)
        self.table_menu.addAction(self.actionRemove_Tags)
        self.table_menu.addSeparator()
        self.table_menu.addAction(self.actionRefund)
        self.table_menu.addAction(self.actionFind_Related)
        self.table_menu.popup(QCursor.pos())

    def _set_icons(self) -> None:
        self.actionFilter_Transactions.setIcon(icons.filter_)
        self.actionIncome.setIcon(icons.income)
        self.actionExpense.setIcon(icons.expense)
        self.actionBuy.setIcon(icons.buy)
        self.actionSell.setIcon(icons.sell)
        self.actionDividend.setIcon(icons.dividend)
        self.actionCash_Transfer.setIcon(icons.cash_transfer)
        self.actionSecurity_Transfer.setIcon(icons.security_transfer)
        self.actionRefund.setIcon(icons.refund)
        self.actionFind_Related.setIcon(icons.magnifier)
        self.actionCopy_UUIDs.setIcon(icons.clipboard_text)
        self.actionEdit.setIcon(icons.edit)
        self.actionDelete.setIcon(icons.remove)
        self.actionDuplicate.setIcon(icons.duplicate)

        self.actionAdd_Tags.setIcon(icons.add_tag)
        self.actionRemove_Tags.setIcon(icons.remove_tag)

        self.searchLineEdit.addAction(
            icons.magnifier, QLineEdit.ActionPosition.LeadingPosition
        )

    def _connect_actions(self) -> None:
        self.filterToolButton.setDefaultAction(self.actionFilter_Transactions)
        self.buyToolButton.setDefaultAction(self.actionBuy)
        self.sellToolButton.setDefaultAction(self.actionSell)
        self.dividendToolButton.setDefaultAction(self.actionDividend)
        self.incomeToolButton.setDefaultAction(self.actionIncome)
        self.expenseToolButton.setDefaultAction(self.actionExpense)
        self.cashTransferToolButton.setDefaultAction(self.actionCash_Transfer)
        self.securityTransferToolButton.setDefaultAction(self.actionSecurity_Transfer)

        self.actionShow_All_Columns.triggered.connect(
            lambda: self.set_all_columns_visibility(show=True)
        )
        self.actionHide_All_Columns.triggered.connect(
            lambda: self.set_all_columns_visibility(show=False)
        )
        self.actionResize_Columns_to_Fit.triggered.connect(
            self.resize_table_to_contents
        )
        self.actionReset_Columns.triggered.connect(self.signal_reset_columns)
        self.actionAuto_Column_Mode.triggered.connect(
            lambda checked: self._toggle_auto_column_mode(checked=checked)
        )
        self.actionSave_Column_Order.triggered.connect(
            self.signal_save_column_order.emit
        )
        self.actionLoad_Column_Order.triggered.connect(
            self.signal_load_column_order.emit
        )

    def _initialize_signals(self) -> None:
        self.tableView.doubleClicked.connect(self.signal_edit.emit)

        self.actionIncome.triggered.connect(self.signal_income.emit)
        self.actionExpense.triggered.connect(self.signal_expense.emit)
        self.actionRefund.triggered.connect(self.signal_refund.emit)
        self.actionCash_Transfer.triggered.connect(self.signal_cash_transfer.emit)
        self.actionBuy.triggered.connect(self.signal_buy.emit)
        self.actionSell.triggered.connect(self.signal_sell.emit)
        self.actionDividend.triggered.connect(self.signal_dividend.emit)
        self.actionSecurity_Transfer.triggered.connect(
            self.signal_security_transfer.emit
        )

        self.actionFind_Related.triggered.connect(self.signal_find_related.emit)

        self.actionEdit.triggered.connect(self.signal_edit.emit)
        self.actionDuplicate.triggered.connect(self.signal_duplicate.emit)
        self.actionDelete.triggered.connect(self.signal_delete.emit)

        self.actionAdd_Tags.triggered.connect(self.signal_add_tags.emit)
        self.actionRemove_Tags.triggered.connect(self.signal_remove_tags.emit)
        self.actionFilter_Transactions.triggered.connect(
            self.signal_filter_transactions.emit
        )
        self.actionCopy_UUIDs.triggered.connect(self.signal_copy_uuids.emit)

        self.searchLineEdit.textChanged.connect(self.signal_search_text_changed.emit)

        self.tableView.horizontalHeader().sectionMoved.connect(
            self._header_section_moved
        )

    def _setup_header(self) -> None:
        header = self.tableView.horizontalHeader()
        header.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        header.customContextMenuRequested.connect(self._create_header_context_menu)
        header.setSectionsMovable(True)

        header.sortIndicatorChanged.disconnect()  # sorting has to be performed manually
        header.sortIndicatorChanged.connect(self._sort_indicator_changed)

    def _setup_table(self) -> None:
        self.tableView.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.tableView.customContextMenuRequested.connect(
            self._create_table_context_menu
        )

    def reset_column_order(self) -> None:
        header = self.tableView.horizontalHeader()
        for column in TransactionTableColumn:
            visual_index = header.visualIndex(column)
            header.moveSection(visual_index, column)
        self.resize_table_to_contents()

    def _sort_indicator_changed(self, section: int, sort_order: Qt.SortOrder) -> None:
        """Logs and sorts the Table. Shows a busy indicator during the process."""
        # IDEA: sorting might be faster by sorting the data and resetting model

        self._busy_dialog = create_simple_busy_indicator(
            self, "Sorting Transactions, please wait..."
        )
        self._busy_dialog.open()
        QApplication.processEvents()
        try:
            logging.debug(
                f"Sorting: column={TransactionTableColumn(section).name}, "
                f"order={sort_order.name}"
            )
            self.tableView.sortByColumn(section, sort_order)
        except:  # noqa: TRY302
            raise
        finally:
            self._busy_dialog.close()

    def _toggle_auto_column_mode(self, *, checked: bool) -> None:
        if checked:
            self.signal_reset_columns.emit()

    def get_column_order(self) -> list[TransactionTableColumn]:
        columns: list[TransactionTableColumn] = []
        header: QHeaderView = self.tableView.horizontalHeader()
        for visual_index in range(header.count()):
            logical_index = header.logicalIndex(visual_index)
            column = TransactionTableColumn(logical_index)
            columns.append(column)
        return columns

    def load_column_order(self, column_order: Sequence[TransactionTableColumn]) -> None:
        header: QHeaderView = self.tableView.horizontalHeader()
        for target_index, logical_index in enumerate(column_order):
            current_index = header.visualIndex(logical_index)
            header.moveSection(current_index, target_index)

    def _header_section_moved(
        self,
        section: int,  # noqa: ARG002
        old_index: int,  # noqa: ARG002
        new_index: int,  # noqa: ARG002
    ) -> None:
        self.actionSave_Column_Order.setEnabled(True)

    def column_order_saved(self) -> None:
        self.actionSave_Column_Order.setEnabled(False)
