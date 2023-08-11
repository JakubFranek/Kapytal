from collections.abc import Collection

from PyQt6.QtCore import QSignalBlocker, Qt, pyqtSignal
from PyQt6.QtGui import QAction
from PyQt6.QtWidgets import QHBoxLayout, QToolButton, QWidget
from src.views import icons
from src.views.widgets.smart_combo_box import SmartComboBox


class SingleCategoryRowWidget(QWidget):
    signal_split_categories = pyqtSignal()

    def __init__(self, parent: QWidget | None) -> None:
        super().__init__(parent)

        self.combo_box = SmartComboBox(parent=self)
        self.combo_box.setToolTip("Both existing or new Category paths are valid")
        self.require_category(required=True)  # default value

        self.split_tool_button = QToolButton(self)
        self.actionSplit_Categories = QAction("Split Categories", self)
        self.actionSplit_Categories.setIcon(icons.split_attribute)
        self.actionSplit_Categories.triggered.connect(self.signal_split_categories.emit)
        self.split_tool_button.setDefaultAction(self.actionSplit_Categories)

        self.horizontal_layout = QHBoxLayout(self)
        self.horizontal_layout.addWidget(self.combo_box)
        self.horizontal_layout.addWidget(self.split_tool_button)

        self.layout().setContentsMargins(0, 0, 0, 0)

        self.setFocusPolicy(Qt.FocusPolicy.TabFocus)
        self.setFocusProxy(self.combo_box)
        self.enable_split(enable=True)

    @property
    def category(self) -> str | None:
        text = self.combo_box.currentText()
        return text if text else None

    @category.setter
    def category(self, value: str) -> None:
        with QSignalBlocker(self.combo_box):
            self.combo_box.setCurrentText(value)

    def enable_split(self, *, enable: bool) -> None:
        self._split_enabled = enable
        self.actionSplit_Categories.setEnabled(enable)

    def require_category(self, *, required: bool) -> None:
        if not required:
            self._set_placeholder_text("Leave empty to keep current values")
        else:
            self._set_placeholder_text("Enter Category path")

    def load_categories(
        self, categories: Collection[str], *, keep_current_text: bool
    ) -> None:
        self.combo_box.load_items(
            categories,
            icons.category,
            keep_current_text=keep_current_text,
        )

    def _set_placeholder_text(self, text: str) -> None:
        self.combo_box.lineEdit().setPlaceholderText(text)
