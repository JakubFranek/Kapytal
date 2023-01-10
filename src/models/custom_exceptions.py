class AlreadyExistsError(ValueError):
    """Raised when an attempt is made to add an object which already exists."""


class InvalidCharacterError(ValueError):
    """Raised when invalid character is passed."""


class InvalidOperationError(Exception):
    """Raised when an invalid operation is attempted."""
