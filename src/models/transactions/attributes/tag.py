from datetime import datetime
from decimal import Decimal

from src.models.constants import tzinfo
from src.models.enums import CashTransactionType


class Tag:
    NAME_MIN_LENGTH = 1
    NAME_MAX_LENGTH = 32

    def __init__(self, name: str) -> None:
        self._name = None
        self.name = name
        self._date_created = datetime.now(tzinfo)
        self._date_last_edited = self.date_created
        self._total_expense = Decimal(0)
        self._total_income = Decimal(0)
        self._total_volume = Decimal(0)
        self._total_sum = Decimal(0)

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, value: str) -> None:
        if not isinstance(value, str):
            raise TypeError("Tag name must be a string.")

        if self._name != value:
            if len(value) < Tag.NAME_MIN_LENGTH or len(value) > Tag.NAME_MAX_LENGTH:
                raise ValueError(
                    f"""Tag name length must be between {Tag.NAME_MIN_LENGTH}
                    and {Tag.NAME_MAX_LENGTH} characters."""
                )
            self._name = value
            self._date_last_edited = datetime.now(tzinfo)

    @property
    def total_expense(self) -> Decimal:
        return self._total_expense

    @property
    def total_income(self) -> Decimal:
        return self._total_income

    @property
    def total_volume(self) -> Decimal:
        return self._total_volume

    @property
    def total_sum(self) -> Decimal:
        return self._total_sum

    @property
    def date_created(self) -> datetime:
        return self._date_created

    @property
    def date_last_edited(self) -> datetime:
        return self._date_last_edited

    def update_totals(
        self, amount: Decimal, transaction_type: CashTransactionType
    ) -> None:
        """Updates Tag totals (total_expense, total_income, total_volume and total_sum)
        with the amount of a single tagged transaction.

        Args:
            amount (Decimal): amount of the tagged transaction (positive, finite)
            transaction_type (CashTransactionType): type of the tagged transaction

        Raises:
            TypeError: if amount is not a Decimal
            TypeError: if transaction_type is not a CashTransactionType
            ValueError: if amount is not positive or finite
        """
        if not isinstance(amount, Decimal):
            raise TypeError("Update amount must be of type Decimal.")
        if not isinstance(transaction_type, CashTransactionType):
            raise TypeError("Transaction type must be of type CashTransactionType.")

        if amount.is_signed() or not amount.is_finite():
            raise ValueError("Update amount must be a finite and positive Decimal.")

        if transaction_type == CashTransactionType.EXPENSE:
            self._total_expense += amount
        if transaction_type == CashTransactionType.INCOME:
            self._total_income += amount

        self._total_volume += amount
        self._total_sum = self._total_income - self._total_expense
