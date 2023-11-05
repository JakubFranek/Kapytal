from collections.abc import Collection

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QPalette
from PyQt6.QtWidgets import QHeaderView, QLineEdit, QWidget
from src.views import colors, icons
from src.views.base_classes.custom_widget import CustomWidget
from src.views.constants import (
    OwnedSecuritiesTreeColumn,
    SecurityTableColumn,
    ValueTableColumn,
)
from src.views.ui_files.forms.Ui_security_form import Ui_SecurityForm
from src.views.utilities.helper_functions import calculate_table_width
from src.views.widgets.charts.date_line_chart_view import DateLineChartView
from src.views.widgets.charts.line_chart_widget import LineChartWidget


class SecurityForm(CustomWidget, Ui_SecurityForm):
    signal_add_security = pyqtSignal()
    signal_edit_security = pyqtSignal()
    signal_remove_security = pyqtSignal()

    signal_add_price = pyqtSignal()
    signal_edit_price = pyqtSignal()
    signal_remove_prices = pyqtSignal()
    signal_load_price_data = pyqtSignal()

    signal_manage_search_text_changed = pyqtSignal(str)
    signal_overview_search_text_changed = pyqtSignal(str)
    signal_security_selection_changed = pyqtSignal()
    signal_price_selection_changed = pyqtSignal()
    signal_security_table_double_clicked = pyqtSignal()
    signal_price_table_double_clicked = pyqtSignal()

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent=parent)
        self.setupUi(self)
        self.setWindowFlag(Qt.WindowType.Window)
        self.setWindowIcon(icons.security)

        self.actionAdd_Security.triggered.connect(self.signal_add_security.emit)
        self.actionRemove_Security.triggered.connect(self.signal_remove_security.emit)
        self.actionEdit_Security.triggered.connect(self.signal_edit_security.emit)

        self.addToolButton.setDefaultAction(self.actionAdd_Security)
        self.removeToolButton.setDefaultAction(self.actionRemove_Security)
        self.editToolButton.setDefaultAction(self.actionEdit_Security)

        self.actionAdd_Security.setIcon(icons.add)
        self.actionRemove_Security.setIcon(icons.remove)
        self.actionEdit_Security.setIcon(icons.edit)

        self.actionAdd_Price.setIcon(icons.add)
        self.actionEdit_Price.setIcon(icons.edit)
        self.actionRemove_Price.setIcon(icons.remove)
        self.actionLoad_Price_Data.setIcon(icons.open_file)

        self.actionAdd_Price.triggered.connect(self.signal_add_price.emit)
        self.actionEdit_Price.triggered.connect(self.signal_edit_price.emit)
        self.actionRemove_Price.triggered.connect(self.signal_remove_prices.emit)
        self.actionLoad_Price_Data.triggered.connect(self.signal_load_price_data.emit)

        self.addPriceToolButton.setDefaultAction(self.actionAdd_Price)
        self.editPriceToolButton.setDefaultAction(self.actionEdit_Price)
        self.removePriceToolButton.setDefaultAction(self.actionRemove_Price)
        self.loadPriceDataToolButton.setDefaultAction(self.actionLoad_Price_Data)

        self.manageSearchLineEdit.addAction(
            icons.magnifier, QLineEdit.ActionPosition.LeadingPosition
        )
        self.manageSearchLineEdit.textChanged.connect(
            self.signal_manage_search_text_changed.emit
        )
        self.overviewSearchLineEdit.addAction(
            icons.magnifier, QLineEdit.ActionPosition.LeadingPosition
        )
        self.overviewSearchLineEdit.textChanged.connect(
            self.signal_overview_search_text_changed.emit
        )

        self.actionExpand_All.setIcon(icons.expand)
        self.actionCollapse_All.setIcon(icons.collapse)

        self.actionExpand_All.triggered.connect(self.treeView.expandAll)
        self.actionCollapse_All.triggered.connect(self.treeView.collapseAll)

        self.expandAllToolButton.setDefaultAction(self.actionExpand_All)
        self.collapseAllToolButton.setDefaultAction(self.actionCollapse_All)

        background = colors.get_tab_widget_background()

        self.chart_widget = DateLineChartView(self, background)
        self.securityPriceHorizontalLayout.addWidget(self.chart_widget)
        self.securityPriceHorizontalLayout.setStretchFactor(self.chart_widget, 100)
        self.securityPriceHorizontalLayout.setStretchFactor(
            self.securityPriceVerticalLayout, 1
        )

        height = self.tabWidget.currentWidget().height()
        self.splitter.setSizes([200, height - 200])

        self.securityTableView.horizontalHeader().setSortIndicatorClearable(True)
        self.securityPriceTableView.horizontalHeader().setSortIndicatorClearable(True)
        self.treeView.header().setSortIndicatorClearable(True)

        self.securityTableView.doubleClicked.connect(
            self.signal_security_table_double_clicked.emit
        )
        self.securityPriceTableView.doubleClicked.connect(
            self.signal_price_table_double_clicked.emit
        )

    def load_chart_data(  # noqa: PLR0913
        self,
        x: Collection,
        y: Collection,
        title: str,
        y_label: str,
        y_unit: str,
        y_decimals: int,
    ) -> None:
        self.chart_widget.load_data(
            x, y, title, y_label, y_unit=y_unit, y_decimals=y_decimals
        )
        self.update_price_table_width()

    def enable_security_table_actions(self, *, is_security_selected: bool) -> None:
        self.actionRemove_Security.setEnabled(is_security_selected)
        self.actionEdit_Security.setEnabled(is_security_selected)

    def set_price_actions(
        self,
        *,
        is_security_selected: bool,
        is_price_selected: bool,
        is_single_price_selected: bool,
    ) -> None:
        self.actionAdd_Price.setEnabled(is_security_selected)
        self.actionEdit_Price.setEnabled(
            is_security_selected and is_single_price_selected
        )
        self.actionRemove_Price.setEnabled(is_security_selected and is_price_selected)
        self.actionLoad_Price_Data.setEnabled(is_security_selected)

    def finalize_setup(self) -> None:
        self.securityTableView.horizontalHeader().setStretchLastSection(False)
        self.securityTableView.horizontalHeader().setSectionResizeMode(
            SecurityTableColumn.NAME,
            QHeaderView.ResizeMode.ResizeToContents,
        )
        self.securityTableView.horizontalHeader().setSectionResizeMode(
            SecurityTableColumn.SYMBOL,
            QHeaderView.ResizeMode.ResizeToContents,
        )
        self.securityTableView.horizontalHeader().setSectionResizeMode(
            SecurityTableColumn.TYPE,
            QHeaderView.ResizeMode.ResizeToContents,
        )
        self.securityTableView.horizontalHeader().setSectionResizeMode(
            SecurityTableColumn.PRICE,
            QHeaderView.ResizeMode.ResizeToContents,
        )
        self.securityTableView.horizontalHeader().setSectionResizeMode(
            SecurityTableColumn.LAST_DATE,
            QHeaderView.ResizeMode.Stretch,
        )

        style = self.style()
        last_section_text = self.securityTableView.model().headerData(
            SecurityTableColumn.LAST_DATE,
            Qt.Orientation.Horizontal,
            Qt.ItemDataRole.DisplayRole,
        )
        self.securityTableView.horizontalHeader().setMinimumSectionSize(
            style.pixelMetric(style.PixelMetric.PM_HeaderMarkSize)
            + style.pixelMetric(style.PixelMetric.PM_HeaderGripMargin) * 2
            + self.fontMetrics().horizontalAdvance(last_section_text)
        )

        self.securityTableView.selectionModel().selectionChanged.connect(
            self.signal_security_selection_changed.emit
        )
        self.securityTableView.sortByColumn(0, Qt.SortOrder.AscendingOrder)

        self.treeView.header().setStretchLastSection(False)
        self.treeView.header().setSectionResizeMode(
            OwnedSecuritiesTreeColumn.NAME,
            QHeaderView.ResizeMode.Stretch,
        )
        self.treeView.header().setSectionResizeMode(
            OwnedSecuritiesTreeColumn.SHARES,
            QHeaderView.ResizeMode.ResizeToContents,
        )
        self.treeView.header().setSectionResizeMode(
            OwnedSecuritiesTreeColumn.AMOUNT_NATIVE,
            QHeaderView.ResizeMode.ResizeToContents,
        )
        self.treeView.header().setSectionResizeMode(
            OwnedSecuritiesTreeColumn.AMOUNT_BASE,
            QHeaderView.ResizeMode.ResizeToContents,
        )

        self.securityPriceTableView.horizontalHeader().setStretchLastSection(False)
        self.securityPriceTableView.horizontalHeader().setSectionResizeMode(
            ValueTableColumn.DATE,
            QHeaderView.ResizeMode.ResizeToContents,
        )
        self.securityPriceTableView.horizontalHeader().setSectionResizeMode(
            ValueTableColumn.VALUE,
            QHeaderView.ResizeMode.Stretch,
        )
        self.securityPriceTableView.selectionModel().selectionChanged.connect(
            self.signal_price_selection_changed.emit
        )

    def refresh_tree_view(self) -> None:
        self.treeView.expandAll()
        for column in OwnedSecuritiesTreeColumn:
            self.treeView.resizeColumnToContents(column)

    def update_price_table_width(self) -> None:
        self.securityPriceTableView.resizeColumnsToContents()

        price_table_width = calculate_table_width(self.securityPriceTableView)
        self.securityPriceTableView.setFixedWidth(price_table_width + 25)
        self.securityPriceTableView.horizontalHeader().setSectionResizeMode(
            ValueTableColumn.VALUE,
            QHeaderView.ResizeMode.Stretch,
        )
