import logging

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QCloseEvent, QKeyEvent
from PyQt6.QtWidgets import QWidget


class CustomWidget(QWidget):
    """Can be closed by via ESC key."""

    signal_widget_closed = pyqtSignal()

    def keyPressEvent(self, a0: QKeyEvent) -> None:
        if a0.key() == Qt.Key.Key_Escape:
            self.close()
        return super().keyPressEvent(a0)

    def closeEvent(self, a0: QCloseEvent) -> None:
        logging.debug(f"Closing {self.__class__.__name__}")
        super().closeEvent(a0)
        self.signal_widget_closed.emit()

    def show_form(self) -> None:
        logging.debug(f"Showing {self.__class__.__name__}")
        self.show()
