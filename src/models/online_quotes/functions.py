from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING

import yfinance as yf

if TYPE_CHECKING:
    import pandas as pd


class QuoteUpdateError(ValueError):
    """Raised when an error occurs while updating quotes."""


def get_latest_quote(ticker_code: str) -> tuple[date, Decimal]:
    ticker = yf.Ticker(ticker_code)
    history = ticker.history(period="1d", rounding=True)
    if history.empty:
        raise QuoteUpdateError(f"No data found for ticker '{ticker_code}'.")
    last_quote = history["Close"].iloc[-1]
    last_quote_decimal = Decimal(str(last_quote))
    last_timestamp: pd.Timestamp = history.index[-1]
    return last_timestamp.date(), last_quote_decimal
