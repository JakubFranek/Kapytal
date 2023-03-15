from collections.abc import Collection

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtGui import QAction, QIcon
from PyQt6.QtWidgets import QComboBox, QHBoxLayout, QToolButton, QWidget

from src.views.dialogs.select_item_dialog import ask_user_for_selection


class SingleCategoryRowWidget(QWidget):
    signal_split_categories = pyqtSignal()

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)

        self.combo_box = QComboBox(self)
        self.combo_box.setEditable(True)
        self.combo_box.lineEdit().setPlaceholderText("Enter Category path")

        self.select_tool_button = QToolButton(self)
        self.actionSelect_Category = QAction("Select Category", self)
        self.actionSelect_Category.setIcon(QIcon("icons_custom:category.png"))
        self.actionSelect_Category.triggered.connect(self._select_category)
        self.select_tool_button.setDefaultAction(self.actionSelect_Category)

        self.split_tool_button = QToolButton(self)
        self.actionSplit_Categories = QAction("Split Categories", self)
        self.actionSplit_Categories.setIcon(QIcon("icons_16:arrow-split.png"))
        self.actionSplit_Categories.triggered.connect(self.signal_split_categories.emit)
        self.split_tool_button.setDefaultAction(self.actionSplit_Categories)

        self.horizontal_layout = QHBoxLayout(self)
        self.horizontal_layout.addWidget(self.combo_box)
        self.horizontal_layout.addWidget(self.select_tool_button)
        self.horizontal_layout.addWidget(self.split_tool_button)

        self.layout().setContentsMargins(0, 0, 0, 0)

    @property
    def category(self) -> str:
        return self.combo_box.currentText()

    @category.setter
    def category(self, value: str) -> None:
        self.combo_box.setCurrentText(value)

    def load_categories(self, items: Collection[str]) -> None:
        current_text = self.category
        self._combo_box_items = items
        self.combo_box.clear()
        for item in items:
            self.combo_box.addItem(item)
        if current_text in items:
            self.combo_box.setCurrentText(current_text)
        else:
            self.combo_box.setCurrentIndex(-1)

    def _select_category(self) -> None:
        category = ask_user_for_selection(
            self,
            self._combo_box_items,
            "Select Category",
            QIcon("icons_custom:category.png"),
        )
        self.combo_box.setCurrentText(category)
