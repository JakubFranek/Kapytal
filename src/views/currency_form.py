from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QWidget

from src.views.ui_files.Ui_currency_form import Ui_CurrencyForm


class CurrencyForm(QWidget, Ui_CurrencyForm):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent=parent)
        self.setupUi(self)
        self.setWindowFlag(Qt.WindowType.Window)

    def show_form(self) -> None:
        self.show()

    def close_form(self) -> None:
        self.close()
