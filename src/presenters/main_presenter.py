import logging
import webbrowser

from PyQt6.QtWidgets import QApplication
from src.models.record_keeper import RecordKeeper
from src.presenters.file_presenter import FilePresenter
from src.presenters.form.category_form_presenter import CategoryFormPresenter
from src.presenters.form.currency_form_presenter import CurrencyFormPresenter
from src.presenters.form.payee_form_presenter import PayeeFormPresenter
from src.presenters.form.quotes_update_form_presenter import QuotesUpdateFormPresenter
from src.presenters.form.security_form_presenter import SecurityFormPresenter
from src.presenters.form.settings_form_presenter import SettingsFormPresenter
from src.presenters.form.tag_form_presenter import TagFormPresenter
from src.presenters.reports.report_presenter import ReportPresenter
from src.presenters.update_presenter import UpdatePresenter
from src.presenters.widget.account_tree_presenter import AccountTreePresenter
from src.presenters.widget.transactions_presenter import (
    TransactionsPresenter,
)
from src.utilities import constants
from src.views.dialogs.welcome_dialog import WelcomeDialog
from src.views.forms.category_form import CategoryForm
from src.views.forms.currency_form import CurrencyForm
from src.views.forms.payee_form import PayeeForm
from src.views.forms.quotes_update_form import QuotesUpdateForm
from src.views.forms.security_form import SecurityForm
from src.views.forms.settings_form import SettingsForm
from src.views.forms.tag_form import TagForm
from src.views.main_view import MainView


