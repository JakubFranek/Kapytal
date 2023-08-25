import logging
from datetime import date
from decimal import Decimal

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QAbstractButton, QDialogButtonBox, QWidget
from src.models.user_settings import user_settings
from src.views import icons
from src.views.base_classes.custom_dialog import CustomDialog
from src.views.ui_files.dialogs.Ui_set_security_price_dialog import (
    Ui_SetSecurityPriceDialog,
)
from src.views.utilities.helper_functions import convert_datetime_format_to_qt


class SetSecurityPriceDialog(CustomDialog, Ui_SetSecurityPriceDialog):
    signal_ok = pyqtSignal()

    def __init__(  # noqa: PLR0913
        self,
        date_: date,
        value: Decimal,
        security_name: str,
        currency_code: str,
        parent: QWidget | None = None,
        *,
        edit: bool,
    ) -> None:
        super().__init__(parent)
        self.setupUi(self)
        self.setWindowIcon(icons.set_security_price)

        if edit:
            self.setWindowTitle(f"Edit {security_name} price")
            self.dateEdit.setEnabled(False)
        else:
            self.setWindowTitle(f"Add {security_name} price")

        self.priceDoubleSpinBox.setMaximum(1_000_000_000_000)
        self.priceDoubleSpinBox.setValue(value)
        self.priceDoubleSpinBox.setDecimals(9)
        self.priceDoubleSpinBox.setSuffix(" " + currency_code)
        self.dateEdit.setDate(date_)
        self.dateEdit.setMaximumDate(date_)

        self.buttonBox.clicked.connect(self._handle_button_box_click)

        display_format = convert_datetime_format_to_qt(
            user_settings.settings.general_date_format
        )
        self.dateEdit.setDisplayFormat(display_format)

    @property
    def value(self) -> Decimal:
        return Decimal(self.priceDoubleSpinBox.cleanText().replace(",", ""))

    @property
    def date_(self) -> date:
        return self.dateEdit.date().toPyDate()

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
