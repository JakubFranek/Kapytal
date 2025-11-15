IBANS_VALID = (
    "CZ6508000000192000145399",  # Czech Republic
    "DE89370400440532013000",  # Germany
    "GB82WEST12345698765432",  # United Kingdom
    "FR1420041010050500013M02606",  # France
    "NL91ABNA0417164300",  # Netherlands
)

IBANS_INVALID = (
    "CZ6508000000192000145390",  # Wrong checksum
    "CZ650800*000192000145390",  # Special character
    "DE8937040044053201300",  # Too short
    "GB82WEST1234569876543A",  # Contains invalid letter at end
    "FR1420041010050500013M0260X",  # Extra character
    "NL91ABNA0417164301",  # Wrong checksum
)
