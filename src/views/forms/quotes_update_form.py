from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QCloseEvent
from PyQt6.QtWidgets import QHeaderView, QLineEdit, QTableView, QWidget
from src.views import icons
from src.views.base_classes.custom_widget import CustomWidget
from src.views.constants import QuotesUpdateTableColumn
from src.views.ui_files.forms.Ui_quotes_update_form import Ui_QuotesUpdateForm
from src.views.utilities.message_box_functions import show_info_box


class QuotesUpdateForm(CustomWidget, Ui_QuotesUpdateForm):
    signal_download = pyqtSignal()
    signal_save = pyqtSignal()
    signal_select_all = pyqtSignal()
    signal_unselect_all = pyqtSignal()
    signal_exit = pyqtSignal()
    signal_search_text_changed = pyqtSignal(str)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setupUi(self)
        self.setWindowFlag(Qt.WindowType.Window)
        self.setWindowIcon(icons.refresh)

        self._close_allowed = False

        self.downloadQuotesPushButton.clicked.connect(self.signal_download.emit)
        self.saveQuotesPushButton.clicked.connect(self.signal_save.emit)

        self.actionSelect_All.setIcon(icons.select_all)
        self.actionUnselect_All.setIcon(icons.unselect_all)

        self.actionSelect_All.triggered.connect(self.signal_select_all.emit)
        self.actionUnselect_All.triggered.connect(self.signal_unselect_all.emit)

        self.selectAllToolButton.setDefaultAction(self.actionSelect_All)
        self.unselectAllToolButton.setDefaultAction(self.actionUnselect_All)

        self.helpPushButton.clicked.connect(self._show_help)

        self.searchLineEdit.textChanged.connect(self.signal_search_text_changed.emit)

        self.searchLineEdit.addAction(
            icons.magnifier, QLineEdit.ActionPosition.LeadingPosition
        )

    def finalize_setup(self) -> None:
        self.tableView.horizontalHeader().setSectionResizeMode(
            QuotesUpdateTableColumn.ITEM,
            QHeaderView.ResizeMode.ResizeToContents,
        )

    @property
    def table_view(self) -> QTableView:
        return self.tableView

    def closeEvent(self, event: QCloseEvent) -> None:
        self.signal_exit.emit()
        if not self._close_allowed:
            event.ignore()
        else:
            super().closeEvent(event)

    def set_close_allowed(self, *, allowed: bool) -> None:
        self._close_allowed = allowed

    def set_button_state(self, *, download: bool, save: bool) -> None:
        self.downloadQuotesPushButton.setEnabled(download)
        self.saveQuotesPushButton.setEnabled(save)

    def _show_help(self) -> None:
        text = (
            "<html>"
            "To update quotes, first select the Exchange Rates and Securities you wish "
            "to update, and then click the <b>Download selected</b> button."
            "<br/>"
            "Review the downloaded quotes, deselect the quotes you do not wish to "
            "save, and finally click the <b>Save selected</b> button."
            "<br/>"
            "You can always view, edit or delete the quotes in the <b>Currencies and "
            "Exchange Rates</b> form or in the <b>Securities</b> form respectively."
            "<br/><br/>"
            "Quotes are downloaded from Yahoo Finance."
            "<br/>"
            "If you encounter issues with the quote update, make sure the Exchange "
            "Rates and Securities you selected are available on Yahoo Finance."
            "<br/><br/>"
            "When querying Security prices from Yahoo Finance API, the Security Symbol "
            "strings are used. Securities with empty Symbol string are not eligible "
            "for quote update."
            "<br/><br/>"
            "When querying Exchange Rates, two attempts are made. "
            "<br/>"
            "First, ticker <tt>AAABBB=X</tt> is attempted (where <tt>AAA</tt> is the "
            "primary Currency code and <tt>BBB</tt> is the secondary Currency code). "
            "This ticker format usually works for Exchange Rates between government "
            "issued currencies."
            "<br/>"
            "If the first attempt fails, ticker <tt>AAA-BBB</tt> is attempted. "
            "This ticker format usually works for cryptocurrencies."
            "</html>"
        )
        show_info_box(self, text, "Update Quotes Help")
