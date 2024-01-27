import numbers
from decimal import Decimal

DECIMAL_ONE = Decimal(1)

quantizers: dict[int, Decimal] = {i: Decimal(f"1e-{i}") for i in range(18 + 1)}


def get_short_percentage_string(
    number: numbers.Real, max_length: int = 12, decimals: int = 2
) -> str:
    return_text = f"{number:,.{decimals}f} %"
    if len(return_text) <= max_length:
        return return_text
    return f"{number:,.{decimals}e} %"


def convert_decimal_to_string(
    value: Decimal, significant_digits: int = 4, min_decimals: int | None = None
) -> str:
    """Returns a string representation of a Decimal with min_decimals precision.
    Trailing zeroes are removed. An approximate symbol '≈' is prepended to
    the string if the string representation is not exact.
    Floating point numbers are rounded to the specified number of significant digits,
    integral numbers keep all their digits."""

    if value != value.to_integral_value():
        if -1 < value < 1:
            # significant digit rounding for numbers in (-1,1)
            _value = Decimal(f"{value:.{significant_digits}g}")
            _value = _quantize_if_needed(_value, min_decimals)
            return "≈" + f"{_value:,}" if _value != value else f"{_value:,}"

        # simple rounding for non-integral numbers outside (-1,1)
        _value = round(value, significant_digits).normalize()
        _value = _quantize_if_needed(_value, min_decimals)
        return "≈" + f"{_value:,}" if _value != value else f"{_value:,}"

    # no rounding for integral numbers
    return (
        f"{value.quantize(DECIMAL_ONE):,}"
        if min_decimals is None
        else f"{value.quantize(quantizers[min_decimals]):,f}"
    )


def _quantize_if_needed(value: Decimal, min_decimals: int | None) -> Decimal:
    if min_decimals is not None:
        exponent = -value.as_tuple().exponent
        if exponent < min_decimals:
            return value.quantize(quantizers[min_decimals])
    return value
