from PyQt6.QtGui import QIcon

folder_open: QIcon | None = None
folder_closed: QIcon | None = None
security_account: QIcon | None = None
cash_account: QIcon | None = None
cash_account_empty: QIcon | None = None
eye_open: QIcon | None = None
eye_partial: QIcon | None = None
eye_closed: QIcon | None = None
income: QIcon | None = None
expense: QIcon | None = None
refund: QIcon | None = None
cash_transfer: QIcon | None = None
buy: QIcon | None = None
sell: QIcon | None = None
security_transfer: QIcon | None = None
payee: QIcon | None = None
split_attribute: QIcon | None = None


def setup() -> None:
    global folder_open, folder_closed, security_account, cash_account  # noqa: PLW0603
    global cash_account_empty, eye_open, eye_partial, eye_closed  # noqa: PLW0603
    global income, expense, refund, cash_transfer, buy, sell  # noqa: PLW0603
    global security_transfer, payee, split_attribute  # noqa: PLW0603

    folder_open = QIcon("icons_16:folder-open.png")
    folder_closed = QIcon("icons_16:folder.png")
    security_account = QIcon("icons_16:bank.png")
    cash_account = QIcon("icons_16:piggy-bank.png")
    cash_account_empty = QIcon("icons_16:piggy-bank-empty.png")
    eye_open = QIcon("icons_16:eye.png")
    eye_partial = QIcon("icons_16:eye-half.png")
    eye_closed = QIcon("icons_16:eye-close.png")
    income = QIcon("icons_custom:coins-plus.png")
    expense = QIcon("icons_custom:coins-minus.png")
    refund = QIcon("icons_custom:coins-arrow-back.png")
    cash_transfer = QIcon("icons_custom:coins-arrow.png")
    buy = QIcon("icons_custom:certificate-plus.png")
    sell = QIcon("icons_custom:certificate-minus.png")
    security_transfer = QIcon("icons_custom:certificate-arrow.png")
    payee = QIcon("icons_16:user-business.png")
    split_attribute = QIcon("icons_16:arrow-split.png")
