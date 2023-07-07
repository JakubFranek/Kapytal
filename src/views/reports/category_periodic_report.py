from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QHeaderView, QWidget
from src.views import icons
from src.views.base_classes.custom_widget import CustomWidget
from src.views.ui_files.reports.Ui_category_periodic_report import (
    Ui_CategoryPeriodicReport,
)


class CategoryPeriodicReport(CustomWidget, Ui_CategoryPeriodicReport):
    def __init__(
        self,
        title: str,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent=parent)
        self.setupUi(self)

        font = self.font()
        font_size = font.pointSize()
        tree_font = self.incomeTreeView.font()
        tree_font.setPointSize(font_size)
        self.incomeTreeView.setFont(tree_font)
        self.expenseTreeView.setFont(tree_font)

        self.setWindowFlag(Qt.WindowType.Window)
        self.setWindowTitle(title)
        self.setWindowIcon(icons.bar_chart)

        self.actionExpand_All_Income.setIcon(icons.expand)
        self.actionExpand_All_Expense.setIcon(icons.expand)
        self.actionCollapse_All_Income.setIcon(icons.collapse)
        self.actionCollapse_All_Expense.setIcon(icons.collapse)

        self.actionExpand_All_Income.triggered.connect(self.incomeTreeView.expandAll)
        self.actionExpand_All_Expense.triggered.connect(self.expenseTreeView.expandAll)
        self.actionCollapse_All_Income.triggered.connect(
            self.incomeTreeView.collapseAll
        )
        self.actionCollapse_All_Expense.triggered.connect(
            self.expenseTreeView.collapseAll
        )

        self.incomeExpandAllToolButton.setDefaultAction(self.actionExpand_All_Income)
        self.expenseExpandAllToolButton.setDefaultAction(self.actionExpand_All_Expense)
        self.incomeCollapseAllToolButton.setDefaultAction(
            self.actionCollapse_All_Income
        )
        self.expenseCollapseAllToolButton.setDefaultAction(
            self.actionCollapse_All_Expense
        )

    def finalize_setup(self) -> None:
        for column in range(self.incomeTreeView.model().columnCount()):
            self.incomeTreeView.header().setSectionResizeMode(
                column,
                QHeaderView.ResizeMode.ResizeToContents,
            )
        for column in range(self.expenseTreeView.model().columnCount()):
            self.expenseTreeView.header().setSectionResizeMode(
                column,
                QHeaderView.ResizeMode.ResizeToContents,
            )
