from datetime import date
from decimal import Decimal

from src.models.model_objects.currency import CashAmount, Currency, ExchangeRate


def test_convert() -> None:
    currencies = get_currencies()
    cash_amount = CashAmount(Decimal(1_000_000), currencies["CZK"])
    res = cash_amount.convert(currencies["BTC"])
    print(res)


def get_currencies() -> dict[str, Currency]:
    btc = Currency("BTC")
    usd = Currency("USD")
    eur = Currency("EUR")
    czk = Currency("CZK")
    pln = Currency("PLN")
    dkk = Currency("DKK")
    rub = Currency("RUB")

    exchange_eur_czk = ExchangeRate(eur, czk)
    exchange_eur_czk.set_rate(date.today(), Decimal("25"))
    exchange_eur_pln = ExchangeRate(eur, pln)
    exchange_pln_rub = ExchangeRate(pln, rub)
    exchange_eur_dkk = ExchangeRate(eur, dkk)
    exchange_eur_rub = ExchangeRate(eur, rub)
    exchange_usd_eur = ExchangeRate(usd, eur)
    exchange_usd_eur.set_rate(date.today(), Decimal("0.8"))
    exchange_btc_usd = ExchangeRate(btc, usd)
    exchange_btc_usd.set_rate(date.today(), Decimal("40000"))

    exchange_usd_rub = ExchangeRate(usd, rub)

    return {
        "BTC": btc,
        "USD": usd,
        "EUR": eur,
        "CZK": czk,
        "PLN": pln,
        "DKK": dkk,
        "RUB": rub,
    }
