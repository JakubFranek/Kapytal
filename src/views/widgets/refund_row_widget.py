from decimal import Decimal

from PyQt6.QtCore import QSignalBlocker, Qt, pyqtSignal
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QDoubleSpinBox, QHBoxLayout, QLineEdit, QWidget
from src.views.utilities.helper_functions import get_spinbox_value_as_decimal


class RefundRowWidget(QWidget):
    signal_amount_changed = pyqtSignal()

    def __init__(
        self, parent: QWidget | None, text: str, currency_code: str, icon: QIcon
    ) -> None:
        super().__init__(parent)

        self.line_edit = QLineEdit(self)
        self.line_edit.setEnabled(False)
        self.line_edit.setText(text)
        self.line_edit.setMinimumWidth(175)

        # the following makes icons colourful even when QLineEdit is disabled
        icon.addPixmap(icon.pixmap(16, 16), QIcon.Mode.Disabled)
        self.line_edit.addAction(icon, QLineEdit.ActionPosition.LeadingPosition)

        self._currency_code = currency_code

        self.double_spin_box = QDoubleSpinBox(self)
        self.double_spin_box.setGroupSeparatorShown(True)
        self.double_spin_box.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.double_spin_box.setMinimumWidth(125)
        self.double_spin_box.setSuffix(" " + currency_code)
        self.double_spin_box.valueChanged.connect(self.signal_amount_changed.emit)

        self.horizontal_layout = QHBoxLayout(self)
        self.horizontal_layout.addWidget(self.line_edit)
        self.horizontal_layout.addWidget(self.double_spin_box)

        self.layout().setContentsMargins(0, 0, 0, 0)

        self.setFocusPolicy(Qt.FocusPolicy.TabFocus)
        self.setFocusProxy(self.double_spin_box)

    @property
    def amount(self) -> Decimal:
        return get_spinbox_value_as_decimal(self.double_spin_box)

    @amount.setter
    def amount(self, value: Decimal) -> None:
        self.double_spin_box.setValue(value)

    @property
    def text(self) -> str:
        return self.line_edit.text()

    def set_max(self, value: Decimal) -> None:
        with QSignalBlocker(self.double_spin_box):
            self.double_spin_box.setMaximum(value)

    def set_min(self, value: Decimal) -> None:
        with QSignalBlocker(self.double_spin_box):
            self.double_spin_box.setMinimum(value)

    def set_spinbox_enabled(self, *, enable: bool) -> None:
        self.double_spin_box.setEnabled(enable)
