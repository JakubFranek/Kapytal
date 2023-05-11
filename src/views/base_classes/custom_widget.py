import logging

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QKeyEvent
from PyQt6.QtWidgets import QWidget


class CustomWidget(QWidget):
    """Can be closed by via ESC key."""

    def keyPressEvent(self, a0: QKeyEvent) -> None:  # noqa: N802
        if a0.key() == Qt.Key.Key_Escape:
            logging.debug(f"Closing {self.__class__.__name__}")
            self.close()
        return super().keyPressEvent(a0)
