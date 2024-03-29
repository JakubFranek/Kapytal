from collections.abc import Collection
from decimal import Decimal

from PyQt6.QtCore import QSignalBlocker, Qt, pyqtSignal
from PyQt6.QtGui import QAction
from PyQt6.QtWidgets import (
    QDoubleSpinBox,
    QHBoxLayout,
    QToolButton,
    QWidget,
)
from src.views import icons
from src.views.utilities.helper_functions import get_spinbox_value_as_decimal
from src.views.widgets.smart_combo_box import SmartComboBox


class SplitCategoryRowWidget(QWidget):
    signal_remove_row = pyqtSignal(QWidget)
    signal_amount_changed = pyqtSignal(QWidget)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)

        self.combo_box = SmartComboBox(parent=self)
        self.combo_box.lineEdit().setPlaceholderText("Enter Category path")
        self.combo_box.setToolTip("Both existing or new Category paths are valid")
        self.combo_box.setMinimumWidth(175)

        self.double_spin_box = QDoubleSpinBox(self)
        self.double_spin_box.setMaximum(1e16)
        self.double_spin_box.setGroupSeparatorShown(True)
        self.double_spin_box.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.double_spin_box.setMinimumWidth(125)
        self.double_spin_box.valueChanged.connect(
            lambda: self.signal_amount_changed.emit(self)
        )

        self.remove_tool_button = QToolButton(self)
        self.actionRemove_Row = QAction("Remove", self)
        self.actionRemove_Row.setIcon(icons.remove)
        self.actionRemove_Row.triggered.connect(
            lambda: self.signal_remove_row.emit(self)
        )
        self.remove_tool_button.setDefaultAction(self.actionRemove_Row)

        self.horizontal_layout = QHBoxLayout(self)
        self.horizontal_layout.addWidget(self.combo_box)
        self.horizontal_layout.addWidget(self.double_spin_box)
        self.horizontal_layout.addWidget(self.remove_tool_button)

        self.layout().setContentsMargins(0, 0, 0, 0)
        self.horizontal_layout.setStretchFactor(self.combo_box, 66)
        self.horizontal_layout.setStretchFactor(self.double_spin_box, 34)

        self.setFocusPolicy(Qt.FocusPolicy.TabFocus)
        self.setFocusProxy(self.combo_box)

    @property
    def category(self) -> str:
        return self.combo_box.currentText()

    @category.setter
    def category(self, value: str) -> None:
        with QSignalBlocker(self.combo_box):
            self.combo_box.setCurrentText(value)

    @property
    def amount(self) -> Decimal:
        return get_spinbox_value_as_decimal(self.double_spin_box)

    @amount.setter
    def amount(self, value: Decimal) -> None:
        with QSignalBlocker(self.double_spin_box):
            self.double_spin_box.setValue(value)

    @property
    def currency_code(self) -> str:
        return self._currency_code

    @currency_code.setter
    def currency_code(self, code: str) -> None:
        self._currency_code = code
        self.double_spin_box.setSuffix(" " + code)

    @property
    def amount_decimals(self) -> int:
        return self.double_spin_box.decimals()

    @amount_decimals.setter
    def amount_decimals(self, value: int) -> None:
        self.double_spin_box.setDecimals(value)

    @property
    def maximum_amount(self) -> Decimal:
        return Decimal(self.double_spin_box.maximum())

    @maximum_amount.setter
    def maximum_amount(self, maximum: Decimal) -> None:
        self.double_spin_box.setMaximum(maximum)

    def __repr__(self) -> str:
        return f"SplitCategoryRowWidget('{self.category}')"

    def load_categories(
        self, categories: Collection[str], *, keep_current_text: bool
    ) -> None:
        self.combo_box.load_items(
            categories, icons.category, keep_current_text=keep_current_text
        )
