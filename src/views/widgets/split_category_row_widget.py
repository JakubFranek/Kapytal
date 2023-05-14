from collections.abc import Collection
from decimal import Decimal

from PyQt6.QtCore import QSignalBlocker, Qt, pyqtSignal
from PyQt6.QtGui import QAction
from PyQt6.QtWidgets import QComboBox, QDoubleSpinBox, QHBoxLayout, QToolButton, QWidget
from src.views import icons
from src.views.dialogs.select_item_dialog import ask_user_for_selection


class SplitCategoryRowWidget(QWidget):
    signal_remove_row = pyqtSignal(QWidget)
    signal_amount_changed = pyqtSignal(QWidget)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)

        self.combo_box = QComboBox(self)
        self.combo_box.setEditable(True)
        self.combo_box.lineEdit().setPlaceholderText("Enter Category path")
        self.combo_box.setToolTip("Both existing or new Category paths are valid")

        self.select_tool_button = QToolButton(self)
        self.actionSelect_Item = QAction("Select Category", self)
        self.actionSelect_Item.setIcon(icons.category)
        self.actionSelect_Item.triggered.connect(self._select_item)
        self.select_tool_button.setDefaultAction(self.actionSelect_Item)

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
        self.horizontal_layout.addWidget(self.select_tool_button)
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
        self.combo_box.setCurrentText(value)

    @property
    def amount(self) -> Decimal:
        text = self.double_spin_box.cleanText().replace(",", "")
        return Decimal(text)

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

    def load_categories(self, categories: Collection[str], *, keep_text: bool) -> None:
        current_text = self.category
        self._categories = categories
        self.combo_box.clear()
        for item in categories:
            self.combo_box.addItem(item)
        if keep_text:
            self.combo_box.setCurrentText(current_text)
        else:
            self.combo_box.setCurrentIndex(-1)

    def _select_item(self) -> None:
        item = ask_user_for_selection(
            self,
            self._categories,
            "Select Category",
            icons.category,
        )
        if item:
            self.combo_box.setCurrentText(item)
