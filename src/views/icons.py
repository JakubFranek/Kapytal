# REFACTOR: refactor the icons module


from PyQt6.QtCore import QDir, Qt
from PyQt6.QtGui import QIcon
from src.utilities import constants
from src.views import colors

folder_open: QIcon | None = None
folder_closed: QIcon | None = None
security_account: QIcon | None = None
cash_account: QIcon | None = None
cash_account_empty: QIcon | None = None
select_all: QIcon | None = None
unselect_all: QIcon | None = None
select_cash_accounts: QIcon | None = None
select_security_accounts: QIcon | None = None
select_this: QIcon | None = None
income: QIcon | None = None
expense: QIcon | None = None
refund: QIcon | None = None
cash_transfer: QIcon | None = None
buy: QIcon | None = None
sell: QIcon | None = None
dividend: QIcon | None = None
security_transfer: QIcon | None = None
payee: QIcon | None = None
split_attribute: QIcon | None = None
base_currency: QIcon | None = None
question: QIcon | None = None
disk: QIcon | None = None
disk_warning: QIcon | None = None
disks: QIcon | None = None
open_file: QIcon | None = None
currency: QIcon | None = None
quit_: QIcon | None = None
security: QIcon | None = None
category: QIcon | None = None
tag: QIcon | None = None
settings: QIcon | None = None
about: QIcon | None = None
account_tree: QIcon | None = None
add_account_group: QIcon | None = None
edit_account_group: QIcon | None = None
exchange_rate: QIcon | None = None
add_cash_account: QIcon | None = None
edit_cash_account: QIcon | None = None
add_cash_transaction: QIcon | None = None
edit_cash_transaction: QIcon | None = None
add_category: QIcon | None = None
edit_category: QIcon | None = None
add_currency: QIcon | None = None
add_payee: QIcon | None = None
edit_payee: QIcon | None = None
add_security_account: QIcon | None = None
edit_security_account: QIcon | None = None
add_security: QIcon | None = None
edit_security: QIcon | None = None
set_security_price: QIcon | None = None
magnifier: QIcon | None = None
add_tag: QIcon | None = None
edit_tag: QIcon | None = None
remove_tag: QIcon | None = None
filter_: QIcon | None = None
filter_warning: QIcon | None = None
expand: QIcon | None = None
expand_below: QIcon | None = None
collapse: QIcon | None = None
critical: QIcon | None = None
warning: QIcon | None = None
add: QIcon | None = None
edit: QIcon | None = None
remove: QIcon | None = None
duplicate: QIcon | None = None
transfer: QIcon | None = None
hourglass: QIcon | None = None
arrow_right: QIcon | None = None
arrow_left: QIcon | None = None
arrow_move: QIcon | None = None
home: QIcon | None = None
slider: QIcon | None = None
bar_chart: QIcon | None = None
pie_chart: QIcon | None = None
calendar: QIcon | None = None
document_smiley: QIcon | None = None
document_clock: QIcon | None = None
document_plus: QIcon | None = None
book_question: QIcon | None = None
table: QIcon | None = None
percent: QIcon | None = None
swap: QIcon | None = None
refresh: QIcon | None = None
clipboard_text: QIcon | None = None
globe: QIcon | None = None
sum_: QIcon | None = None
securities: QIcon | None = None
password: QIcon | None = None
document_import: QIcon | None = None


