from collections.abc import Collection

from PyQt6 import QtGui
from PyQt6.QtCore import (
    QEvent,
    QObject,
    QSignalBlocker,
    QStringListModel,
    Qt,
    pyqtSignal,
)
from PyQt6.QtGui import QKeyEvent, QTextCursor
from PyQt6.QtWidgets import (
    QCompleter,
    QLabel,
    QPlainTextEdit,
    QSizePolicy,
    QSpacerItem,
    QVBoxLayout,
    QWidget,
)

COMPLETER_KEYS = (
    Qt.Key.Key_Enter,
    Qt.Key.Key_Return,
    Qt.Key.Key_Escape,
    Qt.Key.Key_Tab,
    Qt.Key.Key_Backtab,
)


class DescriptionCompleter(QCompleter):
    def __init__(
        self, descriptions: Collection[str], parent: QWidget | None = None
    ) -> None:
        super().__init__(descriptions, parent)
        self._descriptions: tuple[str] = tuple(sorted(descriptions, key=str.lower))
        self._matches_cache: dict[str, tuple[str]] = {}
        self._model = QStringListModel(descriptions)
        self.setModel(self._model)

    def update(self, text: str) -> None:
        lowered_text = text.lower()

        if lowered_text in self._matches_cache:
            matches = self._matches_cache[lowered_text]
            self._model.setStringList(matches)
            self.complete()
            return

        _descriptions = self._matches_cache.get(lowered_text[:-1], self._descriptions)

        matches: list[str] = []
        _not_start_with: list[str] = []
        for description in _descriptions:
            lowered_description = description.lower()
            if lowered_description.startswith(lowered_text):
                matches.append(description)
            elif lowered_text in lowered_description:
                _not_start_with.append(description)

        matches.extend(_not_start_with)
        self._matches_cache[lowered_text] = tuple(matches)

        self._model.setStringList(matches)
        self.complete()


class DescriptionPlainTextEdit(QPlainTextEdit):
    def __init__(
        self,
        descriptions: Collection[str],
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.setTabChangesFocus(True)
        self.setPlaceholderText("Enter optional description")
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.setMinimumHeight(50)

        self.completer = DescriptionCompleter(descriptions)
        self.completer.setWidget(self)
        self.completer.activated.connect(self._handle_completion)
        self.textChanged.connect(self._handle_text_changed)

        self._completing = False

    def _handle_text_changed(self) -> None:
        if not self._completing:
            prefix = self.toPlainText()
            if len(prefix) > 0:
                self.completer.update(prefix)
                return
            self.completer.popup().hide()

    def _handle_completion(self, text: str) -> None:
        self._completing = True
        self.setPlainText(text)
        cursor = self.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        self.setTextCursor(cursor)
        self._completing = False

    def keyPressEvent(self, e: QKeyEvent) -> None:
        if self.completer.popup().isVisible() and e.key() in COMPLETER_KEYS:
            e.ignore()  # have QCompleter handle these keys
            return None
        return super().keyPressEvent(e)
