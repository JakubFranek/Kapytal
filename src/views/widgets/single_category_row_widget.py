from collections.abc import Collection

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QAction, QIcon
from PyQt6.QtWidgets import QComboBox, QHBoxLayout, QToolButton, QWidget
from src.views.dialogs.select_item_dialog import ask_user_for_selection


class SingleCategoryRowWidget(QWidget):
    signal_split_categories = pyqtSignal()

    def __init__(self, parent: QWidget | None, *, edit: bool) -> None:
        super().__init__(parent)
        self._edit = edit

        self.combo_box = QComboBox(self)
        self.combo_box.setEditable(True)
        self.require_category(required=not edit)
        self.combo_box.setToolTip("Both existing or new Category paths are valid")

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

        self.setFocusPolicy(Qt.FocusPolicy.TabFocus)
        self.setFocusProxy(self.combo_box)
        self.enable_split(enable=True)

    @property
    def category(self) -> str | None:
        text = self.combo_box.currentText()
        return text if text or not self._edit else None

    @category.setter
    def category(self, value: str) -> None:
        self.combo_box.setCurrentText(value)

    def enable_split(self, *, enable: bool) -> None:
        self._split_enabled = enable
        self.actionSplit_Categories.setEnabled(enable)

    def require_category(self, *, required: bool) -> None:
        if not required:
            self.combo_box.lineEdit().setPlaceholderText(
                "Leave empty to keep current values"
            )
        else:
            self.combo_box.lineEdit().setPlaceholderText("Enter Category path")

    def load_categories(self, categories: Collection[str]) -> None:
        current_text = self.category
        self._combo_box_items = categories
        self.combo_box.clear()
        for item in categories:
            self.combo_box.addItem(item)
        if current_text in categories:
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
        if category:
            self.combo_box.setCurrentText(category)
