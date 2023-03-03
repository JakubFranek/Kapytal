import logging

from PyQt6 import QtGui
from PyQt6.QtCore import pyqtSignal
from PyQt6.QtGui import QContextMenuEvent, QCursor, QIcon
from PyQt6.QtWidgets import QHeaderView, QMenu, QTreeView, QWidget

from src.views.constants import CategoryTreeColumns


class CategoryTree(QTreeView):
    signal_selection_changed = pyqtSignal()
    signal_expand_below = pyqtSignal()
    signal_delete_category = pyqtSignal()
    signal_add_category = pyqtSignal()
    signal_edit_category = pyqtSignal()

    def __init__(self, parent: QWidget | None = ...) -> None:
        super().__init__(parent)

        self.setObjectName("categoryTree")
        self.header().setSortIndicatorShown(False)
        self.header().setStretchLastSection(False)

        self.actionAdd_Category = QtGui.QAction(self)
        self.actionAdd_Category.setText("Add Category")
        self.actionEdit_Category = QtGui.QAction(self)
        self.actionEdit_Category.setText("Edit")
        self.actionDelete_Category = QtGui.QAction(self)
        self.actionDelete_Category.setText("Delete")
        self.actionExpand_All = QtGui.QAction(self)
        self.actionExpand_All.setText("Expand All")
        self.actionExpand_All_Below = QtGui.QAction(self)
        self.actionExpand_All_Below.setText("Expand All Below")
        self.actionCollapse_All = QtGui.QAction(self)
        self.actionCollapse_All.setText("Collapse All")

        self.actionExpand_All.setIcon(QIcon("icons_custom:arrow-out.png"))
        self.actionExpand_All_Below.setIcon(QIcon("icons_16:arrow-stop-270.png"))
        self.actionCollapse_All.setIcon(QIcon("icons_16:arrow-in.png"))
        self.actionAdd_Category.setIcon(QIcon("icons_custom:category-plus.png"))
        self.actionEdit_Category.setIcon(QIcon("icons_16:pencil.png"))
        self.actionDelete_Category.setIcon(QIcon("icons_16:minus.png"))

        self.actionExpand_All.triggered.connect(self._expand_all)
        self.actionExpand_All_Below.triggered.connect(self.signal_expand_below.emit)
        self.actionCollapse_All.triggered.connect(self._collapse_all)
        self.actionDelete_Category.triggered.connect(self.signal_delete_category.emit)
        self.actionAdd_Category.triggered.connect(self.signal_add_category.emit)
        self.actionEdit_Category.triggered.connect(self.signal_edit_category.emit)

        self.contextMenuEvent = self.create_context_menu

    def expand_all(self) -> None:
        self.expandAll()

    def collapse_all(self) -> None:
        self.collapseAll()

    def enable_actions(
        self,
        enable_add_objects: bool,
        enable_modify_object: bool,
        enable_expand_below: bool,
    ) -> None:
        self.actionAdd_Category.setEnabled(enable_add_objects)
        self.actionEdit_Category.setEnabled(enable_modify_object)
        self.actionDelete_Category.setEnabled(enable_modify_object)
        self.actionExpand_All_Below.setEnabled(enable_expand_below)

    def create_context_menu(self, event: QContextMenuEvent) -> None:  # noqa: U100
        self.menu = QMenu(self)
        self.menu.addAction(self.actionAdd_Category)
        self.menu.addAction(self.actionEdit_Category)
        self.menu.addAction(self.actionDelete_Category)
        self.menu.addSeparator()
        self.menu.addAction(self.actionExpand_All_Below)
        self.menu.popup(QCursor.pos())

    def finalize_setup(self) -> None:
        self.header().setSectionResizeMode(
            CategoryTreeColumns.COLUMN_NAME,
            QHeaderView.ResizeMode.ResizeToContents,
        )
        self.header().setSectionResizeMode(
            CategoryTreeColumns.COLUMN_TRANSACTIONS,
            QHeaderView.ResizeMode.ResizeToContents,
        )
        self.header().setSectionResizeMode(
            CategoryTreeColumns.COLUMN_BALANCE,
            QHeaderView.ResizeMode.Stretch,
        )

        self.selectionModel().selectionChanged.connect(
            self.signal_selection_changed.emit
        )

    def _expand_all(self) -> None:
        logging.debug("Expanding all CategoryTree nodes")
        self.expand_all()

    def _collapse_all(self) -> None:
        logging.debug("Collapsing all CategoryTree nodes")
        self.collapse_all()
