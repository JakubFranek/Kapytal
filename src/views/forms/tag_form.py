import logging

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QCloseEvent
from PyQt6.QtWidgets import QHeaderView, QLineEdit, QWidget
from src.views import icons
from src.views.constants import TagTableColumn
from src.views.ui_files.forms.Ui_tag_form import Ui_TagForm


# TODO: change visual style from side buttons to tool buttons and context menu
class TagForm(QWidget, Ui_TagForm):
    signal_add_tag = pyqtSignal()
    signal_rename_tag = pyqtSignal()
    signal_remove_tag = pyqtSignal()
    signal_select_tag = pyqtSignal()
    signal_search_text_changed = pyqtSignal(str)
    signal_selection_changed = pyqtSignal()

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent=parent)
        self.setupUi(self)
        self.setWindowFlag(Qt.WindowType.Window)
        self.setWindowIcon(icons.tag)

        self._initialize_actions()
        self.searchLineEdit.textChanged.connect(self.signal_search_text_changed.emit)

        self.searchLineEdit.addAction(
            icons.magnifier, QLineEdit.ActionPosition.LeadingPosition
        )

    @property
    def search_bar_text(self) -> str:
        return self.searchLineEdit.text()

    def show_form(self) -> None:
        logging.debug(f"Showing {self.__class__.__name__}")
        self.tableView.resizeColumnsToContents()
        self.show()

    def closeEvent(self, a0: QCloseEvent) -> None:  # noqa: N802
        logging.debug(f"Closing {self.__class__.__name__}")
        return super().closeEvent(a0)

    def enable_actions(
        self, *, is_tag_selected: bool, is_one_tag_selected: bool
    ) -> None:
        self.actionRename_Tag.setEnabled(is_one_tag_selected)
        self.actionRemove_Tag.setEnabled(is_tag_selected)

    def finalize_setup(self) -> None:
        self.tableView.horizontalHeader().setStretchLastSection(False)
        self.tableView.horizontalHeader().setSectionResizeMode(
            TagTableColumn.NAME,
            QHeaderView.ResizeMode.ResizeToContents,
        )
        self.tableView.horizontalHeader().setSectionResizeMode(
            TagTableColumn.TRANSACTIONS,
            QHeaderView.ResizeMode.ResizeToContents,
        )
        self.tableView.horizontalHeader().setSectionResizeMode(
            TagTableColumn.BALANCE,
            QHeaderView.ResizeMode.Stretch,
        )

        style = self.style()
        last_section_text = self.tableView.model().headerData(
            TagTableColumn.BALANCE,
            Qt.Orientation.Horizontal,
            Qt.ItemDataRole.DisplayRole,
        )
        self.tableView.horizontalHeader().setMinimumSectionSize(
            style.pixelMetric(style.PixelMetric.PM_HeaderMarkSize)
            + style.pixelMetric(style.PixelMetric.PM_HeaderGripMargin) * 2
            + self.fontMetrics().horizontalAdvance(last_section_text)
        )

        self.tableView.selectionModel().selectionChanged.connect(
            self.signal_selection_changed.emit
        )
        self.tableView.sortByColumn(0, Qt.SortOrder.AscendingOrder)

    def _initialize_actions(self) -> None:
        self.actionAdd_Tag.setIcon(icons.add_tag)
        self.actionRename_Tag.setIcon(icons.edit_tag)
        self.actionRemove_Tag.setIcon(icons.remove_tag)

        self.actionAdd_Tag.triggered.connect(self.signal_add_tag.emit)
        self.actionRename_Tag.triggered.connect(self.signal_rename_tag.emit)
        self.actionRemove_Tag.triggered.connect(self.signal_remove_tag.emit)

        self.addToolButton.setDefaultAction(self.actionAdd_Tag)
        self.renameToolButton.setDefaultAction(self.actionRename_Tag)
        self.removeToolButton.setDefaultAction(self.actionRemove_Tag)
