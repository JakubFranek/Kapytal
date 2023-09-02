import logging
from typing import Any

from PyQt6.QtCore import QSortFilterProxyModel, Qt
from PyQt6.QtWidgets import QApplication
from src.models.custom_exceptions import AlreadyExistsError, InvalidOperationError
from src.models.model_objects.attributes import AttributeType
from src.models.record_keeper import RecordKeeper
from src.models.statistics.attribute_stats import calculate_attribute_stats
from src.presenters.form.transaction_table_form_presenter import (
    TransactionTableFormPresenter,
)
from src.presenters.utilities.event import Event
from src.presenters.utilities.handle_exception import handle_exception
from src.view_models.attribute_table_model import AttributeTableModel
from src.views.dialogs.busy_dialog import create_simple_busy_indicator
from src.views.dialogs.tag_dialog import TagDialog
from src.views.forms.tag_form import TagForm
from src.views.utilities.message_box_functions import ask_yes_no_question

BUSY_DIALOG_TRANSACTION_LIMIT = 20_000


class TagFormPresenter:
    event_data_changed = Event()

    def __init__(
        self,
        view: TagForm,
        record_keeper: RecordKeeper,
        transaction_table_form_presenter: TransactionTableFormPresenter,
    ) -> None:
        self._view = view
        self._record_keeper = record_keeper
        self._transaction_table_form_presenter = transaction_table_form_presenter

        self._proxy_model = QSortFilterProxyModel(self._view.tableView)
        self._model = AttributeTableModel(self._view.tableView, self._proxy_model)
        self._update_model_data()
        self._proxy_model.setSourceModel(self._model)
        self._proxy_model.setSortRole(Qt.ItemDataRole.UserRole)
        self._proxy_model.setSortCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self._proxy_model.setFilterCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self._view.tableView.setModel(self._proxy_model)

        self._view.signal_add_tag.connect(lambda: self._run_tag_dialog(edit=False))
        self._view.signal_remove_tag.connect(self._remove_tag)
        self._view.signal_rename_tag.connect(lambda: self._run_tag_dialog(edit=True))
        self._view.signal_show_transactions.connect(self._show_transactions)
        self._view.signal_search_text_changed.connect(self._filter)

        self._view.finalize_setup()
        self._view.signal_selection_changed.connect(self._selection_changed)
        self._selection_changed()

    def load_record_keeper(self, record_keeper: RecordKeeper) -> None:
        self._record_keeper = record_keeper
        self._recalculate_data = True

    def data_changed(self) -> None:
        self._recalculate_data = True

    def reset_model(self) -> None:
        self._model.pre_reset_model()
        self._update_model_data_with_busy_dialog()
        self._model.post_reset_model()

    def show_form(self) -> None:
        if self._recalculate_data:
            self.reset_model()
        self._view.show_form()

    def _update_model_data(self) -> None:
        relevant_transactions = (
            self._record_keeper.cash_transactions
            + self._record_keeper.refund_transactions
        )
        tag_stats = calculate_attribute_stats(
            relevant_transactions,
            self._record_keeper.base_currency,
            self._record_keeper.tags,
        ).values()
        self._model.load_attribute_stats(tag_stats)
        self._recalculate_data = False

    def _update_model_data_with_busy_dialog(self) -> None:
        no_of_transactions = len(self._record_keeper.transactions)
        if no_of_transactions >= BUSY_DIALOG_TRANSACTION_LIMIT:
            self._busy_dialog = create_simple_busy_indicator(
                self._view, "Calculating Tag stats, please wait..."
            )
            self._busy_dialog.open()
            QApplication.processEvents()
        try:
            self._update_model_data()
        except:  # noqa: TRY302
            raise
        finally:
            if no_of_transactions >= BUSY_DIALOG_TRANSACTION_LIMIT:
                self._busy_dialog.close()

    def _run_tag_dialog(self, *, edit: bool) -> None:
        self._dialog = TagDialog(self._view, edit=edit)
        if edit:
            tags = self._model.get_selected_attributes()
            if len(tags) == 0:
                raise ValueError("Cannot edit an unselected item.")
            if len(tags) > 1:
                raise ValueError("Cannot edit more than one item.")
            tag = tags[0]
            self._dialog.signal_ok.connect(self._rename_tag)
            self._dialog.name = tag.name
        else:
            self._dialog.signal_ok.connect(self._add_tag)
        logging.debug(f"Running TagDialog ({edit=})")
        self._dialog.exec()

    def _add_tag(self) -> None:
        name = self._dialog.name

        logging.info(f"Adding Tag: {name=}")
        try:
            self._record_keeper.add_tag(name)
        except Exception as exception:  # noqa: BLE001
            handle_exception(exception)
            return

        self._model.pre_add()
        self._update_model_data_with_busy_dialog()
        self._model.post_add()
        self._dialog.close()
        self.event_data_changed()
        self._recalculate_data = False

    def _rename_tag(self) -> None:
        tags = self._model.get_selected_attributes()
        if len(tags) == 0:
            raise ValueError("Cannot edit an unselected item.")
        if len(tags) > 1:
            raise ValueError("Cannot edit more than one item.")
        tag = tags[0]
        current_name = tag.name
        new_name = self._dialog.name

        logging.info(f"Renaming Tag '{current_name}' to '{new_name}'")
        try:
            self._record_keeper.edit_attribute(
                current_name, new_name, AttributeType.TAG
            )
            self._update_model_data_with_busy_dialog()
        except AlreadyExistsError:
            if not ask_yes_no_question(
                self._dialog,
                f"<html>Tag <b><i>{new_name}</i></b> already exists.<br/>"
                f"Do you want to merge <b><i>{current_name}</i></b> into "
                f"<b><i>{new_name}</i></b>?</html>",
                "Merge Tags?",
            ):
                logging.debug(
                    f"User cancelled Tag merge ('{current_name}' into '{new_name}')"
                )
                return
            self._model.pre_remove_item(tag)
            self._record_keeper.edit_attribute(
                current_name, new_name, AttributeType.TAG, merge=True
            )
            self._update_model_data_with_busy_dialog()
            self._model.post_remove_item()
        except Exception as exception:  # noqa: BLE001
            handle_exception(exception)
            return

        self._dialog.close()
        self.event_data_changed()
        self._recalculate_data = False

    def _remove_tag(self) -> None:
        tags = self._model.get_selected_attributes()
        if len(tags) == 0:
            raise ValueError("Cannot remove an unselected item.")

        tag_names = ["'" + tag.name + "'" for tag in tags]
        logging.info(f"Removing Tags: {', '.join(tag_names)}")
        any_deleted = False
        for tag in tags:
            try:
                self._record_keeper.remove_tag(tag.name)
                self._model.pre_remove_item(tag)
                self._update_model_data_with_busy_dialog()
                self._model.post_remove_item()
                any_deleted = True
            except Exception as exception:  # noqa: BLE001
                handle_exception(exception)
        if any_deleted:
            self.event_data_changed()
            self._recalculate_data = False

    def _filter(self, pattern: str) -> None:
        if ("[" in pattern and "]" not in pattern) or "[]" in pattern:
            return
        self._proxy_model.setFilterWildcard(pattern)

    def _selection_changed(self) -> None:
        tags = self._model.get_selected_attributes()
        try:
            transactions = self._model.get_selected_attribute_transactions()
        except InvalidOperationError:
            show_transactions = False
        else:
            show_transactions = len(transactions) > 0
        is_tag_selected = len(tags) > 0
        is_one_tag_selected = len(tags) == 1
        self._view.enable_actions(
            is_tag_selected=is_tag_selected,
            is_one_tag_selected=is_one_tag_selected,
            show_transactions=show_transactions,
        )

    def _show_transactions(self) -> None:
        tag = self._model.get_selected_attributes()[0]
        transactions = self._model.get_selected_attribute_transactions()
        title = f"Tag Transactions - {tag.name}"
        self._transaction_table_form_presenter.event_data_changed.append(
            self._transaction_table_form_data_changed
        )
        self._transaction_table_form_presenter.event_form_closed.append(
            self._transaction_table_form_closed
        )
        self._transaction_table_form_presenter.load_data(transactions, title)
        self._transaction_table_form_presenter.show_form(self._view)

    def _transaction_table_form_data_changed(
        self, *_: Any, **__: Any  # noqa: ANN401
    ) -> None:
        self._recalculate_data = True

    def _transaction_table_form_closed(self) -> None:
        if self._recalculate_data:
            self.reset_model()
        self._transaction_table_form_presenter.event_data_changed.remove(
            self._transaction_table_form_data_changed
        )
        self._transaction_table_form_presenter.event_form_closed.remove(
            self._transaction_table_form_closed
        )
