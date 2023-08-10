from collections.abc import Collection

from PyQt6.QtGui import QAction, QIcon
from PyQt6.QtWidgets import QComboBox, QCompleter, QLineEdit, QWidget
from src.views.widgets.smart_completer import SmartCompleter


class SmartComboBox(QComboBox):
    def __init__(
        self,
        parent: QWidget | None = ...,
    ) -> None:
        super().__init__(parent)

        self.setEditable(True)
        self.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)
        self.setCompleter(None)

        self.editTextChanged.connect(self._handle_text_changed)

    def load_items(
        self,
        items: Collection[str],
        icon: QIcon | None = None,
        placeholder_text: str | None = None,
        *,
        keep_current_text: bool = False
    ) -> None:
        current_text = self.currentText()
        _items = sorted(items, key=str.lower)
        self.clear()
        for item in _items:
            self.addItem(item)
        if icon is not None:
            if hasattr(self, "_line_edit_action"):
                self.lineEdit().removeAction(self._line_edit_action)
            self._line_edit_action = QAction(icon, "", self)
            self.lineEdit().addAction(
                self._line_edit_action, QLineEdit.ActionPosition.LeadingPosition
            )

        if placeholder_text is not None:
            _placeholder_text = placeholder_text
            self.lineEdit().setPlaceholderText(placeholder_text)
        else:
            _placeholder_text = self.lineEdit().placeholderText()

        if keep_current_text:
            self.setCurrentText(current_text)
        elif len(_items) > 0:
            if _placeholder_text:
                self.setCurrentText("")
            else:
                self.setCurrentText(_items[0])
        elif len(_items) == 0:
            self.setCurrentText("")

        self._completer = SmartCompleter(_items, self)
        self._completer.setCompletionMode(QCompleter.CompletionMode.PopupCompletion)
        self._completer.activated.connect(self._handle_completion)
        self._completer.setWidget(self)

    def _handle_text_changed(self) -> None:
        if not hasattr(self, "_completer"):
            return

        prefix = self.lineEdit().text()
        if len(prefix) > 0 and self.hasFocus():
            self._completer.popup_from_text(prefix)
        else:
            self._completer.popup().hide()

    def _handle_completion(self, text: str) -> None:
        self.setCurrentText(text)
