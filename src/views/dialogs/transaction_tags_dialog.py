import logging
from collections.abc import Collection

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import (
    QAbstractButton,
    QDialogButtonBox,
    QFormLayout,
    QLabel,
    QWidget,
)
from src.views import icons
from src.views.base_classes.custom_dialog import CustomDialog
from src.views.widgets.multiple_tags_selector_widget import MultipleTagsSelectorWidget


class TransactionTagsDialog(CustomDialog):
    signal_ok = pyqtSignal()

    def __init__(
        self, parent: QWidget, tag_names: Collection[str], *, add: bool
    ) -> None:
        super().__init__(parent=parent)
        self.resize(350, 60)

        self._tags = tuple(tag_names)
        self.tags_widget = MultipleTagsSelectorWidget(self, self._tags)

        self.label = QLabel("Tags", self)

        self.dialog_layout = QFormLayout(self)
        self.dialog_layout.addRow(self.label, self.tags_widget)

        if add:
            self.setWindowTitle("Add Tags")
            self.setWindowIcon(icons.add_tag)
        else:
            self.setWindowTitle("Remove Tags")
            self.setWindowIcon(icons.remove_tag)

        self.buttonBox = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel,
            self,
        )
        self.dialog_layout.setWidget(
            1, QFormLayout.ItemRole.SpanningRole, self.buttonBox
        )
        self.buttonBox.clicked.connect(self._handle_button_box_click)

    @property
    def tags(self) -> tuple[str]:
        return self.tags_widget.tag_names

    @tags.setter
    def tags(self, values: Collection[str]) -> None:
        self.tags_widget.tag_names = values

    def reject(self) -> None:
        logging.debug(f"Closing {self.__class__.__name__}")
        return super().reject()

    def _handle_button_box_click(self, button: QAbstractButton) -> None:
        role = self.buttonBox.buttonRole(button)
        if role == QDialogButtonBox.ButtonRole.AcceptRole:
            self.signal_ok.emit()
        elif role == QDialogButtonBox.ButtonRole.RejectRole:
            self.reject()
        else:
            raise ValueError("Unknown role of the clicked button in the ButtonBox")
