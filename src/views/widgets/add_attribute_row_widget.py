from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QAction
from PyQt6.QtWidgets import QHBoxLayout, QSizePolicy, QSpacerItem, QToolButton, QWidget
from src.views import icons


class AddAttributeRowWidget(QWidget):
    signal_add_row = pyqtSignal()

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)

        self.actionAdd_Row = QAction(icons.add, "Add row", parent)
        self.actionAdd_Row.triggered.connect(self.signal_add_row.emit)

        self.tool_button = QToolButton(self)
        self.tool_button.setDefaultAction(self.actionAdd_Row)

        self.spacer1 = QSpacerItem(
            20, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum
        )
        self.spacer2 = QSpacerItem(
            20, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum
        )

        self.horizontal_layout = QHBoxLayout(self)
        self.horizontal_layout.addSpacerItem(self.spacer1)
        self.horizontal_layout.addWidget(self.tool_button)
        self.horizontal_layout.addSpacerItem(self.spacer2)

        self.layout().setContentsMargins(0, 0, 0, 0)

        self.setFocusPolicy(Qt.FocusPolicy.TabFocus)
        self.setFocusProxy(self.tool_button)
