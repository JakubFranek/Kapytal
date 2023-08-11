from collections.abc import Collection

from PyQt6.QtCore import QSignalBlocker, Qt
from PyQt6.QtGui import QKeyEvent, QTextCursor
from PyQt6.QtWidgets import QPlainTextEdit, QSizePolicy, QWidget
from src.views.widgets.smart_completer import SmartCompleter

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

        self.completer = SmartCompleter(descriptions)
        self.completer.setWidget(self)
        self.completer.activated.connect(self._handle_completion)
        self.textChanged.connect(self._handle_text_changed)

    def _handle_text_changed(self) -> None:
        prefix = self.toPlainText()
        if len(prefix) > 0 and self.hasFocus():
            self.completer.popup_from_text(prefix)
            return
        self.completer.popup().hide()

    def _handle_completion(self, text: str) -> None:
        with QSignalBlocker(self):
            self.setPlainText(text)
            cursor = self.textCursor()
            cursor.movePosition(QTextCursor.MoveOperation.End)
            self.setTextCursor(cursor)

    def keyPressEvent(self, e: QKeyEvent) -> None:  # noqa: N802
        if self.completer.popup().isVisible() and e.key() in COMPLETER_KEYS:
            e.ignore()  # have QCompleter handle these keys
            return None
        return super().keyPressEvent(e)
