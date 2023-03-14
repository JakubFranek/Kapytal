from collections.abc import Collection
from enum import Enum, auto

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtGui import QAction, QIcon
from PyQt6.QtWidgets import QComboBox, QDoubleSpinBox, QHBoxLayout, QToolButton, QWidget

from src.views.dialogs.select_item_dialog import ask_user_for_selection


class ItemType(Enum):
    CATEGORY = auto()
    TAG = auto()


class SplitItemRowWidget(QWidget):
    signal_remove_row = pyqtSignal(QWidget)

    def __init__(self, type_: ItemType, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.type_ = type_

        self.combo_box = QComboBox(self)
        self.combo_box.setEditable(True)
        if type_ == ItemType.CATEGORY:
            self.combo_box.lineEdit().setPlaceholderText("Enter Category path")
        else:
            self.combo_box.lineEdit().setPlaceholderText("Enter Tag path")

        self.select_tool_button = QToolButton(self)
        if type_ == ItemType.CATEGORY:
            self.actionSelect_Item = QAction("Select Category", self)
            self.actionSelect_Item.setIcon(QIcon("icons_custom:category.png"))
        else:
            self.actionSelect_Item = QAction("Select Tag", self)
            self.actionSelect_Item.setIcon(QIcon("icons_16:tag.png"))
        self.actionSelect_Item.triggered.connect(self._select_item)
        self.select_tool_button.setDefaultAction(self.actionSelect_Item)

        self.double_spin_box = QDoubleSpinBox(self)

        self.remove_tool_button = QToolButton(self)
        self.actionRemove_Row = QAction("Remove", self)
        self.actionRemove_Row.setIcon(QIcon("icons_16:minus.png"))
        self.actionRemove_Row.triggered.connect(
            lambda: self.signal_remove_row.emit(self)
        )
        self.remove_tool_button.setDefaultAction(self.actionRemove_Row)

        self.horizontal_layout = QHBoxLayout(self)
        self.horizontal_layout.addWidget(self.combo_box)
        self.horizontal_layout.addWidget(self.select_tool_button)
        self.horizontal_layout.addWidget(self.double_spin_box)
        self.horizontal_layout.addWidget(self.remove_tool_button)

        self.layout().setContentsMargins(0, 0, 0, 0)

    @property
    def category(self) -> str:
        return self.combo_box.currentText()

    @category.setter
    def category(self, value: str) -> None:
        self.combo_box.setCurrentText(value)

    def load_categories(self, items: Collection[str]) -> None:
        self._combo_box_items = items
        self.combo_box.clear()
        for item in items:
            self.combo_box.addItem(item)
        self.combo_box.setCurrentIndex(-1)

    def _select_item(self) -> None:
        if self.type_ == ItemType.CATEGORY:
            text = "Select Category"
            icon = QIcon("icons_custom:category.png")
        else:
            text = "Select Tag"
            icon = QIcon("icons_custom:category.png")

        item = ask_user_for_selection(
            self,
            self._combo_box_items,
            text,
            icon,
        )
        self.combo_box.setCurrentText(item)
