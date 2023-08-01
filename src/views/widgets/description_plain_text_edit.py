from collections.abc import Collection

from PyQt6 import QtGui
from PyQt6.QtCore import QEvent, QObject, QSignalBlocker, Qt, pyqtSignal
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

        self.completer = QCompleter(descriptions)
        self.completer.setFilterMode(Qt.MatchFlag.MatchContains)
        self.completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self.completer.setWidget(self)
        self.completer.activated.connect(self._handle_completion)
        self.textChanged.connect(self._handle_text_changed)

        self._completing = False

    def _handle_text_changed(self) -> None:
        if not self._completing:
            prefix = self.toPlainText()
            if len(prefix) > 0:
                self.completer.setCompletionPrefix(prefix)
                if self.completer.currentRow() >= 0:
                    self.completer.complete()
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
