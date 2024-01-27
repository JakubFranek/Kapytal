import locale
from collections.abc import Collection
from decimal import Decimal

from PyQt6.QtCore import QSignalBlocker, Qt, pyqtSignal
from PyQt6.QtGui import QAction
from PyQt6.QtWidgets import (
    QDoubleSpinBox,
    QHBoxLayout,
    QMenu,
    QToolButton,
    QWidget,
)
from src.views import icons
from src.views.widgets.smart_combo_box import SmartComboBox


class SplitTagRowWidget(QWidget):
    signal_remove_row = pyqtSignal(QWidget)

    def __init__(
        self, parent: QWidget | None, tag_names: Collection[str], total: Decimal
    ) -> None:
        super().__init__(parent)

        self._tag_names = tuple(sorted(tag_names, key=str.lower))
        self._total = total

        self.combo_box = SmartComboBox(parent=self)
        self.combo_box.lineEdit().setPlaceholderText("Enter Tag name")
        self.combo_box.load_items(self._tag_names, icons.tag)
        self.combo_box.setToolTip("Both existing or new Tag names are valid")
        self.combo_box.setMinimumWidth(150)

        self.double_spin_box = QDoubleSpinBox(self)
        self.double_spin_box.setMaximum(1e16)
        self.double_spin_box.setGroupSeparatorShown(True)
        self.double_spin_box.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.double_spin_box.setMinimumWidth(125)
        self.double_spin_box.setToolTip(
            "Max amount assignable to a Tag is the total transaction amount."
        )

        self.action25pct = QAction("25%", self)
        self.action33pct = QAction("33%", self)
        self.action50pct = QAction("50%", self)
        self.action66pct = QAction("66%", self)
        self.action75pct = QAction("75%", self)
        self.action100pct = QAction("100%", self)

        self.action25pct.triggered.connect(lambda: self._scale_total(Decimal("0.25")))
        self.action33pct.triggered.connect(lambda: self._scale_total(1 / Decimal(3)))
        self.action50pct.triggered.connect(lambda: self._scale_total(Decimal("0.5")))
        self.action66pct.triggered.connect(lambda: self._scale_total(2 / Decimal(3)))
        self.action75pct.triggered.connect(lambda: self._scale_total(Decimal("0.75")))
        self.action100pct.triggered.connect(lambda: self._scale_total(Decimal(1)))

        self.divide_menu = QMenu(self)
        self.divide_menu.addAction(self.action25pct)
        self.divide_menu.addAction(self.action33pct)
        self.divide_menu.addAction(self.action50pct)
        self.divide_menu.addAction(self.action66pct)
        self.divide_menu.addAction(self.action75pct)
        self.divide_menu.addAction(self.action100pct)

        self.divide_amount_tool_button = QToolButton(self)
        self.divide_amount_tool_button.setPopupMode(
            QToolButton.ToolButtonPopupMode.InstantPopup
        )
        self.divide_amount_tool_button.setMenu(self.divide_menu)
        self.actionDivide_Amount = QAction("Scale Tag Amount", self)
        self.actionDivide_Amount.setIcon(icons.percent)
        self.divide_amount_tool_button.setDefaultAction(self.actionDivide_Amount)

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
        self.horizontal_layout.addWidget(self.divide_amount_tool_button)
        self.horizontal_layout.addWidget(self.remove_tool_button)

        self.layout().setContentsMargins(0, 0, 0, 0)
        self.horizontal_layout.setStretchFactor(self.combo_box, 66)
        self.horizontal_layout.setStretchFactor(self.double_spin_box, 34)

        self.setFocusPolicy(Qt.FocusPolicy.TabFocus)
        self.setFocusProxy(self.combo_box)

    @property
    def tag_name(self) -> str:
        return self.combo_box.currentText()

    @tag_name.setter
    def tag_name(self, value: str) -> None:
        with QSignalBlocker(self.combo_box):
            self.combo_box.setCurrentText(value.strip())

    @property
    def amount(self) -> Decimal:
        text = self.double_spin_box.cleanText()
        text_delocalized = locale.delocalize(text)
        return Decimal(text_delocalized)

    @amount.setter
    def amount(self, value: Decimal) -> None:
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
        return f"SplitTagRowWidget('{self.tag_name}')"

    def set_total_amount(self, total: Decimal) -> None:
        self._total = total

    def _scale_total(self, scale_factor: Decimal) -> None:
        self.amount = self._total * scale_factor
