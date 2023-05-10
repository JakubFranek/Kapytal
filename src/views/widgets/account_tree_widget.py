import logging

from PyQt6.QtCore import QEvent, QObject, Qt, pyqtSignal
from PyQt6.QtGui import QContextMenuEvent, QCursor, QKeyEvent, QMouseEvent
from PyQt6.QtWidgets import QHeaderView, QLineEdit, QMenu, QWidget
from src.views import icons
from src.views.constants import AccountTreeColumn
from src.views.ui_files.widgets.Ui_account_tree_widget import Ui_AccountTreeWidget


class AccountTreeWidget(QWidget, Ui_AccountTreeWidget):
    signal_selection_changed = pyqtSignal()
    signal_expand_below = pyqtSignal()
    signal_reset_sort_order = pyqtSignal()
    signal_sort = pyqtSignal(int)
    signal_show_all = pyqtSignal()
    signal_hide_all = pyqtSignal()
    signal_show_selection_only = pyqtSignal()
    signal_select_all_cash_accounts_below = pyqtSignal()
    signal_select_all_security_accounts_below = pyqtSignal()

    signal_show_securities = pyqtSignal()

    signal_add_account_group = pyqtSignal()
    signal_add_security_account = pyqtSignal()
    signal_add_cash_account = pyqtSignal()

    signal_edit_item = pyqtSignal()
    signal_delete_item = pyqtSignal()

    signal_search_text_changed = pyqtSignal(str)

    def __init__(self, parent: QWidget | None) -> None:
        super().__init__(parent)
        self.setupUi(self)
        self.controlsHorizontalLayout.setContentsMargins(-1, 2, -1, 0)

        self._set_action_icons()
        self._connect_actions()

        self.treeView.contextMenuEvent = self._create_context_menu

        self.treeView.installEventFilter(self)
        self.treeView.viewport().installEventFilter(self)
        self.treeView.header().setSectionsClickable(True)
        self.treeView.header().sectionClicked.connect(
            lambda index: self._header_clicked(index)
        )

        self.searchLineEdit.textChanged.connect(self.signal_search_text_changed)

    @property
    def sort_order(self) -> Qt.SortOrder:
        return self.treeView.header().sortIndicatorOrder()

    def set_total_base_balance(self, total_base_balance: str) -> None:
        self.totalBaseBalanceAmountLabel.setText(total_base_balance)

    def _header_clicked(self, index: int) -> None:
        header = self.treeView.header()
        if not header.isSortIndicatorShown():
            header.setSortIndicatorShown(True)
            header.setSortIndicator(index, Qt.SortOrder.AscendingOrder)
        # BUG: this below seems like a bug but it works
        elif header.sortIndicatorOrder() == Qt.SortOrder.DescendingOrder:
            header.setSortIndicator(index, Qt.SortOrder.DescendingOrder)
        else:
            header.setSortIndicator(index, Qt.SortOrder.AscendingOrder)
        self.signal_sort.emit(index)

    def eventFilter(self, source: QObject, event: QEvent) -> bool:  # noqa: N802
        if (
            source is self.treeView
            and isinstance(event, QKeyEvent)
            and event.key() == Qt.Key.Key_Escape
            and event.modifiers() == Qt.KeyboardModifier.NoModifier
        ) or (
            source is self.treeView.viewport()
            and isinstance(event, QMouseEvent)
            and (
                event.button() == Qt.MouseButton.LeftButton
                or event.button() == Qt.MouseButton.RightButton
            )
            and not self.treeView.indexAt(event.pos()).isValid()
        ):
            self.treeView.selectionModel().clear()
        return super().eventFilter(source, event)

    def refresh(self) -> None:
        self.treeView.viewport().update()

    def expand_all(self) -> None:
        logging.debug("Expanding all AccountTree nodes")
        self.treeView.expandAll()

    def collapse_all(self) -> None:
        logging.debug("Collapsing all AccountTree nodes")
        self.treeView.collapseAll()

    def enable_actions(
        self,
        *,
        enable_add_objects: bool,
        enable_modify_object: bool,
        enable_expand_below: bool,
        enable_show_securities: bool
    ) -> None:
        self.actionAdd_Account_Group.setEnabled(enable_add_objects)
        self.actionAdd_Security_Account.setEnabled(enable_add_objects)
        self.actionAdd_Cash_Account.setEnabled(enable_add_objects)
        self.actionEdit.setEnabled(enable_modify_object)
        self.actionDelete.setEnabled(enable_modify_object)
        self.actionExpand_All_Below.setEnabled(enable_expand_below)
        self.actionSelect_All_Cash_Accounts_Below.setEnabled(enable_expand_below)
        self.actionSelect_All_Security_Accounts_Below.setEnabled(enable_expand_below)
        self.actionShow_Selection_Only.setEnabled(enable_modify_object)
        self.actionShow_Securities.setEnabled(enable_show_securities)

        self._enable_add_objects = enable_add_objects
        self._enable_modify_object = enable_modify_object
        self._enable_expand_below = enable_expand_below
        self._enable_show_securities = enable_show_securities

    def _create_context_menu(self, event: QContextMenuEvent) -> None:
        del event
        self.menu = QMenu(self)
        if self._enable_add_objects:
            self.menu.addAction(self.actionAdd_Account_Group)
            self.menu.addAction(self.actionAdd_Cash_Account)
            self.menu.addAction(self.actionAdd_Security_Account)
            self.menu.addSeparator()
        if self._enable_modify_object:
            self.menu.addAction(self.actionEdit)
            self.menu.addAction(self.actionDelete)
            self.menu.addSeparator()
        if self._enable_show_securities:
            self.menu.addAction(self.actionShow_Securities)
            self.menu.addSeparator()
        if self._enable_modify_object:
            self.menu.addAction(self.actionShow_Selection_Only)
        if self._enable_expand_below:
            self.menu.addAction(self.actionSelect_All_Cash_Accounts_Below)
            self.menu.addAction(self.actionSelect_All_Security_Accounts_Below)
            self.menu.addSeparator()
            self.menu.addAction(self.actionExpand_All_Below)
        self.menu.popup(QCursor.pos())

    def finalize_setup(self) -> None:
        self.treeView.header().setSectionResizeMode(
            AccountTreeColumn.NAME,
            QHeaderView.ResizeMode.ResizeToContents,
        )
        self.treeView.header().setSectionResizeMode(
            AccountTreeColumn.BALANCE_NATIVE,
            QHeaderView.ResizeMode.ResizeToContents,
        )
        self.treeView.header().setSectionResizeMode(
            AccountTreeColumn.BALANCE_BASE,
            QHeaderView.ResizeMode.ResizeToContents,
        )
        self.treeView.header().setSectionResizeMode(
            AccountTreeColumn.SHOW,
            QHeaderView.ResizeMode.ResizeToContents,
        )

        self.treeView.selectionModel().selectionChanged.connect(
            self.signal_selection_changed.emit
        )

    def _set_action_icons(self) -> None:
        self.actionExpand_All.setIcon(icons.expand)
        self.actionExpand_All_Below.setIcon(icons.expand_below)
        self.actionCollapse_All.setIcon(icons.collapse)

        self.actionReset_Sort_Order.setIcon(icons.reset_sort_order)

        self.actionShow_All.setIcon(icons.select_all)
        self.actionHide_All.setIcon(icons.unselect_all)
        self.actionShow_Selection_Only.setIcon(icons.select_this)
        self.actionSelect_All_Cash_Accounts_Below.setIcon(icons.select_cash_accounts)
        self.actionSelect_All_Security_Accounts_Below.setIcon(
            icons.select_security_accounts
        )

        self.actionAdd_Account_Group.setIcon(icons.add_account_group)
        self.actionAdd_Security_Account.setIcon(icons.add_security_account)
        self.actionAdd_Cash_Account.setIcon(icons.add_cash_account)

        self.actionEdit.setIcon(icons.edit)
        self.actionDelete.setIcon(icons.remove)

        self.actionShow_Securities.setIcon(icons.security)

        self.searchLineEdit.addAction(
            icons.magnifier, QLineEdit.ActionPosition.LeadingPosition
        )

    def _connect_actions(self) -> None:
        self.actionExpand_All.triggered.connect(self.expand_all)
        self.actionExpand_All_Below.triggered.connect(self.signal_expand_below.emit)
        self.actionCollapse_All.triggered.connect(self.collapse_all)

        self.actionReset_Sort_Order.triggered.connect(self.signal_reset_sort_order.emit)

        self.actionShow_All.triggered.connect(self.signal_show_all.emit)
        self.actionHide_All.triggered.connect(self.signal_hide_all.emit)
        self.actionShow_Selection_Only.triggered.connect(
            self.signal_show_selection_only.emit
        )
        self.actionSelect_All_Cash_Accounts_Below.triggered.connect(
            self.signal_select_all_cash_accounts_below.emit
        )
        self.actionSelect_All_Security_Accounts_Below.triggered.connect(
            self.signal_select_all_security_accounts_below.emit
        )

        self.actionAdd_Account_Group.triggered.connect(
            self.signal_add_account_group.emit
        )
        self.actionAdd_Security_Account.triggered.connect(
            self.signal_add_security_account.emit
        )
        self.actionAdd_Cash_Account.triggered.connect(self.signal_add_cash_account.emit)
        self.actionEdit.triggered.connect(self.signal_edit_item.emit)
        self.actionDelete.triggered.connect(self.signal_delete_item.emit)

        self.actionShow_Securities.triggered.connect(self.signal_show_securities.emit)

        self.expandAllToolButton.setDefaultAction(self.actionExpand_All)
        self.collapseAllToolButton.setDefaultAction(self.actionCollapse_All)

        self.resetSortOrderToolButton.setDefaultAction(self.actionReset_Sort_Order)

        self.showAllToolButton.setDefaultAction(self.actionShow_All)
        self.hideAllToolButton.setDefaultAction(self.actionHide_All)
