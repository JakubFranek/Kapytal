from collections.abc import Collection

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QAction
from PyQt6.QtWidgets import QComboBox, QCompleter, QHBoxLayout, QToolButton, QWidget
from src.views import icons
from src.views.widgets.smart_completer import SmartCompleter


class SingleCategoryRowWidget(QWidget):
    signal_split_categories = pyqtSignal()

    def __init__(self, parent: QWidget | None, *, edit: bool) -> None:
        super().__init__(parent)
        self._edit = edit

        self.combo_box = QComboBox(self)
        self.combo_box.setEditable(True)
        self.require_category(required=not edit)
        self.combo_box.setToolTip("Both existing or new Category paths are valid")

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

    def load_categories(
        self, categories: Collection[str], *, keep_current_text: bool
    ) -> None:
        current_text = self.category
        self._categories = sorted(categories, key=str.lower)
        self.combo_box.clear()
        for item in self._categories:
            self.combo_box.addItem(item)
        if keep_current_text:
            self.combo_box.setCurrentText(current_text)
        else:
            self.combo_box.setCurrentIndex(-1)

        self._completer = SmartCompleter(self._categories, self)
        self._completer.setCompletionMode(QCompleter.CompletionMode.PopupCompletion)
        self._completer.activated.connect(self._handle_completion)
        self._completer.setWidget(self.combo_box.lineEdit())
        self.combo_box.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)
        self.combo_box.editTextChanged.connect(self._handle_text_changed)

        self._completing = False

    def _handle_text_changed(self) -> None:
        if not self._completing:
            prefix = self.combo_box.lineEdit().text()
            if len(prefix) > 0:
                self._completer.update(prefix)
                return
            self._completer.popup().hide()

    def _handle_completion(self, text: str) -> None:
        self._completing = True
        self.combo_box.setCurrentText(text)
        self._completing = False
