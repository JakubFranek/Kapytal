from PyQt6.QtWidgets import (
    QLabel,
    QSizePolicy,
    QSpacerItem,
    QVBoxLayout,
    QWidget,
)


class LabelWidget(QWidget):
    def __init__(self, parent: QWidget, text: str) -> None:
        super().__init__(parent)

        self.label = QLabel(text, self)

        self.spacer1 = QSpacerItem(
            20, 5, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed
        )
        self.spacer2 = QSpacerItem(
            20, 0, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Maximum
        )

        self.vertical_layout = QVBoxLayout(self)
        self.vertical_layout.addSpacerItem(self.spacer1)
        self.vertical_layout.addWidget(self.label)
        self.vertical_layout.addSpacerItem(self.spacer2)

        self.layout().setContentsMargins(0, 0, 0, 0)