def setup() -> None:  # noqa: PLR0915
    global folder_open, folder_closed, security_account  # noqa: PLW0603
    global cash_account, cash_account_empty  # noqa: PLW0603
    global select_all, unselect_all  # noqa: PLW0603
    global select_cash_accounts, select_security_accounts, select_this  # noqa: PLW0603
    global income, expense, refund, cash_transfer, buy, sell, dividend  # noqa: PLW0603
    global security_transfer, payee, split_attribute  # noqa: PLW0603
    global base_currency, question, disk, disk_warning, disks  # noqa: PLW0603
    global open_file, currency, quit_, security, category, settings  # noqa: PLW0603
    global about, account_tree, add_account_group, edit_account_group  # noqa: PLW0603
    global exchange_rate, add_cash_account, edit_cash_account  # noqa: PLW0603
    global add_cash_transaction, edit_cash_transaction  # noqa: PLW0603
    global add_category, edit_category, add_currency  # noqa: PLW0603
    global add_payee, edit_payee  # noqa: PLW0603
    global add_security_account, edit_security_account  # noqa: PLW0603
    global add_security, edit_security, set_security_price  # noqa: PLW0603
    global magnifier  # noqa: PLW0603
    global tag, add_tag, edit_tag, remove_tag  # noqa: PLW0603
    global filter_, filter_warning  # noqa: PLW0603
    global expand, expand_below, collapse  # noqa: PLW0603
    global critical, warning  # noqa: PLW0603
    global add, edit, remove, duplicate  # noqa: PLW0603
    global transfer  # noqa: PLW0603
    global hourglass  # noqa: PLW0603
    global arrow_right, arrow_left, arrow_move, home, slider  # noqa: PLW0603
    global bar_chart, pie_chart, calendar  # noqa: PLW0603
    global document_smiley, document_clock, document_plus  # noqa: PLW0603
    global book_question, table, percent  # noqa: PLW0603
    global swap, refresh, clipboard_text, globe, sum_, securities  # noqa: PLW0603
    global password, document_import  # noqa: PLW0603

    QDir.addSearchPath(
        "icons_24",
        str(constants.app_root_path / "resources/icons/icons-24"),
    )
    QDir.addSearchPath(
        "icons_16",
        str(constants.app_root_path / "resources/icons/icons-16"),
    )
    QDir.addSearchPath(
        "icons_custom",
        str(constants.app_root_path / "resources/icons/icons-custom"),
    )

    folder_open = QIcon("icons_16:folder-open.ico")
    folder_closed = QIcon("icons_16:folder.ico")
    security_account = QIcon("icons_16:bank.ico")
    cash_account = QIcon("icons_16:piggy-bank.ico")
    cash_account_empty = QIcon("icons_16:piggy-bank-empty.ico")
    select_all = QIcon("icons_custom:ui-check-boxes-checked.ico")
    unselect_all = QIcon("icons_custom:ui-check-boxes-unchecked.ico")
    select_cash_accounts = QIcon("icons_custom:piggy-bank-check.ico")
    select_security_accounts = QIcon("icons_custom:bank-check.ico")
    select_this = QIcon("icons_16:ui-check-box.ico")
    income = QIcon("icons_custom:coins-plus.ico")
    expense = QIcon("icons_custom:coins-minus.ico")
    refund = QIcon("icons_custom:coins-arrow-back.ico")
    cash_transfer = QIcon("icons_custom:coins-arrow.ico")
    buy = QIcon("icons_custom:certificate-plus.ico")
    sell = QIcon("icons_custom:certificate-minus.ico")
    security_transfer = QIcon("icons_custom:certificate-arrow.ico")
    payee = QIcon("icons_16:user-business.ico")
    split_attribute = QIcon("icons_16:arrow-split.ico")
    base_currency = QIcon("icons_16:star.ico")
    question = QIcon("icons_16:question.ico")
    disk = QIcon("icons_16:disk.ico")
    disk_warning = QIcon("icons_16:disk--exclamation.ico")
    disks = QIcon("icons_16:disks.ico")
    open_file = QIcon("icons_16:folder-open-document.ico")
    currency = QIcon("icons_custom:currency.ico")
    quit_ = QIcon("icons_16:door-open-out.ico")
    security = QIcon("icons_16:certificate.ico")
    category = QIcon("icons_custom:category.ico")
    tag = QIcon("icons_16:tag.ico")
    settings = QIcon("icons_16:gear.ico")
    about = QIcon("icons_16:information.ico")
    account_tree = QIcon("icons_16:folder-tree.ico")
    add_account_group = QIcon("icons_16:folder--plus.ico")
    edit_account_group = QIcon("icons_16:folder--pencil.ico")
    exchange_rate = QIcon("icons_custom:currency-arrow.ico")
    add_cash_account = QIcon("icons_custom:piggy-bank-plus.ico")
    edit_cash_account = QIcon("icons_custom:piggy-bank-pencil.ico")
    add_cash_transaction = QIcon("icons_custom:coins.ico")
    edit_cash_transaction = QIcon("icons_custom:coins-pencil.ico")
    add_category = QIcon("icons_custom:category-plus.ico")
    edit_category = QIcon("icons_custom:category-pencil.ico")
    add_currency = QIcon("icons_custom:currency-plus.ico")
    add_payee = QIcon("icons_custom:user-business-plus.ico")
    edit_payee = QIcon("icons_custom:user-business-pencil.ico")
    add_security_account = QIcon("icons_custom:bank-plus.ico")
    edit_security_account = QIcon("icons_16:bank--pencil.ico")
    add_security = QIcon("icons_custom:certificate-plus.ico")
    edit_security = QIcon("icons_custom:certificate-pencil.ico")
    set_security_price = QIcon("icons_16:chart-up.ico")
    magnifier = QIcon("icons_16:magnifier.ico")
    add_tag = QIcon("icons_16:tag--plus.ico")
    edit_tag = QIcon("icons_custom:tag-pencil.ico")
    remove_tag = QIcon("icons_16:tag--minus.ico")
    filter_ = QIcon("icons_16:funnel.ico")
    filter_warning = QIcon("icons_16:funnel--exclamation.ico")
    expand = QIcon("icons_custom:arrow-out.ico")
    expand_below = QIcon("icons_16:arrow-stop-270.ico")
    collapse = QIcon("icons_16:arrow-in.ico")
    critical = QIcon("icons_24:cross.ico")
    warning = QIcon("icons_24:exclamation.ico")
    add = QIcon("icons_16:plus.ico")
    edit = QIcon("icons_16:pencil.ico")
    remove = QIcon("icons_16:minus.ico")
    duplicate = QIcon("icons_16:document-copy.ico")
    transfer = QIcon("icons_16:arrow-curve-000-left.ico")
    hourglass = QIcon("icons_16:hourglass.ico")
    arrow_right = QIcon("icons_16:arrow.ico")
    arrow_left = QIcon("icons_16:arrow-180.ico")
    arrow_move = QIcon("icons_16:arrow-move.ico")
    home = QIcon("icons_16:home.ico")
    slider = QIcon("icons_16:ui-slider-050.ico")
    bar_chart = QIcon("icons_16:chart.ico")
    pie_chart = QIcon("icons_16:chart-pie.ico")
    calendar = QIcon("icons_16:calendar.ico")
    document_smiley = QIcon("icons_16:document-smiley.ico")
    document_clock = QIcon("icons_16:document-clock.ico")
    document_plus = QIcon("icons_16:document--plus.ico")
    book_question = QIcon("icons_16:book-question.ico")
    table = QIcon("icons_16:table.ico")
    percent = (
        QIcon("icons_custom:percent_dark_mode.ico")
        if colors.color_scheme == Qt.ColorScheme.Dark
        else QIcon("icons_custom:percent_light_mode.ico")
    )
    swap = QIcon("icons_16:arrow-switch.ico")
    refresh = QIcon("icons_16:arrow-circle-double.ico")
    clipboard_text = QIcon("icons_16:clipboard-text.ico")
    globe = QIcon("icons_16:globe-green.ico")
    sum_ = (
        QIcon("icons_custom:sum_dark_mode.ico")
        if colors.color_scheme == Qt.ColorScheme.Dark
        else QIcon("icons_custom:sum_light_mode.ico")
    )
    dividend = QIcon("icons_custom:certificate-coin.ico")
    securities = QIcon("icons_custom:certificates.ico")
    password = QIcon("icons_16:ui-text-field-password.ico")
    document_import = QIcon("icons_16:document-import.ico")
