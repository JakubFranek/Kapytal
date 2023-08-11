import logging
from collections.abc import Collection

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import (
    QAbstractButton,
    QDialogButtonBox,
    QWidget,
)
from src.views import icons
from src.views.base_classes.custom_dialog import CustomDialog
from src.views.ui_files.dialogs.Ui_security_account_dialog import (
    Ui_SecurityAccountDialog,
)
from src.views.widgets.smart_combo_box import SmartComboBox


class SecurityAccountDialog(CustomDialog, Ui_SecurityAccountDialog):
    signal_ok = pyqtSignal()
    signal_path_changed = pyqtSignal(str)

    def __init__(self, parent: QWidget, paths: Collection[str], *, edit: bool) -> None:
        super().__init__(parent=parent)
        self.setupUi(self)
        self.resize(400, 105)

        self._edit = edit
        self.currentPathLineEdit.setEnabled(False)

        self.pathComboBox = SmartComboBox(parent=self)
        self.pathComboBox.load_items(paths)
        self.pathComboBox.setCurrentText("")
        self.formLayout.insertRow(1, "Path", self.pathComboBox)
        self.pathComboBox.setFocus()

        if edit:
            self.setWindowTitle("Edit Security Account")
            self.setWindowIcon(icons.edit_security_account)
        else:
            self.setWindowTitle("Add Security Account")
            self.setWindowIcon(icons.add_security_account)
            self.currentPathLabel.setVisible(False)
            self.currentPathLineEdit.setVisible(False)

        self.positionSpinBox.setMinimum(1)
        self.buttonBox.clicked.connect(self._handle_button_box_click)
        self.pathComboBox.currentTextChanged.connect(self.signal_path_changed.emit)

    @property
    def path(self) -> str:
        return self.pathComboBox.currentText()

    @path.setter
    def path(self, text: str) -> None:
        self.pathComboBox.setCurrentText(text)

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

    @property
    def maximum_position(self) -> int:
        return self.positionSpinBox.maximum()

    @maximum_position.setter
    def maximum_position(self, value: int) -> None:
        self.positionSpinBox.setMaximum(value)

    @property
    def edit(self) -> bool:
        return self._edit

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
