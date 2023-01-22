import sys
from datetime import datetime

from PyQt6.QtWidgets import QApplication

from src.models.constants import tzinfo
from src.models.record_keeper import RecordKeeper
from src.presenters.accounts_tree_presenter import AccountsTreePresenter
from src.views.main_view import MainView

# TODO: logging
# TODO: except hook

if __name__ == "__main__":
    app = QApplication(sys.argv)

    main_view = MainView()
    record_keeper = RecordKeeper()
    record_keeper.add_currency("CZK", 2)
    record_keeper.add_account_group("Group A", None)
    record_keeper.add_security_account("Security Acc 1", "Group A")
    record_keeper.add_security_account("Security Acc 2", "Group A")
    record_keeper.add_account_group("Group A.A", "Group A")
    record_keeper.add_security_account("Security Acc 3", "Group A/Group A.A")
    record_keeper.add_cash_account(
        "Cash Acc 1", "CZK", 0, datetime.now(tzinfo), "Group A/Group A.A"
    )
    record_keeper.add_account_group("Group B", None)
    record_keeper.add_security_account("Security Acc 4", "Group B")

    presenter = AccountsTreePresenter(main_view, record_keeper)

    font = app.font()
    font.setPointSize(10)
    app.setFont(font)
    app.exec()
