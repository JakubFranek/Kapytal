from collections.abc import Collection
from decimal import Decimal

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QAbstractButton, QDialog, QDialogButtonBox, QWidget

from src.views.ui_files.Ui_cash_account_dialog import Ui_CashAccountDialog


class CashAccountDialog(QDialog, Ui_CashAccountDialog):
    signal_OK = pyqtSignal()

    def __init__(
        self,
        parent: QWidget,
        max_position: int,
        code_places_pairs: Collection[tuple[str, int]],
        edit: bool = False,
    ) -> None:
        super().__init__(parent=parent)
        self.setupUi(self)
        self.resize(270, 105)
        self.currentPathLineEdit.setEnabled(False)
        if edit:
            self.setWindowTitle("Edit Cash Account")
            self.setWindowIcon(QIcon("icons_24:pencil.png"))
            self.currencyComboBox.setVisible(False)
            self.currencyLabel.setVisible(False)
        else:
            self.setWindowTitle("Add Cash Account")
            self.setWindowIcon(QIcon("icons_custom:money-coin-plus.png"))
            self.currentPathLabel.setVisible(False)
            self.currentPathLineEdit.setVisible(False)
            for code, _ in code_places_pairs:
                self.currencyComboBox.addItem(code)
            self.currencyComboBox.setCurrentIndex(0)

        self.positionSpinBox.setMaximum(max_position)
        self.buttonBox.clicked.connect(self._handle_button_box_click)
        self.currencyComboBox.currentTextChanged.connect(self._currency_changed)
        self.initialBalanceDoubleSpinBox.setMaximum(1_000_000_000_000)
        self.code_places_pairs = code_places_pairs

        self._currency_changed()

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
    def currency_code(self) -> str:
        return self.currencyComboBox.currentText()

    @property
    def initial_balance(self) -> Decimal:
        return Decimal(self.initialBalanceDoubleSpinBox.cleanText())

    @initial_balance.setter
    def initial_balance(self, value: Decimal) -> None:
        self.initialBalanceDoubleSpinBox.setValue(value)

    @property
    def position(self) -> int:
        return self.positionSpinBox.value()

    @position.setter
    def position(self, value: int) -> None:
        self.positionSpinBox.setValue(value)

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
            self.signal_OK.emit()
        elif role == QDialogButtonBox.ButtonRole.RejectRole:
            self.close()
        else:
            raise ValueError("Unknown role of the clicked button in the ButtonBox")
