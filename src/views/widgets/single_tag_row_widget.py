from collections.abc import Collection

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QAction, QIcon
from PyQt6.QtWidgets import QCompleter, QHBoxLayout, QLineEdit, QToolButton, QWidget
from src.views.dialogs.select_item_dialog import ask_user_for_selection


class SingleTagRowWidget(QWidget):
    signal_split_tags = pyqtSignal()

    def __init__(self, parent: QWidget | None, tags: Collection[str]) -> None:
        super().__init__(parent)

        self._tags = tuple(tags)

        self.line_edit = QLineEdit(self)
        self.line_edit.setPlaceholderText("Enter Tag names (separator = ;)")
        self._initialize_tags_completer()

        self.select_tool_button = QToolButton(self)
        self.actionSelect_Tag = QAction("Select Tag", self)
        self.actionSelect_Tag.setIcon(QIcon("icons_16:tag.png"))
        self.actionSelect_Tag.triggered.connect(self._select_tag)
        self.select_tool_button.setDefaultAction(self.actionSelect_Tag)

        self.split_tool_button = QToolButton(self)
        self.actionSplit_Tags = QAction("Split Tags", self)
        self.actionSplit_Tags.setIcon(QIcon("icons_16:arrow-split.png"))
        self.actionSplit_Tags.triggered.connect(self.signal_split_tags.emit)
        self.split_tool_button.setDefaultAction(self.actionSplit_Tags)

        self.horizontal_layout = QHBoxLayout(self)
        self.horizontal_layout.addWidget(self.line_edit)
        self.horizontal_layout.addWidget(self.select_tool_button)
        self.horizontal_layout.addWidget(self.split_tool_button)

        self.layout().setContentsMargins(0, 0, 0, 0)

    @property
    def tags(self) -> tuple[str, ...]:
        text = self.line_edit.text()
        return tuple(text.split(";"))

    @tags.setter
    def tags(self, values: Collection[str]) -> None:
        text = "; ".join(values)
        self.line_edit.setText(text)

    def _select_tag(self) -> None:
        tag = ask_user_for_selection(
            self,
            self._tags,
            "Select Tag",
            QIcon("icons_16:tag.png"),
        )
        self.tags = [*self.tags, tag]

    def _initialize_tags_completer(self) -> None:
        self._tags_completer = QCompleter(self._tags)
        self._tags_completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self._tags_completer.setFilterMode(Qt.MatchFlag.MatchContains)
        self._tags_completer.setWidget(self.line_edit)
        self._tags_completer.activated.connect(self._handle_tags_completion)
        self.line_edit.textEdited.connect(self._handle_tags_text_changed)
        self._tags_completing = False

    def _handle_tags_text_changed(self, text: str) -> None:
        if not self._tags_completing:
            found = False
            prefix = text.rpartition(";")[-1].strip()
            if len(prefix) > 0:
                self._tags_completer.setCompletionPrefix(prefix)
                if self._tags_completer.currentRow() >= 0:
                    found = True
            if found:
                self._tags_completer.complete()
            else:
                self._tags_completer.popup().hide()

    def _handle_tags_completion(self, text: str) -> None:
        if not self._tags_completing:
            self._tags_completing = True
            prefix = self._tags_completer.completionPrefix()
            final_text = self.line_edit.text()[: -len(prefix)] + text
            self.line_edit.setText(final_text)
            self._tags_completing = False
