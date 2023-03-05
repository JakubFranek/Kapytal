import logging

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtGui import QContextMenuEvent, QCursor, QIcon
from PyQt6.QtWidgets import QHeaderView, QMenu, QWidget

from src.views.constants import AccountTreeColumns
from src.views.ui_files.widgets.Ui_account_tree_widget import Ui_AccountTreeWidget


# TODO: possibility to hide widget completely
class AccountTreeWidget(QWidget, Ui_AccountTreeWidget):
    signal_selection_changed = pyqtSignal()
    signal_expand_below = pyqtSignal()
    signal_show_all = pyqtSignal()
    signal_hide_all = pyqtSignal()
    signal_show_selection_only = pyqtSignal()

    signal_add_account_group = pyqtSignal()
    signal_add_security_account = pyqtSignal()
    signal_add_cash_account = pyqtSignal()

    signal_edit_item = pyqtSignal()
    signal_delete_item = pyqtSignal()

    def __init__(self, parent: QWidget | None) -> None:
        super().__init__(parent)
        self.setupUi(self)
        self.controlsHorizontalLayout.setContentsMargins(-1, 2, -1, 0)

        self._set_action_icons()
        self._connect_actions()

        self.treeView.contextMenuEvent = self._create_context_menu

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
        enable_add_objects: bool,
        enable_modify_object: bool,
        enable_expand_below: bool,
    ) -> None:
        self.actionAdd_Account_Group.setEnabled(enable_add_objects)
        self.actionAdd_Security_Account.setEnabled(enable_add_objects)
        self.actionAdd_Cash_Account.setEnabled(enable_add_objects)
        self.actionEdit.setEnabled(enable_modify_object)
        self.actionDelete.setEnabled(enable_modify_object)
        self.actionExpand_All_Below.setEnabled(enable_expand_below)

    def _create_context_menu(self, event: QContextMenuEvent) -> None:  # noqa: U100
        self.menu = QMenu(self)
        self.menu.addAction(self.actionAdd_Account_Group)
        self.menu.addAction(self.actionAdd_Cash_Account)
        self.menu.addAction(self.actionAdd_Security_Account)
        self.menu.addSeparator()
        self.menu.addAction(self.actionEdit)
        self.menu.addAction(self.actionDelete)
        self.menu.addSeparator()
        self.menu.addAction(self.actionExpand_All_Below)
        self.menu.addAction(self.actionShow_Selection_Only)
        self.menu.popup(QCursor.pos())

    def finalize_setup(self) -> None:
        self.treeView.header().setSectionResizeMode(
            AccountTreeColumns.COLUMN_NAME,
            QHeaderView.ResizeMode.ResizeToContents,
        )
        self.treeView.header().setSectionResizeMode(
            AccountTreeColumns.COLUMN_BALANCE_NATIVE,
            QHeaderView.ResizeMode.ResizeToContents,
        )
        self.treeView.header().setSectionResizeMode(
            AccountTreeColumns.COLUMN_BALANCE_BASE,
            QHeaderView.ResizeMode.ResizeToContents,
        )
        self.treeView.header().setSectionResizeMode(
            AccountTreeColumns.COLUMN_SHOW,
            QHeaderView.ResizeMode.ResizeToContents,
        )

        self.treeView.selectionModel().selectionChanged.connect(
            self.signal_selection_changed.emit
        )

    def _set_action_icons(self) -> None:
        self.actionExpand_All.setIcon(QIcon("icons_custom:arrow-out.png"))
        self.actionExpand_All_Below.setIcon(QIcon("icons_16:arrow-stop-270.png"))
        self.actionCollapse_All.setIcon(QIcon("icons_16:arrow-in.png"))

        self.actionShow_All.setIcon(QIcon("icons_16:eye.png"))
        self.actionHide_All.setIcon(QIcon("icons_16:eye-close.png"))
        self.actionShow_Selection_Only.setIcon(QIcon("icons_16:eye-red.png"))

        self.actionAdd_Account_Group.setIcon(QIcon("icons_16:folder--plus.png"))
        self.actionAdd_Security_Account.setIcon(QIcon("icons_custom:bank-plus.png"))
        self.actionAdd_Cash_Account.setIcon(QIcon("icons_custom:piggy-bank-plus.png"))

        self.actionEdit.setIcon(QIcon("icons_16:pencil.png"))
        self.actionDelete.setIcon(QIcon("icons_16:minus.png"))

    def _connect_actions(self) -> None:
        self.actionExpand_All.triggered.connect(self.expand_all)
        self.actionExpand_All_Below.triggered.connect(self.signal_expand_below.emit)
        self.actionCollapse_All.triggered.connect(self.collapse_all)

        self.actionShow_All.triggered.connect(self.signal_show_all.emit)
        self.actionShow_Selection_Only.triggered.connect(
            self.signal_show_selection_only.emit
        )
        self.actionHide_All.triggered.connect(self.signal_hide_all.emit)

        self.actionAdd_Account_Group.triggered.connect(
            self.signal_add_account_group.emit
        )
        self.actionAdd_Security_Account.triggered.connect(
            self.signal_add_security_account.emit
        )
        self.actionAdd_Cash_Account.triggered.connect(self.signal_add_cash_account.emit)
        self.actionEdit.triggered.connect(self.signal_edit_item.emit)
        self.actionDelete.triggered.connect(self.signal_delete_item.emit)

        self.expandAllToolButton.setDefaultAction(self.actionExpand_All)
        self.collapseAllToolButton.setDefaultAction(self.actionCollapse_All)

        self.showAllToolButton.setDefaultAction(self.actionShow_All)
        self.hideAllToolButton.setDefaultAction(self.actionHide_All)

        self.addAccountGroupToolButton.setDefaultAction(self.actionAdd_Account_Group)
        self.addCashAccountToolButton.setDefaultAction(self.actionAdd_Cash_Account)
        self.addSecurityAccountToolButton.setDefaultAction(
            self.actionAdd_Security_Account
        )
