import logging

from PyQt6 import QtGui
from PyQt6.QtCore import pyqtSignal
from PyQt6.QtGui import QContextMenuEvent, QCursor
from PyQt6.QtWidgets import QHeaderView, QMenu, QTreeView, QWidget
from src.views import icons
from src.views.constants import CategoryTreeColumn


class CategoryTree(QTreeView):
    signal_selection_changed = pyqtSignal()
    signal_expand_below = pyqtSignal()
    signal_delete_category = pyqtSignal()
    signal_add_category = pyqtSignal()
    signal_edit_category = pyqtSignal()

    def __init__(self, parent: QWidget | None = ...) -> None:
        super().__init__(parent)

        self.setUniformRowHeights(True)

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

        self.actionExpand_All.setIcon(icons.expand)
        self.actionExpand_All_Below.setIcon(icons.expand_below)
        self.actionCollapse_All.setIcon(icons.collapse)
        self.actionAdd_Category.setIcon(icons.add_category)
        self.actionEdit_Category.setIcon(icons.edit)
        self.actionDelete_Category.setIcon(icons.remove)

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
        *,
        enable_add_objects: bool,
        enable_modify_object: bool,
        enable_expand_below: bool,
    ) -> None:
        self.actionAdd_Category.setEnabled(enable_add_objects)
        self.actionEdit_Category.setEnabled(enable_modify_object)
        self.actionDelete_Category.setEnabled(enable_modify_object)
        self.actionExpand_All_Below.setEnabled(enable_expand_below)

    def create_context_menu(self, event: QContextMenuEvent) -> None:
        del event
        self.menu = QMenu(self)
        self.menu.addAction(self.actionAdd_Category)
        self.menu.addAction(self.actionEdit_Category)
        self.menu.addAction(self.actionDelete_Category)
        self.menu.addSeparator()
        self.menu.addAction(self.actionExpand_All_Below)
        self.menu.popup(QCursor.pos())

    def finalize_setup(self) -> None:
        self.header().setSectionResizeMode(
            CategoryTreeColumn.NAME,
            QHeaderView.ResizeMode.ResizeToContents,
        )
        self.header().setSectionResizeMode(
            CategoryTreeColumn.TRANSACTIONS,
            QHeaderView.ResizeMode.ResizeToContents,
        )
        self.header().setSectionResizeMode(
            CategoryTreeColumn.BALANCE,
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
