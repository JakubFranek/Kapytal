from src.models.base_classes.transaction import Transaction
from src.models.model_objects.cash_objects import (
    CashTransactionType,
)
from src.models.model_objects.security_objects import (
    SecurityTransactionType,
)
from src.models.transaction_filters.base_transaction_filter import FilterMode
from src.models.transaction_filters.type_filter import TYPE_NAME_DICT, TypeFilter
from src.presenters.utilities.event import Event
from src.view_models.checkable_list_model import CheckableListModel
from src.views.forms.transaction_filter_form import TransactionFilterForm


class TypeFilterPresenter:
    event_filter_changed = Event()

    def __init__(
        self,
        form: TransactionFilterForm,
    ) -> None:
        self._form = form
        self._initialize_model()
        self._connect_to_signals()

    @property
    def type_filter_mode(self) -> FilterMode:
        return FilterMode.KEEP

    @property
    def checked_types(
        self,
    ) -> frozenset[type[Transaction] | CashTransactionType | SecurityTransactionType,]:
        # use type_dict to get value from key
        return frozenset(
            type_
            for type_ in TYPE_NAME_DICT
            if TYPE_NAME_DICT[type_] in self._type_list_model.checked_items
        )

    @checked_types.setter
    def checked_types(
        self,
        types: tuple[
            type[Transaction] | CashTransactionType | SecurityTransactionType, ...
        ],
    ) -> None:
        self._type_list_model.pre_reset_model()
        self._type_list_model.load_checked_items(
            tuple(TYPE_NAME_DICT[type_] for type_ in types)
        )
        self._type_list_model.post_reset_model()

    def load_from_type_filter(
        self,
        type_filter: TypeFilter,
    ) -> None:
        self._type_list_model.load_checked_items(type_filter.type_names)

    def _select_all(self) -> None:
        self._type_list_model.load_checked_items(tuple(TYPE_NAME_DICT.values()))

    def _unselect_all(self) -> None:
        self._type_list_model.load_checked_items(())

    def _initialize_model(self) -> None:
        self._type_list_model = CheckableListModel(
            self._form.types_list_view,
            None,
            sort=False,
        )
        self._type_list_model.load_items(tuple(TYPE_NAME_DICT.values()))
        self._type_list_model.load_checked_items(tuple(TYPE_NAME_DICT.values()))

        self._form.types_list_view.setModel(self._type_list_model)

    def _connect_to_signals(self) -> None:
        self._form.signal_types_select_all.connect(self._select_all)
        self._form.signal_types_unselect_all.connect(self._unselect_all)
