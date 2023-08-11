from collections.abc import Collection

from PyQt6.QtCore import QSignalBlocker, Qt, pyqtSignal
from PyQt6.QtGui import QAction
from PyQt6.QtWidgets import QHBoxLayout, QLineEdit, QToolButton, QWidget
from src.views import icons
from src.views.dialogs.select_item_dialog import ask_user_for_selection
from src.views.widgets.smart_completer import SmartCompleter


class MultipleTagsSelectorWidget(QWidget):
    signal_split_tags = pyqtSignal()

    def __init__(self, parent: QWidget | None, tag_names: Collection[str]) -> None:
        super().__init__(parent)

        self._tag_names = tuple(sorted(tag_names, key=str.lower))

        self.line_edit = QLineEdit(self)
        self.line_edit.setPlaceholderText("Enter optional Tags (separated by ';')")
        self.line_edit.setToolTip("Both existing or new Tags are valid")
        self.line_edit.addAction(icons.tag, QLineEdit.ActionPosition.LeadingPosition)
        self.line_edit.setMinimumWidth(250)
        self._initialize_tags_completer()

        self.select_tool_button = QToolButton(self)
        self.actionSelect_Tag = QAction("Find && Select Tag", self)
        self.actionSelect_Tag.setIcon(icons.magnifier)
        self.actionSelect_Tag.triggered.connect(self._select_tag)
        self.select_tool_button.setDefaultAction(self.actionSelect_Tag)

        self.horizontal_layout = QHBoxLayout(self)
        self.horizontal_layout.addWidget(self.line_edit)
        self.horizontal_layout.addWidget(self.select_tool_button)

        self.layout().setContentsMargins(0, 0, 0, 0)

        self.setFocusPolicy(Qt.FocusPolicy.TabFocus)
        self.setFocusProxy(self.line_edit)

    @property
    def tag_names(self) -> tuple[str, ...]:
        text = self.line_edit.text()
        tag_names = text.split(";")
        return tuple(tag_name.strip() for tag_name in tag_names if tag_name)

    @tag_names.setter
    def tag_names(self, values: Collection[str]) -> None:
        text = "; ".join(values)
        self.line_edit.setText(text)

    def set_placeholder_text(self, text: str) -> None:
        self.line_edit.setPlaceholderText(text)

    def _select_tag(self) -> None:
        tag = ask_user_for_selection(
            self,
            self._tag_names,
            "Select Tag",
            icons.tag,
        )
        if tag and self.tag_names != ("",):
            if tag not in self.tag_names:
                self.tag_names = [*self.tag_names, tag]
        elif tag:
            self.tag_names = [tag]

    def _initialize_tags_completer(self) -> None:
        self._tags_completer = SmartCompleter(self._tag_names, self)
        self._tags_completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self._tags_completer.setFilterMode(Qt.MatchFlag.MatchContains)
        self._tags_completer.setWidget(self.line_edit)
        self._tags_completer.activated.connect(self._handle_tags_completion)
        self.line_edit.textEdited.connect(self._handle_tags_text_changed)

    def _handle_tags_text_changed(self, text: str) -> None:
        prefix = text.rpartition(";")[-1].strip()
        if len(prefix) > 0 and self.line_edit.hasFocus():
            self._prefix = prefix
            self._tags_completer.popup_from_text(prefix)
        else:
            self._tags_completer.popup().hide()

    def _handle_tags_completion(self, text: str) -> None:
        with QSignalBlocker(self.line_edit):
            prefix = self._prefix
            current_text = self.line_edit.text()
            completed_text = current_text[: -len(prefix)] + text
            tag_names = completed_text.split(";")
            tag_names = [tag_name.strip() for tag_name in tag_names]
            final_text = "; ".join(tag_names)
            self.line_edit.setText(final_text)
