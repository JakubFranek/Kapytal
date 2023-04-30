import logging

from PyQt6.QtCore import QEvent, QObject, Qt, pyqtSignal
from PyQt6.QtGui import QContextMenuEvent, QCursor, QKeyEvent, QMouseEvent
from PyQt6.QtWidgets import QHeaderView, QMenu, QWidget
from src.views import icons
from src.views.constants import AccountTreeColumn
from src.views.ui_files.widgets.Ui_account_tree_widget import Ui_AccountTreeWidget


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

        self.treeView.installEventFilter(self)
        self.treeView.viewport().installEventFilter(self)

    def eventFilter(self, source: QObject, event: QEvent) -> bool:  # noqa: N802
        if (
            source is self.treeView
            and isinstance(event, QKeyEvent)
            and event.key() == Qt.Key.Key_Escape
            and event.modifiers() == Qt.KeyboardModifier.NoModifier
        ) or (
            source is self.treeView.viewport()
            and isinstance(event, QMouseEvent)
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
    ) -> None:
        self.actionAdd_Account_Group.setEnabled(enable_add_objects)
        self.actionAdd_Security_Account.setEnabled(enable_add_objects)
        self.actionAdd_Cash_Account.setEnabled(enable_add_objects)
        self.actionEdit.setEnabled(enable_modify_object)
        self.actionDelete.setEnabled(enable_modify_object)
        self.actionExpand_All_Below.setEnabled(enable_expand_below)
        self.actionShow_Selection_Only.setEnabled(enable_modify_object)

    def _create_context_menu(self, event: QContextMenuEvent) -> None:
        del event
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

        self.actionShow_All.setIcon(icons.eye_open)
        self.actionHide_All.setIcon(icons.eye_closed)
        self.actionShow_Selection_Only.setIcon(icons.eye_red)

        self.actionAdd_Account_Group.setIcon(icons.add_account_group)
        self.actionAdd_Security_Account.setIcon(icons.add_security_account)
        self.actionAdd_Cash_Account.setIcon(icons.add_cash_account)

        self.actionEdit.setIcon(icons.edit)
        self.actionDelete.setIcon(icons.remove)

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
