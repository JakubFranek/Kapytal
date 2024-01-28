import locale
import numbers
from decimal import Decimal

DECIMAL_ONE = Decimal(1)

quantizers: dict[int, Decimal] = {i: Decimal(f"1e-{i}") for i in range(18 + 1)}


def format_real(number: numbers.Real, decimals: int = 2) -> str:
    """Returns a string representation of a number with min_decimals precision.
    Is locale-aware and includes group separators."""
    return locale.format_string(f"%.{decimals}f", number, grouping=True)


def format_percentage(
    number: numbers.Real, max_length: int = 12, decimals: int = 2
) -> str:
    return_text = f"{format_real(number, decimals)} %"
    if len(return_text) <= max_length:
        return return_text
    return f"{locale.format_string(f"%.{decimals}e", number, grouping=True)} %"


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
            return "≈" + f"{_value:n}" if _value != value else f"{_value:n}"

        # simple rounding for non-integral numbers outside (-1,1)
        _value = round(value, significant_digits).normalize()
        _value = _quantize_if_needed(_value, min_decimals)
        return "≈" + f"{_value:n}" if _value != value else f"{_value:n}"

    # no rounding for integral numbers
    return (
        f"{value.quantize(DECIMAL_ONE):n}"
        if min_decimals is None
        else locale.format_string(f"%.{min_decimals}f", value, grouping=True)
    )


def _quantize_if_needed(value: Decimal, min_decimals: int | None) -> Decimal:
    if min_decimals is not None:
        exponent = -value.as_tuple().exponent
        if exponent < min_decimals:
            return value.quantize(quantizers[min_decimals])
    return value
