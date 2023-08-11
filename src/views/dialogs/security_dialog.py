import logging
from collections.abc import Collection
from decimal import Decimal

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import (
    QAbstractButton,
    QDialogButtonBox,
    QWidget,
)
from src.views import icons
from src.views.base_classes.custom_dialog import CustomDialog
from src.views.ui_files.dialogs.Ui_security_dialog import Ui_SecurityDialog
from src.views.widgets.smart_combo_box import SmartComboBox


class SecurityDialog(CustomDialog, Ui_SecurityDialog):
    signal_ok = pyqtSignal()

    def __init__(
        self,
        parent: QWidget,
        security_types: Collection[str],
        currency_codes: Collection[str],
        *,
        edit: bool,
    ) -> None:
        super().__init__(parent=parent)
        self.setupUi(self)
        self.resize(270, 105)

        self.typeComboBox = SmartComboBox(parent=self)
        self.typeComboBox.load_items(security_types)
        self.typeComboBox.setCurrentText("")
        self.formLayout.insertRow(2, "Type", self.typeComboBox)

        if edit:
            self.setWindowTitle("Edit Security")
            self.setWindowIcon(icons.edit_security)
            self.currencyComboBox.setVisible(False)
            self.currencyLabel.setVisible(False)
            self.unitDoubleSpinBox.setVisible(False)
            self.unitLabel.setVisible(False)
        else:
            self.setWindowTitle("Add Security")
            self.setWindowIcon(icons.add_security)
            for code in currency_codes:
                self.currencyComboBox.addItem(code)

        self.currencyComboBox.setCurrentIndex(0)

        self.buttonBox.clicked.connect(self._handle_button_box_click)
        self._set_tab_order()

    @property
    def name(self) -> str:
        return self.nameLineEdit.text()

    @name.setter
    def name(self, text: str) -> None:
        self.nameLineEdit.setText(text)

    @property
    def symbol(self) -> str:
        return self.symbolLineEdit.text()

    @symbol.setter
    def symbol(self, text: str) -> None:
        self.symbolLineEdit.setText(text)

    @property
    def type_(self) -> str:
        return self.typeComboBox.currentText()

    @type_.setter
    def type_(self, text: str) -> None:
        self.typeComboBox.setCurrentText(text)

    @property
    def currency_code(self) -> str:
        return self.currencyComboBox.currentText()

    @currency_code.setter
    def currency_code(self, text: str) -> None:
        self.currencyComboBox.setCurrentText(text)

    @property
    def unit(self) -> Decimal:
        return Decimal(self.unitDoubleSpinBox.cleanText().replace(",", ""))

    @unit.setter
    def unit(self, value: Decimal) -> None:
        self.unitDoubleSpinBox.setValue(value)

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

    def _set_tab_order(self) -> None:
        self.setTabOrder(self.nameLineEdit, self.symbolLineEdit)
        self.setTabOrder(self.symbolLineEdit, self.typeComboBox)
        self.setTabOrder(self.typeComboBox, self.unitDoubleSpinBox)
        self.setTabOrder(self.unitDoubleSpinBox, self.currencyComboBox)
