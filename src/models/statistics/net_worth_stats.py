from collections.abc import Collection
from dataclasses import dataclass
from datetime import date, timedelta
from enum import Enum, auto
from typing import Self

from src.models.base_classes.account import Account
from src.models.model_objects.cash_objects import CashAccount
from src.models.model_objects.currency_objects import CashAmount, Currency
from src.models.model_objects.security_objects import SecurityAccount


class RootAssetType(Enum):
    CURRENCY = auto()
    SECURITY = auto()


@dataclass
class AssetStats:
    name: str
    amount_base: CashAmount
    amount_native: CashAmount | None
    root_asset_type: RootAssetType
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
        root_asset_type=RootAssetType.CURRENCY,
        children=[],
        parent=None,
    )
    stats["Securities"] = AssetStats(
        name="Securities",
        amount_base=base_currency.zero_amount,
        amount_native=None,
        root_asset_type=RootAssetType.SECURITY,
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
        amount = account.get_balance(base_currency)
        if currency.code not in stats:
            stats[currency.code] = AssetStats(
                name=currency.code,
                amount_base=amount,
                amount_native=account.get_balance(account.currency),
                root_asset_type=RootAssetType.CURRENCY,
                children=[],
                parent=stats["Currencies"],
            )
        else:
            stats[currency.code].amount_base += amount
            stats[currency.code].amount_native += account.get_balance(account.currency)

        if stats[currency.code] not in stats["Currencies"].children:
            stats["Currencies"].children.append(stats[currency.code])
        stats["Currencies"].amount_base += amount

    for account in security_accounts:
        for security in account.securities:
            amount = account.securities[security] * security.price.convert(
                base_currency
            )
            if security.type_ not in stats:
                stats[security.type_] = AssetStats(
                    name=security.type_,
                    amount_base=amount,
                    amount_native=None,
                    root_asset_type=RootAssetType.SECURITY,
                    children=[],
                    parent=stats["Securities"],
                )
                stats["Securities"].children.append(stats[security.type_])
            else:
                stats[security.type_].amount_base += amount

            if security.name not in stats:
                stats[security.name] = AssetStats(
                    name=security.name,
                    amount_base=amount,
                    amount_native=account.securities[security] * security.price,
                    root_asset_type=RootAssetType.SECURITY,
                    children=[],
                    parent=stats[security.type_],
                )
                stats[security.type_].children.append(stats[security.name])
            else:
                stats[security.name].amount_base += amount
                stats[security.name].amount_native += (
                    account.securities[security] * security.price
                )
            stats["Securities"].amount_base += amount

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
