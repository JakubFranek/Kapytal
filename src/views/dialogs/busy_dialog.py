from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QDialog, QWidget
from src.views import icons
from src.views.ui_files.dialogs.Ui_busy_dialog import Ui_BusyDialog


class BusyDialog(QDialog, Ui_BusyDialog):
    def __init__(self, parent: QWidget = None) -> None:
        super().__init__(parent)
        self.setupUi(self)
        self.setWindowFlag(Qt.WindowType.FramelessWindowHint)
        if not isinstance(icons.hourglass, QIcon):
            raise TypeError("icons.hourglass is not a QIcon")
        self.iconLabel.setPixmap(icons.hourglass.pixmap(16, 16))

    def set_state(self, text: str, value: int) -> None:
        self.label.setText(text)
        self.progressBar.setValue(value)

    def show_progress_bar(self, *, show: bool) -> None:
        self.progressBar.setVisible(show)

    def show_lower_text(self, *, show: bool) -> None:
        self.belowLabel.setVisible(show)


def create_simple_busy_indicator(parent: QWidget, text: str) -> BusyDialog:
    dialog = BusyDialog(parent)
    dialog.show_lower_text(show=False)
    dialog.show_progress_bar(show=False)
    dialog.label.setText(text)
    dialog.setFixedSize(0, 0)
    return dialog
