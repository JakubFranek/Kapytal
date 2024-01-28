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
from src.views.ui_files.dialogs.Ui_cash_account_dialog import Ui_CashAccountDialog
from src.views.utilities.helper_functions import get_spinbox_value_as_decimal
from src.views.widgets.smart_combo_box import SmartComboBox


class CashAccountDialog(CustomDialog, Ui_CashAccountDialog):
    signal_ok = pyqtSignal()
    signal_path_changed = pyqtSignal(str)

    def __init__(
        self,
        parent: QWidget,
        paths: Collection[str],
        code_places_pairs: Collection[tuple[str, int]],
        *,
        edit: bool,
    ) -> None:
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
            self.setWindowTitle("Edit Cash Account")
            self.setWindowIcon(icons.edit_cash_account)
            self.currencyComboBox.setVisible(False)
            self.currencyLabel.setVisible(False)
        else:
            self.setWindowTitle("Add Cash Account")
            self.setWindowIcon(icons.add_cash_account)
            self.currentPathLabel.setVisible(False)
            self.currentPathLineEdit.setVisible(False)
            for code, _ in code_places_pairs:
                self.currencyComboBox.addItem(code)
            self.currencyComboBox.setCurrentIndex(0)

        self.positionSpinBox.setMinimum(1)
        self.buttonBox.clicked.connect(self._handle_button_box_click)
        self.currencyComboBox.currentTextChanged.connect(self._currency_changed)
        self.pathComboBox.currentTextChanged.connect(self.signal_path_changed.emit)
        self.initialBalanceDoubleSpinBox.setMaximum(1_000_000_000_000)
        self.code_places_pairs = code_places_pairs

        self._currency_changed()

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
    def currency_code(self) -> str:
        return self.currencyComboBox.currentText()

    @property
    def initial_balance(self) -> Decimal:
        return get_spinbox_value_as_decimal(self.initialBalanceDoubleSpinBox)

    @initial_balance.setter
    def initial_balance(self, value: Decimal) -> None:
        self.initialBalanceDoubleSpinBox.setValue(value)

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

    def _currency_changed(self) -> None:
        index = self.currencyComboBox.currentIndex()
        if len(self.code_places_pairs) != 0:
            code, places = self.code_places_pairs[index]
        else:
            code = ""
            places = 0
        self.initialBalanceDoubleSpinBox.setSuffix(" " + code)
        self.initialBalanceDoubleSpinBox.setDecimals(places)

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
