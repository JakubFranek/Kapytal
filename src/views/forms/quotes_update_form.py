from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import QTableView, QWidget
from src.views import icons
from src.views.base_classes.custom_widget import CustomWidget
from src.views.ui_files.forms.Ui_quotes_update_form import Ui_QuotesUpdateForm


class QuotesUpdateForm(CustomWidget, Ui_QuotesUpdateForm):
    signal_download = pyqtSignal()
    signal_save = pyqtSignal()

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setupUi(self)
        self.setWindowFlag(Qt.WindowType.Window)
        self.setWindowIcon(icons.refresh)

        self.downloadQuotesPushButton.clicked.connect(self.signal_download.emit)
        self.saveQuotesPushButton.clicked.connect(self.signal_save.emit)

    @property
    def table_view(self) -> QTableView:
        return self.tableView
