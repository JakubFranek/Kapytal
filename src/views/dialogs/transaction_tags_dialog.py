import logging
from collections.abc import Collection

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QAction, QIcon
from PyQt6.QtWidgets import (
    QAbstractButton,
    QCompleter,
    QDialog,
    QDialogButtonBox,
    QWidget,
)
from src.views.dialogs.select_item_dialog import ask_user_for_selection
from src.views.ui_files.dialogs.Ui_transaction_tags_dialog import (
    Ui_TransactionTagsDialog,
)


class TransactionTagsDialog(QDialog, Ui_TransactionTagsDialog):
    signal_ok = pyqtSignal()

    def __init__(
        self, parent: QWidget, tag_names: Collection[str], *, add: bool
    ) -> None:
        super().__init__(parent=parent)
        self.setupUi(self)

        self._tags = tuple(tag_names)
        self._initialize_tags_completer()

        self.actionSelect_Tag = QAction("Select Tag", self)
        self.actionSelect_Tag.setIcon(QIcon("icons_16:tag.png"))
        self.actionSelect_Tag.triggered.connect(self._select_tag)
        self.selectTagToolButton.setDefaultAction(self.actionSelect_Tag)

        if add:
            self.setWindowTitle("Add Tags")
            self.setWindowIcon(QIcon("icons_16:tag--plus.png"))
        else:
            self.setWindowTitle("Remove Tags")
            self.setWindowIcon(QIcon("icons_16:tag--minus.png"))

        self.buttonBox.clicked.connect(self._handle_button_box_click)

    @property
    def tags(self) -> tuple[str]:
        text = self.tagsLineEdit.text()
        tag_names = text.split(";")
        return tuple(tag_name.strip() for tag_name in tag_names if tag_name)

    @tags.setter
    def tags(self, values: Collection[str]) -> None:
        text = "; ".join(values)
        self.tagsLineEdit.setText(text)

    def reject(self) -> None:
        logging.debug(f"Closing {self.__class__.__name__}")
        return super().reject()

    def _select_tag(self) -> None:
        tag = ask_user_for_selection(
            self,
            self._tags,
            "Select Tag",
            QIcon("icons_16:tag.png"),
        )
        if tag and self.tags != ("",):
            self.tags = [*self.tags, tag]
        elif tag:
            self.tags = [tag]

    def _handle_button_box_click(self, button: QAbstractButton) -> None:
        role = self.buttonBox.buttonRole(button)
        if role == QDialogButtonBox.ButtonRole.AcceptRole:
            self.signal_ok.emit()
        elif role == QDialogButtonBox.ButtonRole.RejectRole:
            self.reject()
        else:
            raise ValueError("Unknown role of the clicked button in the ButtonBox")

    def _initialize_tags_completer(self) -> None:
        self._tags_completer = QCompleter(self._tags)
        self._tags_completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self._tags_completer.setFilterMode(Qt.MatchFlag.MatchContains)
        self._tags_completer.setWidget(self.tagsLineEdit)
        self._tags_completer.activated.connect(self._handle_tags_completion)
        self.tagsLineEdit.textEdited.connect(self._handle_tags_text_changed)
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
            current_text = self.tagsLineEdit.text()
            completed_text = current_text[: -len(prefix)] + text
            tag_names = completed_text.split(";")
            tag_names = [tag_name.strip() for tag_name in tag_names]
            final_text = "; ".join(tag_names)
            self.tagsLineEdit.setText(final_text)
            self._tags_completing = False
