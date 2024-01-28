from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import QAbstractButton, QDialogButtonBox, QFileDialog, QWidget
from src.models.user_settings.user_settings_class import NumberFormat
from src.views import icons
from src.views.base_classes.custom_widget import CustomWidget
from src.views.ui_files.forms.Ui_settings_form import Ui_SettingsForm

# IDEA: link to documentation instead of notes?


class SettingsForm(CustomWidget, Ui_SettingsForm):
    signal_ok = pyqtSignal()
    signal_apply = pyqtSignal()

    signal_data_changed = pyqtSignal()

    signal_open_logs = pyqtSignal()

    signal_open_backup_path = pyqtSignal()
    signal_add_backup_path = pyqtSignal()
    signal_remove_backup_path = pyqtSignal()
    signal_backup_path_selection_changed = pyqtSignal()

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent=parent)
        self.setupUi(self)
        self.setWindowFlag(Qt.WindowType.Window)
        self.setWindowIcon(icons.settings)

        for item in NumberFormat:
            self.numberFormatComboBox.addItem(item.value)

        self.buttonBox.clicked.connect(self._handle_button_box_click)
        self.addBackupDirectoryButton.clicked.connect(self.signal_add_backup_path)
        self.removeBackupDirectoryButton.clicked.connect(self.signal_remove_backup_path)
        self.openBackupDirectoryButton.clicked.connect(self.signal_open_backup_path)
        self.openLogsDirectoryButton.clicked.connect(self.signal_open_logs)

        self.logsSizeLimitSpinBox.valueChanged.connect(self.signal_data_changed.emit)
        self.backupsSizeLimitSpinBox.valueChanged.connect(self.signal_data_changed.emit)
        self.generalDateFormatLineEdit.textEdited.connect(self.signal_data_changed.emit)
        self.transactionTableDateFormatLineEdit.textEdited.connect(
            self.signal_data_changed.emit
        )
        self.numberFormatComboBox.currentTextChanged.connect(self.signal_data_changed)
        self.exchangeRateDecimalsSpinBox.valueChanged.connect(
            self.signal_data_changed.emit
        )
        self.pricePerShareDecimalsSpinBox.valueChanged.connect(
            self.signal_data_changed.emit
        )
        self.checkforUpdatesCheckBox.toggled.connect(self.signal_data_changed.emit)

        self.exchangeRateDecimalsSpinBox.setMaximum(18)
        self.pricePerShareDecimalsSpinBox.setMaximum(18)

    @property
    def exchange_rate_decimals(self) -> int:
        return self.exchangeRateDecimalsSpinBox.value()

    @exchange_rate_decimals.setter
    def exchange_rate_decimals(self, value: int) -> None:
        self.exchangeRateDecimalsSpinBox.setValue(value)

    @property
    def amount_per_share_decimals(self) -> int:
        return self.pricePerShareDecimalsSpinBox.value()

    @amount_per_share_decimals.setter
    def amount_per_share_decimals(self, value: int) -> None:
        self.pricePerShareDecimalsSpinBox.setValue(value)

    @property
    def general_date_format(self) -> str:
        return self.generalDateFormatLineEdit.text()

    @general_date_format.setter
    def general_date_format(self, value: str) -> None:
        self.generalDateFormatLineEdit.setText(value)

    @property
    def transaction_date_format(self) -> str:
        return self.transactionTableDateFormatLineEdit.text()

    @transaction_date_format.setter
    def transaction_date_format(self, value: str) -> None:
        self.transactionTableDateFormatLineEdit.setText(value)

    @property
    def backups_max_size_kb(self) -> int:
        return self.backupsSizeLimitSpinBox.value()

    @backups_max_size_kb.setter
    def backups_max_size_kb(self, value: int) -> None:
        self.backupsSizeLimitSpinBox.setValue(value)

    @property
    def logs_max_size_kb(self) -> int:
        return self.logsSizeLimitSpinBox.value()

    @logs_max_size_kb.setter
    def logs_max_size_kb(self, value: int) -> None:
        self.logsSizeLimitSpinBox.setValue(value)

    @property
    def check_for_updates_on_startup(self) -> bool:
        return self.checkforUpdatesCheckBox.isChecked()

    @check_for_updates_on_startup.setter
    def check_for_updates_on_startup(self, value: bool) -> None:
        self.checkforUpdatesCheckBox.setChecked(value)

    @property
    def number_format(self) -> NumberFormat:
        return NumberFormat(self.numberFormatComboBox.currentText())

    @number_format.setter
    def number_format(self, value: NumberFormat) -> None:
        self.numberFormatComboBox.setCurrentText(value.value)

    def get_directory_path(self) -> str:
        return QFileDialog.getExistingDirectory(self)

    def set_backup_path_buttons(self, *, is_backup_path_selected: bool) -> None:
        self.openBackupDirectoryButton.setEnabled(is_backup_path_selected)
        self.removeBackupDirectoryButton.setEnabled(is_backup_path_selected)

    def finalize_setup(self) -> None:
        self.backupsListView.selectionModel().selectionChanged.connect(
            self.signal_backup_path_selection_changed.emit
        )

    def _handle_button_box_click(self, button: QAbstractButton) -> None:
        role = self.buttonBox.buttonRole(button)
        if role == QDialogButtonBox.ButtonRole.AcceptRole:
            self.signal_ok.emit()
        elif role == QDialogButtonBox.ButtonRole.ApplyRole:
            self.signal_apply.emit()
        elif role == QDialogButtonBox.ButtonRole.RejectRole:
            self.close()
        else:
            raise ValueError("Unknown role of the clicked button in the ButtonBox")