class MainPresenter:
    def __init__(self, view: MainView, app: QApplication) -> None:
        self._view = view
        self._record_keeper = RecordKeeper()
        self._app = app

        self._initialize_presenters()
        self._setup_event_observers()
        self._connect_view_signals()

    def check_for_updates(self, *, silent: bool = True) -> None:
        self._update_presenter.check_for_updates(silent=silent)

    def show_welcome_dialog(self) -> None:
        self._welcome_dialog = WelcomeDialog(self._view)
        self._welcome_dialog.signal_new_file.connect(self._welcome_dialog.close)
        self._welcome_dialog.signal_open_file.connect(self._load_file)
        self._welcome_dialog.signal_open_recent_file.connect(
            self._load_most_recent_file
        )
        self._welcome_dialog.signal_open_demo_file.connect(self._load_demo_file)
        self._welcome_dialog.signal_quit.connect(self._quit)
        self._welcome_dialog.set_open_recent_file_button(
            enabled=len(self._file_presenter.recent_file_paths) > 0
        )
        self._welcome_dialog.show()

    def _load_most_recent_file(self) -> None:
        if self._file_presenter.load_most_recent_file():
            self._welcome_dialog.close()

    def _load_file(self) -> None:
        if self._file_presenter.load_from_file():
            self._welcome_dialog.close()

    def _load_demo_file(self) -> None:
        if (
            self._file_presenter.load_from_file(constants.demo_file_path)
            and self._welcome_dialog.isVisible()
        ):
            self._welcome_dialog.close()

    def _quit(self) -> None:
        if self._file_presenter.check_for_unsaved_changes("Quit") is False:
            return
        logging.info("Qutting")
        self._app.quit()

    def _load_record_keeper(self, record_keeper: RecordKeeper) -> None:
        self._record_keeper = record_keeper
        self._file_presenter.load_record_keeper(record_keeper)
        self._transactions_presenter.load_record_keeper(record_keeper)
        self._account_tree_presenter.load_record_keeper(record_keeper)

        self._currency_form_presenter.load_record_keeper(record_keeper)
        self._payee_form_presenter.load_record_keeper(record_keeper)
        self._tag_form_presenter.load_record_keeper(record_keeper)
        self._security_form_presenter.load_record_keeper(record_keeper)
        self._category_form_presenter.load_record_keeper(record_keeper)

        self._report_presenter.load_record_keeper(record_keeper)
        self._quotes_update_form_presenter.load_record_keeper(record_keeper)

    def _initialize_presenters(self) -> None:
        self._file_presenter = FilePresenter(self._view, self._record_keeper)
        self._update_presenter = UpdatePresenter(self._view)

        self._account_tree_presenter = AccountTreePresenter(
            self._view.account_tree_widget, self._record_keeper
        )
        self._transactions_presenter = TransactionsPresenter(
            self._view.transaction_table_widget, self._record_keeper
        )
        currency_form = CurrencyForm(parent=self._view)
        self._currency_form_presenter = CurrencyFormPresenter(
            currency_form, self._record_keeper
        )
        security_form = SecurityForm(parent=self._view)
        self._security_form_presenter = SecurityFormPresenter(
            security_form, self._record_keeper
        )
        payee_form = PayeeForm(parent=self._view)
        self._payee_form_presenter = PayeeFormPresenter(
            payee_form,
            self._record_keeper,
            self._transactions_presenter.transaction_table_form_presenter,
        )

        tag_form = TagForm(parent=self._view)
        self._tag_form_presenter = TagFormPresenter(
            tag_form,
            self._record_keeper,
            self._transactions_presenter.transaction_table_form_presenter,
        )

        category_form = CategoryForm(parent=self._view)
        self._category_form_presenter = CategoryFormPresenter(
            category_form,
            self._record_keeper,
            self._transactions_presenter.transaction_table_form_presenter,
        )

        settings_form = SettingsForm(parent=self._view)
        self._settings_form_presenter = SettingsFormPresenter(settings_form)

        self._report_presenter = ReportPresenter(
            self._view, self._transactions_presenter, self._record_keeper
        )

        quotes_update_form = QuotesUpdateForm(parent=self._view)
        self._quotes_update_form_presenter = QuotesUpdateFormPresenter(
            quotes_update_form, self._record_keeper
        )

    def _setup_event_observers(self) -> None:
        self._file_presenter.event_load_record_keeper.append(
            lambda record_keeper: self._load_record_keeper(record_keeper)
        )

        self._transactions_presenter.event_account_tree_check_all_items.append(
            lambda: self._account_tree_presenter.set_check_state_all(visible=True)
        )

        self._account_tree_presenter.event_data_changed.append(self._data_changed)
        self._account_tree_presenter.event_check_state_changed.append(
            self._update_checked_accounts
        )
        self._currency_form_presenter.event_base_currency_changed.append(
            self._base_currency_changed
        )
        self._currency_form_presenter.event_data_changed.append(self._data_changed)
        self._security_form_presenter.event_data_changed.append(self._data_changed)
        self._payee_form_presenter.event_data_changed.append(self._data_changed)
        self._tag_form_presenter.event_data_changed.append(self._data_changed)
        self._category_form_presenter.event_data_changed.append(self._data_changed)
        self._transactions_presenter.event_data_changed.append(self._data_changed)
        self._quotes_update_form_presenter.event_data_changed.append(self._data_changed)

    def _connect_view_signals(self) -> None:
        self._view.signal_exit.connect(self._quit)
        self._view.signal_open_currency_form.connect(
            self._currency_form_presenter.show_form
        )
        self._view.signal_open_security_form.connect(
            self._security_form_presenter.show_form
        )
        self._view.signal_open_payee_form.connect(self._payee_form_presenter.show_form)
        self._view.signal_open_tag_form.connect(self._tag_form_presenter.show_form)
        self._view.signal_open_category_form.connect(
            self._category_form_presenter.show_form
        )
        self._view.signal_open_settings_form.connect(
            self._settings_form_presenter.show_form
        )

        self._view.signal_save_file.connect(
            lambda: self._file_presenter.save_to_file(
                self._record_keeper, save_as=False
            )
        )
        self._view.signal_save_file_as.connect(
            lambda: self._file_presenter.save_to_file(self._record_keeper, save_as=True)
        )
        self._view.signal_open_file.connect(self._file_presenter.load_from_file)
        self._view.signal_open_demo_file.connect(self._load_demo_file)
        self._view.signal_open_recent_file.connect(
            lambda path: self._file_presenter.load_from_file(path)
        )
        self._view.signal_clear_recent_files.connect(
            self._file_presenter.clear_recent_paths
        )
        self._view.signal_close_file.connect(self._file_presenter.close_file)

        self._view.signal_show_account_tree.connect(
            lambda checked: self._account_tree_presenter.set_widget_visibility(
                visible=checked
            )
        )
        self._view.signal_show_transaction_table.connect(
            lambda checked: self._transactions_presenter.set_widget_visibility(
                visible=checked
            )
        )
        self._view.signal_update_quotes.connect(
            self._quotes_update_form_presenter.show_form
        )

        self._view.signal_check_updates.connect(
            lambda: self._update_presenter.check_for_updates(silent=False, timeout=10)
        )

        self._view.signal_open_github.connect(self._open_github)

    def _update_checked_accounts(self) -> None:
        self._transactions_presenter.load_account_tree_checked_items(
            self._account_tree_presenter.checked_account_items
        )

    def _data_changed(self) -> None:
        self._transactions_presenter.update_filter_models()
        self._transactions_presenter.refresh_view()
        self._account_tree_presenter.refresh_view()
        self._account_tree_presenter.update_model_data()
        self._account_tree_presenter.update_geometries()
        self._category_form_presenter.data_changed()
        self._payee_form_presenter.data_changed()
        self._tag_form_presenter.data_changed()
        self._security_form_presenter.data_changed()
        self._file_presenter.update_unsaved_changes(unsaved_changes=True)

    def _base_currency_changed(self) -> None:
        self._account_tree_presenter.update_model_data()
        self._transactions_presenter.update_base_currency()
        self._transactions_presenter.resize_table_to_contents()
        self._data_changed()

    def _open_github(self) -> None:
        webbrowser.open(constants.GITHUB_URL)
