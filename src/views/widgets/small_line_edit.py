from PyQt6.QtCore import QSize
from PyQt6.QtWidgets import QLineEdit


class SmallLineEdit(QLineEdit):
    """Custom QLineEdit with a small size hint. Used in AccountTreeWidget search bar."""

    def sizeHint(self) -> QSize:
        hint = super().sizeHint()
        return QSize(60, hint.height())
