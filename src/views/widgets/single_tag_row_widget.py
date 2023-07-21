from collections.abc import Collection

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QAction
from PyQt6.QtWidgets import QHBoxLayout, QToolButton, QWidget
from src.views import icons
from src.views.widgets.multiple_tags_selector_widget import MultipleTagsSelectorWidget


class SingleTagRowWidget(QWidget):
    signal_split_tags = pyqtSignal()

    def __init__(self, parent: QWidget | None, tag_names: Collection[str]) -> None:
        super().__init__(parent)

        self._tag_names = tuple(tag_names)

        self.tags_widget = MultipleTagsSelectorWidget(self, tag_names)

        self.split_tool_button = QToolButton(self)
        self.actionSplit_Tags = QAction("Split Tags", self)
        self.actionSplit_Tags.setIcon(icons.split_attribute)
        self.actionSplit_Tags.triggered.connect(self.signal_split_tags.emit)
        self.split_tool_button.setDefaultAction(self.actionSplit_Tags)

        self.horizontal_layout = QHBoxLayout(self)
        self.horizontal_layout.addWidget(self.tags_widget)
        self.horizontal_layout.addWidget(self.split_tool_button)

        self.layout().setContentsMargins(0, 0, 0, 0)

        self.setFocusPolicy(Qt.FocusPolicy.TabFocus)
        self.setFocusProxy(self.tags_widget)
        self.enable_split(enable=True)

    @property
    def tag_names(self) -> tuple[str, ...]:
        return self.tags_widget.tag_names

    @tag_names.setter
    def tag_names(self, values: Collection[str]) -> None:
        self.tags_widget.tag_names = values

    def enable_split(self, *, enable: bool) -> None:
        self._split_enabled = enable
        self.actionSplit_Tags.setEnabled(enable)

    def set_placeholder_text(self, text: str) -> None:
        self.tags_widget.set_placeholder_text(text)
