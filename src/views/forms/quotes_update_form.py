from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import QTableView, QWidget
from src.views import icons
from src.views.base_classes.custom_widget import CustomWidget
from src.views.ui_files.forms.Ui_quotes_update_form import Ui_QuotesUpdateForm


class QuotesUpdateForm(CustomWidget, Ui_QuotesUpdateForm):
    signal_download = pyqtSignal()
    signal_save = pyqtSignal()
    signal_select_all = pyqtSignal()
    signal_unselect_all = pyqtSignal()

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setupUi(self)
        self.setWindowFlag(Qt.WindowType.Window)
        self.setWindowIcon(icons.refresh)

        self.downloadQuotesPushButton.clicked.connect(self.signal_download.emit)
        self.saveQuotesPushButton.clicked.connect(self.signal_save.emit)

        self.actionSelect_All.setIcon(icons.select_all)
        self.actionUnselect_All.setIcon(icons.unselect_all)

        self.actionSelect_All.triggered.connect(self.signal_select_all.emit)
        self.actionUnselect_All.triggered.connect(self.signal_unselect_all.emit)

        self.selectAllToolButton.setDefaultAction(self.actionSelect_All)
        self.unselectAllToolButton.setDefaultAction(self.actionUnselect_All)

    @property
    def table_view(self) -> QTableView:
        return self.tableView

    def set_button_state(self, *, download: bool, save: bool) -> None:
        self.downloadQuotesPushButton.setEnabled(download)
        self.saveQuotesPushButton.setEnabled(save)
