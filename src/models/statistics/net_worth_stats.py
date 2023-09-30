from collections.abc import Collection
from dataclasses import dataclass
from datetime import date, timedelta
from enum import Enum, auto
from typing import Self

from src.models.base_classes.account import Account
from src.models.model_objects.cash_objects import CashAccount
from src.models.model_objects.currency_objects import CashAmount, Currency
from src.models.model_objects.security_objects import SecurityAccount


class AssetType(Enum):
    CURRENCY = auto()
    SECURITY = auto()
    ACCOUNT = auto()


@dataclass
class AssetStats:
    name: str
    amount_base: CashAmount
    amount_native: CashAmount | None
    asset_type: AssetType
    children: list[Self]
    parent: Self | None

    def __repr__(self) -> str:
        return f"AssetStats({self.name}, {self.amount_base.to_str_normalized()})"


def calculate_asset_stats(
    accounts: Collection[Account], base_currency: Currency
) -> tuple[AssetStats]:
    stats: dict[str, AssetStats] = {}
    stats["Currencies"] = AssetStats(
        name="Currencies",
        amount_base=base_currency.zero_amount,
        amount_native=None,
        asset_type=AssetType.CURRENCY,
        children=[],
        parent=None,
    )
    stats["Securities"] = AssetStats(
        name="Securities",
        amount_base=base_currency.zero_amount,
        amount_native=None,
        asset_type=AssetType.SECURITY,
        children=[],
        parent=None,
    )

    cash_accounts = [
        account for account in accounts if isinstance(account, CashAccount)
    ]
    security_accounts = [
        account for account in accounts if isinstance(account, SecurityAccount)
    ]

    for account in cash_accounts:
        currency = account.currency

        amount_native = account.get_balance(currency)
        if amount_native.value_rounded == 0:
            continue
        amount_base = account.get_balance(base_currency)
        amount_native_account = (
            amount_native if amount_native.currency != base_currency else None
        )

        account_stats = AssetStats(
            name=account.path,
            amount_base=amount_base,
            amount_native=amount_native_account,
            asset_type=AssetType.ACCOUNT,
            children=[],
            parent=None,
        )

        if currency.code not in stats:
            stats[currency.code] = AssetStats(
                name=currency.code,
                amount_base=base_currency.zero_amount,
                amount_native=currency.zero_amount
                if currency != base_currency
                else None,
                asset_type=AssetType.CURRENCY,
                children=[],
                parent=stats["Currencies"],
            )

        stats[currency.code].amount_base += amount_base
        if amount_native.currency != base_currency:
            stats[currency.code].amount_native += amount_native
        stats[currency.code].children.append(account_stats)
        account_stats.parent = stats[currency.code]

        if stats[currency.code] not in stats["Currencies"].children:
            stats["Currencies"].children.append(stats[currency.code])
        stats["Currencies"].amount_base += amount_base

    for account in security_accounts:
        for security in account.securities:
            amount_native = account.securities[security] * security.price
            amount_base = account.securities[security] * security.price.convert(
                base_currency
            )
            amount_native_account = (
                amount_native if amount_native.currency != base_currency else None
            )

            account_stats = AssetStats(
                name=account.path,
                amount_base=amount_base,
                amount_native=amount_native_account,
                asset_type=AssetType.ACCOUNT,
                children=[],
                parent=None,
            )

            if security.type_ not in stats:
                stats[security.type_] = AssetStats(
                    name=security.type_,
                    amount_base=base_currency.zero_amount,
                    amount_native=None,
                    asset_type=AssetType.SECURITY,
                    children=[],
                    parent=stats["Securities"],
                )
                stats["Securities"].children.append(stats[security.type_])
            stats[security.type_].amount_base += amount_base

            if security.name not in stats:
                stats[security.name] = AssetStats(
                    name=security.name,
                    amount_base=base_currency.zero_amount,
                    amount_native=security.currency.zero_amount
                    if security.currency != base_currency
                    else None,
                    asset_type=AssetType.SECURITY,
                    children=[],
                    parent=stats[security.type_],
                )
                stats[security.type_].children.append(stats[security.name])
            stats[security.name].children.append(account_stats)
            account_stats.parent = stats[security.name]
            stats[security.name].amount_base += amount_base
            if security.currency != base_currency:
                stats[security.name].amount_native += amount_native
            stats["Securities"].amount_base += amount_base

    return tuple(item for item in stats.values() if item.parent is None)


def calculate_net_worth_over_time(
    accounts: Collection[Account],
    base_currency: Currency,
    date_start: date,
    date_end: date,
) -> tuple[tuple[date, CashAmount], ...]:
    data: list[tuple[date, CashAmount]] = []

    current_date = date_start
    while current_date <= date_end:
        net_worth = base_currency.zero_amount
        for account in accounts:
            net_worth += account.get_balance(base_currency, current_date)
        if len(data) == 0 or net_worth != data[-1][1]:
            data.append((current_date, net_worth))
        current_date += timedelta(days=1)
    return tuple(data)
