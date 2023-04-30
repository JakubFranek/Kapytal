# REFACTOR: refactor the icons module

from pathlib import Path

from PyQt6.QtCore import QDir
from PyQt6.QtGui import QIcon

folder_open: QIcon | None = None
folder_closed: QIcon | None = None
security_account: QIcon | None = None
cash_account: QIcon | None = None
cash_account_empty: QIcon | None = None
eye_open: QIcon | None = None
eye_partial: QIcon | None = None
eye_closed: QIcon | None = None
eye_red: QIcon | None = None
income: QIcon | None = None
expense: QIcon | None = None
refund: QIcon | None = None
cash_transfer: QIcon | None = None
buy: QIcon | None = None
sell: QIcon | None = None
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


def setup() -> None:  # noqa: PLR0915
    global folder_open, folder_closed, security_account  # noqa: PLW0603
    global cash_account, cash_account_empty  # noqa: PLW0603
    global eye_open, eye_partial, eye_closed, eye_red  # noqa: PLW0603
    global income, expense, refund, cash_transfer, buy, sell  # noqa: PLW0603
    global security_transfer, payee, split_attribute  # noqa: PLW0603
    global base_currency, question, disk, disk_warning, disks  # noqa: PLW0603
    global open_file, currency, quit_, security, category, settings  # noqa: PLW0603
    global about, account_tree, add_account_group, edit_account_group  # noqa: PLW0603
    global exchange_rate, add_cash_account, edit_cash_account  # noqa: PLW0603
    global add_cash_transaction, edit_cash_transaction  # noqa: PLW0603
    global add_category, edit_category, add_currency  # noqa: PLW0603
    global add_payee, edit_payee  # noqa: PLW0603
    global add_security_account, edit_security_account  # noqa: PLW0603
    global add_security, edit_security  # noqa: PLW0603
    global magnifier  # noqa: PLW0603
    global tag, add_tag, edit_tag, remove_tag  # noqa: PLW0603
    global filter_, filter_warning  # noqa: PLW0603
    global expand, expand_below, collapse  # noqa: PLW0603
    global critical, warning  # noqa: PLW0603
    global add, edit, remove, duplicate  # noqa: PLW0603
    global transfer  # noqa: PLW0603

    QDir.addSearchPath(
        "icons_24",
        str(Path(QDir.currentPath() + "/resources/icons/icons-24")),
    )
    QDir.addSearchPath(
        "icons_16",
        str(Path(QDir.currentPath() + "/resources/icons/icons-16")),
    )
    QDir.addSearchPath(
        "icons_custom",
        str(Path(QDir.currentPath() + "/resources/icons/icons-custom")),
    )

    folder_open = QIcon("icons_16:folder-open.png")
    folder_closed = QIcon("icons_16:folder.png")
    security_account = QIcon("icons_16:bank.png")
    cash_account = QIcon("icons_16:piggy-bank.png")
    cash_account_empty = QIcon("icons_16:piggy-bank-empty.png")
    eye_open = QIcon("icons_16:eye.png")
    eye_partial = QIcon("icons_16:eye-half.png")
    eye_closed = QIcon("icons_16:eye-close.png")
    eye_red = QIcon("icons_16:eye-red.png")
    income = QIcon("icons_custom:coins-plus.png")
    expense = QIcon("icons_custom:coins-minus.png")
    refund = QIcon("icons_custom:coins-arrow-back.png")
    cash_transfer = QIcon("icons_custom:coins-arrow.png")
    buy = QIcon("icons_custom:certificate-plus.png")
    sell = QIcon("icons_custom:certificate-minus.png")
    security_transfer = QIcon("icons_custom:certificate-arrow.png")
    payee = QIcon("icons_16:user-business.png")
    split_attribute = QIcon("icons_16:arrow-split.png")
    base_currency = QIcon("icons_16:star.png")
    question = QIcon("icons_16:question.png")
    disk = QIcon("icons_16:disk.png")
    disk_warning = QIcon("icons_16:disk--exclamation.png")
    disks = QIcon("icons_16:disks.png")
    open_file = QIcon("icons_16:folder-open-document.png")
    currency = QIcon("icons_custom:currency.png")
    quit_ = QIcon("icons_16:door-open-out.png")
    security = QIcon("icons_16:certificate.png")
    category = QIcon("icons_custom:category.png")
    tag = QIcon("icons_16:tag.png")
    settings = QIcon("icons_16:gear.png")
    about = QIcon("icons_16:information.png")
    account_tree = QIcon("icons_16:folder-tree.png")
    add_account_group = QIcon("icons_16:folder--plus.png")
    edit_account_group = QIcon("icons_16:folder--pencil.png")
    exchange_rate = QIcon("icons_custom:currency-arrow.png")
    add_cash_account = QIcon("icons_custom:piggy-bank-plus.png")
    edit_cash_account = QIcon("icons_custom:piggy-bank-pencil.png")
    add_cash_transaction = QIcon("icons_custom:coins.png")
    edit_cash_transaction = QIcon("icons_custom:coins-pencil.png")
    add_category = QIcon("icons_custom:category-plus.png")
    edit_category = QIcon("icons_custom:category-pencil.png")
    add_currency = QIcon("icons_custom:currency-plus.png")
    add_payee = QIcon("icons_custom:user-business-plus.png")
    edit_payee = QIcon("icons_custom:user-business-pencil.png")
    add_security_account = QIcon("icons_custom:bank-plus.png")
    edit_security_account = QIcon("icons_16:bank--pencil.png")
    add_security = QIcon("icons_custom:certificate-plus.png")
    edit_security = QIcon("icons_custom:certificate-pencil.png")
    magnifier = QIcon("icons_16:magnifier.png")
    add_tag = QIcon("icons_16:tag--plus.png")
    edit_tag = QIcon("icons_16:tag--pencil.png")
    remove_tag = QIcon("icons_16:tag--minus.png")
    filter_ = QIcon("icons_16:funnel.png")
    filter_warning = QIcon("icons_16:funnel--exclamation.png")
    expand = QIcon("icons_custom:arrow-out.png")
    expand_below = QIcon("icons_16:arrow-stop-270.png")
    collapse = QIcon("icons_16:arrow-in.png")
    critical = QIcon("icons_24:cross.png")
    warning = QIcon("icons_24:exclamation.png")
    add = QIcon("icons_16:plus.png")
    edit = QIcon("icons_16:pencil.png")
    remove = QIcon("icons_16:minus.png")
    duplicate = QIcon("icons_16:document-copy.png")
    transfer = QIcon("icons_16:arrow-curve-000-left.png")
