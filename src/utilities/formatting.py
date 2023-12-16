import numbers


def get_short_percentage_string(
    number: numbers.Real, max_length: int = 12, decimals: int = 2
) -> str:
    return_text = f"{number:,.{decimals}f} %"
    if len(return_text) <= max_length:
        return return_text
    return f"{number:,.{decimals}e} %"
