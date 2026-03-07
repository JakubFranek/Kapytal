from datetime import date, datetime
from decimal import Decimal

import requests
from src.models.user_settings import user_settings


class QuoteUpdateError(ValueError):
    """Raised when an error occurs while updating quotes."""


def get_latest_quote(ticker_code: str) -> tuple[date, Decimal]:
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker_code}"
    params = {"interval": "1d", "range": "1d"}
    response = requests.get(
        url, headers={"User-Agent": "Mozilla/5.0"}, params=params, timeout=10
    )
    response.raise_for_status()

    data = response.json()
    result = data["chart"]["result"]
    if not result:
        raise QuoteUpdateError(f"No data found for ticker '{ticker_code}'.")

    close = result[0]["indicators"]["quote"][0]["close"][-1]
    timestamp = result[0]["timestamp"][-1]

    return datetime.fromtimestamp(
        timestamp, tz=user_settings.settings.time_zone
    ).date(), Decimal(str(round(close, 2)))
