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
        # self._connect_to_signals()

    # @property
    # def checked_categories(self) -> tuple[Category, ...]:
    #     return self._category_tree_model.checked_items

    def load_record_keeper(self, record_keeper: RecordKeeper) -> None:
        self._record_keeper = record_keeper
        self._income_categories_model.pre_reset_model()
        self._expense_categories_model.pre_reset_model()
        self._income_and_expense_categories_model.pre_reset_model()
        self._income_categories_model.root_categories = (
            record_keeper.root_income_categories
        )
        self._expense_categories_model.root_categories = (
            record_keeper.root_expense_categories
        )
        self._income_and_expense_categories_model.root_categories = (
            record_keeper.root_income_and_expense_categories
        )
        self._income_categories_model.post_reset_model()
        self._expense_categories_model.post_reset_model()
        self._income_and_expense_categories_model.post_reset_model()

    # def load_from_category_filter(
    #     self,
    #     category_filter: CategoryFilter,
    # ) -> None:
    #     pass

    # def _select_all(self) -> None:
    #     self._income_categories_model.pre_reset_model()
    #     # self._category_tree_model.checked_items =
    #     self._income_categories_model.post_reset_model()

    # def _unselect_all(self) -> None:
    #     self._income_categories_model.pre_reset_model()
    #     # self._category_tree_model.checked_items =
    #     self._income_categories_model.post_reset_model()

    def _initialize_models(self) -> None:
        self._income_categories_model = CheckableCategoryTreeModel(
            self._form.currency_list_view, self._record_keeper.root_income_categories
        )
        self._expense_categories_model = CheckableCategoryTreeModel(
            self._form.currency_list_view, self._record_keeper.root_expense_categories
        )
        self._income_and_expense_categories_model = CheckableCategoryTreeModel(
            self._form.currency_list_view,
            self._record_keeper.root_income_and_expense_categories,
        )

        self._form.income_category_tree_view.setModel(self._income_categories_model)
        self._form.expense_category_tree_view.setModel(self._expense_categories_model)
        self._form.income_and_expense_category_tree_view.setModel(
            self._income_and_expense_categories_model
        )

    # def _connect_to_signals(self) -> None:
    # self._form.signal_currencies_select_all.connect(self._select_all)
    # self._form.signal_currencies_unselect_all.connect(self._unselect_all)
