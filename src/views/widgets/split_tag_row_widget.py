from collections.abc import Collection
from decimal import Decimal

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QAction, QIcon
from PyQt6.QtWidgets import QComboBox, QDoubleSpinBox, QHBoxLayout, QToolButton, QWidget
from src.views.dialogs.select_item_dialog import ask_user_for_selection


class SplitTagRowWidget(QWidget):
    signal_remove_row = pyqtSignal(QWidget)

    def __init__(self, parent: QWidget | None, tag_names: Collection[str]) -> None:
        super().__init__(parent)

        self._tag_names = tuple(tag_names)

        self.combo_box = QComboBox(self)
        self.combo_box.setEditable(True)
        self.combo_box.lineEdit().setPlaceholderText("Enter Tag name")
        for tag in tag_names:
            self.combo_box.addItem(tag)
        self.combo_box.setCurrentIndex(-1)
        self.combo_box.setToolTip("Both existing or new Tag names are valid")

        self.select_tool_button = QToolButton(self)
        self.actionSelect_Item = QAction("Select Tag", self)
        self.actionSelect_Item.setIcon(QIcon("icons_16:tag.png"))
        self.actionSelect_Item.triggered.connect(self._select_item)
        self.select_tool_button.setDefaultAction(self.actionSelect_Item)

        self.double_spin_box = QDoubleSpinBox(self)
        self.double_spin_box.setMaximum(1e16)
        self.double_spin_box.setGroupSeparatorShown(True)
        self.double_spin_box.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.double_spin_box.setMinimumWidth(125)
        self.double_spin_box.setToolTip(
            "Max amount assignable to a Tag is the total transaction amount."
        )

        self.remove_tool_button = QToolButton(self)
        self.actionRemove_Row = QAction("Remove", self)
        self.actionRemove_Row.setIcon(QIcon("icons_16:minus.png"))
        self.actionRemove_Row.triggered.connect(
            lambda: self.signal_remove_row.emit(self)
        )
        self.remove_tool_button.setDefaultAction(self.actionRemove_Row)

        self.horizontal_layout = QHBoxLayout(self)
        self.horizontal_layout.addWidget(self.combo_box)
        self.horizontal_layout.addWidget(self.select_tool_button)
        self.horizontal_layout.addWidget(self.double_spin_box)
        self.horizontal_layout.addWidget(self.remove_tool_button)

        self.layout().setContentsMargins(0, 0, 0, 0)
        self.horizontal_layout.setStretchFactor(self.combo_box, 66)
        self.horizontal_layout.setStretchFactor(self.double_spin_box, 34)

        self.setFocusPolicy(Qt.FocusPolicy.TabFocus)
        self.setFocusProxy(self.combo_box)

    @property
    def tag(self) -> str:
        return self.combo_box.currentText()

    @tag.setter
    def tag(self, value: str) -> None:
        self.combo_box.setCurrentText(value.strip())

    @property
    def amount(self) -> Decimal:
        text = self.double_spin_box.text()
        text = text.removesuffix(" " + self._currency_code)
        text = text.replace(",", "")
        return Decimal(text)

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
        return f"SplitTagRowWidget('{self.tag}')"

    def _select_item(self) -> None:
        item = ask_user_for_selection(
            self,
            self._tag_names,
            "Select Tag",
            QIcon("icons_custom:category.png"),
        )
        if item:
            self.combo_box.setCurrentText(item)
