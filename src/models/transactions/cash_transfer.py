from datetime import datetime
from decimal import Decimal

from src.models.accounts.cash_account import CashAccount
from src.models.constants import tzinfo
from src.models.transactions.transaction import Transaction


class CashTransfer(Transaction):
    def __init__(  # noqa: TMN001, CFQ002
        self,
        description: str,
        datetime_: datetime,
        account_sender: CashAccount,
        account_recipient: CashAccount,
        amount_sent: Decimal,
        amount_received: Decimal,
    ) -> None:
        super().__init__(description, datetime_)
        self.account_sender = account_sender
        self.account_recipient = account_recipient
        self.amount_sent = amount_sent
        self.amount_received = amount_received

    @property
    def account_sender(self) -> CashAccount:
        return self._account_sender

    @account_sender.setter
    def account_sender(self, value: CashAccount) -> None:
        if not isinstance(value, CashAccount):
            raise TypeError("CashTransfer.account_sender must be a CashAccount.")
        self._account_sender = value
        self._datetime_edited = datetime.now(tzinfo)

    @property
    def account_recipient(self) -> CashAccount:
        return self._account_recipient

    @account_recipient.setter
    def account_recipient(self, value: CashAccount) -> None:
        if not isinstance(value, CashAccount):
            raise TypeError("CashTransfer.account_recipient must be a CashAccount.")
        self._account_recipient = value
        self._datetime_edited = datetime.now(tzinfo)

    @property
    def amount_sent(self) -> Decimal:
        return self._amount_sent

    @amount_sent.setter
    def amount_sent(self, value: Decimal) -> None:
        if not isinstance(value, Decimal):
            raise TypeError("CashTransfer.amount_sent must be a Decimal.")
        if not value.is_finite() or value <= 0:
            raise ValueError(
                "CashTransfer.amount_sent must be a finite and positive Decimal."
            )
        self._amount_sent = value
        self._datetime_edited = datetime.now(tzinfo)

    @property
    def amount_received(self) -> Decimal:
        return self._amount_received

    @amount_received.setter
    def amount_received(self, value: Decimal) -> None:
        if not isinstance(value, Decimal):
            raise TypeError("CashTransfer.amount_received must be a Decimal.")
        if not value.is_finite() or value <= 0:
            raise ValueError(
                "CashTransfer.amount_received must be a finite and positive Decimal."
            )
        self._amount_received = value
        self._datetime_edited = datetime.now(tzinfo)
