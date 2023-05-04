import logging

from PyQt6.QtCore import QSortFilterProxyModel, Qt
from src.models.model_objects.attributes import Category
from src.models.record_keeper import RecordKeeper
from src.models.transaction_filters.base_transaction_filter import FilterMode
from src.models.transaction_filters.currency_filter import CurrencyFilter
from src.view_models.checkable_category_tree_model import CheckableCategoryTreeModel
from src.views.forms.transaction_filter_form import TransactionFilterForm


class CategoryFilterPresenter:
    def __init__(
        self, form: TransactionFilterForm, record_keeper: RecordKeeper
    ) -> None:
        self._form = form
        self._record_keeper = record_keeper
        self._initialize_models()
        self._connect_to_signals()

    @property
    def checked_categories(self) -> tuple[Category, ...]:
        return (
            self._income_categories_model.checked_categories
            + self._expense_categories_model.checked_categories
            + self._income_and_expense_categories_model.checked_categories
        )

    def load_record_keeper(self, record_keeper: RecordKeeper) -> None:
        self._record_keeper = record_keeper
        self._income_categories_model.pre_reset_model()
        self._expense_categories_model.pre_reset_model()
        self._income_and_expense_categories_model.pre_reset_model()
        self._income_categories_model.flat_categories = record_keeper.income_categories
        self._expense_categories_model.flat_categories = (
            record_keeper.expense_categories
        )
        self._income_and_expense_categories_model.flat_categories = (
            record_keeper.income_and_expense_categories
        )
        self._income_categories_model.post_reset_model()
        self._expense_categories_model.post_reset_model()
        self._income_and_expense_categories_model.post_reset_model()

    # def load_from_category_filter(
    #     self,
    #     category_filter: CategoryFilter,
    # ) -> None:
    #     pass

    def _filter(self, pattern: str, proxy: QSortFilterProxyModel) -> None:
        if ("[" in pattern and "]" not in pattern) or "[]" in pattern:
            return
        if proxy == self._income_categories_proxy:
            logging.debug(f"Filtering Income Categories: {pattern=}")
        elif proxy == self._expense_categories_proxy:
            logging.debug(f"Filtering Expense Categories: {pattern=}")
        else:
            logging.debug(f"Filtering Income and Expense Categories: {pattern=}")
        proxy.setFilterWildcard(pattern)

    def _initialize_models(self) -> None:
        self._income_categories_proxy = QSortFilterProxyModel(self._form)
        self._expense_categories_proxy = QSortFilterProxyModel(self._form)
        self._income_and_expense_categories_proxy = QSortFilterProxyModel(self._form)

        self._income_categories_proxy.setFilterCaseSensitivity(
            Qt.CaseSensitivity.CaseInsensitive
        )
        self._expense_categories_proxy.setFilterCaseSensitivity(
            Qt.CaseSensitivity.CaseInsensitive
        )
        self._income_and_expense_categories_proxy.setFilterCaseSensitivity(
            Qt.CaseSensitivity.CaseInsensitive
        )

        self._income_categories_proxy.setRecursiveFilteringEnabled(True)  # noqa: FBT003
        self._expense_categories_proxy.setRecursiveFilteringEnabled(
            True  # noqa: FBT003
        )
        self._income_and_expense_categories_proxy.setRecursiveFilteringEnabled(
            True  # noqa: FBT003
        )

        self._income_categories_model = CheckableCategoryTreeModel(
            self._form.currency_list_view, self._record_keeper.income_categories
        )
        self._expense_categories_model = CheckableCategoryTreeModel(
            self._form.currency_list_view, self._record_keeper.expense_categories
        )
        self._income_and_expense_categories_model = CheckableCategoryTreeModel(
            self._form.currency_list_view,
            self._record_keeper.income_and_expense_categories,
        )

        self._income_categories_proxy.setSourceModel(self._income_categories_model)
        self._expense_categories_proxy.setSourceModel(self._expense_categories_model)
        self._income_and_expense_categories_proxy.setSourceModel(
            self._income_and_expense_categories_model
        )

        self._form.income_category_tree_view.setModel(self._income_categories_proxy)
        self._form.expense_category_tree_view.setModel(self._expense_categories_proxy)
        self._form.income_and_expense_category_tree_view.setModel(
            self._income_and_expense_categories_proxy
        )

    def _connect_to_signals(self) -> None:
        self._form.signal_category_selection_mode_changed.connect(
            self._selection_mode_changed
        )

        self._form.signal_income_categories_select_all.connect(
            self._income_categories_model.select_all
        )
        self._form.signal_income_categories_unselect_all.connect(
            self._income_categories_model.unselect_all
        )
        self._form.signal_expense_categories_select_all.connect(
            self._expense_categories_model.select_all
        )
        self._form.signal_expense_categories_unselect_all.connect(
            self._expense_categories_model.unselect_all
        )
        self._form.signal_income_and_expense_categories_select_all.connect(
            self._income_and_expense_categories_model.select_all
        )
        self._form.signal_income_and_expense_categories_unselect_all.connect(
            self._income_and_expense_categories_model.unselect_all
        )

        self._form.signal_income_categories_search_text_changed.connect(
            lambda pattern: self._filter(pattern, self._income_categories_proxy)
        )
        self._form.signal_expense_categories_search_text_changed.connect(
            lambda pattern: self._filter(pattern, self._expense_categories_proxy)
        )
        self._form.signal_income_and_expense_categories_search_text_changed.connect(
            lambda pattern: self._filter(
                pattern, self._income_and_expense_categories_proxy
            )
        )

    def _selection_mode_changed(self) -> None:
        selection_mode = self._form.category_selection_mode
        self._income_categories_model.selection_mode = selection_mode
        self._expense_categories_model.selection_mode = selection_mode
        self._income_and_expense_categories_model.selection_mode = selection_mode
        logging.debug(f"Category selection mode changed: {selection_mode.name}")
