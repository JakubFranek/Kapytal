from decimal import Decimal


def get_decimal_exponent(value: Decimal) -> int:
    exponent = -value.as_tuple().exponent
    if not isinstance(exponent, int):
        raise ValueError("Supplied Decimal is not finite.")  # noqa: TRY004
    return exponent
