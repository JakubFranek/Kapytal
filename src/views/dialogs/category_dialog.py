import logging
from collections.abc import Collection

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QAbstractButton,
    QCompleter,
    QDialog,
    QDialogButtonBox,
    QWidget,
)
from src.views import icons
from src.views.ui_files.dialogs.Ui_category_dialog import Ui_CategoryDialog


# TODO: update position limits based on path state?
class CategoryDialog(QDialog, Ui_CategoryDialog):
    signal_ok = pyqtSignal()

    def __init__(
        self,
        parent: QWidget,
        type_: str,
        paths: Collection[str],
        max_position: int,
        *,
        edit: bool,
    ) -> None:
        super().__init__(parent=parent)
        self.setupUi(self)
        self.resize(400, 105)
        self.currentPathLineEdit.setEnabled(False)

        self.pathCompleter = QCompleter(paths)
        self.pathCompleter.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self.pathLineEdit.setCompleter(self.pathCompleter)

        self.typeLineEdit.setText(type_)
        self.typeLineEdit.setDisabled(True)

        if edit:
            self.setWindowTitle("Edit Category")
            self.setWindowIcon(icons.edit_category)
        else:
            self.setWindowTitle("Add Category")
            self.setWindowIcon(icons.add_category)
            self.currentPathLabel.setVisible(False)
            self.currentPathLineEdit.setVisible(False)

        self.positionSpinBox.setMaximum(max_position)
        self.buttonBox.clicked.connect(self._handle_button_box_click)

    @property
    def type_(self) -> str:
        return self.typeLineEdit.text()

    @property
    def path(self) -> str:
        return self.pathLineEdit.text()

    @path.setter
    def path(self, text: str) -> None:
        self.pathLineEdit.setText(text)

    @property
    def current_path(self) -> str:
        return self.currentPathLineEdit.text()

    @current_path.setter
    def current_path(self, text: str) -> None:
        self.currentPathLineEdit.setText(text)

    @property
    def position(self) -> int:
        return self.positionSpinBox.value()

    @position.setter
    def position(self, value: int) -> None:
        self.positionSpinBox.setValue(value)

    def _handle_button_box_click(self, button: QAbstractButton) -> None:
        role = self.buttonBox.buttonRole(button)
        if role == QDialogButtonBox.ButtonRole.AcceptRole:
            self.signal_ok.emit()
        elif role == QDialogButtonBox.ButtonRole.RejectRole:
            self.reject()
        else:
            raise ValueError("Unknown role of the clicked button in the ButtonBox")

    def reject(self) -> None:
        logging.debug(f"Closing {self.__class__.__name__}")
        return super().reject()
