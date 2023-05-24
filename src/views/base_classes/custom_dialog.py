import logging

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QCloseEvent, QKeyEvent
from PyQt6.QtWidgets import QDialog


# TODO: delete dialogs on close?
class CustomDialog(QDialog):
    """Can be closed by via ESC key."""

    def keyPressEvent(self, a0: QKeyEvent) -> None:  # noqa: N802
        if a0.key() == Qt.Key.Key_Escape:
            self.close()
        return super().keyPressEvent(a0)

    def closeEvent(self, a0: QCloseEvent) -> None:  # noqa: N802
        logging.debug(f"Closing {self.__class__.__name__}")
        return super().closeEvent(a0)