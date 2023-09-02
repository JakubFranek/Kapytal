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
from src.views.ui_files.dialogs.Ui_category_dialog import Ui_CategoryDialog
from src.views.widgets.smart_combo_box import SmartComboBox


class CategoryDialog(CustomDialog, Ui_CategoryDialog):
    signal_ok = pyqtSignal()
    signal_path_changed = pyqtSignal(str)

    def __init__(
        self,
        parent: QWidget,
        type_: str,
        paths: Collection[str],
        *,
        edit: bool,
    ) -> None:
        super().__init__(parent=parent)
        self.setupUi(self)
        self.resize(400, 105)

        self._edit = edit
        self.positionSpinBox.setMinimum(1)

        self.currentPathLineEdit.setEnabled(False)

        self.pathLineEdit = SmartComboBox(parent=self)
        self.pathLineEdit.load_items(paths)
        self.pathLineEdit.setCurrentText("")
        self.formLayout.insertRow(2, "Path", self.pathLineEdit)
        self.pathLineEdit.setFocus()

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

        self.buttonBox.clicked.connect(self._handle_button_box_click)
        self.pathLineEdit.currentTextChanged.connect(self.signal_path_changed.emit)

    @property
    def type_(self) -> str:
        return self.typeLineEdit.text()

    @property
    def path(self) -> str:
        return self.pathLineEdit.currentText()

    @path.setter
    def path(self, text: str) -> None:
        self.pathLineEdit.setCurrentText(text)

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
