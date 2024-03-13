import logging
from datetime import date
from decimal import Decimal

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import QAbstractButton, QDialogButtonBox, QWidget
from src.models.user_settings import user_settings
from src.views import icons
from src.views.base_classes.custom_dialog import CustomDialog
from src.views.ui_files.dialogs.Ui_set_exchange_rate_dialog import (
    Ui_SetExchangeRateDialog,
)
from src.views.utilities.helper_functions import (
    convert_datetime_format_to_qt,
    get_spinbox_value_as_decimal,
)


class SetExchangeRateDialog(CustomDialog, Ui_SetExchangeRateDialog):
    signal_ok = pyqtSignal()

    def __init__(  # noqa: PLR0913
        self,
        date_: date,
        max_date: date,
        exchange_rate: str,
        value: Decimal,
        parent: QWidget | None,
        *,
        edit: bool,
    ) -> None:
        super().__init__(parent)
        self.setupUi(self)
        self.setWindowIcon(icons.exchange_rate)

        self._edit = edit
        if edit:
            self.setWindowTitle(f"Edit {exchange_rate} data point")
            self._original_date = date_
        else:
            self.setWindowTitle(f"Add {exchange_rate} data point")

        primary_code, _, secondary_code = exchange_rate.partition("/")
        self._exchange_rate_code = exchange_rate

        self.exchangeRateLabel.setText(f"1 {primary_code} =")
        self.exchangeRateDoubleSpinBox.setMaximum(1_000_000_000_000)
        self.exchangeRateDoubleSpinBox.setValue(value)
        self.exchangeRateDoubleSpinBox.setDecimals(
            user_settings.settings.exchange_rate_decimals
        )
        self.exchangeRateDoubleSpinBox.setSuffix(f" {secondary_code}")
        self.dateEdit.setDate(date_)
        self.dateEdit.setMaximumDate(max_date)

        self.buttonBox.clicked.connect(self._handle_button_box_click)

        display_format = convert_datetime_format_to_qt(
            user_settings.settings.general_date_format
        )
        self.dateEdit.setDisplayFormat(display_format)
        self.dateEdit.calendarWidget().setFirstDayOfWeek(Qt.DayOfWeek.Monday)

        self.exchangeRateDoubleSpinBox.setFocus()

    @property
    def value(self) -> Decimal:
        return get_spinbox_value_as_decimal(self.exchangeRateDoubleSpinBox)

    @property
    def date_(self) -> date:
        return self.dateEdit.date().toPyDate()

    @property
    def original_date(self) -> date:
        return self._original_date

    @property
    def edit(self) -> bool:
        return self._edit

    @property
    def exchange_rate_code(self) -> str:
        return self._exchange_rate_code

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
