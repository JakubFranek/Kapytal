from decimal import Decimal

import pytest
from src.utilities.formatting import (
    convert_decimal_to_string,
)

test_data = {
    Decimal("97.100000"): "97.1",
    Decimal("97.000000"): "97",
    Decimal("123456789.123456789"): "≈123,456,789.1235",
    Decimal("123456789.1234"): "123,456,789.1234",
    Decimal("1.000012345"): "≈1",
    Decimal("1.00001234"): "≈1",
    Decimal("1.012345"): "≈1.0123",
    Decimal("1.01234"): "≈1.0123",
    Decimal("1.12345"): "≈1.1234",
    Decimal("1.1234"): "1.1234",
    Decimal("1.123"): "1.123",
    Decimal("1.12"): "1.12",
    Decimal("1.1"): "1.1",
    Decimal("0.000012345"): "≈0.00001234",
    Decimal("0.00001234"): "0.00001234",
    Decimal("0.012345"): "≈0.01234",
    Decimal("0.01234"): "0.01234",
    Decimal("0.12345"): "≈0.1234",
    Decimal("0.1234"): "0.1234",
    Decimal("0.123"): "0.123",
    Decimal("0.12"): "0.12",
    Decimal("0.1"): "0.1",
    Decimal("-0.000012345"): "≈-0.00001234",
    Decimal("-0.00001234"): "-0.00001234",
    Decimal("-0.012345"): "≈-0.01234",
    Decimal("-0.01234"): "-0.01234",
    Decimal("-0.12345"): "≈-0.1234",
    Decimal("-0.1234"): "-0.1234",
    Decimal("-0.123"): "-0.123",
    Decimal("-0.12"): "-0.12",
    Decimal("-0.1"): "-0.1",
    Decimal(0): "0",
    Decimal(1): "1",
    Decimal(10): "10",
    Decimal(100): "100",
    Decimal("5.7E+2"): "570",
    Decimal(1000): "1,000",
    Decimal(10_000): "10,000",
    Decimal(100_000): "100,000",
    Decimal(1_000_000): "1,000,000",
}

test_data_2_decimals = {
    Decimal("97.100000"): "97.10",
    Decimal("97.000000"): "97.00",
    Decimal("123456789.123456789"): "≈123,456,789.1235",
    Decimal("123456789.1234"): "123,456,789.1234",
    Decimal("1.000012345"): "≈1.00",
    Decimal("1.00001234"): "≈1.00",
    Decimal("1.012345"): "≈1.0123",
    Decimal("1.01234"): "≈1.0123",
    Decimal("1.12345"): "≈1.1234",
    Decimal("1.1234"): "1.1234",
    Decimal("1.123"): "1.123",
    Decimal("1.12"): "1.12",
    Decimal("1.1"): "1.10",
    Decimal("0.000012345"): "≈0.00001234",
    Decimal("0.00001234"): "0.00001234",
    Decimal("0.012345"): "≈0.01234",
    Decimal("0.01234"): "0.01234",
    Decimal("0.12345"): "≈0.1234",
    Decimal("0.1234"): "0.1234",
    Decimal("0.123"): "0.123",
    Decimal("0.12"): "0.12",
    Decimal("0.1"): "0.10",
    Decimal("-0.000012345"): "≈-0.00001234",
    Decimal("-0.00001234"): "-0.00001234",
    Decimal("-0.012345"): "≈-0.01234",
    Decimal("-0.01234"): "-0.01234",
    Decimal("-0.12345"): "≈-0.1234",
    Decimal("-0.1234"): "-0.1234",
    Decimal("-0.123"): "-0.123",
    Decimal("-0.12"): "-0.12",
    Decimal("-0.1"): "-0.10",
    Decimal(0): "0.00",
    Decimal(1): "1.00",
    Decimal(10): "10.00",
    Decimal(100): "100.00",
    Decimal("5.7E+2"): "570.00",
    Decimal(1000): "1,000.00",
    Decimal(10_000): "10,000.00",
    Decimal(100_000): "100,000.00",
    Decimal(1_000_000): "1,000,000.00",
}


@pytest.mark.parametrize("test_data", test_data.items())
def test_convert_decimal_to_string(test_data: tuple[Decimal, str]) -> None:
    import locale

    locale.setlocale(locale.LC_ALL, "en_US.UTF-8")

    assert convert_decimal_to_string(test_data[0]) == test_data[1]


@pytest.mark.parametrize("test_data", test_data_2_decimals.items())
def test_convert_decimal_to_string_two_decimals(test_data: tuple[Decimal, str]) -> None:
    import locale

    locale.setlocale(locale.LC_ALL, "en_US.UTF-8")
    assert convert_decimal_to_string(test_data[0], min_decimals=2) == test_data[1]


def test_convert_decimal_to_string_twelve_decimals() -> None:
    assert convert_decimal_to_string(Decimal(0), min_decimals=12) == "0.000000000000"


def test_convert_decimal_to_string_czech_locale() -> None:
    import locale

    for locale_name in ["cs_CZ.UTF-8", "cs_CZ"]:
        try:
            locale.setlocale(locale.LC_ALL, locale_name)
            break
        except locale.Error:
            pass
    else:
        pytest.skip("Czech locale not available")

    result = convert_decimal_to_string(
        Decimal("1234567.891234"), significant_digits=2, min_decimals=2
    )
    assert result == "≈1\u202f234\u202f567,89".replace(
        " ",
        "\xa0",  # \xa0 is a non-breaking space
    )
